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
        response = {'status': 'fail', 'message': 'Empty.'}

        alloys = AlloysService().find_all_alloys()

        if len(alloys) == 0:
            return response, 404

        response['alloys'] = alloys
        response['status'] = 'success'
        response.pop('message')
        return response, 200


class Alloys(Resource):
    def get(self, alloy_id):
        response = {'status': 'fail', 'message': 'Invalid ObjectId.'}

        # Verify the request params is a valid ObjectId to use
        if not ObjectId.is_valid(alloy_id):
            return response, 400

        alloy = AlloysService().find_alloy(ObjectId(alloy_id))

        if not alloy:
            response['message'] = 'Alloy not found.'
            return response, 404

        response['status'] = 'success'
        response['data'] = alloy
        response.pop('message')
        return response, 200

    def put(self, alloy_id):
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

        if not good:
            response['message'] = 'Alloy not found.'
            return response, 404

        updated_alloy = AlloysService().find_alloy(ObjectId(alloy_id))

        response['status'] = 'success'
        response['data'] = updated_alloy
        response.pop('message')
        return response, 202

    def delete(self, alloy_id):
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
