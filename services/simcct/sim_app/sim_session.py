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
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.08'
"""sim_session.py: 

This module defines the class to create a RedisSession instance and the
interface to validate and operate on the Redis store of this session. 
"""

from redis import Redis

from logger.arc_logger import AppLogger

logger = AppLogger(__name__)


class SimRedisSession(object):
    pass


class SimSessionService(object):
    """The interface defines how a Simulation Session is operated."""
    def __init__(self, app=None):
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



