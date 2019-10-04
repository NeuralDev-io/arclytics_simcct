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
__version__ = '0.1.0'
__status__ = 'development'
__date__ = '2019.10.03'
"""mongo_service.py: 

This module provides a service to connect to a MongoDB database with simple 
methods to either read from the database and collection and convert them to 
a `pandas.DataFrame`. 
"""

from typing import Union
from os import environ as env

import pandas as pd
from pymongo import MongoClient


class MongoService(object):
    def __init__(self,):
        """Simply makes a connection to a MongoDB instance with `pymongo`."""
        if env.get('FLASK_ENV', 'production') == 'production':
            mongo_uri = (
                'mongodb://{username}:{password}@{host}:{port}/{db}'
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

    def read_mongo(
            self,
            db_name: str = 'arc_dev',
            collection: str = '',
            query: dict = None,
            projections: dict = None,
    ) -> Union[pd.DataFrame, None]:
        """Read from a database and collection with a simple query."""
        if query is None:
            return None

        db = self.conn[db_name]

        # Make a query to the specific DB and Collection
        cursor = db[collection].find(query, projection=projections)

        # Expand the cursor and construct the DataFrame
        df = pd.DataFrame(list(cursor))

        return df

    def read_aggregation(
            self, db_name: str, collection: str, pipeline: list = None
    ) -> Union[pd.DataFrame, None]:
        """Read from a database and collection with an aggregation pipeline."""

        if not pipeline:
            return None

        db = self.conn[db_name]
        cursor = db[collection].aggregate(pipeline=pipeline)

        return pd.DataFrame(list(cursor))
