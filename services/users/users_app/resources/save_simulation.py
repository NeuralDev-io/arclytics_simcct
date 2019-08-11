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

from flask import request, Blueprint, json
from flask_restful import Resource
from mongoengine import ValidationError, FieldDoesNotExist

from users_app.extensions import api
from users_app.middleware import authenticate
from users_app.utilities import (
    ElementInvalid, ElementSymbolInvalid, MissingElementError
)
from users_app.models import User, Configuration, AlloyStore, SavedSimulation

save_simulation_blueprint = Blueprint('user_save_simulation', __name__)

# NOTE: An is_valid = False Configuration instance means it has not been run.


class SaveSimulationList(Resource):

    method_decorators = {'get': [authenticate], 'post': [authenticate]}

    # noinspection PyMethodMayBeStatic
    def post(self, user_id):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()

        if not post_data:
            return response, 400

        post_configs = post_data.get('configurations')
        post_alloy_store = post_data.get('alloy_store')
        # post_results = post_data.get('results')

        # Valid the request body
        if not post_configs:
            response['message'] = 'Missing Configurations in payload.'
            return response, 400

        if not post_alloy_store:
            response['message'] = 'Missing Alloy Store in payload.'
            return response, 400

        user = User.objects.get(id=user_id)

        saved_sim_inst = SavedSimulation(
            user=user,
            configurations=Configuration.from_json(json.dumps(post_configs)),
            alloy_store=AlloyStore.from_json(json.dumps(post_alloy_store))
        )

        # TODO(andrew@neuraldev.io): Add the graphs also
        # The following `mongoengine.EmbeddedDocument` models have in-built
        # custom validation that will be passed down.
        try:
            saved_sim_inst.save()
        except FieldDoesNotExist as e:
            # In case the request has fields we do not expect.
            response['error'] = str(e)
            response['message'] = 'Field does not exist error.'
            return response, 400
        except ElementSymbolInvalid as e:
            # Where the symbol used for the element is not valid meaning it
            # does not exist in a Periodic Table.
            response['error'] = str(e)
            response['message'] = 'Invalid element symbol error.'
            return response, 400
        except ElementInvalid as e:
            # If no "symbol" or "weight" passed as an Element object.
            response['error'] = str(e)
            response['message'] = 'Invalid element error.'
            return response, 400
        except MissingElementError as e:
            # Where the alloy is missing elements we expect to always be
            # available as they are required downstream in the algorithm.
            response['error'] = str(e)
            response['message'] = 'Missing element error.'
            return response, 400
        except ValidationError as e:
            # All other validation errors
            response['error'] = str(e)
            response['message'] = 'Model schema validation error.'
            return response, 400

        response.pop('message')
        response['status'] = 'success'
        response['data'] = saved_sim_inst.to_dict()
        return response, 201

    # noinspection PyMethodMayBeStatic
    def get(self, user_id):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        # TODO(andrew@neuraldev.io): Add the graphs also
        pass


class SaveSimulationDetail(Resource):

    method_decorators = {'get': [authenticate], 'delete': [authenticate]}

    # noinspection PyMethodMayBeStatic
    def get(self, sim_id, user_id):
        response = {'status': 'fail'}

        # TODO(andrew@neuraldev.io): Add the graphs also
        pass


api.add_resource(SaveSimulationList, '/user/simulation/save')
api.add_resource(SaveSimulationDetail, '/user/simulation/<sim_id>')
