# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# mongo_service.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '0.9.0'
__status__ = 'production'
__date__ = '2019.10.15'
"""mongo_service.py: 

This module provides a service to connect to a MongoDB database with simple 
write or read as needed.
"""

from os import environ as env
from pymongo import MongoClient

COLLECTION_NAME = 'celery_beat'


class MongoService(object):
    def __init__(self, collection='celery_beat'):
        """Simply makes a connection to a MongoDB instance with `pymongo`."""
        self.db_name = env.get('MONGO_APP_DB')
        if env.get('FLASK_ENV', 'production') == 'production':
            mongo_uri = (
                'mongodb://{username}:{password}@{host}:{port}/{db}'
                '?authSource=admin&authMechanism=SCRAM-SHA-1'
            ).format(
                username=env.get('MONGO_APP_USER'),
                password=env.get('MONGO_APP_USER_PASSWORD'),
                host=env.get('MONGO_HOST', 'localhost'),
                port=env.get('MONGO_PORT', 27017),
                db=self.db_name
            )
            self.conn = MongoClient(mongo_uri)
        else:
            self.conn = MongoClient(
                host=env.get('MONGO_HOST'), port=int(env.get('MONGO_PORT'))
            )
            # Implement an index to expire after two weeks: 14 * 24 * 60 * 60
            # Note this only done during development as it's created by the
            # Mongo container in production
            self.db.celery_beat.create_index(
                'date', expireAfterSeconds=1209600
            )

        self.db = self.conn[self.db_name]

    def update_one(self, query: dict, update: dict, upsert: bool = False):
        """Do an updateOne query on the Mongo collection."""
        self.db.celery_beat.update_one(query, update, upsert=upsert)
