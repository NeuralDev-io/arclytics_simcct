# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_configs.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.12'

import os
import unittest

from flask import current_app
from flask_testing import TestCase

from sim_app.app import create_app, sess


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        self.app = create_app()
        self.app.config.from_object('configs.flask_conf.DevelopmentConfig')
        sess.init_app(self.app)
        return self.app

    def test_app_is_development(self):
        self.assertTrue(
            self.app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertFalse(current_app is None)
        self.assertTrue(self.app.config['MONGO_DBNAME'] == 'arc_dev')
        self.assertTrue(self.app.config['REDIS_DB'] == 1)
        # This is very stupid I know, but I can't find another way.
        redis = self.app.config['SESSION_REDIS']
        self.assertEqual(int(str(redis)[56:57]), 1)


class TestTestingConfig(TestCase):
    def create_app(self):
        self.app = create_app()
        self.app.config.from_object('configs.flask_conf.TestingConfig')
        sess.init_app(self.app)
        return self.app

    def test_app_is_testing(self):
        self.assertTrue(
            self.app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertTrue(self.app.config['TESTING'])
        self.assertFalse(self.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(self.app.config['MONGO_DBNAME'] == 'arc_test')
        self.assertTrue(self.app.config['REDIS_DB'] == 15)
        self.assertTrue(self.app.config['SESSION_REDIS'])
        redis = self.app.config['SESSION_REDIS']
        self.assertEqual(int(str(redis)[56:58]), 15)


class TestProductionConfig(TestCase):
    def create_app(self):
        self.app = create_app()
        self.app.config.from_object('configs.flask_conf.ProductionConfig')
        sess.init_app(self.app)
        return self.app

    def test_app_is_production(self):
        self.assertTrue(
            self.app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertFalse(self.app.config['TESTING'])
        self.assertTrue(self.app.config['MONGO_DBNAME'] == 'arclytics')
        self.assertTrue(self.app.config['REDIS_DB'] == 0)
        redis = self.app.config['SESSION_REDIS']
        self.assertEqual(int(str(redis)[56:57]), 0)


if __name__ == '__main__':
    unittest.main()
