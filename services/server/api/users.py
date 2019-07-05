# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------------------------------------
# arclytics_sim
# users.py
# 
# Attributions: 
# [1] 
# ------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'
"""users.py: 

This file defines all the API resource routes and controller definitions using the Flask Resource inheritance model.
"""
import json
from bson import ObjectId

from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
from mongoengine import ValidationError, NotUniqueError

from api import JSONEncoder
from logger.arc_logger import AppLogger
from api.models import User

users_blueprint = Blueprint('users', __name__)
api = Api(users_blueprint)

logger = AppLogger(__name__)


# ========== # RESOURCE DEFINITIONS # ========== #
class PingTest(Resource):
    def get(self):
        return {
            'status': 'success',
            'message': 'pong'
        }


class UsersList(Resource):
    """Route for Users for Create and Retrieve List."""
    def get(self):
        """Get all users."""
        queryset = User.objects()
        response = {
            'status': 'success',
            'data': {
                'users': json.loads(queryset.to_json())
            }
        }
        return response, 200

    def post(self):
        """Register a new user."""
        post_data = request.get_json()

        # Validating empty payload
        response = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        if not post_data:
            return response, 400

        # Extract the request body data
        email = post_data.get('email', '')
        username = post_data.get('username', '')
        password = post_data.get('password', '')

        if not email:
            return response, 400

        if not password:
            response['message'] = 'A user account must have a password.'
            return response, 400

        # Validation checks
        try:
            # Create a Mongo User object and save it
            if not User.objects(email=email):
                new_user = User(
                    email=email,
                    username=username,
                )
                new_user.set_password(raw_password=password)  # ensure we set an encrypted password.
                new_user.save()  # should use cascade save
                response['status'] = 'success'
                response['message'] = '{email} was added'.format(email=email)
                return response, 201
            else:
                response['message'] = 'Error, email exists.'
                return response, 400
        except ValidationError as e:
            logger.error('Validation Error: {}'.format(e))
        except NotUniqueError as e:
            logger.error('Not Unique Error: {}'.format(e))

        # We should not reach this point
        response['status'] = 'fail'
        response['message'] = 'Sorry, someone forgot to validate some bug.'
        return response, 400


class Users(Resource):
    """Resource for User Retrieve."""
    def get(self, user_id):
        """Get a single user detail with query as user_id."""
        response = {
            'status': 'fail',
            'message': 'User does not exist.'
        }

        # Validation check fo ObjectId
        if not ObjectId.is_valid(user_id):
            response['message'] = 'Invalid bson.ObjectId type.'
            return response, 404

        # Validation check for User exists
        if not User.objects(id=user_id):
            return response, 404
        else:
            user = User.objects.get(id=user_id)
            response = {
                'status': 'success',
                'data': {
                    'id': JSONEncoder().encode(user.id),  # To serialize bson.ObjectId properly
                    'email': user.email,
                    'username': user.username,
                    'active': user.active,
                }
            }

        return response, 200


# ========== # RESOURCE ROUTES # ========== #
api.add_resource(PingTest, '/users/ping')
api.add_resource(UsersList, '/users')
api.add_resource(Users, '/users/<user_id>')
