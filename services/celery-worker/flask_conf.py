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
__status__ = 'production'
__date__ = '2019.06.04'
"""flask_conf.py: 

Just some configuration settings.
"""
from os import environ as env


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SECRET_KEY = env.get('SECRET_KEY', '')
    SECURITY_PASSWORD_SALT = env.get('SECURITY_PASSWORD_SALT', '')

    # Celery settings
    timezone = 'UTC'

    # Flask Email
    MAIL_SUBJECT_PREFIX = '[Arclytics]'
    MAIL_DEFAULT_SENDER = 'Arclytics Team <admin@arclytics.io>'
    MAIL_SERVER = env.get('MAIL_SERVER', None)
    MAIL_PORT = int(env.get('MAIL_PORT', None))
    MAIL_USE_TLS = True
    MAIL_USERNAME = env.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = env.get('MAIL_PASSWORD', '')
    # Unset this to see the debug messages to logs
    MAIL_DEBUG = False

    # elastic application performance monitoring
    ELASTIC_APM = {
        'SERVER_URL':
        env.get('ELASTIC_APM_SERVER_URL', 'http://localhost:8200'),
        'SERVICE_NAME': 'celery',
        'SECRET_TOKEN': env.get('SECRET_TOKEN'),
        'CAPTURE_BODY': 'all',
        'DEBUG': True
    }


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    # CELERY REDIS
    REDIS_HOST = env.get('REDIS_HOST', None)
    REDIS_PORT = env.get('REDIS_PORT', None)
    CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
    CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/2'


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SESSION_PERMANENT = False

    # CELERY REDIS
    REDIS_HOST = env.get('REDIS_HOST', None)
    REDIS_PORT = env.get('REDIS_PORT', None)
    CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
    CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/2'


class ProductionConfig(BaseConfig):
    """Production configuration"""
    # CELERY REDIS
    REDIS_HOST = env.get('REDIS_HOST', None)
    REDIS_PORT = env.get('REDIS_PORT', None)
    REDIS_PASSWORD = env.get('REDIS_PASSWORD', None)
    redis_uri = f'redis://user:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'
    CELERY_BROKER_URL = f'{redis_uri}/1'
    CELERY_RESULT_BACKEND = f'{redis_uri}/2'

    # production elastic application performance monitoring
    ELASTIC_APM = {
        'SERVER_URL': env.get('ELASTIC_APM_SERVER_URL', None),
        'SERVICE_NAME': 'celery',
        'CAPTURE_BODY': 'all',
        'DEBUG': False,
        # 'SECRET_TOKEN': env.get('ELASTIC_APM_SECRET_TOKEN'),
    }
