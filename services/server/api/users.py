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

        # Extract the request body data
        email = post_data.get('email', '')
        username = post_data.get('username', '')

        # Create a Mongo User object and save it
        new_user = User(email=email, username=username)
        logger.info("New User Instance: {}".format(new_user))
        new_user.save()
        logger.info("New User _id: {}".format(new_user.id))

        response = {
            'status': 'success',
            'message': '{email} was added'.format(email=email)
        }
        return response, 201


# ========== # RESOURCE ROUTES # ========== #
api.add_resource(PingTest, '/users/ping')
api.add_resource(UsersList, '/users')
