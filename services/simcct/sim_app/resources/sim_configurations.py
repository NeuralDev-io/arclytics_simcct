# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# sim_configurations.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['Dr. Philip Bendeich', 'Dr. Ondrej Muransky']
__license__ = 'TBA'
__version__ = '0.3.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.13'
"""sim_configurations.py: 

This module deals with all the endpoints for setting and updating the 
configurations for the main simulations page. 
"""

from flask import Blueprint, session, request
from flask_restful import Resource
from marshmallow import ValidationError

from sim_app.extensions import api
from simulation.simconfiguration import SimConfiguration as SimConfig
from simulation.utilities import Method
from sim_app.middleware import token_required_restful
from sim_app.schemas import AlloyStoreSchema, SetupConfigsSchema, AlloySchema
from simulation.periodic import PeriodicTable as PT

configs_blueprint = Blueprint('sim_configurations', __name__)


class AlloyStore(Resource):
    method_decorators = {
        'patch': [token_required_restful],
        'post': [token_required_restful]
    }

    def post(self, token):
        """This POST endpoint initiates the Alloy Store by setting the alloy
        in the request body to the Session storage.

        Args:
            token: a valid JWT token.

        Returns:
            A response object with appropriate status and message
            strings.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()
        if not post_data:
            return response, 400

        # Extract the method from the post request body
        # REQUEST BODY SHOULD BE
        # {
        #     "alloy_option": "single",
        #     "alloy_type": "parent",
        #     "alloy": [{"symbol": "C", "weight": 1}, ...]
        # }
        alloy_option = post_data.get('alloy_option', None)
        alloy_type = post_data.get('alloy_type', None)
        alloy = post_data.get('alloy', None)

        if not alloy_option:
            response['message'] = 'No alloy option was provided.'
            return response, 400

        # We have a couple of ways the Alloy is stored in both Session and
        # Database based on what is available with the alloy_option and
        # alloy_type. From the client, we expect these two keys to at the
        # very least be in the request body. Otherwise we won't do anything.
        if alloy_option not in ['single', 'both', 'mix']:
            response['message'] = (
                'Alloy option not one of '
                '["single" | "both" | "mix"].'
            )
            return response, 400

        if not alloy_type or not isinstance(alloy_type, str):
            response['message'] = 'No alloy type was provided.'
            return response, 400

        if alloy_type not in ['parent', 'weld', 'mix']:
            response['message'] = (
                'Alloy type not one of ["parent" | "weld" | "mix"].'
            )
            return response, 400

        if not alloy:
            response['message'] = 'No alloy was provided.'
            return response, 400

        # Let's validate the Alloy follows our schema
        try:
            valid_alloy = AlloySchema().load(alloy)
        except ValidationError as e:
            response['errors'] = str(e)
            response['message'] = 'Alloy failed schema validation.'
            return response, 400

        # We create a new session alloy_store for the user
        session_alloy_store = {
            'alloy_option': alloy_option,
            'alloy_type': alloy_type,
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
                session_alloy_store['alloys']['parent'] = valid_alloy
                # Just quickly validate the alloy stored based on schema
                valid_store = AlloyStoreSchema().load(session_alloy_store)
            elif alloy_option == 'mix':
                # TODO(andrew@neuraldev.io): Implement this.
                pass
            else:
                # TODO(andrew@neuraldev.io): Implement this.
                pass
        except ValidationError as e:
            response['errors'] = e.messages
            response['message'] = 'Alloy failed schema validation.'
            return response, 400

        session[f'{token}:alloy_store'] = valid_store

        # In this situation, we always need to auto calculate and set the
        # below configs to default
        default_configs = {
            'is_valid': False,
            'method': 'Li98',
            'grain_size': 0.0,
            'nucleation_start': 0.0,
            'nucleation_finish': 0.0,
            'auto_calculate_ms': True,
            'auto_calculate_bs': True,
            'auto_calculate_ae': True,
            'start_temp': 0,
            'cct_cooling_rate': 0
        }

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

        # We need to store some results so let's prepare an empty dict
        response['message'] = (
            'Compositions and Configurations in Session '
            'initiated.'
        )
        response['data'] = {}

        # We need to convert them to our enums as required by the Sim
        # package - by default we always use Li98
        method = Method.Li98

        ms_temp = SimConfig.get_ms(method, comp=comp_np_arr)
        ms_rate_param = SimConfig.get_ms_alpha(comp=comp_np_arr)
        default_configs['ms_temp'] = ms_temp
        default_configs['ms_rate_param'] = ms_rate_param

        bs_temp = SimConfig.get_bs(method, comp=comp_np_arr)
        default_configs['bs_temp'] = bs_temp

        ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)
        default_configs['ae1_temp'] = ae1
        default_configs['ae3_temp'] = ae3

        session[f'{token}:configurations'] = default_configs

        response['data'] = {
            'ms_temp': ms_temp,
            'ms_rate_param': ms_rate_param,
            'bs_temp': bs_temp,
            'ae1_temp': ae1,
            'ae3_temp': ae3
        }
        response['status'] = 'success'
        return response, 200

    def patch(self, token):
        """This PATCH endpoint simply updates the `alloys` in the session
        store so that we can update all the other transformation temperature.

        Args:
            token: a valid JWT token.

        Returns:
            A response object with appropriate status and message strings.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        patch_data = request.get_json()
        if not patch_data:
            return response, 400
        # Extract the method from the post request body
        # REQUEST BODY SHOULD BE
        # {
        #     "alloy_option": "single",
        #     "alloy_type": "parent",
        #     "alloy": [{"symbol": "C", "weight": 1}, ...]
        # }
        alloy_option = patch_data.get('alloy_option', None)
        alloy_type = patch_data.get('alloy_type', None)
        alloy = patch_data.get('alloy', None)

        if not alloy_option:
            response['message'] = 'No alloy option was provided.'
            return response, 400

        # We have a couple of ways the Alloy is stored in both Session and
        # Database based on what is available with the alloy_option and
        # alloy_type. From the client, we expect these two keys to at the
        # very least be in the request body. Otherwise we won't do anything.
        if alloy_option not in ['single', 'both', 'mix']:
            response['message'] = (
                'Alloy option not one of '
                '["single" | "both" | "mix"].'
            )
            return response, 400

        if not alloy_type or not isinstance(alloy_type, str):
            response['message'] = 'No alloy type was provided.'
            return response, 400

        if alloy_type not in ['parent', 'weld', 'mix']:
            response['message'] = (
                'Alloy type not one of ["parent" | "weld" | "mix"].'
            )
            return response, 400

        if not alloy:
            response['message'] = 'No alloy was provided.'
            return response, 400

        # The alloy might be provided but if it's got no valid keys, we need to
        # check that
        if not alloy.get('name', None) and not alloy.get('compositions', None):
            response['message'] = 'No key in the alloy was provided.'
            return response, 400

        # Let's validate the Alloy follows our schema
        try:
            alloy = AlloySchema().load(alloy)
        except ValidationError as e:
            response['errors'] = str(e)
            response['message'] = 'Alloy failed schema validation.'
            return response, 400

        # We get what's currently stored in the session and we update it
        sess_alloy_store = session.get(f'{token}:alloy_store')
        # Basically, the user should have a session initiated from login
        if not sess_alloy_store:
            response['message'] = 'No previous session initiated.'
            return response, 400

        # We just update the alloy_option straight up
        sess_alloy_store['alloy_option'] = alloy_option

        # Now we dig deeper into the object to update the elements and name
        sess_alloys = sess_alloy_store.get('alloys')

        try:
            if alloy_option == 'single':
                # In this situation, we will only use the parent alloy

                # We first update the compositions of the alloy partially
                req_parent_comp = alloy.get('compositions', None)
                sess_parent_comp = sess_alloys['parent']['compositions']

                # FIXME(andrew@neuraldev.io): This needs to be massively
                #  updated as this is possible the slowest way possible to do
                #  this. One way would be to make an Element class and override
                #  the comparison of each class to only use the Symbol to
                #  compare to each other. That way you can use the Python
                #  "for in" syntax without worries.
                # We first update the compositions of the alloy partially
                if req_parent_comp:
                    for el in req_parent_comp:
                        exists = False
                        for i, ex_el in enumerate(sess_parent_comp):
                            if ex_el['symbol'] == el['symbol']:
                                exists = True
                                sess_parent_comp[i] = el
                                break
                        if not exists:
                            sess_parent_comp.append(el)

                # We update the name if they're not the same
                if not alloy.get('name',
                                 None) == sess_alloys['parent']['name']:
                    sess_alloys['parent']['name'] = alloy['name']
                # Removing the other alloys if they exist
                sess_alloy_store['alloys']['weld'] = None
                sess_alloy_store['alloys']['mix'] = None

                # Just quickly validate the alloy stored based on schema
                sess_alloy_store = AlloyStoreSchema().load(sess_alloy_store)
            elif alloy_option == 'mix':
                # TODO(andrew@neuraldev.io): Implement this.
                pass
            else:
                # TODO(andrew@neuraldev.io): Implement this.
                pass
        except ValidationError as e:
            response['errors'] = e.messages
            response['message'] = 'Alloy failed schema validation.'
            return response, 400

        session[f'{token}:alloy_store'] = sess_alloy_store

        sess_configs = session.get(f'{token}:configurations')

        # Well, if we don't need to auto calc. anything, let's get out of here
        if (
            not sess_configs['auto_calculate_ms']
            and not sess_configs['auto_calculate_bs']
            and not sess_configs['auto_calculate_ae']
        ):
            response['status'] = 'success'
            response['message'] = 'Compositions updated.'
            return response, 200

        # Since we do need to calculate, must get the compositions first in
        # numpy.ndarray structured format and type

        # We update the transformation limits based on which option is chosen
        comp_list: list = []
        if alloy_option == 'single':
            comp_list = sess_alloy_store['alloys']['parent']['compositions']

        # TODO(andrew@neuraldev.io): Implement this.
        # else:
        # comp_list = (
        #     sess_alloy_store['mix']['compositions']
        # )
        # pass

        comp_np_arr = SimConfig.get_compositions(comp_list)

        # We need to store some results so let's prepare an empty dict
        response['message'] = 'Compositions and other values updated.'
        response['data'] = {}

        # We need to convert them to our enums as required by the Sim package.
        method = Method.Li98
        if sess_configs['method'] == 'Kirkaldy83':
            method = Method.Kirkaldy83

        if sess_configs['auto_calculate_ms']:

            ms_temp = SimConfig.get_ms(method, comp=comp_np_arr)
            ms_rate_param = SimConfig.get_ms_alpha(comp=comp_np_arr)

            sess_configs['auto_calculate_ms'] = True
            sess_configs['ms_temp'] = ms_temp
            sess_configs['ms_rate_param'] = ms_rate_param
            response['data']['ms_temp'] = ms_temp
            response['data']['ms_rate_param'] = ms_rate_param

        if sess_configs['auto_calculate_bs']:
            bs_temp = SimConfig.get_bs(method, comp=comp_np_arr)

            sess_configs['auto_calculate_bs'] = True
            sess_configs['bs_temp'] = bs_temp
            response['data']['bs_temp'] = bs_temp

        if sess_configs['auto_calculate_ae']:
            ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)

            sess_configs['auto_calculate_ae'] = True
            sess_configs['ae1_temp'] = ae1
            sess_configs['ae3_temp'] = ae3
            response['data']['ae1_temp'] = ae1
            response['data']['ae3_temp'] = ae3

        session[f'{token}:configurations'] = sess_configs

        response['status'] = 'success'
        return response, 200


