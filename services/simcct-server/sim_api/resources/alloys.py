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

This defines the resources and endpoints for Alloys.
"""

from flask import Blueprint, request, json
from flask_restful import Resource
from marshmallow import ValidationError

from sim_api.schemas import AlloySchema
from sim_api.alloys_service import AlloysService

alloys_blueprint = Blueprint('alloys', __name__)


schema = AlloySchema()


class Alloys(Resource):

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
            return response, 204

        response['alloys'] = alloys
        response['status'] = 'success'
        response.pop('message')
        return response, 200
