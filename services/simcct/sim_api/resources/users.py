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
from sim_api.routes import Routes
from sim_api.search_service import SearchService

logger = AppLogger(__name__)
users_blueprint = Blueprint('users', __name__)


# We need to ensure we only get a certain amount of information for the user
# for speed purposes
PROJECTIONS = {
    '_id': 0,
    'password': 0,
    'ratings': 0,
    'profile': 0,
    'login_data': 0,
    'last_updated': 0,
    'saved_alloys': 0,
    'disable_admin': 0,
    'admin_profile': 0,
    'last_alloy_store': 0,
    'simulations_count': 0,
    'last_configuration': 0,
    'last_simulation_results': 0,
    'last_simulation_invalid_fields': 0,
}


class UserList(Resource):
    """Resource to return all users without pagination."""

    method_decorators = {'get': [authorize_admin_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def get(self, _) -> Tuple[dict, int]:
        """Get all users without pagination but allow sorting."""
        response = {'status': 'fail', 'message': 'Invalid parameters.'}

        # We are only allowing sorting on the full list but we must always
        # return the full list regardless of sorting in the params.
        sort = None
        if request.args:
            sort = request.args.get('sort', None)

        # Pymongo can take a list of queries as objects so we initially just
        # use an empty list which denotes no sorting required because our
        # Mongo data access layers requires a chained function sort param.
        sort_query = []

        # Validate sort parameters
        if sort:
            # If our sorting value begins with a "-" in the string,
            # then we know
            # we are doing a DESCENDING sort so we will appropriately set
            # the
            # sort direction
            sort_direction = 1
            if str(sort).startswith('-'):
                sort_direction = -1

            valid_sort_keys = {
                'email', '-email', 'admin', '-admin', 'verified', '-verified',
                'full_name', '-full_name', 'first_name', '-first_name',
                'last_name', '-last_name'
            }
            if sort not in valid_sort_keys:
                response['message'] = 'Sort value is invalid.'
                return response, 400

            # If we are sorting on fullname, we will need to split the
            # sort query
            # into a 2 element list so we
            if sort in {'full_name', '-full_name'}:
                sort_query.append(('first_name', sort_direction))
                sort_query.append(('last_name', sort_direction))
            else:
                sort_query.append((sort, sort_direction))

        # In this endpoint, we want to return the full list regardless of any
        # offsets or limits. We are only making sorting available for fun.
        data = SearchService().find(
            query={},
            sort=sort_query,
            limit=0,
            projections=PROJECTIONS
        )

        if not data:
            response['message'] = 'No results found.'
            return response, 404

        # Return the query/search parameters so that the client can
        # request different pages in the future
        response.pop('message')
        response.update(
            {
                'status': 'success',
                'data': data,
                'n_documents': len(data)
            }
        )
        return response, 200


class UserListQuery(Resource):
    """Return all users based on a query (admin only)"""

    method_decorators = {'get': [authorize_admin_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def get(self, _) -> Tuple[dict, int]:
        """Get all users only available to admins."""

        response = {'status': 'fail', 'message': 'Invalid parameters.'}

        # ========== # VALIDATION OF PARAMETERS # ========== #
        # Check whether there are any param args
        if not request.args:
            return response, 400

        sort = None
        if request.args:
            sort = request.args.get('sort', None)

        # Skip/offset of 0 is unlimited
        try:
            offset = int(request.args.get('offset', 0))
        except ValueError:
            response.update({'message': 'Invalid offset parameter.'})
            return response, 400

        # Limit of 0 is unlimited
        try:
            # We always want to return a full list if there is no limit
            # requested so that's why it's 0.
            limit = int(request.args.get('limit', 0))
        except ValueError:
            response.update({'message': 'Invalid limit parameter.'})
            return response, 400

        # Validate limit:
        if limit < 0:
            response['message'] = 'Limit must be a positive int.'
            return response, 400

        # Pymongo can take a list of queries as objects so we initially just
        # use an empty list which denotes no sorting required because our
        # Mongo data access layers requires a chained function sort param.
        sort_query = []

        # Validate sort parameters
        if sort:
            valid_sort_keys = {
                'email', '-email', 'admin', '-admin', 'verified', '-verified',
                'full_name', '-full_name', 'first_name', '-first_name',
                'last_name', '-last_name'
            }
            if sort not in valid_sort_keys:
                response['message'] = 'Sort value is invalid.'
                return response, 400

            # ========== # SETTING UP SORTING # ========== #
            # If our sorting value begins with a "-" in the string, then we
            # know we are doing a DESCENDING sort so we will appropriately set
            # the sort direction
            sort_direction = 1
            if str(sort).startswith('-'):
                sort_direction = -1

            # If we are sorting on fullname, we will need to split the
            # sort query into a 2 element list so we
            if sort in {'full_name', '-full_name'}:
                sort_query.append(('first_name', sort_direction))
                sort_query.append(('last_name', sort_direction))
            else:
                sort_query.append((sort, sort_direction))

        # We need the full list to check for pagination
        n_total_documents = SearchService().count(limit=0)

        # Validate offset
        if offset > 0:
            if offset >= n_total_documents:
                response.update(
                    {
                        'message': 'Offset value exceeds number of documents.',
                        'sort': sort,
                        'offset': offset,
                        'limit': limit
                    }
                )
                return response, 400

        # ========== # QUERY THE DATABASE # ========== #
        # Because we want a full list returned, we will not have a query
        # selector.
        users_list = SearchService().find_slice(
            query={},
            projections=PROJECTIONS,
            skip=offset,
            limit=limit,
            sort=sort_query
        )

        n_documents = len(users_list)
        if n_documents <= 0:
            response.update({'message': 'No results found.'})
            return response, 404

        # ========== # PREPARE RESPONSE # ========== #
        # If there are no values for getting the next or previous offset (i.e.
        # no limit has been provided, we just return null for them.
        response.update({
            'status': 'success',
            'sort': sort,
            'offset': offset,
            'limit': limit,
            'next_offset': None,
            'prev_offset': None,
            'n_results': n_documents,
            'data': users_list,
        })
        response.pop('message')

        # A limit of 0, meaning the client does not want any subset of the
        # full list so there is no need to worry about offsets and pages.
        # We also want to just return everything if the limit requested was
        # way more than what results we found any way.
        # Plus we can avoid a divide by zero error from below.
        if limit == 0 or limit > n_total_documents:
            return response, 200

        # Next offset is the offset for the next page of results. Prev is for
        # the previous.
        if offset + limit - 1 < n_total_documents:
            response.update({'next_offset': offset + limit})
        if offset - limit >= 0:
            response.update({'prev_offset': offset - limit})

        if n_total_documents % limit == 0:
            total_pages = int(n_total_documents / limit)
        else:
            total_pages = int(n_total_documents / limit) + 1
        current_page = int(offset / limit) + 1

        response.update(
            {'current_page': current_page, 'total_pages': total_pages}
        )

        return response, 200


class SearchUsers(Resource):
    """Alloys administrators to search the database for a user/users"""

    method_decorators = {'get': [authorize_admin_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def get(self, _) -> Tuple[dict, int]:
        """

        Args:
            _:

        Returns:

        """

        response = {'status': 'fail', 'message': 'Invalid parameters.'}

        # ========== # VALIDATION OF PARAMETERS # ========== #
        # Check the param args if there are any
        if not request.args:
            return response, 400

        query, sort = None, None
        if request.args:
            query = request.args.get('query', None)
            sort = request.args.get('sort', None)

        # Limit of 0 is unlimited
        try:
            # By default, we limit the number of returned searches to 100.
            limit = int(request.args.get('limit', 100))
        except ValueError:
            response.update({'message': 'Invalid limit parameter.'})
            return response, 400

        # Validate limit:
        if limit < 0:
            response['message'] = 'Limit must be a positive int.'
            return response, 400

        # Ensure query parameters have been given, otherwise there is nothing
        # to search for.
        if not query:
            response.update({'message': 'No query parameters provided.'})
            return response, 400

        # Pymongo can take a list of queries as objects so we initially just
        # use an empty list which denotes no sorting required because our
        # Mongo data access layers requires a chained function sort param.
        sort_query = []

        # Validate sort parameter options
        if sort:
            valid_sort_keys = {
                'email', '-email', 'admin', '-admin', 'verified', '-verified',
                'full_name', '-full_name', 'first_name', '-first_name',
                'last_name', '-last_name'
            }
            if sort not in valid_sort_keys:
                response.update({'message': 'Sort value is invalid.'})
                return response, 400

            # ========== # SETTING UP SORTING # ========== #
            # If our sorting value begins with a "-" in the string, then we
            # know we are doing a DESCENDING sort so we will appropriately set
            # the sort direction
            sort_direction = 1
            if str(sort).startswith('-'):
                sort_direction = -1

            # If we are sorting on fullname, we will need to split the
            # sort query into a 2 element list so we
            if sort in {'full_name', '-full_name'}:
                sort_query.append(('first_name', sort_direction))
                sort_query.append(('last_name', sort_direction))
            else:
                sort_query.append((sort, sort_direction))

        # ========== # QUERY THE DATABASE # ========== #
        # This is the key advanced text search.
        # Ensuring no default language helps with searching emails because
        # of the symbols.
        query_selector = {
            '$text': {
                '$search': query,
                '$language': 'none',
                '$caseSensitive': False
            }
        }

        # Check if the user is trying to search for an email by doing a rather
        # simple check if the `@` symbol is in the string. If it is, we
        # will try to search for an email instead.
        # Thus:
        #  - Searching for ironman@avengers.io will only return 1 result.
        #  - Searching for ironman@ will fail
        #  - Searching for ironman will return all emails with that substring
        #    in the email.
        if '@' in str(query):
            data = SearchService().find(
                query={'email': query},
                sort=sort_query,
                limit=limit,
                projections=PROJECTIONS
            )

            n_results = len(data)
            if n_results > 0:
                # We found a user with this email so let's return that
                return {
                    'status': 'success',
                    'query': query,
                    'limit': limit,
                    'data': data,
                    'n_results': n_results
                }, 200

            # we failed to find via email to lets do a string search by going
            # to the next call.

        # Use MongoDB string search on a compound index we created in the
        # `sim_api.models.py` to ensure this is possible for first_name,
        # last_name, and email.
        data = SearchService().find(
            query=query_selector,
            sort=sort_query,
            limit=limit,
            projections=PROJECTIONS
        )

        n_documents = len(data)
        if not n_documents:
            response.update({'message': 'No results found.'})
            return response, 404

        # ========== # PREPARE RESPONSE # ========== #
        # No skip/offset with pagination will be provided because it would
        # take too long to do anyway since you would need to do 2 full searches
        # or manipulate the returned cursor to limit after the fact to get
        # a subset of the results from offset/limit.
        # The best way to avoid this is just to allow the client to limit the
        # number of returned results.
        # May be able to do it in the future but for now we will avoid.
        response.update({
            'status': 'success',
            'sort': sort,
            'limit': limit,
            'n_results': n_documents,
            'data': data,
        })
        response.pop('message')
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


api.add_resource(UserList, Routes.user_list.value)
api.add_resource(UserListQuery, Routes.user_list_query.value)
api.add_resource(SearchUsers, Routes.search_users.value)
api.add_resource(Users, Routes.users.value)
api.add_resource(UserProfiles, Routes.user_profiles.value)
