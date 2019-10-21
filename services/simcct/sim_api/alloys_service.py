# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# alloys.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.14'
"""alloys.py: 

This is a service layer that acts to define and implement the application/
business logic for Global Alloys.
"""

from typing import Union

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from marshmallow import ValidationError

from arc_logging import AppLogger
from sim_api.abstract_adapter import AlloyAbstract
from sim_api.extensions import MongoAlloys, apm
from sim_api.schemas import AlloySchema

logger = AppLogger(__name__)


class AlloysService(object):
    """Service layer where the application logic resides."""
    def __init__(self, client=AlloyAbstract(adapter=MongoAlloys)):
        """Simply connects the service to the MongoAlloys through an adapter."""
        self.client = client

    def find_all_alloys(self) -> list:
        """We use the PyMongo interface find() query to get a `pymongo.Cursor`
        instance which is an iterable that we can loop over.

        Returns:
            We make a list by iterating over the cursor.
        """
        alloys = self.client.find_all()
        return [self.dump(alloy) for alloy in alloys]

    def find_alloy(self, query_params: Union[ObjectId, str]) -> dict:
        """Find the alloy based on _id | name and returns a dict dump from the
        schema or an empty dict.

        Args:
            query_params: the alloy _id as an ObjectId object.

        Returns:
            A dict object of the alloy based on AlloySchema or an empty dict.
        """

        alloy = self.client.find({'_id': query_params})
        if not isinstance(query_params, ObjectId):
            logger.error(
                {
                    'message': 'Invalid Global Alloys search parameter.',
                    'parameter': str(ObjectId)
                }
            )
        return self.dump(alloy)

    def create_alloys_many(self, alloys: list) -> Union[list, str]:
        """We use the PyMongo interface insert_many() method with an instance
        of a Python list with many alloy dictionaries.

        Args:
            alloys: a list of Python dict object that conforms with the
                    AlloySchema.

        Returns:
            A list of ObjectId object of the newly created alloy or a str.
        """
        try:
            alloy_id_list = self.client.create_many(
                self.load(alloys, many=True)
            )
        except ValidationError as e:
            logger.exception({'msg': e.messages})
            apm.capture_exception()
            return e.messages
        except DuplicateKeyError as e:
            logger.exception('Duplicate Key Error')
            apm.capture_exception()
            return str(e)
        return alloy_id_list

    def create_alloy(self, alloy: dict) -> Union[ObjectId, str]:
        """We use the PyMongo interface insert_one() method with an instance
        of a Python dictionary.

        Args:
            alloy: a Python dict object that conforms with the AlloySchema.

        Returns:
            The ObjectId object of the newly created alloy or a str.
        """
        try:
            alloy_id = self.client.create(self.load(alloy))
        except ValidationError as e:
            logger.exception({'msg': e.messages, 'data': str(alloy)})
            apm.capture_exception()
            return e.messages
        except DuplicateKeyError:
            logger.exception(
                {
                    'msg': 'Duplicate Key Error',
                    'data': str(alloy)
                }
            )
            apm.capture_exception()
            return 'Alloy already exists.'
        return alloy_id

    def update_alloy(
        self, query_params: Union[ObjectId, str], alloy: dict
    ) -> bool:
        """We update the alloy by replacing the old one with the new one.

        Args:
            query_params: the ObjectId of the existing alloy.
            alloy: the AlloySchema validated Python dict to replace the old.

        Returns:
            Whether any records have been affected with as a bool.
        """
        records_affected = self.client.update({'_id': query_params}, alloy)
        return records_affected > 0

    def delete_alloy(self, alloy_id: ObjectId) -> bool:
        """We use the PyMongo interface delete_one() query to remove and then
        get the count of any of the documents have been affected.

        Args:
            alloy_id: the ObjectId of the existing alloy.

        Returns:
            Whether any records have been affected with as a bool.
        """
        records_affected = self.client.delete({'_id': alloy_id})
        return records_affected > 0

    @staticmethod
    def dump(data: dict) -> dict:
        """A simple method to validate the Python dict to our schema."""
        return AlloySchema().dump(data)

    @staticmethod
    def load(data: Union[list, dict], many=False) -> dict:
        """A simple method to validate the dict to our schema for loading."""
        return AlloySchema(many=many).load(data)
