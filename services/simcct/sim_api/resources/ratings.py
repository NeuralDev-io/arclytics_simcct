# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# ratings.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>']

__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'David Matthews'
__email__ = 'davidmatthews1004@gmail.com'
__status__ = 'development'
__date__ = '2019.08.26'
"""ratings.py: 

This file defines all the API resource routes and controller definitions for 
Rating and Feedback endpoints using the Flask Resource inheritance model.
"""

from typing import Tuple
from datetime import datetime

from logger.arc_logger import AppLogger
from flask import Blueprint, jsonify, request, render_template
from flask import current_app as app
from flask_restful import Resource
from mongoengine import ValidationError

from sim_api.middleware import authenticate, authenticate_admin
from sim_api.extensions import api
from sim_api.models import Rating, Feedback, User

logger = AppLogger(__name__)

ratings_blueprint = Blueprint('ratings', __name__)


class UserRating(Resource):
    """
    Route for Users to submit ratings.
    """

    method_decorators = {'post': [authenticate]}

    def post(self, resp) -> Tuple[dict, int]:
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

        user = User.objects.get(id=resp)
        user.ratings.append(Rating(rating=rating))
        user.save()

        response['status'] = 'success'
        response['message'] = f'Rating submitted by {user.email}.'
        return response, 200


class UserFeedback(Resource):
    """
    Route for user to submit feedback.
    """

    method_decorators = {'post': [authenticate]}

    def post(self, resp) -> Tuple[dict, int]:
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
        if not rating:
            response['message'] = 'No rating provided.'
            return response, 400
        if not comment:
            response['message'] = 'No comment provided.'
            return response, 400

        try:
            Feedback(category=category, rating=rating,
                     comment=comment).validate()
        except ValidationError as e:
            response['error'] = str(e.message)
            response['message'] = 'Feedback validation error.'
            return response, 400

        user = User.objects.get(id=resp)
        feedback = Feedback(
            user=user.id, category=category, rating=rating, comment=comment
        )
        feedback.save()

        response['status'] = 'success'
        response['message'] = f'Feedback submitted by {user.email}.'
        return response, 200


class FeedbackList(Resource):
    """
    Route for admins to view a list of feedback submissions.
    """

    method_decorators = {'get': [authenticate_admin]}

    def get(self, resp):
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


api.add_resource(UserRating, '/api/v1/sim/user/rating')
api.add_resource(UserFeedback, '/user/feedback')
api.add_resource(FeedbackList, '/admin/feedback/list')
