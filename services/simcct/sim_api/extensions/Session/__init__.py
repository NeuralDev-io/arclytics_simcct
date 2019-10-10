# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# __init__.py.py
#
# Attributions:
# Inspiration for this design largely drew from the below.
# [1] https://github.com/mrichman/flask-redis
# [2] https://pythonhosted.org/Flask-Session/
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.09.06'
"""__init__.py: 

The Session package to change the Flask Session interface to use the Redis
as a server-side storage and to customise the way we want to encode our 
Session ID and Session Key.
"""

from .redis_session import (
    RedisSessionInterface, API_TOKEN_NAME, SESSION_COOKIE_NAME
)


class FlaskRedisSession(object):
    _redis_session_interface = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    @classmethod
    def init_app(cls, app):
        cls._redis_session_interface = RedisSessionInterface(app=app)
        app.session_interface = cls._redis_session_interface

    @property
    def interface(self):
        return self._redis_session_interface


__all__ = [
    'FlaskRedisSession', 'RedisSessionInterface', 'SESSION_COOKIE_NAME',
    'API_TOKEN_NAME'
]
