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


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', None)
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', None)

    # Bcrypt and Token encoding
    BCRYPT_LOG_ROUNDS = 13
    TOKEN_EXPIRATION_DAYS = 30
    TOKEN_EXPIRATION_SECONDS = 0

    # Session variables for Flask
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 1200
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True

    # Flask Email
    MAIL_SUBJECT_PREFIX = '[Arclytics]'
    MAIL_DEFAULT_SENDER = 'Arclytics Team <admin@arclytics.io>'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', None)
    MAIL_PORT = os.environ.get('MAIL_PORT', None)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    # Unset this to see the debug messages to logs
    MAIL_DEBUG = False

    # Redis Queue
    redis_host = os.environ.get('REDIS_HOST', '')
    redis_port = os.environ.get('REDIS_PORT', '')
    REDIS_URL = f'redis://{redis_host}:{redis_port}/14'
    QUEUES = ['default', 'low']


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


class ProductionConfig(BaseConfig):
    """Production configuration"""
    MONGO_DBNAME = 'arclytics'
    BCRYPT_LOG_ROUNDS = 13
