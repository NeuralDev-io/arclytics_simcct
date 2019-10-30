# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# data_personalisation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '2.0.0'
__status__ = 'production'
__date__ = '2019.07.17'
"""data_personalisation.py: 

This module defines and implements the Resource for downloading all user data.
"""

from flask import Blueprint
from flask_restful import Resource

from arc_logging import AppLogger
from sim_api.extensions import api, apm
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.routes import Routes

logger = AppLogger(__name__)
data_personal_blueprint = Blueprint('data_personalisation', __name__)


# noinspection PyMethodMayBeStatic
class DownloadData(Resource):
    """
    This Resource is used to download all the users data.
    """

    method_decorators = {'get': [authenticate_user_cookie_restful]}

    def get(self, user):
        """HTTP GET endpoint to download all user data after the user has
        been validated by the middleware for authentication and authorisation.

        Args:
            user: an instance of a `models.User` passed from the middleware.

        Returns:
            A valid HTTP Response with the results and a status code.
        """
        response = {'status': 'fail'}

        # Save the user's ObjectId
        oid = user.id

        return response, 200


api.add_resource(DownloadData, Routes.DownloadData.value)
