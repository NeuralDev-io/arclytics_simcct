# -*- coding: utf-8 -*-import views, models, resources
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# config.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.09'
"""config.py: 

Just some configuration settings for the SimCCT Flask Server.
"""

import os
import redis


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

    MONGO_HOST = os.environ.get('MONGO_HOST')
    MONGO_PORT = os.environ.get('MONGO_PORT')
    MONGO_USER = os.environ.get('MONGODB_USER')
    MONGO_PASSWORD = os.environ.get('MONGODB_PASSWORD')

    SESSION_PERMANENT = True
    SESSION_USER_SIGNER = True
    SESSION_KEY_PREFIX = 'session:'
    SESSION_TYPE = 'redis'


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    MONGO_DBNAME = 'arc_dev'

    REDIS_DB = 1
    redis_client_dev = redis.Redis(
        host=os.environ.get('REDIS_HOST'),
        port=int(os.environ.get('REDIS_PORT')),
        db=REDIS_DB
    )
    SESSION_REDIS = redis_client_dev


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    MONGO_DBNAME = 'arc_test'

    SESSION_PERMANENT = False
    REDIS_DB = 15
    redis_client_test = redis.Redis(
        host=os.environ.get('REDIS_HOST'),
        port=int(os.environ.get('REDIS_PORT')),
        db=REDIS_DB
    )
    SESSION_REDIS = redis_client_test


class ProductionConfig(BaseConfig):
    """Production configuration"""
    MONGO_DBNAME = 'arclytics'

    REDIS_DB = 0
    redis_client_prod = redis.Redis(
        host=os.environ.get('REDIS_HOST'),
        port=int(os.environ.get('REDIS_PORT')),
        db=REDIS_DB
    )
    SESSION_REDIS = redis_client_prod
