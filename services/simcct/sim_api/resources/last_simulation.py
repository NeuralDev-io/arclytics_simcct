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
            user_id: a valid user_id verified and passed by the
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

        if not post_configs:
            response['message'] = 'Missing Configurations in payload.'
            return response, 400

        if not post_alloy_store:
            response['message'] = 'Missing Alloy Store in payload.'
            return response, 400

        if not post_results:
            response['message'] = 'Missing Simulation results in payload.'
            return response, 400

        # The following `mongoengine.EmbeddedDocument` models have in-built
        # custom validation that will be passed down.
        try:
            valid_configs = Configuration.from_json(json.dumps(post_configs))
            valid_configs.validate(clean=True)
            valid_store = AlloyStore.from_json(json.dumps(post_alloy_store))
            valid_store.validate(clean=True)
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

        # Passing all the validations built into the models so we can save
        user.last_configuration = valid_configs
        user.last_alloy_store = valid_store
        user.last_simulation_results = valid_results
        # TODO(andrew@neuraldev.io): Add the last_results
        user.save()

        response['status'] = 'success'
        response['message'] = 'Saved Alloy Store, Configurations and Results.'
        response['data'] = {
            'last_configuration': user.last_configuration.to_dict(),
            'last_alloy_store': user.last_alloy_store.to_dict(),
            'last_simulation_results': user.last_simulation_results.to_dict()
        }
        return response, 201

    # noinspection PyMethodMayBeStatic
    def get(self, user):
        """Exposes the GET method to get the last configurations and alloy
        storage from the `sim_api.models.User` document.

        Args:
            user_id: a valid user_id verified and passed by the
                     `sim_api.middleware.authenticate` method.

        Returns:
            A HTTP Flask Restful Response.
        """
        response = {'status': 'fail'}

        # We need to check there's something to return first.
        if not user.last_configuration:
            response['message'] = 'User does not have a last configurations.'
            return response, 404

        if not user.last_alloy_store:
            response['message'] = 'User does not have a last alloy stored.'
            return response, 404

        last_alloy_store = user.last_alloy_store.to_dict()
        alloy_option = last_alloy_store.get('alloy_option', None)
        # alloy_type = last_alloy_store.get('alloy_type', None)

        if not alloy_option:
            response['message'] = 'No alloy option was provided.'
            return response, 400

        alloys = last_alloy_store.get('alloys', None)
        if alloy_option == 'single':
            alloy = alloys.get('parent', None)
        elif alloy_option == 'mix':
            # TODO(andrew@neuraldev.io) Implement this.
            pass

        # We have a couple of ways the Alloy is stored in both Session and
        # Database based on what is available with the alloy_option and
        # alloy_type. From the client, we expect these two keys to at the
        # very least be in the request body. Otherwise we won't do anything.
        if alloy_option not in {'single', 'mix'}:
            response['message'] = (
                'Alloy option not one of '
                '["single" | "mix"].'
            )
            return response, 400

        # if not alloy_type or not isinstance(alloy_type, str):
        #     response['message'] = 'No alloy type was provided.'
        #     return response, 400
        #
        # if alloy_type not in {'parent', 'weld', 'mix'}:
        #     response['message'] = (
        #         'Alloy type not one of ["parent" | "weld" | "mix"].'
        #     )
        #     return response, 400

        if not alloy:
            response['message'] = 'No alloy was provided.'
            return response, 400

        alloy_name = alloy.get('name', None)
        alloy_comp = alloy.get('compositions', None)

        if not alloy_name and not alloy_comp:
            response['message'] = (
                'No valid keys was provided for alloy '
                '(i.e. must be "name" or "compositions")'
            )
            return response, 400

        if not alloy_comp:
            response['message'] = 'You must provide an alloy composition.'
            return response, 400

        if not alloy_name:
            response['message'] = 'You must provide an alloy name.'
            return response, 400

        # Let's validate the Alloy follows our schema
        try:
            valid_alloy = AlloySchema().load(alloy)
        except MissingElementError as e:
            response['message'] = str(e)
            return response, 400
        except ValidationError as e:
            response['errors'] = str(e.messages)
            response['message'] = 'Alloy failed schema validation.'
            return response, 400

        # Otherwise we have all the elements we need

        # We create a new session alloy_store for the user
        session_alloy_store = {
            'alloy_option': alloy_option,
            'alloys': {
                'parent': None,
                'weld': None,
                'mix': None
            }
        }

        valid_store = None
        try:
            if alloy_option == 'single':
                # In this situation, we will only use the parent alloy
                # noinspection PyTypeChecker
                session_alloy_store['alloys']['parent'] = valid_alloy
                # Just quickly validate the alloy stored based on schema
                valid_store = AlloyStoreSchema().load(session_alloy_store)
            elif alloy_option == 'mix':
                # TODO(andrew@neuraldev.io): Implement this.
                pass
        except ValidationError as e:
            response['errors'] = e.messages
            response['message'] = 'Alloy failed schema validation.'
            return response, 400

        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            return response, 500

        session_store['alloy_store'] = valid_store

        session_configs = session_store['configurations']

        if not session_configs:
            response['message'
            ] = 'Cannot retrieve configurations from session.'
            return response, 500

        try:
            valid_configs = ConfigurationsSchema().load(session_configs)
        except ValidationError as e:
            response['errors'] = e.messages
            response['message'
            ] = 'Validation error for session configurations.'
            return response, 500

        # Well, if we don't need to auto calc. anything, let's get out of here
        if (
                not valid_configs['auto_calculate_ms']
                and not valid_configs['auto_calculate_bs']
                and not valid_configs['auto_calculate_ae']
        ):
            # If we are only updating the alloy_store in the session,
            # we access Redis at this point and save it.
            SimSessionService().save_session(session_store)

            response['status'] = 'success'
            response['message'] = 'Compositions updated.'
            return response, 200

        # We update the transformation limits based on which option is
        # chosen
        comp_list: list = []
        if alloy_option == 'single':
            comp_list = valid_store['alloys']['parent']['compositions']

        # TODO(andrew@neuraldev.io): Implement this.
        # else:
        # comp_list = (
        #     sess_alloy_store['mix']['compositions']
        # )
        # pass

        comp_np_arr = SimConfig.get_compositions(comp_list)

        if comp_np_arr is False:
            response['message'] = 'Compositions conversion error.'
            return response, 500

        # We need to store some results so let's prepare an empty dict
        response['message'] = (
            'Compositions and Configurations in Session '
            'initiated.'
        )
        response['data'] = {}

        # We need to convert them to our enums as required by the Sim
        # package - by default we always use Li98
        method = Method.Li98

        if valid_configs['auto_calculate_ms']:
            ms_temp = SimConfig.get_ms(method, comp=comp_np_arr)
            ms_rate_param = SimConfig.get_ms_alpha(comp=comp_np_arr)
            valid_configs['ms_temp'] = ms_temp
            valid_configs['ms_rate_param'] = ms_rate_param
            response['data']['ms_temp'] = ms_temp
            response['data']['ms_rate_param'] = ms_rate_param

        if valid_configs['auto_calculate_bs']:
            bs_temp = SimConfig.get_bs(method, comp=comp_np_arr)
            valid_configs['bs_temp'] = bs_temp
            response['data']['bs_temp'] = bs_temp

        if valid_configs['auto_calculate_ae']:
            ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)
            valid_configs['ae1_temp'] = ae1
            valid_configs['ae3_temp'] = ae3
            response['data']['ae1_temp'] = ae1
            response['data']['ae3_temp'] = ae3

        valid_configs['is_valid'] = False
        session_store['configurations'] = valid_configs

        SimSessionService().save_session(session_store)

        # TODO(andrew@neuraldev.io): Add the last_results also

        response['status'] = 'success'
        response['data'] = {
            'last_configurations': user.last_configuration.to_dict(),
            'last_alloy_store': user.last_alloy_store.to_dict(),
        }
        return response, 200


api.add_resource(LastSimulation, '/api/v1/sim/user/last/simulation')
