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
__date__ = '2019.06.04'
"""flask_conf.py: 

Just some configuration settings.
"""

import os
from sim_api.extensions.utilities import JSONEncoder


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', None)
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', None)

    # Bcrypt and Token encoding
    BCRYPT_LOG_ROUNDS = 12
    RESTFUL_JSON = {'cls': JSONEncoder}
    TOKEN_EXPIRATION_DAYS = 30
    TOKEN_EXPIRATION_SECONDS = 0

    # Session variables for Flask
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_PERMANENT = True
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True

    # CELERY REDIS
    REDIS_HOST = os.environ.get('REDIS_HOST', None)
    REDIS_PORT = os.environ.get('REDIS_PORT', None)
    CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/5'
    CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/6'


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    MONGO_DBNAME = 'arc_dev'
    BCRYPT_LOG_ROUNDS = 4


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    MONGO_DBNAME = 'arc_test'
    BCRYPT_LOG_ROUNDS = 4
    TOKEN_EXPIRATION_DAYS = 0
    TOKEN_EXPIRATION_SECONDS = 5
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    SESSION_PERMANENT = False
    REDIS_DB = 2


class ProductionConfig(BaseConfig):
    """Production configuration"""
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    MONGO_DBNAME = os.environ.get('MONGO_APP_DB')
    BCRYPT_LOG_ROUNDS = 12

    # Production Celery
    REDIS_HOST = os.environ.get('REDIS_HOST', None)
    REDIS_PORT = os.environ.get('REDIS_PORT', None)
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    redis_uri = f'redis://user:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'
    CELERY_BROKER_URL = f'{redis_uri}/5'
    CELERY_RESULT_BACKEND = f'{redis_uri}/6'