class Configurations(Resource):
    method_decorators = {'patch': [token_required_restful]}

    def patch(self, token):
        """This PATCH endpoint updates the other configurations that are
        not part of the transformation temperatures.

        Args:
            token: the returned token from the `token_required_restful`
                   middleware decorator.

        Returns:
            A valid HTTP Response with application/json content.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        patch_data = request.get_json()
        if not patch_data:
            return response, 400

        # First we need to make sure there are actually some changes to be made
        # by ensuring the request body data has some keys that are valid.
        valid_keys = [
            'grain_size', 'nucleation_start', 'nucleation_finish',
            'start_temp', 'cct_cooling_rate'
        ]

        # by default we will not change anything until we find at least 1 key
        # in the request body that is a valid_key
        is_update = False
        for k in valid_keys:
            if k in patch_data.keys():
                is_update = True
                break

        if not is_update:
            response['message'] = 'Payload does not have any valid keys.'
            return response, 400

        # If there are changes to be made, then we will get the session store.
        sess_store = session.get(f'{token}:configurations')
        if sess_store is None:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        grain_size = patch_data.get('grain_size', None)
        if grain_size:
            sess_store['grain_size'] = grain_size

        nuc_start = patch_data.get('nucleation_start', None)
        if nuc_start:
            sess_store['nucleation_start'] = nuc_start

        nuc_finish = patch_data.get('nucleation_finish', None)
        if nuc_start:
            sess_store['nucleation_finish'] = nuc_finish

        start_temp = patch_data.get('start_temp', None)
        if start_temp:
            sess_store['start_temp'] = start_temp

        cct_cool_rate = patch_data.get('cct_cooling_rate', None)
        if cct_cool_rate:
            sess_store['cct_cooling_rate'] = cct_cool_rate

        session[f'{token}:configurations'] = sess_store

        response['status'] = 'success'
        response['message'] = 'Setup configurations values have been updated.'
        return response, 202


class ConfigsMethod(Resource):
    method_decorators = {'put': [token_required_restful]}

    def put(self, token):
        """This PUT endpoint simply updates the `method` for CCT and TTT
        calculations in the session store

        Args:
            token: a valid JWT token.

        Returns:
            A response object with appropriate status and message strings.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()
        if not post_data:
            return response, 400
        # Extract the method from the post request body
        method = post_data.get('method', None)

        if not method:
            response['message'] = 'No method was provided.'
            return response, 400

        if (
            not method == Method.Li98.name
            and not method == Method.Kirkaldy83.name
        ):
            response['message'] = (
                'Invalid method provided (must be Li98 or '
                'Kirkaldy83).'
            )
            return response, 400

        session_configs = session.get(f'{token}:configurations')

        if not session_configs:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        # Change the configs
        session_configs['method'] = Method.Li98.name
        if method == 'Kirkaldy83':
            session_configs['method'] = Method.Kirkaldy83.name

        session[f'{token}:configurations'] = session_configs
        response['status'] = 'success'
        response['message'] = f'Changed to {method} method.'
        return response, 200


