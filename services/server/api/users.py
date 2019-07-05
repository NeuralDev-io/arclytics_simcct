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

from flask import Blueprint, request
from flask_restful import Resource, Api, reqparse
from mongoengine import ValidationError, NotUniqueError

from api import JSONEncoder
from logger.arc_logger import AppLogger
from api.models import User
from api.auth_decorators import authenticate_restful, authenticate_admin

users_blueprint = Blueprint('users', __name__)
api = Api(users_blueprint)

logger = AppLogger(__name__)


# A built-in request parse from Flask RESTful
parser = reqparse.RequestParser()

parser.add_argument('email', help='This field cannot be blank.', required=True)
parser.add_argument('username', help='This field cannot be blank.', required=False)
parser.add_argument('password', help='This field cannot be blank.', required=True)


# ========== # RESOURCE DEFINITIONS # ========== #
class PingTest(Resource):
    def get(self):
        return {
            'status': 'success',
            'message': 'pong'
        }


class UsersList(Resource):
    """Route for Users for Create and Retrieve List."""

    method_decorators = {
        'get': [authenticate_admin]
    }

    def get(self, resp):
        """Get all users only available to admins."""
        queryset = User.objects()
        response = {
            'status': 'success',
            'data': {
                'users': json.loads(queryset.to_json())
            }
        }
        return response, 200


# TODO
# class AdminCreate(Resource):
#     """Route for Users for Create Admin."""

    # method_decorators = {
    #     'post': [authenticate_admin]
    # }

    # def post(self):
    #     """Make a user an administrator"""
    #     post_data = request.get_json()
    #
    #     # Validating empty payload
    #     response = {
    #         'status': 'fail',
    #         'message': 'User does not exist.'
    #     }
    #     if not post_data:
    #         return response, 400
    #
    #     # Extract the request body data
    #     email = post_data.get('email', '')
    #
    #     if not email:
    #         response['message'] = 'Invalid email provided.'
    #         return response, 400
    #
    #     # Validation checks
    #     if not User.objects(email=email):
    #         return response, 201
    #
    #     user = User.objects.get(email=email)
    #     user.is_admin = True
    #     # TODO: must validate/verify with email
    #     response['message'] = '{} was made an administrator'.format(user.email)
    #     return response, 200


class Users(Resource):
    """Resource for User Retrieve."""

    method_decorators = {
        'get': [authenticate_restful],
        'update': [authenticate_restful]
    }

    def get(self, user_id):
        """Get a single user detail with query as user_id."""
        response = {
            'status': 'fail',
            'message': 'User does not exist.'
        }

        # Validation check fo ObjectId done in authenticate_restful decorator
        # if not ObjectId.is_valid(user_id):
        #     response['message'] = 'Invalid bson.ObjectId type.'
        #     return response, 404

        # Validation check for User exists done in authenticate_restful decorator
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
api.add_resource(PingTest, '/ping')
api.add_resource(UsersList, '/users')
# api.add_resource(AdminCreate, '/users/register_admin')
api.add_resource(Users, '/users/<user_id>')
