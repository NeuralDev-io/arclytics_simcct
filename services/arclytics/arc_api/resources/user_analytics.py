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

from flask import Blueprint
from flask_restful import Resource

from arc_api.extensions import api
from arc_api.mongo_service import MongoService
from arc_api.middleware import authorize_admin_cookie_restful
from arc_logging import AppLogger

user_analytics_blueprint = Blueprint('user_analytics', __name__)
logger = AppLogger(__name__)


# noinspection PyMethodMayBeStatic
class UserLoginData(Resource):

    # method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self) -> Tuple[dict, int]:
        return {'status': 'success', 'data': {}}, 200


# noinspection PyMethodMayBeStatic
class UserNerdyData(Resource):

    # method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self):
        """Uses various MongoDB Queries and Aggregation Pipeline to get some
        interesting aggregation totals on certain collections and embedded
        documents from the `users` collection. Returns all the values from
        these queries so they can be displayed in the "Nerdy Stats" section.

        Returns:
            A valid HTTP Response with a dictionary of data and a
            status code.
        """

        db_name = 'arc_dev'

        # Get total user count
        users_count = MongoService().find(
            db_name=db_name,
            collection='users',
            query={}
        ).count()

        # Get total saved simulations count
        saved_sim_count = MongoService().find(
            db_name=db_name,
            collection='saved_simulations',
            query={}
        ).count()

        # Get total shares count
        shares_count = MongoService().find(
            db_name=db_name,
            collection='shared_simulations',
            query={}
        ).count()

        # Get total feedback count
        feedback_count = MongoService().find(
            db_name=db_name,
            collection='feedback',
            query={}
        ).count()

        # Get total simulations
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'count': {'$sum': '$simulations_count'}
                }
            }
        ]
        sim_df = MongoService().read_aggregation(db_name, 'users', pipeline)

        # Get total saved alloys
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'count': {'$sum': {'$size': '$saved_alloys'}}
                }
            }
        ]
        saved_alloys_df = MongoService().read_aggregation(
            db_name, 'users', pipeline
        )

        # Get total ratings average

        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'count': {'$sum': {'$size': '$ratings'}}
                }
            }
        ]
        ratings_df = MongoService().read_aggregation(db_name, 'users', pipeline)

        response = {
            'status': 'success',
            'data': {
                'count': {
                    'users': users_count,
                    'saved_simulations': saved_sim_count,
                    'shared_simulations': shares_count,
                    'simulations': sim_df['count'][0],
                    'feedback': feedback_count,
                    'saved_alloys': saved_alloys_df['count'][0],
                    'ratings': ratings_df['count'][0]
                }
            }
        }

        return response, 200


# noinspection PyMethodMayBeStatic
class UserLoginLocationData(Resource):

    # method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self):
        """Use a MongoDB Pipeline to get all the `LoginData` embedded
        documents from Users and generate a count of their location at
        Login time. We provide the data that allows the front-end to generate
        a MapBox map. That's why we also have to pass the `mapbox_token` in
        the response.

        Returns:
            A valid HTTP Response with a dictionary of data and a status code.
        """
        pipeline = [
            {'$unwind': '$login_data'},
            {'$project': {
                '_id': 0,
                'state': '$login_data.state',
                'country': '$login_data.country',
                'continent': '$login_data.continent',
                'timezone': '$login_data.timezone',
                'latitude': {
                    '$arrayElemAt': ['$login_data.geo_point.coordinates', 0]},
                'longitude': {
                    '$arrayElemAt': ['$login_data.geo_point.coordinates', 1]},
            }},
        ]

        df = MongoService().read_aggregation('arc_dev', 'users', pipeline)

        # Because our Plotly Mapbox requires a latitude and longitude input
        # values, we need to ensure we clean up the missing values.
        df.dropna(subset=['latitude', 'longitude'], axis=0, inplace=True)

        # Do a `groupby` on the `dataframe` to ensure we get a count of
        # the values that are grouped with the following properties:
        # [`latitude`, `longitude`, 'country`, `continent`].
        df = df.groupby(
            [
                'latitude',
                'longitude',
                'country',
                'continent'
            ]
        ).size().to_frame('count').reset_index()

        # This token should be stored in the backend and only sent to the
        # front-end when a request for a Mapbox layer is needed.
        token = env.get('MAPBOX_TOKEN', None)

        response = {
            'status': 'success',
            'mapbox_token': token,
            'data': {
                'latitude': df['latitude'].tolist(),
                'longitude': df['longitude'].tolist(),
                'country': df['country'].tolist(),
                'continent': df['continent'].tolist(),
                'count': df['count'].tolist()
            }
        }
        return response, 200


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

        # Not much data cleanup and transformation required as that was mostly
        # done in the Mongo pipeline already.
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


api.add_resource(UserNerdyData, '/v1/arc/users/stats')
api.add_resource(UserLoginData, '/v1/arc/users/login/live')
api.add_resource(UserLoginLocationData, '/v1/arc/users/login/map')
api.add_resource(UserProfileData, '/v1/arc/users/profile')
