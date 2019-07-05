# -*- coding: utf-8 -*-import views, models, resources
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# config.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.04'
"""config.py: 

Just some configuration settings.
"""

import os


class BaseConfig:
    """Base configuration"""
    TESTING = False
    BCRYPT_LOG_ROUNDS = 13
    SECRET_KEY = os.environ.get('SECRET_KEY', '')
    TOKEN_EXPIRATION_DAYS = 30
    TOKEN_EXPIRATION_SECONDS = 0


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


class ProductionConfig(BaseConfig):
    """Production configuration"""
    MONGO_DBNAME = 'arclytics'
    BCRYPT_LOG_ROUNDS = 13
