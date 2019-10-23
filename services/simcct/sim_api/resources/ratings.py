# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# ratings.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.08.26'
"""ratings.py: 

This file defines all the API resource routes and controller definitions for 
Rating and Feedback endpoints using the Flask Resource inheritance model.
"""

from math import floor
from typing import Tuple

from flask import Blueprint, render_template, request
from flask_restful import Resource
from mongoengine import ValidationError

from arc_logging import AppLogger
from sim_api.extensions import api
from sim_api.middleware import (
    authenticate_user_cookie_restful, authorize_admin_cookie_restful
)
from sim_api.models import Feedback, Rating
from sim_api.routes import Routes
from sim_api.feedback_search_service import (
    FeedbackSearchService as SearchService
)

ratings_blueprint = Blueprint('ratings', __name__)
logger = AppLogger(__name__)


# Projection of the fields we want returned from a feedback collection
PROJECTIONS = {
    "$project": {
        "_id": 0,
        "category": 1,
        "rating": 1,
        "comment": 1,
        "created_date": 1,
        "user.email": 1,
    }
}


# noinspection PyMethodMayBeStatic
class UserRating(Resource):
    """
    Route for Users to submit ratings.
    """

    method_decorators = {'post': [authenticate_user_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def post(self, user) -> Tuple[dict, int]:
        """Post a rating and save it to the user's list of ratings"""
        # Get post data
        data = request.get_json()

        # Validating empty payload
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not data:
            return response, 400

        # Extract the request body data
        rating = data.get('rating', None)

        if not rating:
            response['message'] = 'No rating provided.'
            return response, 400

        try:
            Rating(rating=rating).validate()
        except ValidationError as e:
            response['error'] = str(e.message)
            response['message'] = 'Rating validation error.'
            return response, 400

        user.ratings.append(Rating(rating=rating))
        user.save()

        response['status'] = 'success'
        response['message'] = f'Rating submitted by {user.email}.'
        return response, 200


# noinspection PyMethodMayBeStatic
class UserFeedback(Resource):
    """
    Route for user to submit feedback.
    """

    method_decorators = {
        'post': [authenticate_user_cookie_restful],
        'get': [authenticate_user_cookie_restful]
    }

    def get(self, _):
        """Return a list of feedback based of get request from Admin"""

        response = {'status': 'fail', 'message': 'Invalid parameters.'}

        # ========== # VALIDATION OF PARAMETERS # ========== #
        # Check whether there are any param args
        if not request.args:
            return response, 400

        sort = None
        if request.args:
            sort = request.args.get('sort', None)

        # page number
        try:
            page = int(request.args.get('page', 0))
        except ValueError:
            response.update({'message': 'Required page parameter.'})
            return response, 400

        # Limit of 0 is unlimited
        try:
            # We always want to return a full list if there is no limit
            # requested so that's why it's 0.
            limit = int(request.args.get('limit', 0))
        except ValueError:
            response.update({'message': 'Invalid limit parameter.'})
            return response, 400

        if limit < 0:
            response['message'] = 'Limit must be a positive int.'
            return response, 400

        # We use a lookup to do a left join on the Feedback --> Users
        # collection based on the `localField` to the `foreignField`.
        # We then do all the sort, skip/offset, and limit before only
        # projecting the results we want back.

        # Stage 1 -- Lookup to from Feedback --> Users and get the user
        # to be returned `as` the new Array field `user`. Also setup the
        # pipeline list which we can add to it later.
        pipeline = [
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user",
                    "foreignField": "_id",
                    "as": "user"
                }
            },
            # Stage 2 -- Our returned result is an Array so we unwind it to
            # make it a dictionary.
            {"$unwind": "$user"},
        ]

        # Stage 3 -- If we have to sort, then we validate it first and then
        # add it to our pipeline. We sort before we apply any limit on it.
        if sort:
            valid_sort_keys = {
                'category', '-category', 'rating', '-rating',
                'created_date', '-created_date', 'comment', '-comment'
            }
            if sort not in valid_sort_keys:
                response['message'] = 'Sort value is invalid.'
                return response, 400

            # ========== # SETTING UP SORTING # ========== #
            # If our sorting value begins with a "-" in the string, then we
            # know we are doing a DESCENDING sort so we will
            # appropriately set
            # the sort direction
            sort_direction = 1
            sort_key = sort
            if str(sort).startswith('-'):
                # We remove the first character as it's not a valid key
                sort_key = sort[1:]
                # Reverse for DESCENDING
                sort_direction = -1

            pipeline.append({"$sort": {sort_key: sort_direction}})
        else:
            # By default we always sort on the latest feedback created
            pipeline.append({"$sort": {'created_date': -1}})

        current_page = 0 if limit == 0 else page
        skip = current_page * limit
        pipeline.append({"$skip": skip})

        # Stage 4 -- If we have a limit, we validate then add to the pipeline
        if limit >= 1:
            pipeline.append({"$limit": limit})
            # We need the full list to check for pagination
            n_total_documents = SearchService().count(limit=0)

            total_pages = floor(n_total_documents / limit)
            if n_total_documents % limit == 0:
                total_pages = total_pages - 1
        else:
            total_pages = 0

        # Stage 6 -- Return/select only those things we want.
        pipeline.append(PROJECTIONS)

        # ========== # QUERY THE DATABASE # ========== #
        feedback_list = SearchService().aggregate(pipeline)

        n_documents = len(feedback_list)
        if n_documents <= 0:
            response.update({'message': 'No results found.'})
            return response, 404

        # ========== # PREPARE RESPONSE # ========== #
        # If there are no values for getting the next or previous offset (i.e.
        # no limit has been provided, we just return null for them.
        response.update(
            {
                'sort': sort,
                'limit': limit,
                'status': 'success',
                'current_page': current_page,
                'total_pages': total_pages,
                'n_results': n_documents,
                'data': feedback_list,
            }
        )
        response.pop('message')

        return response, 200

    def post(self, user) -> Tuple[dict, int]:
        """
        Method to post feedback and try to create a Feedback object then
        notify the subscribed admins of the new post.
        """

        # Get post data
        data = request.get_json()

        # Validating empty payload
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not data:
            return response, 400

        # Extract the request body data
        category = data.get('category', None)
        rating = data.get('rating', None)
        comment = data.get('comment', None)

        if not category:
            response['message'] = 'No category provided.'
            return response, 400
        if not comment:
            response['message'] = 'No comment provided.'
            return response, 400

        try:
            feedback = Feedback(
                user=user.id,
                category=category,
                rating=rating,
                comment=comment
            )
            feedback.save()
        except ValidationError as e:
            response['error'] = str(e.message)
            response['message'] = 'Feedback validation error.'
            return response, 400

        feedback_mailing_list = [
            # 'feedback@arclytics.io',
            'admin@arclytics.io'
        ]

        from sim_api.email_service import send_email
        send_email(
            to=feedback_mailing_list,
            subject_suffix='A User has submitted Feedback',
            html_template=render_template(
                'feedback_submitted.html',
                user_name=f'{user.first_name} {user.last_name}',
                category=category,
                rating=rating,
                comment=comment
            ),
            text_template=render_template(
                'feedback_submitted.txt',
                user_name=f'{user.first_name} {user.last_name}',
                category=category,
                rating=rating,
                comment=comment
            )
        )

        response['status'] = 'success'
        response['message'] = f'Feedback submitted by {user.email}.'
        return response, 200


