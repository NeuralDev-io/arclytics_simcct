# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_api_config.py
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
__date__ = '2019.07.03'
"""test_api_config.py: 

This test module ensures all configuration settings for the API server is as expected.
"""

import os
import unittest

from flask import current_app
from flask_testing import TestCase

from users_app import create_app

app = create_app()


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('users_app.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY', '')
        )
        self.assertFalse(current_app is None)
        self.assertTrue(app.config['MONGO_DBNAME'] == 'arc_dev')
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 4)
        self.assertTrue(app.config['TOKEN_EXPIRATION_DAYS'] == 30)
        self.assertTrue(app.config['TOKEN_EXPIRATION_SECONDS'] == 0)


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('users_app.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY', '')
        )
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(app.config['MONGO_DBNAME'] == 'arc_test')
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 4)
        self.assertTrue(app.config['TOKEN_EXPIRATION_DAYS'] == 0)
        self.assertTrue(app.config['TOKEN_EXPIRATION_SECONDS'] == 5)


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('users_app.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY', '')
        )
        self.assertFalse(app.config['TESTING'])
        self.assertTrue(app.config['MONGO_DBNAME'] == 'arclytics')
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 13)
        self.assertTrue(app.config['TOKEN_EXPIRATION_DAYS'] == 30)
        self.assertTrue(app.config['TOKEN_EXPIRATION_SECONDS'] == 0)


if __name__ == '__main__':
    unittest.main()
