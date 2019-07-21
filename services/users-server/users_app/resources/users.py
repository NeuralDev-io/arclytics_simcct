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

from logger.arc_logger import AppLogger
from users_app.models import User
from users_app.middleware import authenticate, authenticate_admin

users_blueprint = Blueprint('users', __name__)

logger = AppLogger(__name__)

@users_blueprint.route(rule='/ping', methods=['GET'])
def ping_test() -> dict:
    """A simple resource for sanity checking that the server is working."""
    response = {'status': 'success', 'message': 'pong'}
    return jsonify(response)


@users_blueprint.route(rule='/users', methods=['GET'])
@authenticate_admin
def user_list(resp) -> Tuple[dict, int]:
    """Get all users only available to admins."""
    user_list = User.as_dict
    response = {'status': 'success', 'data': {'users': user_list}}
    return jsonify(response), 200


@users_blueprint.route(rule='/user', methods=['GET'])
@authenticate
def user(resp) -> Tuple[dict, int]:
    user = User.objects.get(id=resp)
    response = {'status': 'success', 'data': user.to_dict()}
    return jsonify(response), 200


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