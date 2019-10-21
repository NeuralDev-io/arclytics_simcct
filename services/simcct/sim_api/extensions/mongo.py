# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# mongo.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.14'
"""mongo.py: 

This module contains the MongoDB mapper for a generic schema and document 
to be used as a wrapper for Pymongo colletcion methods.
"""

from os import environ as env

from pymongo import MongoClient


class Mongo(object):
    """
    This is a concrete definition of Alloys as a data access layer.
    """
    def __init__(self):
        """Simply makes a connection to a MongoDB instance with `pymongo`."""
        if env.get('FLASK_ENV', 'production') == 'production':
            mongo_uri = (
                'mongodb://{username}:{password}@{host}:{port}/{db}'
                '?authSource=admin&authMechanism=SCRAM-SHA-1'
            ).format(
                username=env.get('MONGO_APP_USER'),
                password=env.get('MONGO_APP_USER_PASSWORD'),
                host=env.get('MONGO_HOST', 'localhost'),
                port=env.get('MONGO_PORT', 27017),
                db=env.get('MONGO_APP_DB')
            )
            self.conn = MongoClient(mongo_uri)
        else:
            self.conn = MongoClient(
                host=env.get('MONGO_HOST'), port=int(env.get('MONGO_PORT'))
            )

    def find(
        self,
        db_name: str = 'arc_dev',
        collection: str = '',
        query: dict = None,
        projections: dict = None,
    ):
        if not collection:
            return None

        if query is None:
            return None

        db = self.conn[db_name]
        return db[collection].find(query, projections)

    # noinspection PyShadowingBuiltins
    def count(
        self,
        db_name: str = 'arc_dev',
        collection: str = '',
        filter: dict = None,
        skip: int = 0,
        limit: int = 0
    ):
        if not collection:
            return None

        db = self.conn[db_name]

        _filter = filter
        if filter is None:
            _filter = {}

        # Because limit must be positive in this method, we will validate it
        # and not use if we don't want to limit the count.
        if limit <= 0:
            return db[collection].count_documents(filter, skip=skip)

        return db[collection].count_documents(filter, skip=skip, limit=limit)

    def find_one(
        self,
        db_name: str = 'arc_dev',
        collection: str = 'arc_dev',
        query_selector: dict = None,
        projections: dict = None
    ):
        if query_selector is None:
            return None
        db = self.conn[db_name]

        return db[collection].find_one(query_selector, projections)

    def aggregate(
            self,
            db_name: str = 'arc_dev',
            collection: str = 'arc_dev',
            pipeline: list = None,
    ):
        if pipeline is None:
            return None
        db = self.conn[db_name]

        return db[collection].aggregate(pipeline, allowDiskUse=True)
