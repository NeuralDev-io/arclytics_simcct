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

import os
import json
import re
import time
from datetime import timedelta, datetime, timezone
from uuid import uuid4

from flask.sessions import SessionMixin, SessionInterface
from redis import ReadOnlyError
from redis import Redis
from werkzeug.datastructures import CallbackDict


SESSION_EXPIRY_MINUTES = 60
SESSION_COOKIE_NAME = 'session'


def utctimestamp_by_second(utc_date_time):
    return int((utc_date_time.replace(tzinfo=timezone.utc).timestamp()))


class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(s):
            s.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    def __init__(self, redis=None):
        if redis is None:
            if os.environ.get('FLASK_ENV', 'development') == 'production':
                self.redis = Redis(
                    host=os.environ.get('REDIS_HOST'),
                    port=int(os.environ.get('REDIS_PORT')),
                    password=os.environ.get('REDIS_PASSWORD'),
                    db=1,
                )
            else:
                self.redis = Redis(
                    host=os.environ.get('REDIS_HOST'),
                    port=int(os.environ.get('REDIS_PORT')),
                    db=1,
                )

    def open_session(self, app, request):
        session_key = request.cookies.get(SESSION_COOKIE_NAME)
        if not session_key:
            return self._new_session()

        sid, expiry_timestamp = self._extract_sid_and_expiry_ts_from(
            session_key
        )
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
        user_id = session.get('user_id')

        def session_is_modified_empty():
            return not session and session.modified

        def session_is_invalid():
            return not user_id

        if session_is_modified_empty() or session_is_invalid():
            self._clean_redis_and_cookie(app, response, session)
            return

        redis_value = json.dumps(dict(session))
        expiry_duration = self._get_expiry_duration(app, session)
        expiry_date = datetime.utcnow() + expiry_duration
        expires_in_seconds = int(expiry_duration.total_seconds())

        session.sid = self._inject_user_id_in_sid(session.sid, user_id)
        session_key = self._create_session_key(session.sid, expiry_date)

        self._write_wrapper(
            self.redis.setex,
            self._redis_key(session.sid),
            redis_value,
            expires_in_seconds
        )

        response.set_cookie(
            SESSION_COOKIE_NAME, session_key, expires=expiry_date,
            httponly=True, domain=self.get_cookie_domain(app)
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
    def _redis_key(sid):
        return 's:{}'.format(sid)

    def _write_wrapper(self, write_method, *args):
        for i in range(3):
            try:
                write_method(*args)
                break
            except ReadOnlyError:
                self.redis.connection_pool.reset()
                time.sleep(1)

    def _get_redis_value_and_ttl_of(self, sid):
        redis_key = self._redis_key(sid)
        pipeline = self.redis.pipeline()
        pipeline.get(redis_key)
        pipeline.ttl(redis_key)
        results = pipeline.execute()

        return tuple(results)

    @staticmethod
    def _expiry_timestamp_not_match(expiry_timestamp, redis_key_ttl):
        datetime_from_ttl = datetime.utcnow() + timedelta(seconds=redis_key_ttl)
        timestamp_from_ttl = utctimestamp_by_second(datetime_from_ttl)

        try:
            return abs(int(expiry_timestamp) - timestamp_from_ttl) > 10
        except (ValueError, TypeError):
            return True

    @staticmethod
    def _extract_sid_and_expiry_ts_from(session_key):
        matched = re.match(r"^(.+)\.(\d+)$", session_key)
        if not matched:
            return session_key, None

        return matched.group(1), matched.group(2)

    @staticmethod
    def _create_session_key(sid, expiry_date):
        return "{}.{}".format(sid, utctimestamp_by_second(expiry_date))

    @staticmethod
    def _inject_user_id_in_sid(sid, user_id):
        prefix = "{}.".format(user_id)
        if not sid.startswith(prefix):
            sid = prefix + sid
        return sid

    def _clean_redis_and_cookie(self, app, response, session):
        self._write_wrapper(self.redis.delete, self._redis_key(session.sid))
        response.delete_cookie(
            SESSION_COOKIE_NAME, domain=self.get_cookie_domain(app)
        )
