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

ratings_blueprint = Blueprint('ratings', __name__)
logger = AppLogger(__name__)


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


class UserFeedback(Resource):
    """
    Route for user to submit feedback.
    """

    method_decorators = {'post': [authenticate_user_cookie_restful]}

    # noinspection PyMethodMayBeStatic
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
        # if not rating:
        #     response['message'] = 'No rating provided.'
        #     return response, 400
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

        feedback_mailing_list = []
        # TODO(davidmatthews1004@gmail.com) Get all admins that are subscribed
        #  to the feedback mailing list.
        feedback_mailing_list.append('feedback@arclytics.io')

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


class FeedbackList(Resource):
    """
    Route for admins to view a list of feedback submissions.
    """

    method_decorators = {'get': [authorize_admin_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def get(self, _):
        """Return a list of feedback based of get request from Admin"""

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        data = request.get_json()

        sort_on = data.get('sort_on', None)
        offset = data.get('offset', None)
        limit = data.get('limit', None)

        # Validate sort parameters
        if sort_on:
            valid_sort_keys = [
                'category', '-category', 'rating', '-rating', 'created_date',
                '-category_date'
            ]
            sort_valid = False
            for k in valid_sort_keys:
                if k == sort_on:
                    sort_valid = True
                    break

            if not sort_valid:
                response['message'] = 'Sort value is invalid.'
                return response, 400

        # Validate limit
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
        feedback_size = Feedback.objects.count()

        if offset:
            if not isinstance(offset, int):
                response['message'] = 'Offset value is invalid.'
                return response, 400
            if offset > feedback_size + 1:
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
            query_set = Feedback.objects[offset - 1:offset + limit -
                                         1].order_by(sort_on)
        else:
            # Get the objects starting at the offset and limit the number of
            # results.
            query_set = Feedback.objects[offset - 1:offset + limit - 1]

        response['sort_on'] = sort_on
        # Next offset is the offset for the next page of results. Prev is for
        # the previous.
        response['next_offset'] = None
        response['prev_offset'] = None
        response['limit'] = limit

        if offset + limit - 1 < feedback_size:
            response['next_offset'] = offset + limit
        if offset - limit >= 1:
            response['prev_offset'] = offset - limit

        if feedback_size % limit == 0:
            total_pages = int(feedback_size / limit)
        else:
            total_pages = int(feedback_size / limit) + 1
        current_page = int(offset / limit) + 1

        response.pop('message')
        response['status'] = 'success'
        response['current_page'] = current_page
        response['total_pages'] = total_pages
        response['data'] = [obj.to_dict() for obj in query_set]
        return response, 200


class SubscribeFeedback(Resource):
    """
    Route for Admins to subscribe to the feedback mailing list.
    """

    method_decorators = {'post': [authorize_admin_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def post(self, user):
        """
        Toggle subscription to the feedback mailing list.
        """

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
api.add_resource(FeedbackList, Routes.FeedbackList.value)
api.add_resource(SubscribeFeedback, Routes.SubscribeFeedback.value)
