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

import os
from datetime import datetime

from typing import Tuple
from socket import gaierror

from celery.states import PENDING
from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, jsonify, request, render_template
from flask import current_app as app
from flask_restful import Resource
from mongoengine.errors import ValidationError

from logger.arc_logger import AppLogger
from users_app.models import User, UserProfile, AdminProfile
from users_app.middleware import authenticate, authenticate_admin
from users_app.extensions import api
from users_app.token import (
    generate_confirmation_token, generate_url, confirm_token, URLTokenError
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
        'patch': [authenticate]
    }

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        response = {'status': 'success', 'data': user.to_dict()}
        return response, 200

    def patch(self, resp) -> Tuple[dict, int]:
        # Get patch data
        data = request.get_json()

        # Validating empty payload
        response = {}
        response['status'] = 'fail'
        response['message'] = 'Invalid payload.'
        if not data:
            return response, 400

        # Ensure there are valid keys in the request body
        valid_keys = [
            'first_name',
            'last_name',
            'aim',
            'highest_education',
            'sci_tech_exp',
            'phase_transform_exp',
            'mobile_number',
            'position'
        ]
        is_update = False
        for k in valid_keys:
            if k in data.keys():
                is_update = True
                break

        # If there are no valid keys, reject request.
        if not is_update:
            response['message'] = 'Payload does not have any valid keys.'
            return response, 400

        # If there are valid keys, begin extracting them.
        first_name = data.get('first_name', None)
        last_name = data.get('last_name', None)
        aim = data.get('aim', None)
        highest_education = data.get('highest_education', None)
        sci_tech_exp = data.get('sci_tech_exp', None)
        phase_transform_exp = data.get('phase_transform_exp', None)

        # If we are going to update the user profile, create a dictionary so
        # that we can store the updated profile fields for the response body.
        if aim or highest_education or sci_tech_exp or highest_education:
            response['profile'] = {}

        # Get the user so we can begin updating fields.
        user = User.objects.get(id=resp)

        # If the user does not already have profile details set we need to
        # create a user profile object.
        if not user.profile:
            # If we do not have all the profile fields, we will need to reject
            # the request as we are unable to create a profile object.
            if not aim or not highest_education or not sci_tech_exp or not phase_transform_exp:
                response.pop('profile')
                response['message'] = 'User profile cannot be patched as there is no existing profile.'
                return response, 400

            # Once we have ensured we have all the fields, we can create the
            # profile object and put the information in the response body.
            response['profile']['aim'] = aim
            response['profile']['highest_education'] = highest_education
            response['profile']['sci_tech_exp'] = sci_tech_exp
            response['profile']['phase_transform_exp'] = phase_transform_exp
            profile = UserProfile(
                aim=aim, highest_education=highest_education,
                sci_tech_exp=sci_tech_exp,
                phase_transform_exp=phase_transform_exp
            )
            user.profile = profile

        # Otherwise if the user already has a profile, we can update individual
        # fields.
        else:
            if aim:
                user.profile.aim = aim
                response['profile']['aim'] = aim
            if highest_education:
                user.profile.highest_education = highest_education
                response['profile']['highest_education'] = highest_education
            if sci_tech_exp:
                user.profile.sci_tech_exp = sci_tech_exp
                response['profile']['sci_tech_exp'] = sci_tech_exp
            if phase_transform_exp:
                user.profile.phase_transform_exp = phase_transform_exp
                response['profile']['phase_transform_exp'] = phase_transform_exp

        # If the user is an admin, we can also update their admin profile
        # details
        if user.is_admin:
            # If the user is an admin but does not have an admin profile or they
            # do not have a position then something has gone wrong when they
            # were made an admin and we need to reject the request so as to not
            # put more invalid information in the user's document.
            if not user.admin_profile or not user.admin_profile.position:
                response['message'] = 'User admin profile is invalid and cannot be patched.'
                response.pop('profile')
                return response, 400

            # If the user is an admin but is not verified, we must also reject
            # the request.
            if not user.admin_profile.verified:
                response['message'] = 'User is not verified as an admin.'
                response.pop('profile')
                return response, 400

            # Otherwise, we can proceed to update the admin profile fields.
            mobile_number = data.get('mobile_number', None)
            position = data.get('position', None)

            # If there is data to be patched, we must create a dictionary for
            # admin profile information in the response body.
            if mobile_number or position:
                response['admin_profile'] = {}

            if mobile_number:
                user.admin_profile.mobile_number = mobile_number
                response['admin_profile']['mobile_number'] = mobile_number
            if position:
                user.admin_profile.position = position
                response['admin_profile']['position'] = position

        # Lastly we check for changes to the base user document.
        if first_name:
            user.first_name = first_name
            response['first_name'] = first_name
        if last_name:
            user.last_name = last_name
            response['last_name'] = last_name

        # Updated the user's last_updated field to now.
        user.last_updated = datetime.utcnow()

        # Save the changes.
        user.save()
        user.cascade_save()

        # Return response body.
        response['status'] = 'success'
        response['message'] = f'Successfully updated User details for {user.id}.'
        return response, 200


