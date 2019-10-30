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

from bson import ObjectId
from flask import Blueprint
from flask_restful import Resource

from arc_logging import AppLogger
from sim_api.extensions import api, apm
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.models import SavedSimulation, SharedSimulation, Feedback
from sim_api.search_service import SearchService
from sim_api.mongo_service import MongoService
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
        # Save the user's ObjectId
        oid = ObjectId(user.id)

        user_data = SearchService().find(
            query={'_id': oid},
            projections={'password': 0}
        )

        saved_simulations = MongoService().find(
            query={'user': oid},
            projections={'_id': 0, 'user': 0},
            collection='saved_simulations'
        )

        shared_simulations = MongoService().find(
            query={'owner_email': user.email},
            projections={'_id': 0},
            collection='shared_simulations'
        )

        feedback = MongoService().find(
            query={'user': oid},
            projections={'_id': 0, 'user': 0},
            collection='feedback'
        )

        response = {
            'status': 'success',
            'data': {
                'user': user_data,
                'saved_simulations': saved_simulations,
                'shared_simulations': shared_simulations,
                'feedback': feedback,
            }
        }

        return response, 200


api.add_resource(DownloadData, Routes.DownloadData.value)
