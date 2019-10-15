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
class LiveLoginData(Resource):

    # method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self) -> Tuple[dict, int]:

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

        df.dropna(inplace=True)
        # Convert the Python `datetime.datetime` object to a timestamp as
        # defined by Pandas.DatetimeIndex
        df['timestamp'] = pd.to_datetime(df['datetime'])
        df.set_index('timestamp', inplace=True)

        response = {
            'status': 'success',
            'data': {
                'x': df.index.tolist(),
                'y': df['logged_in_users'].tolist()
            }
        }

        return response, 200

api.add_resource(LiveLoginData, Routes.LiveLoginData.value)
