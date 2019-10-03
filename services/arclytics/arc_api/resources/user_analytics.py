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
        df = MongoService().read_mongo('arc_dev', 'users')
        profiles = df['profile'].dropna()
        return {'profiles': profiles.to_dict(), 'dataframe': df.to_dict()}, 200


api.add_resource(UserLoginData, '/v1/arc/users/login/live')
api.add_resource(UserProfileData, '/v1/arc/users/profile')
