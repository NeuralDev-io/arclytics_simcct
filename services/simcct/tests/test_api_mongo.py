# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_api_mongo.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__status__ = '{dev_status}'
__date__ = '2019.07.05'

import unittest

import pymongo
from flask import current_app as app
from mongoengine.connection import get_connection, get_db

from sim_api import get_flask_mongo, init_db, set_flask_mongo
from sim_api.extensions import MongoSingleton
from tests.test_api_base import BaseTestCase


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
        self.assertIsInstance(
            current_client.instance.client, pymongo.MongoClient
        )
        set_flask_mongo(None)
        wrong_client = get_flask_mongo()
        self.assertIsNone(wrong_client)
        self.mongo_client = init_db(
            app=None,
            db_name='testing_mongoengine',
            host=app.config['MONGO_HOST'],
            port=app.config['MONGO_PORT']
        )
        self.assertIsInstance(self.mongo_client, MongoSingleton)
        # Make sure the Singleton objects are not the same as they are not
        # meant to be
        self.assertNotEqual(current_client, self.mongo_client)

        db = get_db('default')
        self.assertEqual('testing_mongoengine', db.name)

    def test_mongo_connection(self):
        conn = get_connection('default')
        self.assertIsInstance(conn, pymongo.mongo_client.MongoClient)


if __name__ == '__main__':
    unittest.main()
