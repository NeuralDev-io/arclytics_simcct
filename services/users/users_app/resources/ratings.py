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

from logger.arc_logger import AppLogger
from flask import Blueprint, jsonify, request, render_template
from flask import current_app as app
from flask_restful import Resource

from users_app.middleware import authenticate
from users_app.extensions import api

logger = AppLogger(__name__)

ratings_blueprint = Blueprint('share', __name__)


class Rating(Resource):
    """

    """

    method_decorators = {'post': [authenticate]}

    def post(self, resp) -> Tuple[dict, int]:
        # Get post data
        data = request.get_json()
        pass


api.add_resource(Rating, '/user/rating')
