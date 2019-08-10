# -*- coding: utf-8 -*-import views, models, resources
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# flask_conf.py
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
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')

    PERMANENT_SESSION_LIFETIME = True

    os.environ['MONGO_DBNAME'] = 'arc_dev'

    MONGO_HOST = os.environ.get('MONGO_HOST')
    MONGO_PORT = os.environ.get('MONGO_PORT')
    MONGO_USER = os.environ.get('MONGODB_USER')
    MONGO_PASSWORD = os.environ.get('MONGODB_PASSWORD')

    REDIS_HOST = os.environ.get('REDIS_HOST', None)
    REDIS_PORT = os.environ.get('REDIS_PORT', None)
    REDIS_DB = 0


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    MONGO_DBNAME = 'arc_dev'
    os.environ['MONGO_DBNAME'] = MONGO_DBNAME
    REDIS_DB = 1


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    MONGO_DBNAME = 'arc_test'
    os.environ['MONGO_DBNAME'] = MONGO_DBNAME

    REDIS_DB = 2


class ProductionConfig(BaseConfig):
    """Production configuration"""
    MONGO_DBNAME = 'arclytics'
    # TODO(andrew@neuraldev.io): Ensure the database changes over during
    #  production mode and that there are passwords set on Mongo and Redis.
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
