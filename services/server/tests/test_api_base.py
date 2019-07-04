# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# base.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'
"""base.py: 

{Description}
"""

from pymongo import MongoClient
from mongoengine.connection import get_db, get_connection
from flask_testing import TestCase

from api import create_app, db, connect_mongodb
from logger.arc_logger import AppLogger

logger = AppLogger(__name__)
app = create_app()


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('api.config.TestingConfig')
        global db
        db = connect_mongodb(app)
        return app

    def setUp(self) -> None:
        conn = get_connection('default')
        self.assertIsInstance(conn, MongoClient)
        db_in_use = get_db()
        self.assertEqual(db_in_use.name, 'arc_test')

    def tearDown(self) -> None:
        db.instance.client.drop_database()
