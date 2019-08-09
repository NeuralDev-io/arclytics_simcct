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

from flask import Blueprint, request
from flask_restful import Resource

from sim_app.extensions import api
from sim_app.sim_session import SimSessionService
from simulation.simconfiguration import SimConfiguration as SimConfig
from simulation.utilities import Method
from sim_app.middleware import token_required_flask, token_and_session_required

configs_blueprint = Blueprint('sim_configurations', __name__)


class Configurations(Resource):
    method_decorators = {'patch': [token_and_session_required]}

    # noinspection PyMethodMayBeStatic
    def patch(self, token, session_key):
        """This PATCH endpoint updates the other configurations that are
        not part of the transformation temperatures.

        Args:
            session_key:
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
        sid, session_store = SimSessionService().load_session(session_key)
        sess_configs = session_store.get('configurations')
        if sess_configs is None:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        grain_size = patch_data.get('grain_size', None)
        if grain_size:
            sess_configs['grain_size'] = grain_size

        nuc_start = patch_data.get('nucleation_start', None)
        if nuc_start:
            sess_configs['nucleation_start'] = nuc_start

        nuc_finish = patch_data.get('nucleation_finish', None)
        if nuc_start:
            sess_configs['nucleation_finish'] = nuc_finish

        start_temp = patch_data.get('start_temp', None)
        if start_temp:
            sess_configs['start_temp'] = start_temp

        cct_cool_rate = patch_data.get('cct_cooling_rate', None)
        if cct_cool_rate:
            sess_configs['cct_cooling_rate'] = cct_cool_rate

        session_store['configurations'] = sess_configs
        SimSessionService().save_session(sid, session_store)

        response['status'] = 'success'
        response['message'] = 'Setup configurations values have been updated.'
        return response, 202


class ConfigsMethod(Resource):
    method_decorators = {'put': [token_and_session_required]}

    # noinspection PyMethodMayBeStatic
    def put(self, token, session_key):
        """This PUT endpoint simply updates the `method` for CCT and TTT
        calculations in the session store

        Args:
            session_key:
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

        sid, session_store = SimSessionService().load_session(session_key)
        session_configs = session_store.get('configurations')

        if not session_configs:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        # Change the configs
        session_configs['method'] = Method.Li98.name
        if method == 'Kirkaldy83':
            session_configs['method'] = Method.Kirkaldy83.name

        session_store['configurations'] = session_configs
        SimSessionService().save_session(sid, session_store)

        response['status'] = 'success'
        response['message'] = f'Changed to {method} method.'
        return response, 200


