# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_configs.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.12'
"""test_api_configs.py: 

This module tests the configurations are as we expect them. 
"""

import os
import unittest

from flask import current_app
from flask_testing import TestCase

from sim_app.app import create_app, mongo, sess

app = create_app()


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('configs.flask_conf.DevelopmentConfig')
        mongo.init_app(app)
        sess.init_app(app)
        return app

    def test_app_is_development(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertFalse(current_app is None)
        self.assertTrue(app.config['MONGO_DBNAME'] == 'arc_dev')
        self.assertTrue(app.config['REDIS_DB'] == 1)
        self.assertEqual(mongo.db.name, 'arc_dev')
        # This is very stupid I know, but I can't find another way.
        redis = app.config['SESSION_REDIS']
        self.assertEqual(int(str(redis)[56:57]), 1)


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('configs.flask_conf.TestingConfig')
        mongo.init_app(app)
        sess.init_app(app)
        return app

    def test_app_is_testing(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(app.config['MONGO_DBNAME'] == 'arc_test')
        self.assertEqual(mongo.db.name, 'arc_test')
        self.assertTrue(app.config['REDIS_DB'] == 15)
        self.assertTrue(app.config['SESSION_REDIS'])
        redis = app.config['SESSION_REDIS']
        self.assertEqual(int(str(redis)[56:58]), 15)


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('configs.flask_conf.ProductionConfig')
        mongo.init_app(app)
        sess.init_app(app)
        return app

    def test_app_is_production(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertFalse(app.config['TESTING'])
        self.assertTrue(app.config['MONGO_DBNAME'] == 'arclytics')
        self.assertTrue(app.config['REDIS_DB'] == 0)
        self.assertEqual(mongo.db.name, 'arclytics')
        redis = app.config['SESSION_REDIS']
        self.assertEqual(int(str(redis)[56:57]), 0)


if __name__ == '__main__':
    unittest.main()
