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

from flask import Blueprint, jsonify, render_template, request, redirect

from logger.arc_logger import AppLogger
from users_app.models import User, UserProfile
from users_app.middleware import authenticate, authenticate_admin
from users_app.token import (
    confirm_token, generate_confirmation_token, generate_url
)
from users_app.email import send_email

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


@users_blueprint.route(rule='/user/updateprofile', methods=['POST'])
@authenticate
def update_user_profile(resp) -> Tuple[dict, int]:
    """Blueprint route for updating user profile"""

    # Get the post data
    post_data = request.get_json()

    # Validating empty payload
    response = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response), 400

    # Extract the request body data
    aim = post_data.get('aim', None)
    highest_education = post_data.get('highest_education', None)
    sci_tech_exp = post_data.get('sci_tech_exp', None)
    phase_transform_exp = post_data.get('phase_transform_exp', None)

    # Get the user
    user = User.objects.get(id=resp)

    # Make sure to not overwrite existing user data with nulls
    if user.profile:
        if not aim:
            aim = user.profile.aim

        if not highest_education:
            highest_education = user.profile.highest_education

        if not sci_tech_exp:
            sci_tech_exp = user.profile.sci_tech_exp

        if not phase_transform_exp:
            phase_transform_exp = user.profile.phase_transform_exp

    profile = UserProfile(
        aim=aim, highest_education=highest_education,
        sci_tech_exp=sci_tech_exp, phase_transform_exp=phase_transform_exp
    )
    user.reload()
    user.profile = profile
    user.save()

    response['status'] = 'success'
    response['message'] = f'Successfully updated User profile for {resp}'
    return jsonify(response), 200


@users_blueprint.route(rule='/user/viewprofile', methods=['GET'])
@authenticate
def view_user_profile(resp) -> Tuple[dict, int]:
    user = User.objects.get(id=resp)
    if user.profile:
        response = {'status': 'success', 'data': user.profile.to_dict()}
        return jsonify(response), 200
    else:
        response = {'status': 'fail', 'message': 'User Profile not set yet.'}
        return jsonify(response), 400


@users_blueprint.route('/test/send', methods=['POST'])
def test_email_send():

    response = {'status': 'fail', 'message': 'Invalid payload.'}

    post_data = request.get_json()

    if not post_data:
        return jsonify(), 400

    email = post_data.get('email', None)

    if not email:
        response['message'] = 'No email.'

    token = generate_confirmation_token(email)
    confirm_url = generate_url('users.confirm_email', token)
    send_email(
        to=email,
        subject='Please Confirm Your Email',
        template=render_template(
            'activate.html',
            confirm_url=confirm_url
        )
    )

    return jsonify({'status': 'success'}), 202


@users_blueprint.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    try:
        email = confirm_token(token)
    except Exception as e:
        return jsonify(response), 400

    user = User.objects.get(email=email)

    user.verified = True

    response['status'] = 'success'
    response.pop('message')
    return redirect('http://localhost:3000/signin', code=302)


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

# @users_blueprint.route('/createadmin', methods=['POST'])
# @authenticate_admin
# def create_admin() -> Tuple[dict, int]:
#
#     post_data = request.get_json()
#
#     response = {'status': 'fail', 'message': 'Invalid payload.'}
#     if not post_data:
#         return jsonify(response), 400
#
#     email = post_data.get('email', None)
#     password = post_data.get('password', None)
#     first_name = post_data.get('first_name', None)
#     last_name = post_data.get('last_name', None)
#
#     if not email:
#         response['message'] = 'A user account must have an email.'
#         return jsonify(response), 400
#
#     if not password:
#         response['message'] = 'A user account must have a password.'
#         return jsonify(response), 400
#
#     if len(str(password)) < 6 or len(str(password)) > 120:
#         response['message'] = 'The password is invalid.'
#         return jsonify(response), 400