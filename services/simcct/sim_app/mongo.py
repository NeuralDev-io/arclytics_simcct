# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# alloys.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.14'
"""alloys.py: 

This module contains the MongoDB mapper for the Alloy schema and document.
"""

import os
from pymongo import ASCENDING, MongoClient

COLLECTION_NAME = 'alloys'


class MongoAlloys(object):
    """
    This is a concrete definition of Alloys as a data access layer.
    """

    def __init__(self):
        if os.environ.get('FLASK_ENV', 'production') == 'development':
            mongo_client = MongoClient(
                host=os.environ.get('MONGO_HOST'),
                port=int(os.environ.get('MONGO_PORT')),
            )
        else:
            host = os.environ.get('MONGO_HOST')
            port = int(os.environ.get('MONGO_PORT'))
            username = str(os.environ.get('MONGO_APP_USER'))
            password = str(os.environ.get('MONGO_APP_USER_PASSWORD'))
            db = str(os.environ.get('MONGO_APP_DB'))
            uri = f'{username}:{password}@{host}:{port}/{db}'
            mongo_client = MongoClient(f'mongodb://{uri}')
        db_name = os.environ.get('MONGO_APP_DB', 'arc_dev')
        self.db = mongo_client[db_name]
        # We create an index to avoid duplicates
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
