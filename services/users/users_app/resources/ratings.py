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

from users_app.middleware import authenticate
from users_app.extensions import api
from users_app.models import Rating, Feedback, User

logger = AppLogger(__name__)

ratings_blueprint = Blueprint('ratings', __name__)


class RatingsEndpoints(Resource):
    """

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
        if not user.ratings:
            user.ratings = []
        user.ratings.append(Rating(rating=rating))
        user.save()

        response['status'] = 'success'
        response['message'] = f'Rating submitted by {user.email}.'
        return response, 200


class FeedbackEndpoints(Resource):
    """

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


api.add_resource(RatingsEndpoints, '/user/rating')
api.add_resource(FeedbackEndpoints, '/user/feedback')
