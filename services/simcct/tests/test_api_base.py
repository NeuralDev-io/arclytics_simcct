# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# base.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__status__ = 'development'
__date__ = '2019.07.03'

import os

from flask_testing import TestCase
from mongoengine.connection import disconnect, get_connection, get_db
from pymongo import MongoClient
from redis import Redis

from arc_logging import AppLogger
from sim_api import create_app
from sim_api import init_db, set_flask_mongo

logger = AppLogger(__name__)

app = create_app(configs_path='configs.flask_conf.TestingConfig')


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('configs.flask_conf.TestingConfig')
        self.db = init_db(app)
        set_flask_mongo(self.db)
        # app.wsgi_app = FlaskTestClientProxy(app.wsgi_app)
        return app

    def setUp(self) -> None:
        conn = get_connection()
        self.assertIsInstance(conn, MongoClient)
        db_in_use = get_db()
        self.assertEqual(db_in_use.name, 'arc_test')

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
        db = get_db()
        db.alloys.drop()
        db.users.drop()
        disconnect('default')
