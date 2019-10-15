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

from typing import Tuple

from flask import Blueprint
from flask_restful import Resource

from arc_api.extensions import api
from arc_api.routes import Routes
from arc_api.mongo_service import MongoService
from arc_api.middleware import authorize_admin_cookie_restful
from arc_logging import AppLogger

app_analytics_blueprint = Blueprint('user_analytics', __name__)
logger = AppLogger(__name__)


# noinspection PyMethodMayBeStatic
class LiveLoginData(Resource):

    # method_decorators = {'get': [authorize_admin_cookie_restful]}

    def get(self) -> Tuple[dict, int]:
        return {'status': 'success', 'data': {}}, 200

api.add_resource(LiveLoginData, Routes.LiveLoginData.value)
