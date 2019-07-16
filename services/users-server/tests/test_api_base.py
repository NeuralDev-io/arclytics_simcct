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

from users_api import create_app, set_flask_mongo, init_db
from logger.arc_logger import AppLogger

logger = AppLogger(__name__)
app = create_app()


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('users_api.config.TestingConfig')
        self.db = init_db(app)
        set_flask_mongo(self.db)
        return app

    def setUp(self) -> None:
        conn = get_connection('default')
        self.assertIsInstance(conn, MongoClient)
        db_in_use = get_db()
        self.assertEqual(db_in_use.name, 'arc_test')

    def tearDown(self) -> None:
        self.db.instance.client.drop_database('arc_test')
