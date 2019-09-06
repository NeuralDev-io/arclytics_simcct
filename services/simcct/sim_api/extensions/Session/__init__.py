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

__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.09.06'

"""__init__.py.py: 

The Session package to change the Flask Session interface to use the Redis
as a server-side storage and to customise the way we want to encode our 
Session ID and Session Key.
"""

from .redis_session import RedisSessionInterface


class FlaskRedisSession(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    @staticmethod
    def init_app(app):
        app.session_interface = RedisSessionInterface(app=app)
