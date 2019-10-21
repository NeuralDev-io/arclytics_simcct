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
        sort: list = None,
        limit: int = None
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

    def find_slice(
        self,
        query: dict = None,
        projections: dict = None,
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
        """Simply count the number of documents with a skip and limit query."""
        return self.client.count(
            db_name=self.db_name,
            collection='users',
            filter={},  # We always count ALL documents
            skip=skip,
            limit=limit
        )
