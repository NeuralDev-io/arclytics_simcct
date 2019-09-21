# -*- coding: utf-8 -*-import views, models, resources
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# flask_conf.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>',
    'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.04'
"""flask_conf.py: 

These configurations define the way that a Flask application is create and 
the context used for it.
"""

from os import environ as env
from sim_api.extensions.utilities import JSONEncoder


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SECRET_KEY = env.get('SECRET_KEY', None)
    SECURITY_PASSWORD_SALT = env.get('SECURITY_PASSWORD_SALT', None)

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

    # Redis Connection
    redis_host = env.get('REDIS_HOST', None)
    redis_port = env.get('REDIS_PORT', None)

    # CELERY REDIS
    CELERY_BROKER_URL = f'redis://{redis_host}:{redis_port}/5'
    CELERY_RESULT_BACKEND = f'redis://{redis_host}:{redis_port}/6'

    # fluentd
    FLUENTD_HOST = env.get('FLUENTD_HOST', 'localhost')
    FLUENTD_PORT = env.get('FLUENTD_PORT', 24224)
    FLUENTD_SCHEME = 'http'
    FLUENTD_PREFIX_TAG = 'simcct.fluentd.logger'

    # elastic application performance monitoring
    ELASTIC_APM = {
        'SERVER_URL': env.get('ELASTIC_APM_SERVER_URL', 'http://localhost:8200'),
        'SERVICE_NAME': 'simcct',
        'SECRET_TOKEN': SECRET_KEY,
        'DEBUG': True
    }


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
    MONGO_DBNAME = env.get('MONGO_APP_DB')
    BCRYPT_LOG_ROUNDS = 12

    # Redis Connection
    REDIS_HOST = env.get('REDIS_HOST', None)
    REDIS_PORT = env.get('REDIS_PORT', None)
    REDIS_PASSWORD = env.get('REDIS_PASSWORD', None)
    redis_uri = f'redis://user:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'

    # Production Celery
    CELERY_BROKER_URL = f'{redis_uri}/5'
    CELERY_RESULT_BACKEND = f'{redis_uri}/6'

    # production elastic application performance monitoring
    ELASTIC_APM = {
        'SERVICE_NAME': 'simcct',
        'SECRET_TOKEN': env.get('SECRET_KEY'),
        'DEBUG': False
    }
