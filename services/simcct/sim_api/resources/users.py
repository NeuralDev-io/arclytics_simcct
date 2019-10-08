# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# users.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.03'
"""users.py: 

This file defines all the API resource routes and controller definitions using 
the Flask Resource inheritance model.
"""

from datetime import datetime
from typing import Tuple

from flask import Blueprint, request
from flask_restful import Resource
from mongoengine.errors import ValidationError

from arc_logging import AppLogger
from sim_api.extensions import api, apm
from sim_api.middleware import (
    authenticate_user_cookie_restful, authorize_admin_cookie_restful
)
from sim_api.models import (User, UserProfile)

logger = AppLogger(__name__)
users_blueprint = Blueprint('users', __name__)


class UserList(Resource):
    """Return all users (admin only)"""

    method_decorators = {'get': [authorize_admin_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def get(self, _) -> Tuple[dict, int]:
        """Get all users only available to admins."""
        # user_list = User.as_dict
        # response = {'status': 'success', 'data': {'users': user_list}}
        # return response, 200

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        data = request.get_json()

        if isinstance(data, dict):
            sort_on = data.get('sort_on', None)
            offset = data.get('offset', None)
            limit = data.get('limit', None)
        else:
            sort_on = None
            offset = None
            limit = None

        # Validate sort parameters
        if sort_on:
            valid_sort_keys = [
                'email', '-email', 'admin', '-admmin', 'verified', '-verified',
                'fullname', '-fullname'
            ]
            sort_valid = False
            for k in valid_sort_keys:
                if k == sort_on:
                    sort_valid = True
                    break

            if not sort_valid:
                response['message'] = 'Sort value is invalid.'
                return response, 400

        # Validate limit:
        if limit:
            if not isinstance(limit, int):
                response['message'] = 'Limit value is invalid.'
                return response, 400
            if not limit >= 1:
                response['message'] = 'Limit must be > 1.'
                return response, 400
        else:
            limit = 10

        # Validate offset
        user_size = User.objects.count()
        if offset:
            if not isinstance(offset, int):
                response['message'] = 'Offset value is invalid.'
                return response, 400
            if offset > user_size + 1:
                response['message'] = 'Offset value exceeds number of records.'
                return response, 400
            if offset < 1:
                response['message'] = 'Offset must be > 1.'
                return response, 400
        else:
            offset = 1

        # Query
        if sort_on:
            # Get the objects starting at the offset, limit the number of
            # results and sort on the sort_on value.
            if sort_on == 'fullname':
                query_set = User.objects[
                            offset - 1: offset + limit - 1
                            ].order_by('last_name', 'first_name')
            elif sort_on == '-fullname':
                query_set = User.objects[
                            offset - 1: offset + limit - 1
                            ].order_by('-last_name', '-first_name')
            else:
                query_set = User.objects[
                            offset - 1: offset + limit - 1
                            ].order_by(sort_on)
        else:
            query_set = User.objects[offset - 1:offset + limit - 1]

        response['sort_on'] = sort_on
        # Next offset is the offset for the next page of results. Prev is for
        # the previous.
        response['next_offset'] = None
        response['prev_offset'] = None
        response['limit'] = limit

        if offset + limit - 1 < user_size:
            response['next_offset'] = offset + limit
        if offset - limit >= 1:
            response['prev_offset'] = offset - limit

        if user_size % limit == 0:
            total_pages = int(user_size / limit)
        else:
            total_pages = int(user_size / limit) + 1
        current_page = int(offset / limit) + 1

        response.pop('message')
        response['status'] = 'success'
        response['current_page'] = current_page
        response['total_pages'] = total_pages
        response['data'] = [obj.to_dict() for obj in query_set]
        return response, 200


class Users(Resource):
    """Get/Put a single user's details."""

    method_decorators = {
        'get': [authenticate_user_cookie_restful],
        'patch': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def get(self, user) -> Tuple[dict, int]:
        response = {'status': 'success', 'data': user.to_dict()}
        return response, 200

    # noinspection PyMethodMayBeStatic
    def patch(self, user: User) -> Tuple[dict, int]:
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
                response['data']['profile']['phase_transform_exp'] = \
                    phase_transform_exp

        # If the user is an admin, we can also update their admin profile
        # details
        if user.is_admin:
            # If the user is an admin but is not verified, we must also reject
            # the request.
            if not user.admin_profile.verified:
                response['message'] = 'User is not verified as an admin.'
                response.pop('data')
                logger.info(response['message'])
                apm.capture_message(response['message'])
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
            response['error'] = str(e)
            response['message'] = 'Validation error.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 418

        # Return response body.
        response['status'] = 'success'
        response.pop('message')
        return response, 200


class UserProfiles(Resource):
    """Create/Retrieve/Update User's profile details"""

    method_decorators = {'post': [authenticate_user_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def post(self, user) -> Tuple[dict, int]:
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
        except ValidationError as e:
            response['error'] = str(e)
            response['message'] = 'Validation error.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
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


api.add_resource(UserList, '/v1/sim/users')
api.add_resource(Users, '/v1/sim/user')
api.add_resource(UserProfiles, '/v1/sim/user/profile')
