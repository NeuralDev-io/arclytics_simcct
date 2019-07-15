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

{Description}
"""

from typing import Union

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from sim_app.abstract_adapter import AlloyAbstract
from sim_app.mongo import MongoAlloys
from sim_app.schemas import AlloySchema


class AlloysService(object):
    """Service layer where the application logic resides."""

    def __init__(self, client=AlloyAbstract(adapter=MongoAlloys)):
        self.alloys_client = client

    def find_all_alloys(self):
        alloys = self.alloys_client.find_all()
        return [self.dump(alloy) for alloy in alloys]

    def find_alloy(self, alloy_id: ObjectId):
        alloy = self.alloys_client.find({'_id': alloy_id})
        return self.dump(alloy)

    def create_alloy(self, alloy) -> Union[ObjectId, str]:
        try:
            alloy_id = self.alloys_client.create(alloy)
        except DuplicateKeyError as e:
            return 'Alloy already exists.'
        return alloy_id

    def update_alloy(self, alloy_id: ObjectId, alloy):
        pass

    def delete_alloy(self, alloy_id: ObjectId):
        records_affected = self.alloys_client.delete({'_id': alloy_id})
        return records_affected > 0

    def dump(self, data):
        return AlloySchema(exclude=['_id']).dump(data)
