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
from socket import gaierror

from celery.states import PENDING
from flask import Blueprint, jsonify, request, render_template
from flask_restful import Resource

from logger.arc_logger import AppLogger
from users_app.models import User, UserProfile, AdminProfile
from users_app.middleware import authenticate, authenticate_admin
from users_app.extensions import api
from users_app.token import (
    generate_confirmation_token, generate_url, confirm_token
)

users_blueprint = Blueprint('users', __name__)

logger = AppLogger(__name__)


class PingTest(Resource):
    """Just a sanity check"""

    def get(self) -> Tuple[dict, int]:
        response = {'status': 'success', 'message': 'pong'}
        return response, 200


class UserList(Resource):
    """Return all users (admin only)"""

    method_decorators = {'get': [authenticate_admin]}

    def get(self, resp) -> Tuple[dict, int]:
        """Get all users only available to admins."""
        user_list = User.as_dict
        response = {'status': 'success', 'data': {'users': user_list}}
        return response, 200


class SingleUser(Resource):
    """Get/Put a single user's details."""

    method_decorators = {'get': [authenticate], 'put': [authenticate]}

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
                aim=aim,
                highest_education=highest_education,
                sci_tech_exp=sci_tech_exp,
                phase_transform_exp=phase_transform_exp
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
        response['message'
                 ] = f'Successfully updated User details for {user.id}.'
        return response, 200


class UserLast(Resource):
    """Returns the user's Alloy and Configurations used, and CCT/TTT results
    (if any)
    """

    method_decorators = {'get': [authenticate]}

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        if not user.last_alloy:
            response = {
                'status': 'fail',
                'message': 'No last composition was found.'
            }
            return response, 400
        if not user.last_configuration:
            response = {
                'status': 'fail',
                'message': 'No last configuration was found.'
            }
            return response, 400

        response = {
            'status': 'success',
            'configuration': user.last_configuration.to_dict(),
            'composition': user.last_alloy.to_dict()
        }
        return response, 200


class UserAlloys(Resource):
    """We get the list of User's alloys stored in their document"""

    method_decorators = {'get': [authenticate], 'post': [authenticate]}

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        if not user.saved_alloys:
            response = {'status': 'fail', 'message': 'No alloys found.'}
            return response, 400
        alloys = []
        for a in user.saved_alloys:
            alloys.append(a.to_dict())
        response = {'status': 'success', 'alloys': alloys}
        return response, 200

    def post(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        data = request.get_json()
        if not data:
            response = {'status': 'fail', 'message': 'Invalid payload.'}
            return response, 400
        #TODO(davidmatthews1004@gmail.com)


class UserProfiles(Resource):
    """Create/Retrieve/Update User's profile details"""

    method_decorators = {
        'get': [authenticate],
        'put': [authenticate],
        'post': [authenticate]
    }

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        response = {
            'status': 'success',
            'profile': {
                'aim': user.profile.aim,
                'highest_education': user.profile.highest_education,
                'sci_tech_exp': user.profile.sci_tech_exp,
                'phase_transform_exp': user.profile.phase_transform_exp
            }
        }
        return response, 200

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
                aim=aim,
                highest_education=highest_education,
                sci_tech_exp=sci_tech_exp,
                phase_transform_exp=phase_transform_exp
            )
            user.profile = profile

        user.save()

        response['status'] = 'success'
        response['message'] = f'Successfully updated User profile for {id}.'
        return response, 200

    def post(self, resp) -> Tuple[dict, int]:
        # Get post data
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
        id = data.get('id')
        user = User.objects.get(data.get(id))

        if not aim:
            response = {'status': 'fail', 'message': 'Missing aim.'}
            return response, 400
        if not highest_education:
            response = {
                'status': 'fail',
                'message': 'Missing highest education.'
            }
            return response, 400
        if not sci_tech_exp:
            response = {
                'status': 'fail',
                'message': 'Missing science technology experience.'
            }
            return response, 400
        if not phase_transform_exp:
            response = {
                'status': 'fail',
                'message': 'Missing phase transformation experience.'
            }
            return response, 400

        profile = UserProfile(
            aim=aim,
            highest_education=highest_education,
            sci_tech_exp=sci_tech_exp,
            phase_transform_exp=phase_transform_exp
        )
        user.profile = profile
        user.save()

        response['status'] = 'success'
        response['message'] = f'Successfully updated User profile for {id}.'
        return response, 200


