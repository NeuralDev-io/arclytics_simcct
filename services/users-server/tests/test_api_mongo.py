# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_api_mongo.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.05'
"""test_api_mongo.py: 

{Description}
"""

import unittest

import pymongo
from mongoengine.connection import get_db, get_connection

from tests.test_api_base import BaseTestCase, app
from api.mongodb import MongoSingleton
from api import get_flask_mongo, set_flask_mongo, init_db


class TestMongoSingleton(BaseTestCase):

    def setUp(self) -> None:
        super(TestMongoSingleton, self).setUp()
        self.mongo_client = None

    def test_mongo_singleton(self):
        parent = MongoSingleton(None)
        flask_mongo_client = get_flask_mongo()
        inst_client = MongoSingleton(flask_mongo_client)
        child = getattr(parent, 'instance')
        attr = MongoSingleton.__getattr__(parent, 'client')
        self.assertIsInstance(parent, MongoSingleton)
        self.assertEqual(attr.__class__, pymongo.MongoClient)
        self.assertEqual(str(child), '__Mongo.MongoClient')
        self.assertEqual(parent.instance, child)
        self.assertIsInstance(inst_client.instance.client, pymongo.MongoClient)

    def test_api_module_methods(self):
        current_client = get_flask_mongo()
        self.assertIsInstance(current_client.instance.client,
                              pymongo.MongoClient)
        set_flask_mongo(None)
        wrong_client = get_flask_mongo()
        self.assertIsNone(wrong_client)
        self.mongo_client = init_db(app=None,
                                    db_name='testing_mongoengine',
                                    host=app.config['MONGO_HOST'],
                                    port=app.config['MONGO_PORT'])
        self.assertIsInstance(self.mongo_client, MongoSingleton)
        # Make sure the Singleton objects are not the same as they are not meant to be
        self.assertNotEqual(current_client, self.mongo_client)

        db = get_db('default')
        self.assertEqual('testing_mongoengine', db.name)

    def test_mongo_connection(self):
        conn = get_connection('default')
        self.assertIsInstance(conn, pymongo.mongo_client.MongoClient)


if __name__ == '__main__':
    unittest.main()
