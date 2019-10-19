# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# app_analytics.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '0.1.0'
__status__ = 'development'
__date__ = '2019.10.15'

"""app_analytics.py: 

This module provides the resources for analytical querying, manipulation and 
transformations to display interesting data about the application itself. 
"""
from os import environ as env
from datetime import datetime
from typing import Tuple

from flask import Blueprint
from flask_restful import Resource
import pandas as pd

from arc_api.extensions import api
from arc_api.routes import Routes
from arc_api.mongo_service import MongoService
from arc_api.middleware import authorize_admin_cookie_restful
from arc_logging import AppLogger

app_analytics_blueprint = Blueprint('app_analytics', __name__)
logger = AppLogger(__name__)

DATABASE = env.get('MONGO_APP_DB')


# noinspection PyMethodMayBeStatic
class GeneralData(Resource):

    method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self, _) -> Tuple[dict, int]:
        """Uses various MongoDB Queries and Aggregation Pipelines to get some
        interesting aggregation totals on certain collections and for the
        general application collection. Returns all the values from these
        queries so they can be displayed in the "General Data" section.

        Returns:
            A valid HTTP Response with a dictionary of data and a status code.
        """

        # Get total global alloys
        alloys_count = MongoService().find(
            db_name=DATABASE,
            collection='alloys',
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
        sim_df = MongoService().read_aggregation(DATABASE, 'users', pipeline)

        # Get total ratings average
        pipeline = [
            {'$unwind': '$ratings'},
            {
                '$group': {
                    '_id': None,
                    # 'count': {'$sum': 1},
                    'average': {'$avg': {'$sum': '$ratings.rating'}}
                }
            }
        ]
        ratings_df = MongoService().read_aggregation(
            DATABASE, 'users', pipeline
        )

        response = {
            'status': 'success',
            'data': {
                'count': {
                    'simulations': sim_df['count'][0],
                    'global_alloys': alloys_count,
                    # 'ratings': ratings_df['count'][0],
                },
                'average': {
                    'ratings': ratings_df['average'][0]
                }
            }
        }

        return response, 200


# noinspection PyMethodMayBeStatic
class LiveLoginData(Resource):

    method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self, _) -> Tuple[dict, int]:

        # Get the current date
        date = datetime.utcnow().strftime('%Y-%m-%d')

        # The pipeline will find the document that contains the login data
        # for the current day and then project the required properties for
        # us to manipulate
        pipeline = [
            {'$match': {'date': date}},
            {'$unwind': '$logged_in'},
            {
                '$project': {
                    '_id': 0,
                    'datetime': '$logged_in.datetime',
                    'logged_in_users': '$logged_in.value'
                }
            }
        ]

        df = MongoService().read_aggregation(DATABASE, 'celery_beat', pipeline)

        # df.dropna(inplace=True)
        # Convert the Python `datetime.datetime` object to a timestamp as
        # defined by Pandas.DatetimeIndex
        df['timestamp'] = pd.to_datetime(df['datetime'])
        df.set_index('timestamp', inplace=True)

        response = {
            'status': 'success',
            'data': {
                'date': date,
                'x': df.index.tolist(),
                'y': df['logged_in_users'].tolist()
            }
        }

        return response, 200


api.add_resource(GeneralData, Routes.GeneralData.value)
api.add_resource(LiveLoginData, Routes.LiveLoginData.value)