class MartensiteStart(Resource):
    method_decorators = {
        'get': [token_required_restful],
        'put': [token_required_restful]
    }

    def get(self, token):
        """This GET endpoint auto calculates the `MS` and `MS Rate Param` as the
        user has selected the auto calculate feature without the need for
        sending
        the compositions as they are already stored in the session store.

        Args:
            token: a valid JWT token.

        Returns:
            A response object with appropriate status and message strings
            as well as the calculated MS temperature and MS Rate Parameter.
        """

        # - If user has logged in first time, then this endpoint should not be
        #   possible as they have no compositions.
        #   * Need to do the validation checks for this.

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        session_configs = session.get(f'{token}:configurations')

        if not session_configs:
            response['message'] = "No previous session initiated."
            return response, 400

        # We need to convert them to our enums as required by the calculations.
        transformation_method = Method.Li98
        if session_configs['method'] == 'Kirkaldy83':
            transformation_method = Method.Kirkaldy83

        session_configs['auto_calculate_ms'] = True

        # TODO(andrew@neuraldev.io): Accessing "Alloy Compositions" would be by
        #  the name of the alloy_type.
        sess_alloy_store = session.get(f'{token}:alloy_store')

        if not sess_alloy_store:
            response['message'] = 'No previous session initiated.'
            return response, 400

        # TODO(andrew@neuraldev.io): Implement the other options
        comp_list: list = []
        if sess_alloy_store['alloy_option'] == 'single':
            comp_list = sess_alloy_store['alloys']['parent']['compositions']

        if comp_list is None:
            response['message'] = 'User has not set an Alloy.'
            return response, 400

        comp_np_arr = SimConfig.get_compositions(comp_list)

        ms_temp = SimConfig.get_ms(
            method=transformation_method, comp=comp_np_arr
        )
        ms_rate_param = SimConfig.get_ms_alpha(comp=comp_np_arr)

        # Save the new calculated BS and MS to the Session store
        session_configs['ms_temp'] = ms_temp
        session_configs['ms_rate_param'] = ms_rate_param
        session[f'{token}:configurations'] = session_configs

        response['status'] = 'success'
        response.pop('message')
        response['data'] = {'ms_temp': ms_temp, 'ms_rate_param': ms_rate_param}

        return response, 200

    def put(self, token):
        """If the user manually updates the MS temperatures in the client,
        we receive those and update the session cache.

        Args:
            token: a valid JWT token.

        Returns:
            A response body of with the `status` and a 202 status code.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()
        if not post_data:
            return response, 400

        # Let's do some validation of those arguments we really need.
        ms_temp = post_data.get('ms_temp', None)
        ms_rate_param = post_data.get('ms_rate_param', None)

        if not ms_temp:
            response['message'] = 'MS temperature is required.'
            return response, 400

        if not ms_rate_param:
            response['message'] = 'MS Rate Parameter temperature is required.'
            return response, 400

        session_configs = session.get(f'{token}:configurations', None)
        if not session_configs:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        session_configs['auto_calculate_ms'] = False
        session_configs['ms_temp'] = ms_temp
        session_configs['ms_rate_param'] = ms_rate_param
        session[f'{token}:configurations'] = session_configs

        return {'status': 'success'}, 202


class BainiteStart(Resource):
    method_decorators = {
        'get': [token_required_restful],
        'put': [token_required_restful]
    }

    def get(self, token):
        """This POST endpoint auto calculates the `BS` as the user has
        selected the auto calculate feature without the need for sending the
        compositions as they are already stored in the session store.

        Args:
            token: a valid JWT token.

        Returns:
            A response object with appropriate status and message strings
            as well as the calculated BS temperature.
        """

        # - If user has logged in first time, then this endpoint should not be
        #   possible as they have no compositions.
        #   * Need to do the validation checks for this.

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        session_configs = session.get(f'{token}:configurations')

        if not session_configs:
            response['message'] = "No previous session initiated."
            return response, 400

        # We need to convert them to our enums as required by the calculations.
        transformation_method = Method.Li98
        if session_configs['method'] == 'Kirkaldy83':
            transformation_method = Method.Kirkaldy83

        session_configs['auto_calculate_bs'] = True

        sess_alloy_store = session.get(f'{token}:alloy_store')

        if not sess_alloy_store:
            response['message'] = 'No previous session initiated.'
            return response, 400

        # TODO(andrew@neuraldev.io): Implement the other options
        comp_list: list = []
        if sess_alloy_store['alloy_option'] == 'single':
            comp_list = sess_alloy_store['alloys']['parent']['compositions']

        if comp_list is None:
            response['message'] = 'User has not set an Alloy.'
            return response, 400

        comp_np_arr = SimConfig.get_compositions(comp_list)

        bs_temp = SimConfig.get_bs(
            method=transformation_method, comp=comp_np_arr
        )

        # Save the new calculated BS and MS to the Session store
        session_configs['bs_temp'] = bs_temp
        session[f'{token}:configurations'] = session_configs

        response['status'] = 'success'
        response.pop('message')
        response['data'] = {'bs_temp': bs_temp}

        return response, 200

    def put(self, token):
        """If the user manually updates the BS temperatures in the client, we
        receive those and update the session cache.

        Args:
            token: a valid JWT token.

        Returns:
            A response body of with the `status` and a 202 status code.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()
        if not post_data:
            return response, 400

        # Let's do some validation of those arguments we really need.
        bs_temp = post_data.get('bs_temp', None)

        if not bs_temp:
            response['message'] = 'BS temperature is required.'
            return response, 400

        session_configs = session.get(f'{token}:configurations')
        if not session_configs:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        session_configs['auto_calculate_bs'] = False
        session_configs['bs_temp'] = bs_temp
        session[f'{token}:configurations'] = session_configs

        return {'status': 'success'}, 202