class MartensiteStart(Resource):
    method_decorators = {
        'get': [token_and_session_required],
        'put': [token_and_session_required]
    }

    # noinspection PyMethodMayBeStatic
    def get(self, token, session_key):
        """This GET endpoint auto calculates the `MS` and `MS Rate Param` as the
        user has selected the auto calculate feature without the need for
        sending
        the compositions as they are already stored in the session store.

        Args:
            session_key:
            token: a valid JWT token.

        Returns:
            A response object with appropriate status and message strings
            as well as the calculated MS temperature and MS Rate Parameter.
        """

        # - If user has logged in first time, then this endpoint should not be
        #   possible as they have no compositions.
        #   * Need to do the validation checks for this.

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        sid, session_store = SimSessionService().load_session(session_key)
        session_configs = session_store.get('configurations')

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
        sess_alloy_store = session_store.get('alloy_store')

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

        if comp_np_arr is False:
            response['message'] = 'Compositions conversion error.'
            return response, 500

        ms_temp = SimConfig.get_ms(
            method=transformation_method, comp=comp_np_arr
        )
        ms_rate_param = SimConfig.get_ms_alpha(comp=comp_np_arr)

        # Save the new calculated BS and MS to the Session store
        session_configs['ms_temp'] = ms_temp
        session_configs['ms_rate_param'] = ms_rate_param
        session_store['configurations'] = session_configs
        SimSessionService().save_session(sid, session_store)

        response['status'] = 'success'
        response.pop('message')
        response['data'] = {'ms_temp': ms_temp, 'ms_rate_param': ms_rate_param}

        return response, 200

    # noinspection PyMethodMayBeStatic
    def put(self, token, session_key):
        """If the user manually updates the MS temperatures in the client,
        we receive those and update the session cache.

        Args:
            session_key:
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

        sid, session_store = SimSessionService().load_session(session_key)
        session_configs = session_store.get('configurations', None)

        if not session_configs:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        session_configs['auto_calculate_ms'] = False
        session_configs['ms_temp'] = ms_temp
        session_configs['ms_rate_param'] = ms_rate_param
        session_store['configurations'] = session_configs
        SimSessionService().save_session(sid, session_store)

        return {'status': 'success'}, 202


class BainiteStart(Resource):
    method_decorators = {
        'get': [token_and_session_required],
        'put': [token_and_session_required]
    }

    # noinspection PyMethodMayBeStatic
    def get(self, token, session_key):
        """This POST endpoint auto calculates the `BS` as the user has
        selected the auto calculate feature without the need for sending the
        compositions as they are already stored in the session store.

        Args:
            session_key:
            token: a valid JWT token.

        Returns:
            A response object with appropriate status and message strings
            as well as the calculated BS temperature.
        """

        # - If user has logged in first time, then this endpoint should not be
        #   possible as they have no compositions.
        #   * Need to do the validation checks for this.

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        sid, session_store = SimSessionService().load_session(session_key)
        session_configs = session_store.get('configurations')

        if not session_configs:
            response['message'] = "No previous session initiated."
            return response, 400

        # We need to convert them to our enums as required by the calculations.
        transformation_method = Method.Li98
        if session_configs['method'] == 'Kirkaldy83':
            transformation_method = Method.Kirkaldy83

        session_configs['auto_calculate_bs'] = True

        sess_alloy_store = session_store.get('alloy_store')

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

        if comp_np_arr is False:
            response['message'] = 'Compositions conversion error.'
            return response, 500

        bs_temp = SimConfig.get_bs(
            method=transformation_method, comp=comp_np_arr
        )

        # Save the new calculated BS and MS to the Session store
        session_configs['bs_temp'] = bs_temp
        session_store['configurations'] = session_configs
        SimSessionService().save_session(sid, session_store)

        response['status'] = 'success'
        response.pop('message')
        response['data'] = {'bs_temp': bs_temp}

        return response, 200

    # noinspection PyMethodMayBeStatic
    def put(self, token, session_key):
        """If the user manually updates the BS temperatures in the client, we
        receive those and update the session cache.

        Args:
            session_key:
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

        sid, session_store = SimSessionService().load_session(session_key)
        session_configs = session_store.get('configurations')
        if not session_configs:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        session_configs['auto_calculate_bs'] = False
        session_configs['bs_temp'] = bs_temp
        session_store[f'configurations'] = session_configs
        SimSessionService().save_session(sid, session_store)

        return {'status': 'success'}, 202


class Austenite(Resource):
    method_decorators = {
        'get': [token_and_session_required],
        'put': [token_and_session_required]
    }

    # noinspection PyMethodMayBeStatic
    def get(self, token, session_key):
        """This GET endpoint auto calculates the `Ae1` and `Ae3` as the user has
        selected the auto calculate feature without the need for sending the
        compositions as they are already stored in the session store.

        Args:
            session_key:
            token: a valid JWT token.

        Returns:
            A response object with appropriate status and message strings as
            well as the calculated Ae1 and Ae3 temperatures.
        """
        # - If user has logged in first time, then this endpoint should not be
        #   possible as they have no compositions.
        #   * Need to do the validation checks for this.
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        sid, session_store = SimSessionService().load_session(session_key)
        session_configs = session_store.get('configurations')

        if not session_configs:
            response['message'] = "No previous session initiated."
            return response, 400

        session_configs['auto_calculate_ae'] = True

        sess_alloy_store = session_store.get('alloy_store')

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

        if comp_np_arr is False:
            response['message'] = 'Compositions conversion error.'
            return response, 500

        ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)

        # Save the new calculated Ae1 and Ae3 to the Session store
        session_configs['ae1_temp'] = ae1
        session_configs['ae3_temp'] = ae3
        session_store['configurations'] = session_configs
        SimSessionService().save_session(sid, session_store)

        response['status'] = 'success'
        response.pop('message')
        response['data'] = {'ae1_temp': ae1, 'ae3_temp': ae3}

        return response, 200

    # noinspection PyMethodMayBeStatic
    def put(self, token, session_key):
        """If the user manually updates the Ae1 and Ae3 temperatures in the
        client, we receive those and update the session cache.

        Args:
            session_key:
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

        sid, session_store = SimSessionService().load_session(session_key)
        session_configs = session_store.get('configurations')

        if session_configs is None:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        session_configs['auto_calculate_ae'] = False
        session_configs['ae1_temp'] = ae1_temp
        session_configs['ae3_temp'] = ae3_temp
        session_store['configurations'] = session_configs
        SimSessionService().save_session(sid, session_store)

        return {'status': 'success'}, 202


api.add_resource(Configurations, '/configs/update')
api.add_resource(ConfigsMethod, '/configs/method/update')
api.add_resource(MartensiteStart, '/configs/ms')
api.add_resource(BainiteStart, '/configs/bs')
api.add_resource(Austenite, '/configs/ae')
