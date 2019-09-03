# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_base.py
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
__status__ = '{dev_status}'
__date__ = '2019.07.12'
"""test_api_base.py: 

This module is the base TestCase so that we can inherit from it and the settings
for testing that are initialised in create_app() -- interface by Flask-Testing.
"""

import os

from flask_testing import TestCase
from pymongo import MongoClient
from redis import Redis

import settings
from sim_app.app import create_app
from sim_app.utilities import get_mongo_uri


class BaseTestCase(TestCase):
    def create_app(self):
        os.environ['APP_SETTINGS'] = 'configs.flask_conf.TestingConfig'
        app = create_app()

        app.config.from_object('configs.flask_conf.TestingConfig')

        return app

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up logic for the test suite declared in the test module."""
        # Executed after all tests in one test run.
        redis = Redis(
            host=os.environ.get('REDIS_HOST'),
            port=int(os.environ.get('REDIS_PORT')),
            db=15
        )
        redis.flushall()
        redis.flushdb()
        if os.environ.get('FLASK_ENV') == 'production':
            mongo = MongoClient(get_mongo_uri())
        else:
            mongo = MongoClient(
                host=os.environ.get('MONGO_HOST'),
                port=int(os.environ.get('MONGO_PORT'))
            )
        mongo.drop_database('arc_test')
