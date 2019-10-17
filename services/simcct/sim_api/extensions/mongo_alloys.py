# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# mongo_alloys.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.14'
"""mongo_alloys.py: 

This module contains the MongoDB mapper for the Alloy schema and document.
"""

from mongoengine import get_db
from pymongo import ASCENDING

COLLECTION_NAME = 'alloys'


class MongoAlloys(object):
    """
    This is a concrete definition of Alloys as a data access layer.
    """
    def __init__(self):
        # Instead of making another connection to Mongo, we use the one defined
        # in `app.py` extension `MongoSingleton` by calling the `MongoEngine`
        # get_db() which should get the current app context database.
        self.db = get_db('default')

        # We create an index to avoid duplicates
        # TODO(ANDREW): Find the Master Error that occurred today.
        self.db.alloys.create_index([('name', ASCENDING)], unique=True)

    def find_all(self):
        return self.db.alloys.find()

    def find(self, query_selector: dict):
        return self.db.alloys.find_one(query_selector)

    def create(self, instance: dict):
        return self.db.alloys.insert_one(instance).inserted_id

    def create_many(self, instance_list: list):
        return self.db.alloys.insert_many(instance_list).inserted_ids

    def update(self, query_selector, instance):
        return (
            self.db.alloys.replace_one(query_selector, instance).modified_count
        )

    def delete(self, query_selector):
        return self.db.alloys.delete_one(query_selector).deleted_count
