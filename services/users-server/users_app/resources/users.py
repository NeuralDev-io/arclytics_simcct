# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# users.py
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
__date__ = '2019.07.03'
"""users.py: 

This file defines all the API resource routes and controller definitions using 
the Flask Resource inheritance model.
"""

from typing import Tuple

from flask import Blueprint, jsonify
#from flask_restful import Resource, Api

from logger.arc_logger import AppLogger
from users_app.models import User
from users_app.middleware import login_required, authenticate_admin

users_blueprint = Blueprint('users', __name__)
#api = Api(users_blueprint)

logger = AppLogger(__name__)

@users_blueprint.route(rule='/ping', methods=['GET'])
def ping_test() -> dict:
    """A simple resource for sanity checking that the server is working."""
    response = {'status': 'success', 'message': 'pong'}
    return jsonify(response)


@users_blueprint.route(rule='/users', methods=['GET'])
@authenticate_admin
def user_list() -> Tuple[dict, int]:
    """Get all users only available to admins."""
    user_list = User.as_dict
    response = {'status': 'success', 'data': {'users': user_list}}
    return jsonify(response), 200


@users_blueprint.route(rule='/users/<user_id>', methods=['GET'])
@login_required
def user(user_id) -> Tuple[dict, int]:
    user = User.objects.get(id=user_id)
    response = {'status': 'success', 'data': user.to_dict()}
    return jsonify(response), 200

# ========== # RESOURCE DEFINITIONS # ========== #
# class PingTest(Resource):
#     """A simple resource for sanity checking that the server is working."""
#
#     def get(self):
#         return {'status': 'success', 'message': 'pong'}


# class UsersList(Resource):
#     """Route for Users for Create and Retrieve List."""
#
#     method_decorators = {'get': [authenticate_admin]}
#
#     def get(self, resp):
#         """Get all users only available to admins."""
#         user_list = User.as_dict
#         response = {'status': 'success', 'data': {'users': user_list}}
#         return response, 200, {'Content-type': 'application/json'}


# TODO(andrew@neuraldev.io -- Sprint 6)
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


# class Users(Resource):
#     """Resource for User Retrieve and Update."""
#
#     method_decorators = {'get': [login_required], 'update': [login_required]}
#
#     def get(self, user_id):
#         """Get a single user detail with query parameter as user_id."""
#
#         # Validation check fo ObjectId done in authenticate_restful decorator
#         # if not ObjectId.is_valid(user_id):
#         #     response['message'] = 'Invalid bson.ObjectId type.'
#         #     return response, 404
#
#         # Validation check for User exists done in authenticate_restful
#         # decorator
#         user = User.objects.get(id=user_id)
#         response = {'status': 'success', 'data': user.to_dict()}
#         return response, 200, {'Content-type': 'application/json'}


# ========== # RESOURCE ROUTES # ========== #
# api.add_resource(PingTest, '/ping')
# api.add_resource(UsersList, '/users')
# # users_app.add_resource(AdminCreate, '/users/register_admin')
# api.add_resource(Users, '/users/<user_id>')
