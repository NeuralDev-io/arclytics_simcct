# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# last_simulation.py
# 
# Attributions: 
# [1] 
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.11'
"""last_simulation.py: 

This module defines the Resource for saving and retrieving a user's last 
simulation they ran with all the configurations, alloy, and results if it was
successfully simulated.
"""

from flask import request, Blueprint
from flask_restful import Resource

from users_app.extensions import api
from users_app.middleware import authenticate


last_simulation_blueprint = Blueprint('user_last_simulation', __name__)


class LastSimulation(Resource):

    method_decorators = {
        'post': [authenticate],
        'get': [authenticate]
    }

    # noinspection PyMethodMayBeStatic
    def post(self, user_id):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()

        if not post_data:
            return response, 400

        # TODO(andrew@neuraldev.io): Add the graphs also
        pass

    # noinspection PyMethodMayBeStatic
    def get(self, user_id):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        # TODO(andrew@neuraldev.io): Add the graphs also
        pass


api.add_resource(LastSimulation, '/user/last/simulation')
