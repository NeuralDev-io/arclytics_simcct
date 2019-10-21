# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# redis_session.py
#
# Attributions:
# [1] https://gist.github.com/wushaobo/52be20bc801243dddf52a8be4c13179a
# [2] https://github.com/mrichman/flask-redis
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.08.07'
"""redis_session.py: 

This module implements a Redis Session Server-Side storage using Cookies and
encoding and storing the JWT token which is signed by the server and ensuring 
it is not tampered with at each request. 
"""

import json
import time
from datetime import datetime, timedelta, timezone
from os import environ as env
from typing import Tuple, Union
from uuid import uuid4

import itsdangerous
from flask.sessions import SessionInterface, SessionMixin
from itsdangerous import BadSignature, SignatureExpired
from redis import ReadOnlyError
from werkzeug.datastructures import CallbackDict

from arc_logging import AppLogger
from sim_api.extensions import apm
from sim_api.extensions.utilities import JSONEncoder

logger = AppLogger(__name__)

SESSION_EXPIRY_MINUTES = 120
SESSION_COOKIE_NAME = 'SESSION_TOKEN'
API_TOKEN_NAME = 'JWT_TOKEN'


def utctimestamp_by_second(utc_date_time):
    return int((utc_date_time.replace(tzinfo=timezone.utc).timestamp()))


class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(s):
            s.modified = True
            s.accessed = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False

    def clear(self) -> None:
        """Clear the Session dictionary."""
        super().clear()


