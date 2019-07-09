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


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', '')


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    MONGO_DBNAME = 'simcct_dev'


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    MONGO_DBNAME = 'simcct_test'


class ProductionConfig(BaseConfig):
    """Production configuration"""
    MONGO_DBNAME = 'simcct'
