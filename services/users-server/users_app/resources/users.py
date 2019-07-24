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
from flask_restful import Resource, Api

from logger.arc_logger import AppLogger
from users_app.models import User, UserProfile, AdminProfile
from users_app.middleware import authenticate, authenticate_admin
from users_app.token import (
    confirm_token, generate_confirmation_token, generate_url
)
from users_app.email import send_email
from users_app import api

users_blueprint = Blueprint('users', __name__)

logger = AppLogger(__name__)


class PingTest(Resource):
    """Just a sanity check"""

    def get(self) -> Tuple[dict, int]:
        response = {'status': 'success', 'message': 'pong'}
        return response, 200


class UserList(Resource):
    """Return all users (admin only)"""

    method_decorators = {
        'get': [authenticate_admin]
    }

    def get(self, resp) -> Tuple[dict, int]:
        """Get all users only available to admins."""
        user_list = User.as_dict
        response = {'status': 'success', 'data': {'users': user_list}}
        return response, 200


class SingleUser(Resource):
    """Get/Put a single user's details."""

    method_decorators = {
        'get': [authenticate],
        'put': [authenticate]
    }

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        response = {'status': 'success', 'data': user.to_dict()}
        return response, 200

    def put(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        # Get put data
        data = request.get_json()

        # Validating empty payload
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not data:
            return response, 400

        # Extract put body

        # TODO(davidmatthews1004@gmail.com) Speak to Andrew about user changing
        #  their email address
        # email = data.get('email', '')

        # Not password - this will be handled elsewhere (another endpoint)
        first_name = data.get('first_name', None)
        last_name = data.get('last_name', None)
        # Not active, admin, created, verified, last_updated, last_login
        aim = data.get('aim', None)
        highest_education = data.get('highest_education', None)
        sci_tech_exp = data.get('sci_tech_exp', None)
        phase_transform_exp = data.get('phase_transform_exp', None)

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name

        if user.profile:
            if aim:
                user.profile.aim = aim
            if highest_education:
                user.profile.highest_education = highest_education
            if sci_tech_exp:
                user.profile.sci_tech_exp = sci_tech_exp
            if phase_transform_exp:
                user.profile.phase_transform_exp = phase_transform_exp
        else:
            profile = UserProfile(
                aim=aim, highest_education=highest_education,
                sci_tech_exp=sci_tech_exp, phase_transform_exp=phase_transform_exp
            )
            user.profile = profile

        if user.is_admin:
            mobile_number = data.get('mobile_number', None)
            position = data.get('position', None)
            if user.admin_profile:
                if mobile_number:
                    user.admin_profile.mobile_number = mobile_number
                if position:
                    user.admin_profile.position = position
            else:
                admin_profile = AdminProfile(
                    mobile_number=mobile_number, position=position
                )
                user.admin_profile = admin_profile

        user.save()

        response['status'] = 'success'
        response['message'] = f'Successfully updated User details for {user.id}.'
        return response, 200


class UserLastAlloy(Resource):
    """Returns the user's Alloy and Configurations used, and CCT/TTT results
    (if any)
    """

    method_decorators = {
        'get': [authenticate]
    }

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        # TODO(davidmatthews1004gmail.com) waiting for Alloy embedded doc
        response = {'status': 'fail', 'message': 'No alloy was found.'}
        return response, 400


class UserAlloys(Resource):
    """We get the list of User's alloys stored in their document"""

    method_decorators = {
        'get': [authenticate],
        'post': [authenticate]
    }

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        # TODO(davidmatthews1004gmail.com) this also needs tests
        response = {'status': 'fail', 'message': 'No alloys found.'}
        return response, 400

    def post(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        # TODO(davidmatthews1004gmail.com) this also needs tests
        response = {'status': 'fail', 'message': 'Alloy could not be saved.'}
        return response, 400


class UpdateUserProfile(Resource):
    """"""

    method_decorators = {
        'put': [authenticate]
        # TODO(davidmatthews1004@gmail.com) get and post
    }

    def put(self, resp) -> Tuple[dict, int]:
        # Get put data
        data = request.get_json()

        # Validating empty payload
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not data:
            return response, 400

        # Extract the request body data
        aim = data.get('aim', None)
        highest_education = data.get('highest_education', None)
        sci_tech_exp = data.get('sci_tech_exp', None)
        phase_transform_exp = data.get('phase_transform_exp', None)

        # Get the user
        id = data.get('id', '')
        user = User.objects.get(data.get(id))

        # Make sure to not overwrite existing user data with nulls
        if user.profile:
            if aim:
                user.profile.aim = aim

            if highest_education:
                 user.profile.highest_education = highest_education

            if sci_tech_exp:
                user.profile.sci_tech_exp = sci_tech_exp

            if phase_transform_exp:
                user.profile.phase_transform_exp = phase_transform_exp
        else:
            profile = UserProfile(
                aim=aim, highest_education=highest_education,
                sci_tech_exp=sci_tech_exp, phase_transform_exp=phase_transform_exp
            )
            user.profile = profile

        user.save()

        response['status'] = 'success'
        response['message'] = f'Successfully updated User profile for {id}.'
        return response, 200


# TODO(davidmatthews1004@gmail.com) get /user/configurations


# TODO(davidmatthews1004@gmail.com) get /user/graphs


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


api.add_resource(PingTest, '/ping')
api.add_resource(UserList, '/users')
api.add_resource(SingleUser, '/user')
api.add_resource(UpdateUserProfile, '/user/profile')
api.add_resource(UserLastAlloy, '/user/last')
api.add_resource(UserAlloys, '/user/alloys')

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
