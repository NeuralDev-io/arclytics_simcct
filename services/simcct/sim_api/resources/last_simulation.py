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

from flask import Blueprint, json, request
from flask_restful import Resource
from mongoengine import FieldDoesNotExist, ValidationError

from sim_api.extensions import api
from sim_api.extensions.utilities import (DuplicateElementError, ElementInvalid,
                                          ElementSymbolInvalid,
                                          MissingElementError)
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.models import AlloyStore, Configuration, SimulationResults
from sim_api.extensions.SimSession.sim_session_service import SimSessionService
from sim_api.schemas import (
    AlloySchema, AlloyStoreSchema, ConfigurationsSchema
)
from simulation.utilities import Method
from simulation.simconfiguration import SimConfiguration as SimConfig
from logger import AppLogger

logger = AppLogger(__name__)

last_sim_blueprint = Blueprint('user_last_simulation', __name__)


class LastSimulation(Resource):

    method_decorators = {
        'post': [authenticate_user_cookie_restful],
        'get': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def post(self, user):
        """Exposes the POST method to save the last configurations and alloy
        storage to the `sim_api.models.User` document in the fields
        `last_configurations` and `last_alloy_store`.

        Args:
            user: a valid `models.User` object verified and passed by the
            `sim_api.middleware.authenticate` method.

        Returns:
            A HTTP Flask Restful Response.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()

        # First we validate the request data
        if not post_data:
            return response, 400

        post_configs = post_data.get('configurations', None)
        post_alloy_store = post_data.get('alloy_store', None)
        post_results = post_data.get('simulation_results', None)
        post_invalid_fields = post_data.get('invalid_fields', None)

        if (not post_configs and not post_alloy_store and not post_results
                and not post_invalid_fields):
            return response, 400

        valid_configs = None
        valid_store = None
        valid_results = None

        try:
            if post_configs:
                valid_configs = Configuration.from_json(json.dumps(post_configs))
                valid_configs.validate(clean=True)
            if post_alloy_store:
                valid_store = AlloyStore.from_json(json.dumps(post_alloy_store))
                valid_store.validate(clean=True)
            if post_results:
                valid_results = SimulationResults.from_json(
                    json.dumps(post_results)
                )
                valid_results.validate(clean=True)
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
        except DuplicateElementError as e:
            # One of the alloys contains two or more elements with the same
            # chemical symbol.
            response['error'] = str(e)
            response['message'] = 'Alloy contains a duplicate element.'
            return response, 400
        except ValidationError as e:
            # All other validation errors
            response['error'] = str(e)
            response['message'] = 'Model schema validation error.'
            return response, 400

        response['data'] = {}
        # Passing all the validations built into the models so we can save
        if post_configs and valid_configs:
            user.last_configuration = valid_configs
            response['data']['last_configuration'] = (
                user.last_configuration.to_dict()
            )
        else:
            user.last_configuration = None

        if post_alloy_store and valid_store:
            user.last_alloy_store = valid_store
            response['data']['last_alloy_store'] = (
                user.last_alloy_store.to_dict()
            )
        else:
            user.last_alloy_store = None

        if post_results and valid_results:
            user.last_simulation_results = valid_results
            response['data']['last_simulation_results'] = (
                user.last_simulation_results.to_dict()
            )
        else:
            user.last_simulation_results = None

        if post_invalid_fields:
            user.last_simulation_invalid_fields = post_invalid_fields
            response['data']['last_simulation_invalid_fields'] = (
                user.last_simulation_invalid_fields
            )
        else:
            user.last_simulation_invalid_fields = None

        user.save()

        response['status'] = 'success'
        response['message'] = 'Saved Last Simulation Data.'
        return response, 201

    # noinspection PyMethodMayBeStatic
    def get(self, user):
        """Exposes the GET method to get the last configurations and alloy
        storage from the `sim_api.models.User` document.

        Args:
            user: a valid `models.User` object verified and passed by the
            `sim_api.middleware.authenticate` method.

        Returns:
            A HTTP Flask Restful Response.
        """
        response = {'status': 'fail'}

        if not user.last_configuration and not user.last_alloy_store:
            response['message'] = (
                'User does not have a last configurations or alloy store.'
            )
            return response, 404

        response['data'] = {}

        session_store = SimSessionService().load_session()

        if user.last_configuration:
            session_store['configurations'] = user.last_configuration.to_dict()
            response['data']['last_configurations'] = (
                user.last_configuration.to_dict()
            )
        else:
            session_store['configurations'] = None

        if user.last_alloy_store:
            session_store['alloy_store'] = user.last_alloy_store.to_dict()
            response['data']['last_alloy_store'] = user.last_alloy_store.to_dict()
        else:
            session_store['alloy_store'] = None

        if user.last_simulation_results:
            session_store['simulation_results'] = (
                user.last_simulation_results.to_dict()
            )
            response['data']['last_simulation_results'] = (
                user.last_simulation_results.to_dict()
            )

        if user.last_simulation_invalid_fields:
            response['data']['last_simulation_invalid_fields'] = (
                user.last_simulation_invalid_fields
            )

        SimSessionService().save_session(session_store)

        response['status'] = 'success'
        return response, 200


api.add_resource(LastSimulation, '/api/v1/sim/user/last/simulation')
