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

import settings
from arc_api.app import create_app


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        self.app = create_app()
        self.app.config.from_object('configs.flask_conf.DevelopmentConfig')
        return self.app

    def test_app_is_development(self):
        self.assertTrue(
            self.app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertFalse(current_app is None)
        self.assertTrue(os.environ.get('MONGO_APP_DB') == 'arc_dev')


class TestTestingConfig(TestCase):
    def create_app(self):
        self.app = create_app()
        self.app.config.from_object('configs.flask_conf.TestingConfig')
        return self.app

    def test_app_is_testing(self):
        self.assertTrue(
            self.app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertTrue(self.app.config['TESTING'])
        self.assertFalse(self.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        # self.assertTrue(self.app.config['MONGO_DBNAME'] == 'arc_test')


class TestProductionConfig(TestCase):
    def create_app(self):
        self.app = create_app()
        self.app.config.from_object('configs.flask_conf.ProductionConfig')
        return self.app

    def test_app_is_production(self):
        self.assertTrue(
            self.app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY')
        )
        self.assertFalse(self.app.config['TESTING'])
        # self.assertTrue(os.environ.get('MONGO_APP_DB') == 'arclytics')


if __name__ == '__main__':
    unittest.main()
