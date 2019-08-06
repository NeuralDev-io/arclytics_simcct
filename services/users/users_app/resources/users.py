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
    generate_confirmation_token, generate_url, confirm_token, URLTokenError,
    generate_promotion_confirmation_token
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


class Users(Resource):
    """Get/Put a single user's details."""

<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
    method_decorators = {'get': [authenticate], 'put': [authenticate]}
=======
    method_decorators = {'get': [authenticate], 'patch': [authenticate]}
>>>>>>> ARC-105
<<<<<<< Updated upstream
=======
    method_decorators = {'get': [authenticate], 'patch': [authenticate]}
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        response = {'status': 'success', 'data': user.to_dict()}
        return response, 200

    def patch(self, resp) -> Tuple[dict, int]:
        # Get patch data
        data = request.get_json()

        # Validating empty payload
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not data:
            return response, 400

        # Ensure there are valid keys in the request body
        valid_keys = [
            'first_name', 'last_name', 'aim', 'highest_education',
            'sci_tech_exp', 'phase_transform_exp', 'mobile_number', 'position'
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

        response['data'] = {}

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
            response['data'] = {'profile': {}}
<<<<<<< Updated upstream

        # Get the user so we can begin updating fields.
        user = User.objects.get(id=resp)
<<<<<<< HEAD

        # If the user does not already have profile details set we need to
        # create a user profile object.
        if not user.profile:
            # If we do not have all the profile fields, we will need to reject
            # the request as we are unable to create a profile object.
            if (
                not aim or not highest_education or not sci_tech_exp
                or not phase_transform_exp
            ):
                response.pop('data')
                response['message'] = (
                    'User profile cannot be updated as '
                    'there is no existing profile.'
                )
                return response, 400

            # Once we have ensured we have all the fields, we can create the
            # profile object and put the information in the response body.
            response['data']['profile'] = {
                'aim': aim,
                'highest_education': highest_education,
                'sci_tech_exp': sci_tech_exp,
                'phase_transform_exp': phase_transform_exp
            }
            profile = UserProfile(
                aim=aim,
                highest_education=highest_education,
                sci_tech_exp=sci_tech_exp,
                phase_transform_exp=phase_transform_exp
            )
            user.profile = profile

=======

        # If the user does not already have profile details set we need to
        # create a user profile object.
        if not user.profile:
            # If we do not have all the profile fields, we will need to reject
            # the request as we are unable to create a profile object.
            if (
                not aim or not highest_education or not sci_tech_exp
                or not phase_transform_exp
            ):
                response.pop('data')
                response['message'] = (
                    'User profile cannot be updated as '
                    'there is no existing profile.'
                )
                return response, 400

            # Once we have ensured we have all the fields, we can create the
            # profile object and put the information in the response body.
            response['data']['profile'] = {
                'aim': aim,
                'highest_education': highest_education,
                'sci_tech_exp': sci_tech_exp,
                'phase_transform_exp': phase_transform_exp
            }
            profile = UserProfile(
                aim=aim,
                highest_education=highest_education,
                sci_tech_exp=sci_tech_exp,
                phase_transform_exp=phase_transform_exp
            )
            user.profile = profile

>>>>>>> ARC-105
=======

        # Get the user so we can begin updating fields.
        user = User.objects.get(id=resp)

        # If the user does not already have profile details set we need to
        # create a user profile object.
        if not user.profile:
            # If we do not have all the profile fields, we will need to reject
            # the request as we are unable to create a profile object.
            if (
                not aim or not highest_education or not sci_tech_exp
                or not phase_transform_exp
            ):
                response.pop('data')
                response['message'] = (
                    'User profile cannot be updated as '
                    'there is no existing profile.'
                )
                return response, 400

            # Once we have ensured we have all the fields, we can create the
            # profile object and put the information in the response body.
            response['data']['profile'] = {
                'aim': aim,
                'highest_education': highest_education,
                'sci_tech_exp': sci_tech_exp,
                'phase_transform_exp': phase_transform_exp
            }
            profile = UserProfile(
                aim=aim,
                highest_education=highest_education,
                sci_tech_exp=sci_tech_exp,
                phase_transform_exp=phase_transform_exp
            )
            user.profile = profile

>>>>>>> Stashed changes
        # Otherwise if the user already has a profile, we can update individual
        # fields.
        else:
            if aim:
                user.profile.aim = aim
                response['data']['profile']['aim'] = aim
            if highest_education:
                user.profile.highest_education = highest_education
                response['data']['profile']['highest_education'] = \
                    highest_education
            if sci_tech_exp:
                user.profile.sci_tech_exp = sci_tech_exp
                response['data']['profile']['sci_tech_exp'] = sci_tech_exp
            if phase_transform_exp:
                user.profile.phase_transform_exp = phase_transform_exp
<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
        else:
            profile = UserProfile(
                aim=aim,
                highest_education=highest_education,
                sci_tech_exp=sci_tech_exp,
                phase_transform_exp=phase_transform_exp
            )
            user.profile = profile
=======
                response['data']['profile']['phase_transform_exp'] = \
                    phase_transform_exp
>>>>>>> ARC-105
<<<<<<< Updated upstream
=======
                response['data']['profile']['phase_transform_exp'] = \
                    phase_transform_exp
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes

        # If the user is an admin, we can also update their admin profile
        # details
        if user.is_admin:
            # If the user is an admin but is not verified, we must also reject
            # the request.
            if not user.admin_profile or not user.admin_profile.verified:
                response['message'] = 'User is not verified as an admin.'
                response.pop('data')
                return response, 401

            # If the user is an admin but does not have an admin profile or they
            # do not have a position then something has gone wrong when they
            # were made an admin and we need to reject the request so as to not
            # put more invalid information in the user's document.
            if not user.admin_profile or not user.admin_profile.position:
                response['message'] = (
                    'User admin profile is invalid and '
                    'cannot be updated.'
                )
                response.pop('data')
                return response, 401

            # Otherwise, we can proceed to update the admin profile fields.
            mobile_number = data.get('mobile_number', None)
            position = data.get('position', None)

            # If there is data to be patched, we must create a dictionary for
            # admin profile information in the response body.
            if mobile_number or position:
                response['data']['admin_profile'] = {}

            if mobile_number:
                user.admin_profile.mobile_number = mobile_number
                response['data']['admin_profile']['mobile_number'] = \
                    mobile_number
            if position:
                user.admin_profile.position = position
                response['data']['admin_profile']['position'] = position

        # Lastly we check for changes to the base user document.
        if first_name:
            user.first_name = first_name
            response['data']['first_name'] = first_name
        if last_name:
            user.last_name = last_name
            response['data']['last_name'] = last_name

        # Updated the user's last_updated field to now.
        user.last_updated = datetime.utcnow()

        # Save the changes for both the user document and embedded document.
        try:
            user.save()
        except ValidationError as e:
            response.pop('data')
            response['errors'] = str(e)
            response['message'] = 'Validation error.'
            return response, 418

        # Return response body.
        response['status'] = 'success'
<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
        response['message'
                 ] = f'Successfully updated User details for {user.id}.'
=======
>>>>>>> ARC-105
<<<<<<< Updated upstream
=======
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
        return response, 200


class UserLast(Resource):
    """
    Returns the user's Alloy and Configurations used, and CCT/TTT results
    (if any)
    """

<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
    # TODO(davidmatthews1004@gmail.com) Update this method to match new schema.

>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
=======
    # TODO(davidmatthews1004@gmail.com) Update this method to match new schema.

>>>>>>> ARC-105
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

<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
    # TODO(davidmatthews1004@gmail.com) Update this method to match new schema.

>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
=======
    # TODO(davidmatthews1004@gmail.com) Update this method to match new schema.

>>>>>>> ARC-105
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
        'patch': [authenticate],
        'post': [authenticate]
    }

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        response = {
            'status': 'success',
            'data': {
                'profile': {
                    'aim': user.profile.aim,
                    'highest_education': user.profile.highest_education,
                    'sci_tech_exp': user.profile.sci_tech_exp,
                    'phase_transform_exp': user.profile.phase_transform_exp
                }
            }
        }

        if user.is_admin:
            response['data']['admin_profile'] = {
                'position': user.admin_profile.position,
                'mobile_number': user.admin_profile.mobile_number
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
            'aim', 'highest_education', 'sci_tech_exp', 'phase_transform_exp'
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

        # Get the user so we can begin updating fields.
        user = User.objects.get(id=resp)
<<<<<<< Updated upstream
<<<<<<< HEAD

        # If the user does not already have profile details set we need to
        # create a user profile object.
        if not user.profile:
            # If we do not have all the profile fields, we will need to reject
            # the request as we are unable to create a profile object.
            if (
                not aim or not highest_education or not sci_tech_exp
                or not phase_transform_exp
            ):
                response['message'] = (
                    'User profile cannot be patched as '
                    'there is no existing profile.'
                )
                return response, 400

            # Once we have ensured we have all the fields, we can create the
            # profile object and put the information in the response body.
            response['data'] = {
                'aim': aim,
                'highest_education': highest_education,
                'sci_tech_exp': sci_tech_exp,
                'phase_transform_exp': phase_transform_exp
            }
            profile = UserProfile(
                aim=aim,
                highest_education=highest_education,
                sci_tech_exp=sci_tech_exp,
                phase_transform_exp=phase_transform_exp
            )
            user.profile = profile

=======

=======

>>>>>>> Stashed changes
        # If the user does not already have profile details set we need to
        # create a user profile object.
        if not user.profile:
            # If we do not have all the profile fields, we will need to reject
            # the request as we are unable to create a profile object.
            if (
                not aim or not highest_education or not sci_tech_exp
                or not phase_transform_exp
            ):
                response['message'] = (
                    'User profile cannot be patched as '
                    'there is no existing profile.'
                )
                return response, 400

            # Once we have ensured we have all the fields, we can create the
            # profile object and put the information in the response body.
            response['data'] = {
                'aim': aim,
                'highest_education': highest_education,
                'sci_tech_exp': sci_tech_exp,
                'phase_transform_exp': phase_transform_exp
            }
            profile = UserProfile(
                aim=aim,
                highest_education=highest_education,
                sci_tech_exp=sci_tech_exp,
                phase_transform_exp=phase_transform_exp
            )
            user.profile = profile

<<<<<<< Updated upstream
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
        # Otherwise if the user already has a profile, we can update individual
        # fields.
        else:
            response['data'] = {}
            if aim:
                user.profile.aim = aim
                response['data']['aim'] = aim
            if highest_education:
                user.profile.highest_education = highest_education
<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes

=======
                response['data']['highest_education'] = highest_education
>>>>>>> ARC-105
<<<<<<< Updated upstream
=======
                response['data']['highest_education'] = highest_education
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
            if sci_tech_exp:
                user.profile.sci_tech_exp = sci_tech_exp
                response['data']['sci_tech_exp'] = sci_tech_exp
            if phase_transform_exp:
                user.profile.phase_transform_exp = phase_transform_exp
<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
        else:
            profile = UserProfile(
                aim=aim,
                highest_education=highest_education,
                sci_tech_exp=sci_tech_exp,
                phase_transform_exp=phase_transform_exp
            )
            user.profile = profile
=======
                response['data']['phase_transform_exp'] = phase_transform_exp
>>>>>>> ARC-105
<<<<<<< Updated upstream
=======
                response['data']['phase_transform_exp'] = phase_transform_exp
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes

        # Updated the user's last_updated field to now.
        user.last_updated = datetime.utcnow()

        # Save the changes for the user and the embedded documents
        user.save()

        # Return the response body
        response['status'] = 'success'
        response.pop('message')
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
<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
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

=======
        user = User.objects.get(id=resp)
        # Create a user profile object that can replace any existing user
        # profile information.
>>>>>>> ARC-105
<<<<<<< Updated upstream
=======
        user = User.objects.get(id=resp)
        # Create a user profile object that can replace any existing user
        # profile information.
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
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
        except ValidationError as e:
            response['errors'] = str(e)
            response['message'] = 'Validation error.'
            return response, 400

        # Otherwise the save was successful and a response with the updated
        # fields can be sent.
        response['status'] = 'success'
        response.pop('message')
        response['data'] = {
            'aim': aim,
            'highest_education': highest_education,
            'sci_tech_exp': sci_tech_exp,
            'phase_transform_exp': phase_transform_exp
        }
        return response, 201


class UserConfigurations(Resource):
    """Retrieve the list of configurations saved in the User's document"""

    method_decorators = {'get': [authenticate]}

    def get(self, resp) -> Tuple[dict, int]:
        user = User.objects.get(id=resp)
        response = {'status': 'success', 'message': 'fail'}
        return response, 400
        #TODO(davidmatthews1004@gmail.com)


class UserGraphs(Resource):
    """Retrieve the list of Graphs saved in the User's document."""

    method_decorators = {'get': [authenticate]}

    def get(self, resp) -> Tuple[dict, int]:
        pass
        # TODO(davidmatthews1004@gmail.com)


class AdminCreate(Resource):
    """Route for Admins to Create Admin."""

    method_decorators = {'post': [authenticate_admin]}

    def post(self, resp):
        """Make a user an administrator"""
        post_data = request.get_json()

        # Validating empty payload
<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
        response = {'status': 'fail', 'message': 'User does not exist.'}
=======
        response = {'status': 'fail', 'message': 'Invalid payload.'}
>>>>>>> ARC-105
<<<<<<< Updated upstream
=======
        response = {'status': 'fail', 'message': 'Invalid payload.'}
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
        if not post_data:
            return response, 400

        # Extract the request body data
        email = post_data.get('email', '')
        position = post_data.get('position', '')

        # Ensure email and position data was given
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

        # Make sure the user exists in the database.
        if not User.objects(email=valid_email):
            response['message'] = 'User does not exist.'
            return response, 404

        # Get the user object and verify that it is verified and an admin
        user = User.objects.get(email=valid_email)
        if not user.verified:
            response['message'] = 'The user must verify their email.'
            return response, 401
        if user.is_admin:
            response['message'] = 'User is already an Administrator.'
            return response, 400

        # Get the admin object so we can email them a confirmation email.
        admin = User.objects.get(id=resp)

<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
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
=======
        # Generate a confirmation email to be sent to the Admin so that they can
        # confirm they want to promote the user.
        promotion_confirm_token = generate_promotion_confirmation_token(
            admin.email, user.email, position
        )
        promotion_confirm_url = generate_url(
            'users.confirm_promotion', promotion_confirm_token
        )
        from celery_runner import celery
        celery.send_task(
            'tasks.send_email',
            kwargs={
                'to':
                admin.email,
                'subject_suffix':
                'Confirm Promotion',
                'html_template':
                render_template(
                    'confirm_promotion.html',
                    promotion_confirm_url=promotion_confirm_url,
                    email=admin.email,
                    position=position,
                    admin_name=f'{admin.first_name} {admin.last_name}',
                    user_name=f'{user.first_name} {user.last_name}'
                ),
                'text_template':
                render_template(
                    'confirm_promotion.txt',
                    promotion_confirm_url=promotion_confirm_url,
                    email=admin.email,
                    position=position,
                    admin_name=f'{admin.first_name} {admin.last_name}',
                    user_name=f'{user.first_name} {user.last_name}'
                )
            }
        )
<<<<<<< Updated upstream

        response['status'] = 'success'
        response.pop('message')
        return response, 202
>>>>>>> ARC-105


@users_blueprint.route('/admin/confirmpromotion/<token>', methods=['GET'])
def confirm_promotion(token):
    """
    Allow an admin to confirm their promotion of another user
=======
        # Generate a confirmation email to be sent to the Admin so that they can
        # confirm they want to promote the user.
        promotion_confirm_token = generate_promotion_confirmation_token(
            admin.email, user.email, position
        )
        promotion_confirm_url = generate_url(
            'users.confirm_promotion', promotion_confirm_token
        )
        from celery_runner import celery
        celery.send_task(
            'tasks.send_email',
            kwargs={
                'to':
                admin.email,
                'subject_suffix':
                'Confirm Promotion',
                'html_template':
                render_template(
                    'confirm_promotion.html',
                    promotion_confirm_url=promotion_confirm_url,
                    email=admin.email,
                    position=position,
                    admin_name=f'{admin.first_name} {admin.last_name}',
                    user_name=f'{user.first_name} {user.last_name}'
                ),
                'text_template':
                render_template(
                    'confirm_promotion.txt',
                    promotion_confirm_url=promotion_confirm_url,
                    email=admin.email,
                    position=position,
                    admin_name=f'{admin.first_name} {admin.last_name}',
                    user_name=f'{user.first_name} {user.last_name}'
                )
            }
        )

        response['status'] = 'success'
        response.pop('message')
        return response, 202


=======

        response['status'] = 'success'
        response.pop('message')
        return response, 202
>>>>>>> ARC-105


>>>>>>> Stashed changes
@users_blueprint.route('/admin/confirmpromotion/<token>', methods=['GET'])
def confirm_promotion(token):
    """
    Allow an admin to confirm their promotion of another user
    """
<<<<<<< Updated upstream

    response = {'status': 'fail', 'message': 'Invalid token.'}

    # Decode the token from the email to confirm it was the right one
    try:
        data = confirm_token(token)
    except URLTokenError as e:
        response['error'] = str(e)
        return jsonify(response), 400
    except Exception as e:
        response['error'] = str(e)
        return jsonify(response), 400

    # Ensure that a list was returned
    if not isinstance(data, list):
        response['message'] = 'Invalid Token.'
        return jsonify(response), 400

    # Ensure data is all present
    admin_email = data[0]
    user_email = data[1]
    position = data[2]
    if not admin_email or not user_email or not position:
        response['message'] = 'Invalid data in Token.'
        return jsonify(response), 400

    # Verify both email addresses are valid
    try:
        # validate and get info
        va = validate_email(admin_email)
        vu = validate_email(user_email)
        # replace with normalized form
        valid_admin_email = va['email']
        valid_user_email = vu['email']
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        response['error'] = str(e)
        response['message'] = 'Invalid email.'
        return jsonify(response), 400

    # Ensure both users exist in the database
    if not User.objects(email=valid_admin_email):
        response['message'] = 'Administrator does not exist.'
        return jsonify(response), 400
    if not User.objects(email=valid_user_email):
        response['message'] = 'Target User does not exist.'
        return jsonify(response), 400

    # Get both user objects
    admin_user = User.objects.get(email=valid_admin_email)
    target_user = User.objects.get(email=valid_user_email)

    # Ensure the admin user is allowed to promote other users.
    if not admin_user.is_admin or not admin_user.admin_profile.verified:
        response['message'] = 'User is not authorised to promote other users.'
        return jsonify(response), 400

    # Ensure the target user has their account verified
    if not target_user.verified:
        response['message'] = 'Target user is not verified.'
        return jsonify(response), 400

    # Start promotion process
    target_user.is_admin = True
    target_user.admin_profile = AdminProfile(
        position=position,
        mobile_number=None,
        verified=False,
        promoted_by=admin_user.id
    )
    target_user.last_updated = datetime.utcnow()
    target_user.save()

    # Generate an acknowledgement email to be sent to the User so that they can
    # verify they have been promoted.
    promotion_acknowledge_token = generate_confirmation_token(target_user.email)
    promotion_acknowledge_url = generate_url(
        'users.acknowledge_promotion', promotion_acknowledge_token
    )
    from celery_runner import celery
    celery.send_task(
        'tasks.send_email',
        kwargs={
            'to':
                target_user.email,
            'subject_suffix':
                'Acknowledge Promotion',
            'html_template':
                render_template(
                    'acknowledge_promotion.html',
                    promotion_acknowledge_url_url=promotion_acknowledge_url,
                    email=target_user.email,
                    position=position,
                    user_name=(
                        f'{target_user.first_name} {target_user.last_name}'
                    )
                ),
            'text_template':
                render_template(
                    'acknowledge_promotion.html',
                    promotion_acknowledge_url_url=promotion_acknowledge_url,
                    email=target_user.email,
                    position=position,
                    user_name=(
                        f'{target_user.first_name} {target_user.last_name}'
                    )
                )
        }
    )

    # TODO(davidmatthews1004@gmail.com): Ensure the link can be dynamic.
    client_host = os.environ.get('CLIENT_HOST')
    # We can make our own redirect response by doing the following
    custom_redir_response = app.response_class(
        status=302, mimetype='application/json'
    )
    # TODO(davidmatthews1004@gmail.com): Redirect the Admin somewhere else,
    #  maybe the home screen or a confirmation page.
    redirect_url = 'http://localhost:3000/signin'
    custom_redir_response.headers['Location'] = redirect_url
    return custom_redir_response


@users_blueprint.route('/user/acknowledgepromotion/<token>', methods=['GET'])
def acknowledge_promotion(token):
    """
    Allow a user to acknowledge their promotion and in doing so verify their
    status as an admin
>>>>>>> ARC-105
    """
=======
>>>>>>> Stashed changes

    response = {'status': 'fail', 'message': 'Invalid token.'}

    # Decode the token from the email to confirm it was the right one
    try:
<<<<<<< Updated upstream
<<<<<<< HEAD
        data = confirm_token(token)
=======
        email = confirm_token(token)
>>>>>>> ARC-105
=======
        data = confirm_token(token)
>>>>>>> Stashed changes
    except URLTokenError as e:
        response['error'] = str(e)
        return jsonify(response), 400
    except Exception as e:
        response['error'] = str(e)
        return jsonify(response), 400

<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
    # Ensure that a list was returned
    if not isinstance(data, list):
        response['message'] = 'Invalid Token.'
        return jsonify(response), 400

    # Ensure data is all present
    admin_email = data[0]
    user_email = data[1]
    position = data[2]
    if not admin_email or not user_email or not position:
        response['message'] = 'Invalid data in Token.'
        return jsonify(response), 400

    # Verify both email addresses are valid
    try:
        # validate and get info
        va = validate_email(admin_email)
        vu = validate_email(user_email)
        # replace with normalized form
        valid_admin_email = va['email']
        valid_user_email = vu['email']
<<<<<<< Updated upstream
=======
    # Verify it is actually a valid email
    try:
        # validate and get info
        v = validate_email(email)
        # replace with normalized form
        valid_email = v['email']
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        response['error'] = str(e)
        response['message'] = 'Invalid email.'
        return jsonify(response), 400

<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
    # Ensure both users exist in the database
    if not User.objects(email=valid_admin_email):
        response['message'] = 'Administrator does not exist.'
        return jsonify(response), 400
    if not User.objects(email=valid_user_email):
        response['message'] = 'Target User does not exist.'
        return jsonify(response), 400

    # Get both user objects
    admin_user = User.objects.get(email=valid_admin_email)
    target_user = User.objects.get(email=valid_user_email)

    # Ensure the admin user is allowed to promote other users.
    if not admin_user.is_admin or not admin_user.admin_profile.verified:
        response['message'] = 'User is not authorised to promote other users.'
        return jsonify(response), 400

    # Ensure the target user has their account verified
    if not target_user.verified:
        response['message'] = 'Target user is not verified.'
        return jsonify(response), 400

    # Start promotion process
    target_user.is_admin = True
    target_user.admin_profile = AdminProfile(
        position=position,
        mobile_number=None,
        verified=False,
        promoted_by=admin_user.id
    )
    target_user.last_updated = datetime.utcnow()
    target_user.save()

    # Generate an acknowledgement email to be sent to the User so that they can
    # verify they have been promoted.
    promotion_acknowledge_token = generate_confirmation_token(target_user.email)
    promotion_acknowledge_url = generate_url(
        'users.acknowledge_promotion', promotion_acknowledge_token
    )
<<<<<<< Updated upstream
=======
    # Ensure the user exists in the database
    if not User.objects(email=valid_email):
        response['message'] = 'User does not exist.'
        return jsonify(response), 400

    # Get the user object
    user = User.objects.get(email=valid_email)

    # Ensure the user is verfiied, an admin and that they have a valid admin
    # profile
    if not user.verified:
        response['message'] = 'User is not verified.'
        return jsonify(response), 400
    if not user.is_admin:
        response['message'] = 'User is not an Admin.'
        return jsonify(response), 400
    if not user.admin_profile:
        response['message'] = 'User has an invalid Admin profile.'
        return jsonify(response), 400

    # Verify user's admin status
    user.admin_profile.verified = True
    user.save()

    # Get promoter information so that they can be sent an email letting them
    # know that the user they promoted has been verified.
    promoter_id = user.admin_profile.promoted_by
    promoter = User.objects.get(id=promoter_id)

>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
    from celery_runner import celery
    celery.send_task(
        'tasks.send_email',
        kwargs={
            'to':
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
                target_user.email,
            'subject_suffix':
                'Acknowledge Promotion',
            'html_template':
                render_template(
                    'acknowledge_promotion.html',
                    promotion_acknowledge_url_url=promotion_acknowledge_url,
                    email=target_user.email,
                    position=position,
                    user_name=(
                        f'{target_user.first_name} {target_user.last_name}'
<<<<<<< Updated upstream
=======
                promoter.email,
            'subject_suffix':
                'Promotion Verified',
            'html_template':
                render_template(
                    'promotion_verified.html',
                    email=promoter.email,
                    promoter_name=(
                        f'{promoter.first_name} {promoter.last_name}'
                    ),
                    user_name=(
                        f'{user.first_name} {user.last_name}'
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
                    )
                ),
            'text_template':
                render_template(
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
                    'acknowledge_promotion.html',
                    promotion_acknowledge_url_url=promotion_acknowledge_url,
                    email=target_user.email,
                    position=position,
                    user_name=(
                        f'{target_user.first_name} {target_user.last_name}'
<<<<<<< Updated upstream
=======
                    'promotion_verified.txt',
                    email=promoter.email,
                    promoter_name=(
                        f'{promoter.first_name} {promoter.last_name}'
                    ),
                    user_name=(
                        f'{user.first_name} {user.last_name}'
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
                    )
                )
        }
    )
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes

    # TODO(davidmatthews1004@gmail.com): Ensure the link can be dynamic.
    client_host = os.environ.get('CLIENT_HOST')
    # We can make our own redirect response by doing the following
    custom_redir_response = app.response_class(
        status=302, mimetype='application/json'
    )
    # TODO(davidmatthews1004@gmail.com): Redirect the Admin somewhere else,
    #  maybe the home screen or a confirmation page.
    redirect_url = 'http://localhost:3000/signin'
    custom_redir_response.headers['Location'] = redirect_url
    return custom_redir_response


@users_blueprint.route('/user/acknowledgepromotion/<token>', methods=['GET'])
def acknowledge_promotion(token):
    """
    Allow a user to acknowledge their promotion and in doing so verify their
    status as an admin
    """

    response = {'status': 'fail', 'message': 'Invalid token.'}

    # Decode the token from the email to confirm it was the right one
    try:
        email = confirm_token(token)
    except URLTokenError as e:
        response['error'] = str(e)
        return jsonify(response), 400
    except Exception as e:
        response['error'] = str(e)
        return jsonify(response), 400

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
        return jsonify(response), 400

    # Ensure the user exists in the database
    if not User.objects(email=valid_email):
        response['message'] = 'User does not exist.'
        return jsonify(response), 400

    # Get the user object
    user = User.objects.get(email=valid_email)

    # Ensure the user is verfiied, an admin and that they have a valid admin
    # profile
    if not user.verified:
        response['message'] = 'User is not verified.'
        return jsonify(response), 400
    if not user.is_admin:
        response['message'] = 'User is not an Admin.'
        return jsonify(response), 400
    if not user.admin_profile:
        response['message'] = 'User has an invalid Admin profile.'
        return jsonify(response), 400

    # Verify user's admin status
    user.admin_profile.verified = True
    user.save()

    # Get promoter information so that they can be sent an email letting them
    # know that the user they promoted has been verified.
    promoter_id = user.admin_profile.promoted_by
    promoter = User.objects.get(id=promoter_id)

    from celery_runner import celery
    celery.send_task(
        'tasks.send_email',
        kwargs={
            'to':
                promoter.email,
            'subject_suffix':
                'Promotion Verified',
            'html_template':
                render_template(
                    'promotion_verified.html',
                    email=promoter.email,
                    promoter_name=(
                        f'{promoter.first_name} {promoter.last_name}'
                    ),
                    user_name=(
                        f'{user.first_name} {user.last_name}'
                    )
                ),
            'text_template':
                render_template(
                    'promotion_verified.txt',
                    email=promoter.email,
                    promoter_name=(
                        f'{promoter.first_name} {promoter.last_name}'
                    ),
                    user_name=(
                        f'{user.first_name} {user.last_name}'
                    )
                )
        }
    )

<<<<<<< Updated upstream
=======

>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
    # TODO(davidmatthews1004@gmail.com): Ensure the link can be dynamic.
    client_host = os.environ.get('CLIENT_HOST')
    # We can make our own redirect response by doing the following
    custom_redir_response = app.response_class(
        status=302, mimetype='application/json'
    )
    redirect_url = f'http://localhost:3000/signin'
    custom_redir_response.headers['Location'] = redirect_url
    # Additionally, if we need to, we can attach the JWT token in the header
    # custom_redir_response.headers['Authorization'] = f'Bearer {jwt_token}'
    return custom_redir_response


class DisableAccount(Resource):
    """Route for Admins to disable user accounts"""

<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
    method_decorators = {'post': [authenticate_admin]}
=======
    method_decorators = {'put': [authenticate_admin]}
>>>>>>> ARC-105
<<<<<<< Updated upstream
=======
    method_decorators = {'put': [authenticate_admin]}
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes

    def put(self, resp):
        post_data = request.get_json()

        # Validating empty payload
<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
>>>>>>> Stashed changes
        response = {'status': 'fail', 'message': 'User does not exist.'}
=======
        response = {'status': 'fail', 'message': 'Invalid payload.'}
>>>>>>> ARC-105
<<<<<<< Updated upstream
=======
        response = {'status': 'fail', 'message': 'Invalid payload.'}
>>>>>>> ARC-105
=======
>>>>>>> Stashed changes
        if not post_data:
            return response, 400

        # Extract the request body data
        email = post_data.get('email', None)

        if not email:
            response['message'] = 'No email provided.'
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
            response['message'] = 'User cannot be found.'
            return response, 404

        user = User.objects.get(email=valid_email)
        user.active = False
        user.last_updated = datetime.utcnow()
        user.save()

        response['status'] = 'success'
<<<<<<< HEAD
<<<<<<< Updated upstream
<<<<<<< HEAD
        response['message'
                 ] = f'The account for User {user.id} has been disabled.'
=======
=======
>>>>>>> ARC-105
=======
        response['message'
                 ] = f'The account for User {user.id} has been disabled.'
=======
>>>>>>> Stashed changes
        response['message'] = (
            f'The account for User {user.email} has been '
            f'disabled.'
        )
<<<<<<< Updated upstream
<<<<<<< HEAD
>>>>>>> ARC-105
=======
=======
>>>>>>> Stashed changes
>>>>>>> ARC-105
        return response, 200


api.add_resource(PingTest, '/ping')
api.add_resource(UserList, '/users')
api.add_resource(Users, '/user')
api.add_resource(UserProfiles, '/user/profile')
api.add_resource(UserLast, '/user/last')
api.add_resource(UserAlloys, '/user/alloys')
api.add_resource(UserConfigurations, '/user/configurations')
api.add_resource(AdminCreate, '/admin/create')
api.add_resource(DisableAccount, '/user/disable')
api.add_resource(UserGraphs, '/user/graphs')
