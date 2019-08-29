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

from users_app.middleware import authenticate, authenticate_admin
from users_app.extensions import api
from users_app.models import Rating, Feedback, User

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
        comments = data.get('comments', None)

        if not category:
            response['message'] = 'No category provided.'
            return response, 400
        if not rating:
            response['message'] = 'No rating provided.'
            return response, 400
        if not comments:
            response['message'] = 'No comments provided.'
            return response, 400

        try:
            Feedback(category=category, rating=rating,
                     comments=comments).validate()
        except ValidationError as e:
            response['error'] = str(e.message)
            response['message'] = 'Rating validation error.'
            return response, 400

        user = User.objects.get(id=resp)
        feedback = Feedback(
            user=user.id, category=category, rating=rating, comments=comments
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
        else:
            offset = 1

        # Start query
        if sort_on:
            query_set = Feedback.objects[offset - 1:offset + limit -
                                         1].order_by(sort_on)
        else:
            query_set = Feedback.objects[offset - 1:offset + limit - 1]

        response['limit'] = limit
        response['sort_on'] = sort_on
        response['next_offset'] = None
        if offset + limit - 1 < feedback_size:
            response['next_offset'] = offset + limit
        response['prev_offset'] = None
        if offset - limit >= 1:
            response['prev_offset'] = offset - limit

        total_pages = int(feedback_size/limit) + 1
        current_page = int(offset/limit) + 1

        response.pop('message')
        response['status'] = 'success'
        response['total_pages'] = total_pages
        response['current_page'] = current_page
        response['data'] = [obj.to_dict() for obj in query_set]
        return response, 200


api.add_resource(UserRating, '/user/rating')
api.add_resource(UserFeedback, '/user/feedback')
api.add_resource(FeedbackList, '/admin/feedback/list')
