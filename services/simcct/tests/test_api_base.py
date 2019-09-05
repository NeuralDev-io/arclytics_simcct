# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# base.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']

__credits__ = ['']
__license__ = 'TBA'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'
"""base.py: 

The base TestCase that all others subclass from.
"""

from pymongo import MongoClient
from mongoengine.connection import get_db, get_connection
from flask_testing import TestCase
from redis import Redis

from sim_api.app import create_app, set_flask_mongo, init_db
from logger.arc_logger import AppLogger

import settings
from sim_api.app import create_app
from sim_api.utilities import get_mongo_uri

logger = AppLogger(__name__)
app = create_app()


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('configs.flask_conf.TestingConfig')
        # os.environ['APP_SETTINGS'] = 'configs.flask_conf.TestingConfig'
        self.db = init_db(app)
        set_flask_mongo(self.db)
        # app = create_app()
        # app.config.from_object('configs.flask_conf.TestingConfig')
        return app

    def setUp(self) -> None:
        conn = get_connection('default')
        self.assertIsInstance(conn, MongoClient)
        db_in_use = get_db()
        self.assertEqual(db_in_use.name, 'arc_test')

    def tearDown(self) -> None:
        self.db.instance.client.drop_database('arc_test')

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
