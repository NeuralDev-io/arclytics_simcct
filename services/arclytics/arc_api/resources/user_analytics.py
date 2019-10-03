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

from flask import Blueprint, request
from flask import current_app as app
from flask_restful import Resource

from arc_api.extensions import api, redis_client
from arc_api.middleware import authorize_admin_cookie_restful
from arc_logging import AppLogger

user_analytics_blueprint = Blueprint('user_analytics', __name__)
logger = AppLogger(__name__)


# noinspection PyMethodMayBeStatic
class UserLoginData(Resource):
    # method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self):
        keys = redis_client.keys(pattern=u'session*')
        logger.debug(keys)
        return {'keys': len(keys)}, 200


api.add_resource(UserLoginData, '/v1/arc/users/login/live')
