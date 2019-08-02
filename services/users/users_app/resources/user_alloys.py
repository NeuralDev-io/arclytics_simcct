# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# user_alloys.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.02'
"""user_alloys.py: 

This module defines the CRUD methods to save an Embedded Document List of an
Alloy on the User's Document. 
"""

from typing import Tuple

from bson import ObjectId
from flask import request, Blueprint
from flask_restful import Resource
from mongoengine import ValidationError
from mongoengine.errors import (
    FieldDoesNotExist, DoesNotExist, MultipleObjectsReturned
)

from users_app.extensions import api
from users_app.middleware import authenticate
from users_app.models import Alloy, User

user_alloys_blueprint = Blueprint('user_alloys', __name__)


class UserAlloysList(Resource):
    """The resource for endpoints to get an Alloy list and create an alloy
    to the User's database.
    """

    method_decorators = {'get': [authenticate], 'post': [authenticate]}

    def post(self, user_id) -> Tuple[dict, int]:
        """The endpoint that exposes a POST HTTP method to create an alloy in
        the User's document.

        Args:
            user_id: a valid user ObjectId passed from the middleware.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()

        if not post_data:
            return response, 400

        if not isinstance(post_data, dict):
            return response, 400

        alloy_name = post_data.get('name', None)
        alloy_comp = post_data.get('compositions', None)

        if not alloy_name:
            response['message'] = 'Name must be provided.'
            return response, 400

        if not alloy_comp or not isinstance(alloy_comp, list):
            response['message'] = (
                'Compositions must be provided as a list '
                'of valid elements e.g. '
                '{"symbol": "C", "weight": 1.0}'
            )
            return response, 400

        try:
            Alloy(name=alloy_name, compositions=alloy_comp).validate()
        except FieldDoesNotExist as e:
            response['error'] = str(e)
            response['message'] = 'Alloy validation error.'
            return response, 400
        except ValidationError as e:
            response['error'] = str(e)
            response['message'] = 'Alloy validation error.'
            return response, 400

        user = User.objects.get(id=user_id)
        alloy = user.saved_alloys.create(**post_data)
        user.save()

        response['status'] = 'success'
        response['data'] = alloy.to_dict()
        response.pop('message')
        return response, 201

    def get(self, user_id) -> Tuple[dict, int]:
        """The endpoint that exposes a GET HTTP method to retrieve a list of
        alloys on the User's document.

        Args:
            user_id: a valid user ObjectId passed from the middleware.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """
        user = User.objects.get(id=user_id)
        alloy_list = [obj.to_dict() for obj in user.saved_alloys]
        response = {'status': 'success', 'data': alloy_list}
        return response, 200


class UserAlloy(Resource):
    method_decorators = {
        'get': [authenticate],
        'patch': [authenticate],
        'delete': [authenticate]
    }

    def get(self, user_id, alloy_id):
        """The endpoint that exposes a GET HTTP method to retrieve an alloy
        detail from the User's document.

        Args:
            user_id: a valid user ObjectId passed from the middleware.
            alloy_id: a valid Alloy ObjectId of the embedded document.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """
        response = {'status': 'fail', 'message': 'No alloys found.'}
        user = User.objects.get(id=user_id)

        # If there is only one alloy to return.
        if user.saved_alloys.count() == 1:
            alloy = user.saved_alloys.first()
        else:
            try:
                alloy = user.saved_alloys.get(**{'oid': ObjectId(alloy_id)})
            except DoesNotExist as e:
                response['error'] = str(e)
                response['message'] = 'Alloy does not exist.'
                return response, 404
            except MultipleObjectsReturned as e:
                response['error'] = str(e)
                response['message'] = 'Multiple objects returned.'
                return response, 418

        response = {'status': 'success', 'data': alloy.to_dict()}
        return response, 200

    def patch(self, user_id, alloy_id):
        pass

    def delete(self, user_id, alloy_id):
        pass


api.add_resource(UserAlloysList, '/user/alloys')
api.add_resource(UserAlloy, '/user/alloys/<alloy_id>')
