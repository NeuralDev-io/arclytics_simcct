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
    SECRET_KEY = os.environ.get('SECRET_KEY', '')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', '')

    # Flask Email
    MAIL_SUBJECT_PREFIX = '[Arclytics]'
    MAIL_DEFAULT_SENDER = 'Arclytics Team <admin@arclytics.io>'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', None)
    MAIL_PORT = int(os.environ.get('MAIL_PORT', None))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    # Unset this to see the debug messages to logs
    MAIL_DEBUG = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    # CELERY REDIS
    REDIS_HOST = os.environ.get('REDIS_HOST', None)
    REDIS_PORT = os.environ.get('REDIS_PORT', None)
    CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/5'
    CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/6'


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SESSION_PERMANENT = False

    # CELERY REDIS
    REDIS_HOST = os.environ.get('REDIS_HOST', None)
    REDIS_PORT = os.environ.get('REDIS_PORT', None)
    CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/5'
    CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/6'


class ProductionConfig(BaseConfig):
    """Production configuration"""
    # CELERY REDIS
    REDIS_HOST = os.environ.get('REDIS_HOST', None)
    REDIS_PORT = os.environ.get('REDIS_PORT', None)
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    redis_uri = f'redis://user:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'
    CELERY_BROKER_URL = f'{redis_uri}/5'
    CELERY_RESULT_BACKEND = f'{redis_uri}/6'
