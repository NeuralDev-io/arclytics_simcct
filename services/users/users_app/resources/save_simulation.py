# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# save_simulation.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------

__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.08.11'

"""save_simulation.py: 

This module defines the Resource for saving and retrieving a user's saved 
simulation to the their personal Document.
"""

from flask import request, Blueprint
from flask_restful import Resource

from users_app.extensions import api
from users_app.middleware import authenticate


save_simulation_blueprint = Blueprint('user_save_simulation', __name__)

# NOTE: An is_valid = False Configuration instance means it has not been run.


class SaveSimulationList(Resource):

    method_decorators = {
        'get': [authenticate],
        'post': [authenticate]
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


class SaveSimulationDetail(Resource):

    method_decorators = {
        'get': [authenticate],
        'delete': [authenticate]
    }

    # noinspection PyMethodMayBeStatic
    def get(self, sim_id, user_id):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        # TODO(andrew@neuraldev.io): Add the graphs also
        pass


api.add_resource(SaveSimulationList, '/user/simulation/save')
api.add_resource(SaveSimulationDetail, '/user/simulation/<sim_id>')
