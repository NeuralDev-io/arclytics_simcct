# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# user_analytics.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '0.1.0'
__status__ = 'development'
__date__ = '2019.10.02'

"""user_analytics.py: 

{Description}
"""

from os import environ as env
from typing import Tuple

import pandas as pd
from flask import Blueprint
from flask_restful import Resource

from arc_api.extensions import api, redis_client
from arc_api.mongo_service import MongoService
from arc_api.middleware import authorize_admin_cookie_restful
from arc_logging import AppLogger

user_analytics_blueprint = Blueprint('user_analytics', __name__)
logger = AppLogger(__name__)


# noinspection PyMethodMayBeStatic
class UserLoginData(Resource):

    # method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self) -> Tuple[dict, int]:
        """Simply get the number of logged in users by Session in Redis."""

        # Get the number of keys using the pattern that we defined
        # in `services.simcct.sim_api.extensions.Session.redis_session`
        # as being `session:{session id}`. We just get all the keys
        # matching this pattern which means they have logged in.
        keys = redis_client.keys(pattern=u'session*')

        return {'status': 'success', 'value': len(keys)}, 200


# noinspection PyMethodMayBeStatic
class UserProfileData(Resource):

    # method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self) -> Tuple[dict, int]:
        """Uses MongoDB Aggregation Pipeline to get all Profile data from
        the `users` collection and then transforms that to allow building
        a bar chart with `plotly.graph_objects.Bar` traces.

        Returns:
            A valid HTTP Response with a dictionary of data and a status code.
        """

        pipeline = [
            {'$unwind': '$profile'},
            {
                '$project': {
                    'aim': '$profile.aim',
                    'highest_education': '$profile.highest_education',
                    'sci_tech_exp': '$profile.sci_tech_exp',
                    'phase_transform_exp': '$profile.phase_transform_exp',
                    '_id': 0
                }
            },
        ]

        df = MongoService().read_aggregation('arc_dev', 'users', pipeline)

        response = {
            'status': 'success',
            'plotly_chart_type': 'bar',
            'data': {
                'aim': {
                    'x': list(df['aim'].unique()),
                    'y': list(df['aim'].value_counts())
                },
                'highest_education': {
                    'x': list(df['highest_education'].unique()),
                    'y': list(df['highest_education'].value_counts())
                },
                'sci_tech_exp': {
                    'x': list(df['sci_tech_exp'].unique()),
                    'y': list(df['sci_tech_exp'].value_counts())
                },
                'phase_transform_exp': {
                    'x': list(df['phase_transform_exp'].unique()),
                    'y': list(df['phase_transform_exp'].value_counts())
                }
            }
        }
        return response, 200


api.add_resource(UserLoginData, '/v1/arc/users/login/live')
api.add_resource(UserProfileData, '/v1/arc/users/profile')