class UserLast(Resource):
    """
    Returns the user's Alloy and Configurations used, and CCT/TTT results
    (if any)
    """

    method_decorators = {
        'get': [authenticate]
    }

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        if not user.last_alloy:
            response = {
                'status': 'fail', 'message': 'No last composition was found.'
            }
            return response, 400
        if not user.last_configuration:
            response = {
                'status': 'fail', 'message': 'No last configuration was found.'
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

    method_decorators = {
        'get': [authenticate],
        'post': [authenticate]
    }

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        if not user.saved_alloys:
            response = {'status': 'fail', 'message': 'No alloys found.'}
            return response, 400
        alloys = []
        for a in user.saved_alloys:
            alloys.append(
                a.to_dict()
            )
        response = {
            'status': 'success',
            'alloys': alloys
        }
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
        'patch': [authenticate],
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

    def patch(self, resp) -> Tuple[dict, int]:
        # Get patch data
        data = request.get_json()

        # Ensure the payload is not empty
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not data:
            return response, 400

        # Ensure there are valid keys in the request body
        valid_keys = [
            'aim',
            'highest_education',
            'sci_tech_exp',
            'phase_transform_exp'
        ]
        is_update = False
        for k in valid_keys:
            if k in data.keys():
                is_update = True
                break

        # If there are no valid keys, reject request.
        if not is_update:
            response['message'] = 'Payload does not have any valid keys.'
            return response, 400

        # Otherwise begin extracting request body
        aim = data.get('aim', None)
        highest_education = data.get('highest_education', None)
        sci_tech_exp = data.get('sci_tech_exp', None)
        phase_transform_exp = data.get('phase_transform_exp', None)

        # Create a dictionary so that we can store the updated profile fields
        # for the response body.
        response['profile'] = {}

        # Get the user so we can begin updating fields.
        user = User.objects.get(id=resp)

        # If the user does not already have profile details set we need to
        # create a user profile object.
        if not user.profile:
            # If we do not have all the profile fields, we will need to reject
            # the request as we are unable to create a profile object.
            if not aim or not highest_education or not sci_tech_exp or not phase_transform_exp:
                response.pop('profile')
                response['message'] = 'User profile cannot be patched as there is no existing profile.'
                return response, 400

            # Once we have ensured we have all the fields, we can create the
            # profile object and put the information in the response body.
            response['profile']['aim'] = aim
            response['profile']['highest_education'] = highest_education
            response['profile']['sci_tech_exp'] = sci_tech_exp
            response['profile']['phase_transform_exp'] = phase_transform_exp
            profile = UserProfile(
                aim=aim, highest_education=highest_education,
                sci_tech_exp=sci_tech_exp,
                phase_transform_exp=phase_transform_exp
            )
            user.profile = profile

        # Otherwise if the user already has a profile, we can update individual
        # fields.
        else:
            if aim:
                user.profile.aim = aim
                response['profile']['aim'] = aim
            if highest_education:
                user.profile.highest_education = highest_education
                response['profile']['highest_education'] = highest_education
            if sci_tech_exp:
                user.profile.sci_tech_exp = sci_tech_exp
                response['profile']['sci_tech_exp'] = sci_tech_exp
            if phase_transform_exp:
                user.profile.phase_transform_exp = phase_transform_exp
                response['profile']['phase_transform_exp'] = phase_transform_exp

        # Updated the user's last_updated field to now.
        user.last_updated = datetime.utcnow()

        # Save the changes.
        user.save()
        user.cascade_save()

        # Return the response body
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
        user = User.objects.get(id=resp)
        # Create a user profile object that can replace any existing user
        # profile information.
        profile = UserProfile(
            aim=aim,
            highest_education=highest_education,
            sci_tech_exp=sci_tech_exp,
            phase_transform_exp=phase_transform_exp
        )
        user.profile = profile

        # Attempt to save the new profile object. If there are missing fields
        # an exception will be raised, caught and sent back.
        try:
            user.last_updated = datetime.utcnow()
            user.save()
            user.cascade_save()
        except ValidationError as e:
            response['errors'] = str(e)
            return response, 400

        # Otherwise the save was successful and a response with the updated
        # fields can be sent.
        response['status'] = 'success'
        response['message'] = f'Successfully updated User profile for {resp}.'
        response['profile'] = {}
        response['profile']['aim'] = aim
        response['profile']['highest_education'] = highest_education
        response['profile']['sci_tech_exp'] = sci_tech_exp
        response['profile']['phase_transform_exp'] = phase_transform_exp
        return response, 200


class UserConfigurations(Resource):
    """Retrieve the list of configurations saved in the User's document"""

    method_decorators = {
        'get': [authenticate]
    }

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        response = {'status': 'success', 'message': 'fail'}
        return response, 400
        #TODO(davidmatthews1004@gmail.com)


class UserGraphs(Resource):
    """Retrieve the list of Graphs saved in the User's document."""

    method_decorators = {
        'get': [authenticate]
    }

    def get(self, resp) -> Tuple[dict, int]:
        pass
        # TODO(davidmatthews1004@gmail.com)


class AdminCreate(Resource):
    """Route for Users for Create Admin."""

    method_decorators = {
        'post': [authenticate_admin]
    }

    def post(self, resp):
        """Make a user an administrator"""
        post_data = request.get_json()

        # Validating empty payload
        response = {
            'status': 'fail',
            'message': 'Empty payload.'
        }
        if not post_data:
            return response, 400

        # Extract the request body data
        email = post_data.get('email', '')
        position = post_data.get('position', '')

        if not email:
            response['message'] = 'No email provided.'
            return response, 400

        if not position:
            response['message'] = 'No position provided.'
            return response, 400

        # Verify it is actually a valid email
        try:
            # validate and get info
            v = validate_email(email)
            # replace with normalized form
            valid_email = v['email']
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            response['error'] = str(e)
            response['message'] = 'Invalid email.'
            return response, 400

        # Validation checks
        if not User.objects(email=valid_email):
            return response, 201

        user = User.objects.get(email=valid_email)

        if not user.verified:
            response['message'] = 'The user must verify their email.'
            return response, 401

        if user.is_admin:
            response['message'] = 'User is already an Administrator.'
            return response, 401

        user.is_admin=True
        user.admin_profile = AdminProfile(
            position=position,
            mobile_number=None,
            verified=False,
            promoted_by=resp
        )
        user.last_updated = datetime.utcnow()
        user.save()
        user.cascade_save()

        admin_token = generate_confirmation_token(user.email)
        admin_url = generate_url('users.confirm_create_admin', admin_token)

        from celery_runner import celery
        celery.send_task(
            'tasks.send_email',
            kwargs={
                'to': user.email,
                'subject_suffix': 'Confirm you are an Admin',
                'html_template': render_template(
                    'activate_admin.html',
                    admin_url=admin_url,
                    email=valid_email,
                    users_name=f'{user.first_name} {user.last_name}'
                ),
                'text_template': render_template(
                    'activate_admin.txt',
                    admin_url=admin_url,
                    email=valid_email,
                    users_name=f'{user.first_name} {user.last_name}'
                )
            }
        )

        response['status'] = 'success'
        response.pop('message')
        return response, 202


@users_blueprint.route('/admincreate/confirm/<token>', methods=['GET'])
def confirm_create_admin(token):
    response = {'status': 'fail', 'message': 'Invalid token.'}

    # Decode the token from the email to the confirm it was the right one
    try:
        email = confirm_token(token)
    except URLTokenError as e:
        response['error'] = str(e)
        return jsonify(response), 400
    except Exception as e:
        response['error'] = str(e)
        return jsonify(response), 400

    user = User.objects.get(email=email)
    user.admin_profile.verified = True
    user.last_updated = datetime.utcnow()
    user.cascade_save()
    user.save()

    promoter = User.objects.get(id=user.admin_profile.promoted_by)
    from celery_runner import celery
    celery.send_task(
        'tasks.send_email',
        kwargs={
            'to': promoter.email,
            'subject_suffix': 'Confirm you are an Admin',
            'html_template': render_template(
                'admin_confirmed.html',
                email=promoter.email,
                users_name=f'{promoter.first_name} {promoter.last_name}'
            ),
            'text_template': render_template(
                'admin_confirmed.txt',
                email=promoter.email,
                users_name=f'{promoter.first_name} {promoter.last_name}'
            )
        }
    )

    # TODO(davidmatthews1004@gmail.com): Ensure the link can be dynamic.
    client_host = os.environ.get('CLIENT_HOST')
    # We can make our own redirect response by doing the following
    custom_redir_response = app.response_class(
        status=302, mimetype='application/json'
    )
    redirect_url = f'http://localhost:3000/signin'
    custom_redir_response.headers['Location'] = redirect_url
    return custom_redir_response


class DisableAccount(Resource):
    """Route for Admins to disable user accounts"""

    method_decorators = {
        'put': [authenticate_admin]
    }

    def put(self, resp):
        post_data = request.get_json()

        # Validating empty payload
        response = {
            'status': 'fail',
            'message': 'User does not exist.'
        }
        if not post_data:
            return response, 400

        # Extract the request body data
        email = post_data.get('email', '')

        if not email:
            response['message'] = 'Invalid email provided.'
            return response, 400

        # Verify it is actually a valid email
        try:
            # validate and get info
            v = validate_email(email)
            # replace with normalized form
            valid_email = v['email']
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            response['error'] = str(e)
            response['message'] = 'Invalid email.'
            return response, 400

        # Validation checks
        if not User.objects(email=valid_email):
            return response, 201

        user = User.objects.get(email=valid_email)
        user.active = False
        user.last_updated = datetime.utcnow()
        user.save()

        response['status'] = 'success'
        response['message'] = f'The account for User {user.id} has been disabled.'
        return response, 200


api.add_resource(PingTest, '/ping')
api.add_resource(UserList, '/users')
api.add_resource(SingleUser, '/user')
api.add_resource(UserProfiles, '/user/profile')
api.add_resource(UserLast, '/user/last')
api.add_resource(UserAlloys, '/user/alloys')
api.add_resource(UserConfigurations, '/user/configurations')
api.add_resource(AdminCreate, '/admincreate')
api.add_resource(DisableAccount, '/user/disable')
api.add_resource(UserGraphs, '/user/graphs')