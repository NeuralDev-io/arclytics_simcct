# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# redis_session.py
#
# Attributions:
# [1] https://gist.github.com/wushaobo/52be20bc801243dddf52a8be4c13179a
# [2] https://github.com/mrichman/flask-redis
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.07'
"""redis_session.py: 

This module implements a Redis Session Server-Side storage without using Cookies
but instead encoding and storing the JWT token and ensuring it is not tampered
with at each request. 
"""

import json
import time
from datetime import timedelta, datetime, timezone
from uuid import uuid4

from itsdangerous import (
    TimedJSONWebSignatureSerializer, JSONWebSignatureSerializer, BadSignature,
    SignatureExpired
)
from flask.sessions import SessionMixin, SessionInterface
from redis import Redis, ReadOnlyError
from werkzeug.datastructures import CallbackDict

from logger.arc_logger import AppLogger

logger = AppLogger(__name__)

SESSION_EXPIRY_MINUTES = 60
SESSION_COOKIE_NAME = "session"


def utc_timestamp_by_second(utc_date_time):
    return int((utc_date_time.replace(tzinfo=timezone.utc).timestamp()))


class RedisSession(CallbackDict, SessionMixin):
    """The class to create a new <RedisSession > Flask Session instance."""

    def __init__(self, initial=None, sid=None, new=False):
        def on_update(s):
            s.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    """The interface defines how a Session is stored and opened in Flask. When
    initialising the interface, it will automatically make instantiate a Redis
    client connection and set `app.session_interface` to itself.

        Usage:
            Option A.
            session = RedisSessionInterface(app)

            Option B.
            session = RedisSessionInterface()

            session.init_app(app)
    """

    def __init__(self, app=None):
        # self.redis = redis if redis is not None else Redis()
        if app:
            self.redis = Redis(
                host=app.config['REDIS_HOST'],
                port=int(app.config['REDIS_PORT']),
                db=int(app.config['REDIS_DB']),
            )
            # Store some secret Hydra stuff
            self.secret_key = app.config.get('SECRET_KEY', None)
            app.secret_key = self.secret_key
            self.salt = app.config.get('SECURITY_PASSWORD_SALT', None)
            # This is where the "magic" happens
            app.session_interface = self

    def init_app(self, app):
        """Flask contextualised initialisation of the RedisSessionInterface."""
        self.redis = Redis(
            host=app.config['REDIS_HOST'],
            port=int(app.config['REDIS_PORT']),
            db=int(app.config['REDIS_DB']),
        )
        # Store some secret Hydra stuff
        self.secret_key = app.config.get('SECRET_KEY', None)
        app.secret_key = self.secret_key
        self.salt = app.config.get('SECURITY_PASSWORD_SALT', None)
        # This is where the "magic" happens with changing the Session interface
        app.session_interface = self

    def open_session(self, app, request):
        # Traditionally a Session implementation will use a Cookie
        # session_key = request.cookies.get(SESSION_COOKIE_NAME)

        # logger.debug(f'open_session(): request: {request.__dict__}')

        # Our middleware will ensure all the requests sent to this server
        # will have the correct header.
        auth_header = request.headers.get('Authorization')
        sid_header = request.headers.get('Session')

        # No auth header means a new Session needs to be initiated
        if not auth_header:
            return self._new_session()

        if not sid_header:
            return self._new_session()

        # We use the JWT Auth Token as the key instead
        jwt_token = auth_header.split(' ')[1]

        sid, expiry_timestamp = self._decode_sid_and_expiry_timestamp_from(
            session_key=sid_header
        )
        # token_sid = self._decode_token_from(session.sid)

        if not expiry_timestamp:
            return self._new_session()

        redis_value, redis_key_ttl = self._get_redis_value_and_ttl_of(sid)
        if not redis_value:
            return self._new_session()

        if self._expiry_timestamp_not_match(expiry_timestamp, redis_key_ttl):
            return self._new_session()

        data = json.loads(redis_value.decode())
        return RedisSession(data, sid=sid)

    def save_session(self, app, session, response):
        # Get the user_id that must be set in the session
        # user_id = session.get('user_id')
        token = session.get('token')

        # Inner methods to check if the session has been modified
        def session_is_modified_empty():
            return not session and session.modified

        def session_is_invalid():
            return not token

        # If the session is modified to be empty, remove the cookie.
        if session_is_modified_empty() or session_is_invalid():
            # If the session is empty, return without setting the cookie.
            self._clean_redis_and_cookie(app, response, session)
            return

        redis_value = json.dumps(dict(session))
        expiry_duration = self._get_expiry_duration(app, session)
        expiry_date = datetime.utcnow() + expiry_duration
        expires_in_seconds = int(expiry_duration.total_seconds())

        # session.sid = self._inject_token_in_sid(session.sid, token)
        # session_key = self._create_session_key(session.sid, expiry_date)
        session.sid = self._encode_token_and_sid(session.sid, token)
        session_key = self._generate_session_key(session.sid, expiry_date)

        self._write_wrapper(
            self.redis.setex,
            name=self._redis_key(session.sid),
            value=redis_value,
            time=expires_in_seconds
        )

        # response.set_cookie(
        #     SESSION_COOKIE_NAME,
        #     session_key,
        #     expires=expiry_date,
        #     httponly=True,
        #     domain=self.get_cookie_domain(app)
        # )
        response.headers['session_key'] = session_key

    @staticmethod
    def _new_session():
        """Simple helper method to create a new RedisSession."""
        return RedisSession(sid=uuid4().hex, new=True)

    @staticmethod
    def _get_expiry_duration(app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(minutes=SESSION_EXPIRY_MINUTES)

    @staticmethod
    def _redis_key(sid):
        return 's:{}'.format(sid)

    def _write_wrapper(self, write_method, *args, **kwargs) -> None:
        """Wrapper to be used for redis-py methods to alloy retrying at least
        three times if there is a ReadOnlyError.

        Args:
            write_method: the method to use.
            *args: any arguments to pass to the method.
            **kwargs: any keyword arguments to pass to the method.

        Returns:
            None
        """
        for i in range(3):
            try:
                write_method(*args, **kwargs)
                break
            except ReadOnlyError:
                self.redis.connection_pool.reset()
                time.sleep(1)

    def _get_redis_value_and_ttl_of(self, sid):
        redis_key = self._redis_key(sid)
        # Redis pipeline creates a pipeline of commands to execute
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
        timestamp_from_ttl = utc_timestamp_by_second(datetime_from_ttl)
        try:
            return abs(int(expiry_timestamp) - timestamp_from_ttl) > 10
        except (ValueError, TypeError):
            return True

    def _encode_token_and_sid(self, sid, token):
        serializer = JSONWebSignatureSerializer(secret_key=self.secret_key)
        encoded_str_sid = serializer.dumps(
            {
                'sid': sid,
                'token': token
            }, salt=self.salt
        )
        return encoded_str_sid.decode('utf-8')

    def _generate_session_key(self, sid, expiry_date):
        expiry_seconds = utc_timestamp_by_second(expiry_date)
        serializer = TimedJSONWebSignatureSerializer(
            secret_key=self.secret_key, expires_in=expiry_seconds
        )
        encoded_bytes = serializer.dumps(
            {
                'sid': sid,
                'expiry_seconds': expiry_seconds
            }, salt=self.salt
        )
        return encoded_bytes.decode('utf-8')

    def _decode_sid_and_expiry_timestamp_from(self, session_key):
        serializer = TimedJSONWebSignatureSerializer(
            secret_key=self.secret_key
        )
        try:
            res = serializer.loads(session_key, salt=self.salt)
        except BadSignature as e:
            return 'BadSignature', None
        except SignatureExpired as e:
            return 'SignatureExpired', None
        return res.get('sid'), res.get('expiry_seconds')

    def _decode_token_from(self, sid):
        serializer = JSONWebSignatureSerializer(secret_key=self.secret_key)
        try:
            sid = serializer.loads(sid, salt=self.salt)
        except BadSignature as e:
            return 'BadSignature'
        except SignatureExpired as e:
            return 'SignatureExpired'
        return sid.get('token')

    def _clean_redis_and_cookie(self, app, response, session):
        self._write_wrapper(self.redis.delete, self._redis_key(session.sid))
        response.delete_cookie(
            SESSION_COOKIE_NAME, domain=self.get_cookie_domain(app)
        )
