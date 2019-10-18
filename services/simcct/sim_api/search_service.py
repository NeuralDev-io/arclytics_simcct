# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# search_service.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'development'
__date__ = '2019.10.17'
"""search_service.py: 

{Description}
"""

from os import environ as env

from arc_logging import AppLogger
from sim_api.extensions import apm, Mongo

logger = AppLogger(__name__)


class SearchService(object):
    """Service layer where the application logic resides."""
    def __init__(self, client=Mongo()):
        """Simply connects the service to the MongoAlloys through an adapter."""
        self.client = client
        self.db_name = env.get('MONGO_APP_DB')

    def find(self, query: dict = None, projections: dict = None,
             sort: list = None, limit: int = None):

        if not sort:
            cursor = self.client.find(
                db_name=self.db_name,
                collection='users',
                query=query,
                projections=projections,
            ).limit(limit)
        else:
            cursor = self.client.find(
                db_name=self.db_name,
                collection='users',
                query=query,
                projections=projections,
            ).sort(sort).limit(limit)

        return [obj for obj in cursor]

    def find_slice(self, query: dict = None, projections: dict = None,
                   sort: list = None, limit: int = 0, skip: int = 0):

        if not sort:
            cursor = self.client.find(
                db_name=self.db_name,
                collection='users',
                query=query,
                projections=projections
            ).skip(skip).limit(limit)
        else:
            cursor = self.client.find(
                db_name=self.db_name,
                collection='users',
                query=query,
                projections=projections,
            ).skip(skip).limit(limit).sort(sort)

        return list(cursor)

    def count(self, skip: int = 0, limit: int = 0):
        return self.client.count(
            db_name=self.db_name,
            collection='users',
            filter={},
            skip=skip,
            limit=limit
        )
