# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_api_config.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'David Matthews <@tree1004>']
__status__ = 'development'
__date__ = '2019.07.03'

import os
import unittest

from flask import current_app
from flask_testing import TestCase

from sim_api import create_app

app = create_app()


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        self.app = create_app()
        self.app.config.from_object('configs.flask_conf.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertFalse(current_app is None)
        self.assertTrue(app.config['MONGO_DBNAME'] == 'arc_dev')
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 4)
        self.assertTrue(app.config['TOKEN_EXPIRATION_DAYS'] == 30)
        self.assertTrue(app.config['TOKEN_EXPIRATION_SECONDS'] == 0)


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('configs.flask_conf.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(app.config['MONGO_DBNAME'] == 'arc_test')
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 4)
        self.assertTrue(app.config['TOKEN_EXPIRATION_DAYS'] == 0)
        self.assertTrue(app.config['TOKEN_EXPIRATION_SECONDS'] == 5)


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('configs.flask_conf.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertFalse(app.config['TESTING'])
        self.assertEqual(
            app.config['MONGO_DBNAME'], os.environ.get('MONGO_APP_DB')
        )
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 12)
        self.assertTrue(app.config['TOKEN_EXPIRATION_DAYS'] == 30)
        self.assertTrue(app.config['TOKEN_EXPIRATION_SECONDS'] == 0)


if __name__ == '__main__':
    unittest.main()