class Austenite(Resource):
    method_decorators = {
        'get': [token_required_restful],
        'put': [token_required_restful]
    }

    def get(self, token):
        """This GET endpoint auto calculates the `Ae1` and `Ae3` as the user has
        selected the auto calculate feature without the need for sending the
        compositions as they are already stored in the session store.

        Args:
            token: a valid JWT token.

        Returns:
            A response object with appropriate status and message strings as
            well as the calculated Ae1 and Ae3 temperatures.
        """
        # - If user has logged in first time, then this endpoint should not be
        #   possible as they have no compositions.
        #   * Need to do the validation checks for this.
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        session_configs = session.get(f'{token}:configurations')
        if not session_configs:
            response['message'] = "No previous session initiated."
            return response, 400

        session_configs['auto_calculate_ae'] = True

        sess_alloy_store = session.get(f'{token}:alloy_store')

        if not sess_alloy_store:
            response['message'] = 'No previous session initiated.'
            return response, 400

        # TODO(andrew@neuraldev.io): Implement the other options
        comp_list: list = []
        if sess_alloy_store['alloy_option'] == 'single':
            comp_list = sess_alloy_store['alloys']['parent']['compositions']

        if comp_list is None:
            response['message'] = 'User has not set an Alloy.'
            return response, 400

        comp_np_arr = SimConfig.get_compositions(comp_list)

        ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)

        # Save the new calculated Ae1 and Ae3 to the Session store
        session_configs['ae1_temp'] = ae1
        session_configs['ae3_temp'] = ae3
        session[f'{token}:configurations'] = session_configs

        response['status'] = 'success'
        response.pop('message')
        response['data'] = {'ae1_temp': ae1, 'ae3_temp': ae3}

        return response, 200

    def put(self, token):
        """If the user manually updates the Ae1 and Ae3 temperatures in the
        client, we receive those and update the session cache.

        Args:
            token: a valid JWT token.

        Returns:
            A response body of with the `status` and a 202 status code.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()
        if not post_data:
            return response, 400

        # Let's do some validation of those arguments we really need.
        ae1_temp = post_data.get('ae1_temp', None)
        ae3_temp = post_data.get('ae3_temp', None)

        if not ae1_temp:
            response['message'] = 'Ae1 temperature is required.'
            return response, 400

        if not ae3_temp:
            response['message'] = 'Ae3 temperature is required.'
            return response, 400

        session_configs = session.get(f'{token}:configurations')
        if session_configs is None:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        session_configs['auto_calculate_ae'] = False
        session_configs['ae1_temp'] = ae1_temp
        session_configs['ae3_temp'] = ae3_temp

        return {'status': 'success'}, 202


api.add_resource(AlloyStore, '/alloys/update')
api.add_resource(Configurations, '/configs/update')
api.add_resource(ConfigsMethod, '/configs/method/update')
api.add_resource(MartensiteStart, '/configs/ms')
api.add_resource(BainiteStart, '/configs/bs')
api.add_resource(Austenite, '/configs/ae')
