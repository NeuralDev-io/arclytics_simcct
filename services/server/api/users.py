# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# users.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
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

from flask import Blueprint, request
from flask_restful import Resource, Api
from mongoengine import ValidationError, NotUniqueError

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
    def post(self):
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

        if not email:
            return response, 400

        # Validation checks
        try:
            # Create a Mongo User object and save it
            if not User.objects(email=email):
                new_user = User(
                    email=email,
                    username=username,
                )
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


# ========== # RESOURCE ROUTES # ========== #
api.add_resource(PingTest, '/users/ping')
api.add_resource(UsersList, '/users')
