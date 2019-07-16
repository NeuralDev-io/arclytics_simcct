# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# alloys.py
#
# Attributions:
# [1]
# TODO:
#  - (andrew@neuraldev.io) Try to not use Flask RESTfil resources and instead
#    use just Flask API decorators so that the AlloysService doesn't get
#    instantiated until it's
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.14'
"""alloys.py: 

This defines the resources and endpoints for Alloys.
"""

from bson import ObjectId
from flask import Blueprint, request, json
from flask_restful import Resource
from marshmallow import ValidationError

from sim_app.schemas import AlloySchema
from sim_app.alloys_service import AlloysService

alloys_blueprint = Blueprint('alloys', __name__)

# Just some shorthands to make it easier to read
schema = AlloySchema()  # alloy schema instance


class AlloysList(Resource):
    """The resource of endpoints for retrieving an alloy list and creating."""

    def post(self):
        """Exposes the POST method for `/alloys` to allow creating an alloy.
        The request must also include a request body of data that will need to
        comply to the schema.

        Returns:
            A Response object as a dict and a status code as an int.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        if not request.get_json():
            return response, 400

        # Extract the request data and validate it
        try:
            post_data = schema.load(json.loads(request.data))
        except ValidationError as e:
            response['errors'] = e.messages
            return response, 400

        alloy = AlloysService().create_alloy(post_data)

        # create_alloy() will return a string on DuplicateKeyError meaning it
        # wasn't created.
        if isinstance(alloy, str):
            response['message'] = alloy
            return response, 412

        response['status'] = 'success'
        response['_id'] = str(alloy)
        response.pop('message')
        return response, 201

    def get(self):
        """Exposes the GET method for `/alloys` to retrieve a list of alloys in
        the database.

        Returns:
            A Response object with a response dict and status code as int.
        """
        response = {'status': 'fail', 'message': 'Empty.'}

        alloys = AlloysService().find_all_alloys()

        # No point returning data if there is none to return.
        if len(alloys) == 0:
            return response, 404

        response['alloys'] = alloys
        response['status'] = 'success'
        response.pop('message')
        return response, 200


class Alloys(Resource):
    def get(self, alloy_id):
        """Allows the GET method with `/alloys/{id}` as an endpoint to get
        a single alloy from the database.

        Args:
            alloy_id: A valid ObjectId string that will be checked.

        Returns:
            A Response object consisting of a dict and status code as an int.
        """
        response = {'status': 'fail', 'message': 'Invalid ObjectId.'}

        # Verify the request params is a valid ObjectId to use
        if not ObjectId.is_valid(alloy_id):
            return response, 400

        alloy = AlloysService().find_alloy(ObjectId(alloy_id))

        # The service will return True or False based on successfully finding
        # an alloy.
        if not alloy:
            response['message'] = 'Alloy not found.'
            return response, 404

        response['status'] = 'success'
        response['data'] = alloy
        response.pop('message')
        return response, 200

    def put(self, alloy_id):
        """Exposes the PUT method for `/alloys` to update an existing alloy by
        user of replacing the old one.

        Args:
            alloy_id: A valid ObjectId string that will be checked.

        Returns:
            A Response object consisting of a dict and status code as an int.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        if not request.get_json():
            return response, 400

        # Verify the request params is a valid ObjectId to use
        if not ObjectId.is_valid(alloy_id):
            response['message'] = 'Invalid ObjectId.'
            return response, 400

        # Extract the request data and validate it
        try:
            put_data = schema.load(json.loads(request.data))
        except ValidationError as e:
            response['errors'] = e.messages
            return response, 400

        good = AlloysService().update_alloy(ObjectId(alloy_id), put_data)

        # The service will return True or False based on successfully updating
        # an alloy.
        if not good:
            response['message'] = 'Alloy not found.'
            return response, 404

        updated_alloy = AlloysService().find_alloy(ObjectId(alloy_id))

        response['status'] = 'success'
        response['data'] = updated_alloy
        response.pop('message')
        return response, 202

    def delete(self, alloy_id):
        """Exposes the DELETE method on `/alloys/{id}` to delete an existing
        alloy in the database.

        Args:
            alloy_id: A valid ObjectId string that will be checked.

        Returns:
            A Response object consisting of a dict and status code as an int.
        """
        response = {'status': 'fail', 'message': 'Invalid ObjectId.'}

        # Verify the request params is a valid ObjectId to use
        if not ObjectId.is_valid(alloy_id):
            return response, 400

        good = AlloysService().delete_alloy(ObjectId(alloy_id))

        if not good:
            response['message'] = 'Alloy not found.'
            return response, 404

        response['status'] = 'success'
        response.pop('message')
        return response, 202
