# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# extensions.__init__.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '1.1.0'
__status__ = 'development'
__date__ = '2019.10.02'
"""extensions.__init__.py: 

This module just defines extensions for Flask that can be used across the
context of the app.
"""

from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_redis import FlaskRedis
from elasticapm.contrib.flask import ElasticAPM

apm = ElasticAPM()
api = Api()
bcrypt = Bcrypt()
cache = Cache()
redis_client = FlaskRedis()

# Used by the __init__ module to loop and init_app() for each element
flask_extensions = [api, bcrypt, cache, redis_client]

from .utilities import JSONEncoder, API_TOKEN_NAME

__all__ = [
    'apm', 'api', 'bcrypt', 'JSONEncoder', 'flask_extensions', 'API_TOKEN_NAME',
    'redis_client', 'cache'
]
