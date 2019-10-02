# -*- coding: utf-8 -*-import views, models, resources
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# flask_conf.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'development'
__date__ = '2019.06.04'
"""flask_conf.py: 

These configurations define the way that a Flask application is create and 
the context used for it.
"""

from os import environ as env
from arc_api.extensions import JSONEncoder


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SECRET_KEY = env.get('SECRET_KEY', None)

    # Flask-RESTful JSON encoder change
    RESTFUL_JSON = {'cls': JSONEncoder}

    # Bcrypt and Token encoding
    BCRYPT_LOG_ROUNDS = 12
    TOKEN_EXPIRATION_DAYS = 30
    TOKEN_EXPIRATION_SECONDS = 0

    # Redis Connection
    redis_host = env.get('REDIS_HOST', None)
    redis_port = env.get('REDIS_PORT', None)

    # fluentd
    FLUENTD_HOST = env.get('FLUENTD_HOST', 'localhost')
    FLUENTD_PORT = env.get('FLUENTD_PORT', 24224)
    FLUENTD_SCHEME = 'http'
    FLUENTD_PREFIX_TAG = 'arclytics.fluentd.logger'

    # elastic application performance monitoring
    ELASTIC_APM = {
        'SERVER_URL':
        env.get('ELASTIC_APM_SERVER_URL', 'http://localhost:8200'),
        'SERVICE_NAME': 'arclytics',
        'SECRET_TOKEN': env.get('SECRET_TOKEN'),
        'CAPTURE_BODY': 'all',
        'DEBUG': True
    }


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    MONGO_DBNAME = 'arc_dev'

    # Bcrypt
    BCRYPT_LOG_ROUNDS = 4


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    MONGO_DBNAME = 'arc_test'
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # Bcrypt
    BCRYPT_LOG_ROUNDS = 4


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    MONGO_DBNAME = env.get('MONGO_APP_DB')

    # Bcrypt
    BCRYPT_LOG_ROUNDS = 12

    # Redis Connection
    REDIS_HOST = env.get('REDIS_HOST', None)
    REDIS_PORT = env.get('REDIS_PORT', None)
    REDIS_PASSWORD = env.get('REDIS_PASSWORD', None)
    redis_uri = f'redis://user:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'

    # production elastic application performance monitoring
    ELASTIC_APM = {
        'SERVER_URL': env.get('ELASTIC_APM_SERVER_URL', None),
        'SERVICE_NAME': 'arclytics',
        'CAPTURE_BODY': 'all',
        'DEBUG': False,
    }
