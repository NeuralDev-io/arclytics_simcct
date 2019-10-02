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
from flask_restful import Resource

from arc_api.extensions import api

user_analytics_blueprint = Blueprint('user_analytics', __name__)


class UserLoginData(Resource):
    def get(self):
        pass

api.add_resource(UserLoginData, '/v1/arc/users/login/live')