# noinspection PyMethodMayBeStatic
class UserFeedbackSearch(Resource):
    method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self, _):
        """Endpoint to do search query on the Feedback collection which also
        returns a paginated result if the user limits the search.

        Args:
            _: a `sim_api.models.User` instance that is passed from the
            middleware and not used.

        Returns:
            A valid HTTP response as a Python dict and a status code.
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

        # Ensure query parameters have been given, otherwise there is
        # nothing to search for.
        if not query:
            response.update({'message': 'No query parameters provided.'})
            return response, 400

        # Limit of 0 is unlimited
        try:
            # By default, we limit the number of returned searches to 200.
            limit = int(request.args.get('limit', 200))
        except ValueError:
            response.update({'message': 'Invalid limit parameter.'})
            return response, 400

        # Validate limit:
        if limit < 0:
            response['message'] = 'Limit must be a positive int.'
            return response, 400

        # Get the page number to check how many skips to return
        try:
            page = int(request.args.get('page', 0))
        except ValueError:
            response.update({'message': 'Invalid page parameter.'})
            return response, 400

        # Stage 3 -- If we have to sort, then we validate it first and then
        # add it to our pipeline. We sort before we apply any limit on it.
        if sort:
            valid_sort_keys = {
                'category', '-category', 'rating', '-rating',
                'created_date', '-created_date', 'comment', '-comment'
            }
            if sort not in valid_sort_keys:
                response['message'] = 'Sort value is invalid.'
                return response, 400

            # ========== # SETTING UP SORTING # ========== #
            # If our sorting value begins with a "-" in the string, then we
            # know we are doing a DESCENDING sort so we will
            # appropriately set
            # the sort direction
            sort_direction = 1
            sort_key = sort
            if str(sort).startswith('-'):
                # We remove the first character as it's not a valid key
                sort_key = sort[1:]
                # Reverse for DESCENDING
                sort_direction = -1

            # Sort on both the chosen sort values and the text search score
            # returned from the weighting.
            sort_stage = {"$sort": {sort_key: sort_direction}}
        else:
            # By default we always sort on the latest feedback created
            sort_stage = {"$sort": {"created_date": -1}}

        # We need to get the number of skips to return the sliced result.
        current_page = 0 if limit == 0 else page
        skip = current_page * limit

        # limit_stage = {"$limit": limit} if limit >= 1 else {"$limit": 200}

        # Check if the user is trying to search for an email by doing a
        # rather simple check if the `@` symbol is in the string. If it is,
        # we will try to search for an email instead.
        # Thus:
        #  - Searching for ironman@avengers.io will only return 1 result.
        #  - Searching for ironman@ will fail
        #  - Searching for ironman will return all emails with that
        #  substring
        #    in the email.
        if '@' in str(query):
            # Stage 1 -- Lookup to from Feedback --> Users and get the user
            # to be returned `as` the new Array field `user`. Also setup the
            # pipeline list which we can add to it later.
            email_pipeline = [
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "user",
                        "foreignField": "_id",
                        "as": "user"
                    }
                },
                # Stage 2 -- Our returned result is an Array so we unwind it to
                # make it a dictionary.
                {"$unwind": "$user"},
                # Stage 3 -- Match the query email with the user.email that we
                # unwound in the last stage.
                {
                    "$match": {
                        "user.email": query
                    }
                },
                sort_stage,
                PROJECTIONS
            ]

            data = SearchService().aggregate(email_pipeline)

            n_results = len(data)
            if n_results == 1:
                # We found a user with this email so let's return that
                return {
                       'status': 'success',
                       'query': query,
                       'sort': sort,
                       'limit': limit,
                       'page': 0,
                       'total_pages': 1,
                       'data': data,
                       'n_total_results': 1
                   }, 200
            if n_results > 1:
                # Since we found more than 1 result, we need to slice based
                # on the limit asked.
                return {
                    'status': 'success',
                    'query': query,
                    'sort': sort,
                    'limit': limit,
                    # Return the slice from the skip to the limit
                    # Note that Python returns the end of the list if the
                    # limit is more than than len(list)
                    'data': data[skip:skip+limit],
                    'n_total_results': n_results
                }, 200

            # we failed to find via email to lets do a string search by
            # going to the next call.

        # We use the compound text index on `comment` and `category` to do a
        # advanced text search. Our indexes are weighted to the categories so
        # we will more than likely see those first.
        pipeline = [{
            "$match": {
                "$text": {
                    "$search": query,
                    "$caseSensitive": False
                }
            }
        }, {
            "$lookup": {
                "from": "users",
                "localField": "user",
                "foreignField": "_id",
                "as": "user"
            }
        }, {"$unwind": "$user"}, sort_stage, PROJECTIONS]

        # Query the database to get the full result
        data = SearchService().aggregate(pipeline)

        # Instead of using a limit stage, we wil just go ahead and get
        # everything and then we can slice based on skip:limit - 1 results.
        n_results = len(data)
        if n_results > 0:
            # We need the full list to check for pagination.
            if limit == 0:
                # No limit was asked so we return everything
                return {
                    'status': 'success',
                    'query': query,
                    'sort': sort,
                    'limit': limit,
                    'page': 0,
                    'total_pages': 1,
                    'data': data,
                    'n_total_results': n_results
                }, 200
            else:
                # We know there is more results than the limit so we need
                # some pagination.
                total_pages = floor(n_results / limit)
                if n_results % limit == 0:
                    total_pages = total_pages - 1
                else:
                    total_pages = total_pages

                return {
                    'status': 'success',
                    'query': query,
                    'sort': sort,
                    'limit': limit,
                    'page': page,
                    'skip': skip,
                    'total_pages': total_pages,
                    'data': data[skip:skip+limit],
                    'n_total_results': n_results
                }, 200

        return {'status': 'fail', 'message': 'No results.'}, 404


# noinspection PyMethodMayBeStatic
class SubscribeFeedback(Resource):
    """
    Route for Admins to subscribe to the feedback mailing list.
    """

    method_decorators = {'post': [authorize_admin_cookie_restful]}

    def post(self, user):
        """Toggle subscription to the feedback mailing list."""

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        data = request.get_json()
        if not data:
            return response, 400

        action = data.get('action', None)

        if not action:
            response['message'] = 'No action provided.'
            return response, 400

        if action == 'subscribe':
            if user.admin_profile.sub_to_feedback:
                response['message'] = 'User is already subscribed.'
                return response, 400
            else:
                user.admin_profile.sub_to_feedback = True
                user.save()
                response['status'] = 'success'
                response['message'] = 'User has been subscribed.'
                return response, 200

        elif action == 'unsubscribe':
            if not user.admin_profile.sub_to_feedback:
                response['message'] = 'User is already unsubscribed.'
                return response, 400
            else:
                user.admin_profile.sub_to_feedback = False
                user.save()
                response['status'] = 'success'
                response['message'] = 'User has been unsubscribed.'
                return response, 200
        else:
            response['message'] = 'Invalid action.'
            return response, 400


api.add_resource(UserRating, Routes.UserRating.value)
api.add_resource(UserFeedback, Routes.UserFeedback.value)
api.add_resource(UserFeedbackSearch, Routes.UserFeedbackSearch.value)
api.add_resource(SubscribeFeedback, Routes.SubscribeFeedback.value)