class RedisSessionInterface(SessionInterface):
    def __init__(self, app=None, use_signer=True):
        if app is not None:
            self._redis = app.config.get('SESSION_REDIS')
            self._secret_key = app.config.get('SECRET_KEY', None)
            self._salt = app.config.get('SECURITY_PASSWORD_SALT', None)
            self.use_signer = use_signer

    @property
    def redis(self):
        return self._redis

    def open_session(self, app, request) -> Union[None, RedisSession]:
        """This method is called at the beginning of every request in the
        context of a Flask request-response cycle.

        Args:
            app: the current Flask app context.
            request: the request from the client as part of the current context.

        Returns:
            A RedisSession instance whether new with a generated `sid`  or one
            with the data from the Redis data store.
        """
        session_key = request.cookies.get(SESSION_COOKIE_NAME)
        # ip_address: str = request.remote_addr

        # We always generate a new RedisSession is the request does not have
        # the session key.
        if not session_key:
            return self._new_session()

        if self.use_signer:
            signer = self._get_signer()
            if signer is None:
                return None
            try:
                sid_as_bytes = signer.unsign(session_key)
                session_key = sid_as_bytes.decode()
            except BadSignature:
                return self._new_session()

        # If we have both the session key and the JWT in the cookies, then
        # we continue.
        sid, expiry_timestamp = self._extract_sid_and_expiry_ts_from(
            session_key
        )
        if not expiry_timestamp:
            return self._new_session()

        # If we don't get anything back from the Redis data store, it usually
        # means the session has already expired so we create a new one.
        redis_value, redis_key_ttl = self._get_redis_value_and_ttl_of(sid)
        if not redis_value:
            return self._new_session()

        # If the current expiry timestamp from the Cookie and that from Redis
        # does not match, we also make a new session.
        if self._expiry_timestamp_not_match(expiry_timestamp, redis_key_ttl):
            return self._new_session()

        data = json.loads(redis_value.decode())
        return RedisSession(data, sid=sid)

    def save_session(self, app, session, response):
        jwt = session.get('jwt')
        is_admin = session.get('is_admin')

        # Initial verification of the Session

        # If the session is modified to be empty, remove the cookie.
        # If the session is empty, return without setting the cookie.
        if not session:
            if session.modified:
                self._clean_redis_and_cookie(app, response, session)
            return

        # Checking if this session has a JWT or not
        if not jwt:
            self._clean_redis_and_cookie(app, response, session)
            return

        redis_value = JSONEncoder().encode(dict(session))

        # Refresh the cookie expiry time if the cookie and session is valid
        # and we need to send back a new cookie.
        expiry_duration = self._get_expiry_duration(app, session)
        expiry_date = datetime.utcnow() + expiry_duration
        expires_in_seconds = int(expiry_duration.total_seconds())

        session.sid = self._inject_jwt_in_sid(session.sid, jwt)
        session_key = self._create_session_key(session.sid, expiry_date)

        self.write_wrapper(
            self.redis.setex,
            name=self.redis_key(session.sid),
            value=redis_value,
            time=expires_in_seconds
        )

        if self.use_signer:
            session_key = self._get_signer().sign(
                itsdangerous.want_bytes(session_key)
            )

        if env.get('FLASK_ENV', 'production') == 'development':
            response.set_cookie(
                SESSION_COOKIE_NAME,
                session_key,
                expires=expiry_date,
                httponly=True,
                domain=self.get_cookie_domain(app)
            )
            if is_admin:
                response.set_cookie(
                    API_TOKEN_NAME,
                    jwt,
                    expires=expiry_date,
                    httponly=True,
                    domain=self.get_cookie_domain(app)
                )
        else:
            response.set_cookie(
                SESSION_COOKIE_NAME,
                session_key,
                expires=expiry_date,
                httponly=True,
                secure=True,
                domain=self.get_cookie_domain(app)
            )
            if is_admin:
                response.set_cookie(
                    API_TOKEN_NAME,
                    jwt,
                    expires=expiry_date,
                    httponly=True,
                    secure=True,
                    domain=self.get_cookie_domain(app)
                )

    @staticmethod
    def _new_session():
        return RedisSession(sid=uuid4().hex, new=True)

    @staticmethod
    def _get_expiry_duration(app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(minutes=SESSION_EXPIRY_MINUTES)

    @staticmethod
    def redis_key(sid):
        return 'session:{}'.format(sid)

    def _get_signer(self):
        if not self._secret_key:
            apm.capture_message('Secret key not set.')
            logger.error({'message': 'Secret key not set.'})
            return None
        if not self._salt:
            apm.capture_message('Salt not set.')
            logger.error({'message': 'Salt not set.'})
            return None
        return itsdangerous.Signer(
            secret_key=self._secret_key,
            salt=self._salt,
            key_derivation='hmac'
        )

    def write_wrapper(self, write_method, *args, **kwargs) -> None:
        """A basic wrapper to call redis-py methods but allows us to set a
        retry of 3 attempts if there are Redis ReadOnlyErrors.

        Args:
            write_method: the `redis-py` method to use.
            *args: arguments.
            **kwargs: keyword arguments.

        Returns:
            None
        """
        for i in range(3):
            try:
                write_method(*args, **kwargs)
                break
            except ReadOnlyError:
                logger.exception('Redis Read error.')
                apm.capture_exception()
                self.redis.connection_pool.reset()
                time.sleep(1)

    def _get_redis_value_and_ttl_of(self, sid):
        """Get the Session value stored in Redis and the Time To Live (TTL)
        of the store in Redis.

        Args:
            sid: the session id.

        Returns:
            A tuple of results.
        """
        redis_key = self.redis_key(sid)
        pipeline = self.redis.pipeline()
        pipeline.get(redis_key)
        pipeline.ttl(redis_key)
        results = pipeline.execute()
        return tuple(results)

    @staticmethod
    def _expiry_timestamp_not_match(expiry_timestamp, redis_key_ttl):
        datetime_from_ttl = datetime.utcnow() + timedelta(
            seconds=redis_key_ttl
        )
        timestamp_from_ttl = utctimestamp_by_second(datetime_from_ttl)

        try:
            return abs(int(expiry_timestamp) - timestamp_from_ttl) > 10
        except (ValueError, TypeError):
            apm.capture_exception()
            return True

    def _extract_sid_and_expiry_ts_from(
        self, session_key: str
    ) -> Union[Tuple[str, None], Tuple[str, int]]:
        """Given the session key, we decode it using the `itsdangerous` package.

        Args:
            session_key: an encoded session key with the
            `itsdangerous.TimedJSONWebSignatureSerializer`

        Returns:
            A Tuple of (str, None) if there is any errors or (str, int).
        """
        s = itsdangerous.TimedJSONWebSignatureSerializer(
            secret_key=self._secret_key
        )

        try:
            res = s.loads(session_key, salt=self._salt)
        except BadSignature:
            logger.exception('Bad Signature.')
            apm.capture_exception()
            return 'BadSignature', None
        except SignatureExpired:
            logger.exception('Signature Expired')
            apm.capture_exception()
            return 'SignatureExpired', None
        return res.get('sid'), res.get('expiry_seconds')

    def _create_session_key(self, sid, expiry_date):
        """We use the `itsdangerous` package to encode the session id and
        expiry time using the `itsdangerous.TimedJSONWebSignatureSerializer`
        which ensures attempting to rainbow attack or have any collisions.

        Args:
            sid: the session id in uuid4 format.
            expiry_date: the date that this session will expire.

        Returns:
            The newly created session key with the session id and expiry time
            in seconds encoded.
        """
        expiry_in_seconds = utctimestamp_by_second(expiry_date)
        s = itsdangerous.TimedJSONWebSignatureSerializer(
            secret_key=self._secret_key, expires_in=expiry_in_seconds
        )
        return s.dumps(
            {
                'sid': sid,
                'expiry_seconds': expiry_in_seconds
            }, salt=self._salt
        )

    @staticmethod
    def _inject_jwt_in_sid(sid, jwt):
        """We simply inject the JWT into the Session ID to further encode."""
        prefix = "{}.".format(jwt)
        if not sid.startswith(prefix):
            sid = prefix + sid
        return sid

    def _clean_redis_and_cookie(self, app, response, session):
        """If the Cookie is bad, we clear out the Cookie and Redis store."""
        self.write_wrapper(self.redis.delete, self.redis_key(session.sid))
        response.delete_cookie(
            API_TOKEN_NAME, domain=self.get_cookie_domain(app)
        )
        response.delete_cookie(
            SESSION_COOKIE_NAME, domain=self.get_cookie_domain(app)
        )
