# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# sim_session.py
#
# Attributions:
# [1] https://gist.github.com/wushaobo/52be20bc801243dddf52a8be4c13179a
# [2] https://github.com/mrichman/flask-redis
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.08'
"""sim_session.py: 

This module defines the class to create a RedisSession instance and the
interface to validate and operate on the Redis store of this session. 
"""

import json
import time
from datetime import timedelta, datetime, timezone
from typing import Union, Tuple

from flask import session
from redis import ReadOnlyError
from itsdangerous import (
    TimedJSONWebSignatureSerializer, JSONWebSignatureSerializer, BadSignature,
    SignatureExpired
)

from sim_api.extensions.utilities import JSONEncoder
from logger.arc_logger import AppLogger

logger = AppLogger(__name__)

SESSION_PREFIX = 'simulation'
SESSION_EXPIRY_MINUTES = 120


class SimSession(object):
    def __init__(self):
        pass


class SaveSessionError(Exception):
    """Raises an Exception if save_session fails in any way."""
    msg = 'Unable to save a Simulation Session Data Store.'

    def __init__(self, message=msg):
        super(SaveSessionError, self).__init__(f'{message}')


def utc_timestamp_by_second(utc_date_time: datetime) -> int:
    """Helper to convert datetime objects to timestamp integers."""
    return int((utc_date_time.replace(tzinfo=timezone.utc).timestamp()))


class SimSessionService(object):
    """The interface defines how a service for Simulation Session works."""
    def __init__(self):
        self.session = session

    def new_session(self, session_data: dict) -> None:
        # The storage value dumped to JSON format. We use our custom JSON
        # Encoder to ensure that numpy.floats get serialized properly
        sim_session_data = JSONEncoder().encode(session_data)
        self.session['simulation'] = sim_session_data

    def save_session(self, sid: str, session_data: dict) -> None:

        if sid is None or not session_data:
            raise SaveSessionError()

        # The storage value dumped to JSON format
        # We use our custom JSON Encoder to ensure that numpy.floats get
        # serialized properly
        redis_value = JSONEncoder().encode(session_data)

        # TODO(andrew@neuraldev.io): Doing the refresh without generating a new
        #  Session Key that has a expiration encoded within will cause the two
        #  timestamps to not match on an additional updates. Hacked a fix for
        #  now in _expiry_timestamp_not_match().
        # We refresh the TTL in Redis at every save to keep the data for longer.
        expiry_duration = self._get_expiry_duration()
        expires_in_seconds = int(expiry_duration.total_seconds())

    def load_session(self, session_key: str
                     ) -> Union[Tuple[str, dict], Tuple[None, str]]:
        """We load the User's current Session from the Redis datastore by
        taking in a session key and decoding it to generate the session ID.

        Args:
            session_key: the encoded session key required to get the session ID.

        Returns:
            None if there is a decoding error or the Session ID and the data.
        """
        sid, expiry_timestamp = self._decode_sid_and_expiry_from(session_key)

        if not expiry_timestamp:
            return None, 'Cannot decode timestamp from Session key.'

        # We access the Redis Datastore and get the Session data and it's
        # Time To Live (TTL) value of the current store
        redis_value, redis_key_ttl = self._get_redis_value_and_ttl_of(sid)
        if not redis_value:
            return None, 'Cannot retrieve data from Redis.'

        if self._expiry_timestamp_not_match(expiry_timestamp, redis_key_ttl):
            return None, 'Session timestamp does not match Redis TTL.'

        sess_data = json.loads(redis_value.decode())

        # Return the data as a dict and the sid to be used later for saving
        return sid, sess_data

    def clean_simulation_session(self, session_key: str) -> None:
        """Used to remove the Session from the Redis datastore.

        Args:
            session_key: the encoded session key required to get the session ID.

        Returns:
            None
        """
        sid, expiry_timestamp = self._decode_sid_and_expiry_from(session_key)

        if not expiry_timestamp:
            return None

        # Use the wrapper method to delete
        self._write_wrapper(self.redis.delete, self._redis_key(sid))

    @staticmethod
    def _get_expiry_duration():
        return timedelta(minutes=SESSION_EXPIRY_MINUTES)

    def _encode_token_and_sid(self, sid, token):
        """We simply encode the Session ID and Token to avoid collisions."""
        s = JSONWebSignatureSerializer(secret_key=self.secret_key)
        return s.dumps({'sid': sid, 'token': token}, salt=self.salt)

    def _generate_session_key(self, sid, expiry_date):
        """We generate the Session Key as timed to ensure expiry."""
        expiry_seconds = utc_timestamp_by_second(expiry_date)
        s = TimedJSONWebSignatureSerializer(
            secret_key=self.secret_key, expires_in=expiry_seconds
        )
        return s.dumps(
            {
                'sid': sid,
                'expiry_seconds': expiry_seconds
            }, salt=self.salt
        )

    @staticmethod
    def _redis_key(sid):
        """Quick method to add the session prefix to the Redis key."""
        return f'simulation:{sid}'

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

    def _decode_sid_and_expiry_from(
        self, session_key: str
    ) -> Union[Tuple[str, None], Tuple[str, int]]:
        """Decode the """
        s = TimedJSONWebSignatureSerializer(secret_key=self.secret_key)
        try:
            res = s.loads(session_key, salt=self.salt)
        except BadSignature as e:
            return 'BadSignature', None
        except SignatureExpired as e:
            return 'SignatureExpired', None
        return res.get('sid'), res.get('expiry_seconds')

    def _get_redis_value_and_ttl_of(self, sid: str) -> Tuple:
        """We use a Redis pipeline to get the data value and TTL from Redis."""
        redis_key = self._redis_key(sid)
        # Redis pipeline creates a pipeline of commands to execute
        pipeline = self.redis.pipeline()
        pipeline.get(redis_key)
        pipeline.ttl(redis_key)
        results = pipeline.execute()

        return tuple(results)

    @staticmethod
    def _expiry_timestamp_not_match(expiry_timestamp, redis_key_ttl):
        """Simple method to compare the Redis and token timestamps match."""
        datetime_from_ttl = datetime.utcnow() + timedelta(
            seconds=redis_key_ttl
        )
        timestamp_from_ttl = utc_timestamp_by_second(datetime_from_ttl)

        try:
            # TODO(andrew@neuraldev.io): Find a way to refresh the session key
            #  for the client if the expiry is getting within 10 minutes.
            #  For now, we just accept it within 2 hours.
            # logger.debug(str(abs(int(expiry_timestamp) - timestamp_from_ttl)))
            # This checks the time difference between the timestamps in seconds
            return abs(int(expiry_timestamp) - timestamp_from_ttl) > 3600
        except (ValueError, TypeError):
            return True
