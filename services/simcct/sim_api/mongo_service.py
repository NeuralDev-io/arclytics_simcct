# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# mongo_service.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'MIT'
__version__ = '2.0.0'
__status__ = 'development'
__date__ = '2019.10.30'
"""mongo_service.py: 

This is a Service Access Layer where the application logic resides for 
methods that access the data persistence layer for connecting to Mongo.
"""

from os import environ as env

from arc_logging import AppLogger
from sim_api.extensions import apm, Mongo

logger = AppLogger(__name__)


class MongoService(object):
    """Service layer where the application logic resides."""
    def __init__(self, client=Mongo()):
        """
        Simply connects the service to the Mongo data access layer through an
        adapter.
        """
        self.client = client
        self.db_name = env.get('MONGO_APP_DB')

    def find(
        self,
        query: dict = None,
        projections: dict = None,
        collection: str = '',
        sort: list = None,
        limit: int = 0
    ):
        """Do a `collections.find()` query with projections. Additionally,
        we can also sort or limit the results returned.

        Usage:
            SearchService().find(
                # search for all documents
                query={},
                # return without _id field but with email
                projections={'_id': 0, 'email': 1},
                # sort ASCENDING on first_name field
                sort=[('first_name': 1)],
                # limit to only 10 returned results
                limit=10
            )

        Args:
            collection: the collection to run find() on.
            query: a dictionary of the query to be used.
            projections: a dictionary of the projections to be used.
            sort: a list of tuple pairs `(field, direction)` to sort results.
            limit: an int to limit the number of returned results.

        Returns:
            A list of the results which are Python dictionaries.
        """
        if not sort:
            cursor = self.client.find(
                db_name=self.db_name,
                collection=collection,
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

    def find_one(self, query: dict = None, projections: dict = None):
        """Simple find one user based on a query and projection."""
        return self.client.find_one(
            db_name=self.db_name,
            collection='users',
            query_selector=query,
            projections=projections
        )

    def find_slice(
        self,
        query: dict = None,
        projections: dict = None,
        collection: str = None,
        sort: list = None,
        limit: int = 0,
        skip: int = 0
    ):
        """Do a `collections.find()` query with projections. Additionally we
        can do a slice on the results by providing the `skip` which will be
        the offset of the first returned result and a `limit` which is the
        end of the slice. We can also do a sort of the results but be away
        the sort always occurs first in the chained method returned.

        Args:
            collection: the collection to run find() on.
            query: a dictionary of the query to be used.
            projections: a dictionary of the projections to be used.
            sort: a list of tuple pairs `(field, direction)` to sort results.
            limit: an int to limit the number of returned results.
            skip: the offset of the result which is the number to start.

        Returns:
            A list of the results which are Python dictionaries.
        """

        if not sort:
            cursor = self.client.find(
                db_name=self.db_name,
                collection=collection,
                query=query,
                projections=projections
            ).skip(skip).limit(limit)
        else:
            cursor = self.client.find(
                db_name=self.db_name,
                collection=collection,
                query=query,
                projections=projections,
            ).skip(skip).limit(limit).sort(sort)

        return list(cursor)

    def count(self, collection: str = None, skip: int = 0, limit: int = 0):
        """Simply count the number of documents with a skip and limit query."""
        return self.client.count(
            db_name=self.db_name,
            collection=collection,
            filter={},  # We always count ALL documents
            skip=skip,
            limit=limit
        )
