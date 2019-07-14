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

from pymongo import MongoClient, ASCENDING

COLLECTION_NAME = 'alloys'


class MongoAlloys(object):
    """
    This is a concrete definition of Alloys as a data access layer.
    """

    def __init__(self):
        mongo_client = MongoClient(
            host=os.environ.get('MONGO_HOST'),
            port=int(os.environ.get('MONGO_PORT'))
        )
        # TODO(andrew@neuraldev.io): Figure out how to set the db dynamically
        #  as trying to use app.config does not work in this case.
        self.db = mongo_client['arc-dev']
        # We create an index to avoid duplicates
        self.db.alloys.create_index([('name', ASCENDING)], unique=True)

    def find_all(self):
        return self.db.alloys.find()

    def find(self, query_selector: dict):
        return self.db.alloys.find_one(query_selector)

    def create(self, instance: dict):
        return self.db.alloys.insert_one(instance).inserted_id

    def update(self, query_selector, instance):
        return (self.db.alloys.replace_one(query_selector, instance)
                .modified_count)

    def delete(self, query_selector):
        return self.db.alloys.delete_one(query_selector).deleted_count
