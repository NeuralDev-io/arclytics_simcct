# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_configs.py
# 
# Attributions: 
# [1] 
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.12'
"""test_api_configs.py: 

{Description}
"""

import os
import unittest

from flask import current_app
from flask_testing import TestCase

from sim_api import create_app

app = create_app()


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('configs.flask_configs.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertFalse(current_app is None)
        self.assertTrue(app.config['MONGO_DBNAME'] == 'arc_dev')
        self.assertTrue(app.config['REDIS_DB'] == 1)


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('configs.flask_configs.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(app.config['MONGO_DBNAME'] == 'arc_test')
        self.assertTrue(app.config['REDIS_DB'] == 15)


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('configs.flask_configs.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertTrue(
            app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertFalse(app.config['TESTING'])
        self.assertTrue(app.config['MONGO_DBNAME'] == 'arclytics')
        self.assertTrue(app.config['REDIS_DB'] == 0)


if __name__ == '__main__':
    unittest.main()