class UserConfigurations(Resource):
    """Retrieve the list of configurations saved in the User's document"""

    method_decorators = {'get': [authenticate]}

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        response = {'status': 'success', 'message': 'fail'}
        return response, 400
        #TODO(davidmatthews1004@gmail.com)


# TODO(davidmatthews1004@gmail.com) get /user/graphs


class AdminCreate(Resource):
    """Route for Users for Create Admin."""

    method_decorators = {'post': [authenticate_admin]}

    def post(self):
        """Make a user an administrator"""
        post_data = request.get_json()

        # Validating empty payload
        response = {'status': 'fail', 'message': 'User does not exist.'}
        if not post_data:
            return response, 400

        # Extract the request body data
        email = post_data.get('email', '')

        if not email:
            response['message'] = 'Invalid email provided.'
            return response, 400

        # Validation checks
        if not User.objects(email=email):
            return response, 201

        user = User.objects.get(email=email)

        if user.is_admin:
            response['message'] = 'User is already an Administrator.'
            return response, 400

        user.is_admin = True

        try:
            user.save()

            # generate auth token
            auth_token = user.encode_auth_token(user.id)
            # generate the confirmation token for verifying email
            confirmation_token = generate_confirmation_token(email)
            confirm_url = generate_url(
                'auth.confirm_email_admin', confirmation_token
            )

            from celery_runner import celery
            task = celery.send_tassk(
                'tasks.send_email',
                kwargs={
                    'to':
                    email,
                    'subject_suffix':
                    'Please Confirm You Are Now Admin',
                    'html_template':
                    render_template(
                        'activate_admin.html',
                        confirm_url=confirm_url,
                        user_name=f'{user.first_name} {user.last_name}'
                    )
                }
            )
            # FIXME(davidmatthews1004@gmail.com): Need to find a way to validate that it has
            #  sent without waiting for the result.
            task_status = celery.AsyncResult(task.id).state

            while task_status == PENDING:
                task_status = celery.AsyncResult(task.id).state
            # The email tasks response with a Tuple[bool, str]
            res = celery.AsyncResult(task.id)

            # Generic response regardless of email task working
            response['status'] = 'success'
            response['token'] = auth_token.decode()

            if isinstance(res.result, gaierror):
                response['error'] = 'Socket error.'
                response['message'] = (
                    'Admin created but confirmation '
                    'email failed.'
                )
                return jsonify(response), 201

            if not res.result[0]:
                response['error'] = res.result[1]
                response['message'] = (
                    'Admin created but confirmation '
                    'email failed.'
                )
                return jsonify(response), 201

            response['message'] = 'Admin has been created.'
            return jsonify(response), 201

        except ValidationError as e:
            # logger.error('Validation Error: {}'.format(e))
            response['message'] = 'The Admin cannot be created.'
            return jsonify(response), 400
        # I don't think this is is needed for this endpoint.
        # except NotUniqueError as e:
        #     # logger.error('Not Unique Error: {}'.format(e))
        #     response['message'] = 'The users details already exists.'
        #     return jsonify(response), 400


class DisableAccount(Resource):
    """Route for Admins to disable user accounts"""

    method_decorators = {'post': [authenticate_admin]}

    def post(self, resp):
        post_data = request.get_json()

        # Validating empty payload
        response = {'status': 'fail', 'message': 'User does not exist.'}
        if not post_data:
            return response, 400

        # Extract the request body data
        email = post_data.get('email', '')

        if not email:
            response['message'] = 'Invalid email provided.'
            return response, 400

        # Validation checks
        if not User.objects(email=email):
            return response, 201

        user = User.objects.get(email=email)
        user.account_disabled = True
        # TODO(davidmatthews1004@gmail.com) Kick user if they are currently logged in
        user.save()

        response['status'] = 'success'
        response['message'
                 ] = f'The account for User {user.id} has been disabled.'
        return response, 200


api.add_resource(PingTest, '/ping')
api.add_resource(UserList, '/users')
api.add_resource(SingleUser, '/user')
api.add_resource(UserProfiles, '/user/profile')
api.add_resource(UserLast, '/user/last')
api.add_resource(UserAlloys, '/user/alloys')
api.add_resource(UserConfigurations, '/user/configurations')
# api.add_resource(AdminCreate, '/admincreate')
api.add_resource(DisableAccount, '/disableaccount')
