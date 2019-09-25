# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# sim_configurations.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__credits__ = ['Dr. Philip Bendeich', 'Dr. Ondrej Muransky']
__license__ = 'MIT'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'production'
__date__ = '2019.07.13'
"""sim_configurations.py: 

This module deals with all the endpoints for setting and updating the 
configurations for the main simulations page. 
"""

from flask import Blueprint, request
from flask_restful import Resource
from marshmallow import ValidationError

from arc_logging import AppLogger
from sim_api.extensions import api, apm
from sim_api.extensions.SimSession import SimSessionService
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.schemas import ConfigurationsSchema
from simulation.simconfiguration import SimConfiguration as SimConfig
from simulation.utilities import Method, ConfigurationError

configs_blueprint = Blueprint('sim_configurations', __name__)

logger = AppLogger(__name__)


class Configurations(Resource):
    method_decorators = {'patch': [authenticate_user_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def patch(self, _):
        """This PATCH endpoint updates the other configurations that are
        not part of the transformation temperatures.

        Args:
            _: a `sim_api.models.User` that is not used.

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
        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            return response, 500

        sess_configs = session_store.get('configurations')
        if sess_configs is None:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        grain_size = patch_data.get('grain_size', None)
        if grain_size:
            sess_configs['grain_size'] = float(grain_size)

        nuc_start = patch_data.get('nucleation_start', None)
        if nuc_start:
            sess_configs['nucleation_start'] = float(nuc_start)

        nuc_finish = patch_data.get('nucleation_finish', None)
        if nuc_finish:
            sess_configs['nucleation_finish'] = float(nuc_finish)

        start_temp = patch_data.get('start_temp', None)
        if start_temp:
            try:
                valid_start_temp = int(start_temp)
            except ValueError as e:
                # Save what we have validated so far
                response['status'] = 'fail'
                response['errors'] = str(e)
                response['message'] = 'Invalid Starting Temperature.'
                logger.exception(response['message'], exc_info=True)
                apm.capture_exception()
                return response, 400
            except Exception as e:
                # Save what we have validated so far
                response['status'] = 'fail'
                response['errors'] = str(e)
                response['message'] = 'Int conversion error.'
                logger.exception(response['message'], exc_info=True)
                apm.capture_exception()
                return response, 400
            sess_configs['start_temp'] = valid_start_temp

        cct_cool_rate = patch_data.get('cct_cooling_rate', None)
        if cct_cool_rate:
            try:
                valid_cct_cool_rate = int(cct_cool_rate)
            except ValueError as e:
                # Save what we have validated so far
                response['status'] = 'fail'
                response['errors'] = str(e)
                response['message'] = 'Invalid CCT Cooling Rate.'
                logger.exception(response['message'], exc_info=True)
                apm.capture_exception()
                return response, 400
            except Exception as e:
                # Save what we have validated so far
                response['status'] = 'fail'
                response['errors'] = str(e)
                response['message'] = 'Int conversion error.'
                logger.exception(response['message'], exc_info=True)
                return response, 400
            sess_configs['cct_cooling_rate'] = valid_cct_cool_rate

        sess_configs['is_valid'] = False

        try:
            valid_configs = ConfigurationsSchema().load(sess_configs)
        except ValidationError as e:
            response['errors'] = str(e)
            response['message'] = 'Configurations not valid.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 400

        session_store['configurations'] = valid_configs
        SimSessionService().save_session(session_store)

        response['status'] = 'success'
        response['message'] = 'Setup configurations values have been updated.'
        return response, 202


class ConfigsMethod(Resource):
    method_decorators = {'put': [authenticate_user_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def put(self, _):
        """This PUT endpoint simply updates the `method` for CCT and TTT
        calculations in the session store

        Args:
            _: a `sim_api.models.User` that is not used.

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

        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            return response, 500

        session_configs = session_store.get('configurations')

        if not session_configs:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        # Change the configs
        session_configs['method'] = Method.Li98.name
        if method == 'Kirkaldy83':
            session_configs['method'] = Method.Kirkaldy83.name

        session_configs['is_valid'] = False
        session_store['configurations'] = session_configs

        SimSessionService().save_session(session_store)

        response['status'] = 'success'
        response['message'] = f'Changed to {method} method.'
        return response, 200


class MartensiteStart(Resource):
    method_decorators = {
        'get': [authenticate_user_cookie_restful],
        'put': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def get(self, _):
        """This GET endpoint auto calculates the `MS` and `MS Rate Param` as
        the user has selected the auto calculate feature without the need
        for sending the compositions as they are already stored in the
        session store.

        Args:
            _: a `sim_api.models.User` that is not used.

        Returns:
            A response object with appropriate status and message strings
            as well as the calculated MS temperature and MS Rate Parameter.
        """

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            return response, 500

        session_configs = session_store.get('configurations')

        if not session_configs:
            response['message'] = "No previous session initiated."
            return response, 400

        # We need to convert them to our enums as required by the calculations.
        transformation_method = Method.Li98
        if session_configs['method'] == 'Kirkaldy83':
            transformation_method = Method.Kirkaldy83

        session_configs['auto_calculate_ms'] = True

        # DECISION:
        # We will not implement this as it adds too much complexity to
        # the logical path of the system state. This was not a core
        # requirement and Dr. Bendeich often said he did not want this
        # implemented at all.
        sess_alloy_store = session_store.get('alloy_store')

        if not sess_alloy_store:
            response['message'] = 'No previous session initiated.'
            return response, 400

        # DECISION:
        # We will not implement this as it adds too much complexity to
        # the logical path of the system state. This was not a core
        # requirement and Dr. Bendeich often said he did not want this
        # implemented at all.
        comp_list: list = []
        if sess_alloy_store['alloy_option'] == 'single':
            comp_list = sess_alloy_store['alloys']['parent']['compositions']
        else:
            # Would normally find the `mix` option.
            pass

        if comp_list is None:
            response['message'] = 'User has not set an Alloy.'
            return response, 400

        try:
            comp_np_arr = SimConfig.get_compositions(comp_list)
        except ConfigurationError as e:
            response['errors'] = str(e)
            response['message'] = str(e)
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500

        ms_temp = SimConfig.get_ms(
            method=transformation_method, comp=comp_np_arr
        )
        ms_rate_param = SimConfig.get_ms_alpha(comp=comp_np_arr)

        # Save the new calculated BS and MS to the Session store
        session_configs['ms_temp'] = ms_temp
        session_configs['ms_rate_param'] = ms_rate_param
        session_configs['is_valid'] = False
        session_store['configurations'] = session_configs

        SimSessionService().save_session(session_store)

        response['status'] = 'success'
        response.pop('message')
        response['data'] = {'ms_temp': ms_temp, 'ms_rate_param': ms_rate_param}

        return response, 200

    # noinspection PyMethodMayBeStatic
    def put(self, _):
        """If the user manually updates the MS temperatures in the client,
        we receive those and update the session cache.

        Args:
            _: a `sim_api.models.User` that is not used.

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

        session_store = SimSessionService().load_session()

        # If there is an error loading the session, we get an error message
        if isinstance(session_store, str):
            response['message'] = session_store
            return response, 500

        session_configs = session_store.get('configurations', None)

        if not session_configs:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        session_configs['auto_calculate_ms'] = False
        session_configs['ms_temp'] = ms_temp
        session_configs['ms_rate_param'] = ms_rate_param
        session_configs['is_valid'] = False
        session_store['configurations'] = session_configs

        SimSessionService().save_session(session_store)

        return {'status': 'success'}, 202


class BainiteStart(Resource):
    method_decorators = {
        'get': [authenticate_user_cookie_restful],
        'put': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def get(self, _):
        """This POST endpoint auto calculates the `BS` as the user has
        selected the auto calculate feature without the need for sending the
        compositions as they are already stored in the session store.

        Args:
            _: a `sim_api.models.User` that is not used.

        Returns:
            A response object with appropriate status and message strings
            as well as the calculated BS temperature.
        """

        # - If user has logged in first time, then this endpoint should not be
        #   possible as they have no compositions.
        #   * Need to do the validation checks for this.

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            return response, 500

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

        # DECISION:
        # We will not implement this as it adds too much complexity to
        # the logical path of the system state. This was not a core
        # requirement and Dr. Bendeich often said he did not want this
        # implemented at all.
        comp_list: list = []
        if sess_alloy_store['alloy_option'] == 'single':
            comp_list = sess_alloy_store['alloys']['parent']['compositions']
        else:
            # Would normally find the `mix` option.
            pass

        if comp_list is None:
            response['message'] = 'User has not set an Alloy.'
            return response, 400

        try:
            comp_np_arr = SimConfig.get_compositions(comp_list)
        except ConfigurationError as e:
            response['errors'] = str(e)
            response['message'] = str(e)
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500

        bs_temp = SimConfig.get_bs(
            method=transformation_method, comp=comp_np_arr
        )

        # Save the new calculated BS and MS to the Session store
        session_configs['bs_temp'] = bs_temp
        session_configs['is_valid'] = False
        session_store['configurations'] = session_configs

        SimSessionService().save_session(session_store)

        response['status'] = 'success'
        response.pop('message')
        response['data'] = {'bs_temp': bs_temp}

        return response, 200

    # noinspection PyMethodMayBeStatic
    def put(self, _):
        """If the user manually updates the BS temperatures in the client, we
        receive those and update the session cache.

        Args:
            _: a `sim_api.models.User` that is not used.

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

        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            return response, 500

        session_configs = session_store.get('configurations')
        if not session_configs:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        session_configs['auto_calculate_bs'] = False
        session_configs['bs_temp'] = bs_temp
        session_configs['is_valid'] = False
        session_store[f'configurations'] = session_configs

        SimSessionService().save_session(session_store)

        return {'status': 'success'}, 202


class Austenite(Resource):
    method_decorators = {
        'get': [authenticate_user_cookie_restful],
        'put': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def get(self, _):
        """This GET endpoint auto calculates the `Ae1` and `Ae3` as the user has
        selected the auto calculate feature without the need for sending the
        compositions as they are already stored in the session store.

        Args:
            _: a `sim_api.models.User` that is not used.

        Returns:
            A response object with appropriate status and message strings as
            well as the calculated Ae1 and Ae3 temperatures.
        """
        # - If user has logged in first time, then this endpoint should not be
        #   possible as they have no compositions.
        #   * Need to do the validation checks for this.
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            return response, 500

        session_configs = session_store.get('configurations')

        if not session_configs:
            response['message'] = "No previous session initiated."
            return response, 400

        session_configs['auto_calculate_ae'] = True

        sess_alloy_store = session_store.get('alloy_store')

        if not sess_alloy_store:
            response['message'] = 'No previous session initiated.'
            return response, 400

        comp_list: list = []
        if sess_alloy_store['alloy_option'] == 'single':
            comp_list = sess_alloy_store['alloys']['parent']['compositions']
        elif sess_alloy_store['alloy_option'] == 'mix':
            # DECISION:
            # We will not implement this as it adds too much complexity to
            # the logical path of the system state. This was not a core
            # requirement and Dr. Bendeich often said he did not want this
            # implemented at all.
            pass

        if comp_list is None:
            response['message'] = 'User has not set an Alloy.'
            return response, 400

        try:
            comp_np_arr = SimConfig.get_compositions(comp_list)
        except ConfigurationError as e:
            response['errors'] = str(e)
            response['message'] = str(e)
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500

        ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)

        # Save the new calculated Ae1 and Ae3 to the Session store
        session_configs['ae1_temp'] = ae1
        session_configs['ae3_temp'] = ae3
        session_configs['is_valid'] = False
        session_store['configurations'] = session_configs

        SimSessionService().save_session(session_store)

        response['status'] = 'success'
        response.pop('message')
        response['data'] = {'ae1_temp': ae1, 'ae3_temp': ae3}

        return response, 200

    # noinspection PyMethodMayBeStatic
    def put(self, _):
        """If the user manually updates the Ae1 and Ae3 temperatures in the
        client, we receive those and update the session cache.

        Args:
            _: a `sim_api.models.User` that is not used.

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

        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            return response, 500

        session_configs = session_store.get('configurations')

        if session_configs is None:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        session_configs['auto_calculate_ae'] = False
        session_configs['ae1_temp'] = ae1_temp
        session_configs['ae3_temp'] = ae3_temp
        session_configs['is_valid'] = False
        session_store['configurations'] = session_configs

        SimSessionService().save_session(session_store)

        return {'status': 'success'}, 202


api.add_resource(Configurations, '/api/v1/sim/configs/update')
api.add_resource(ConfigsMethod, '/api/v1/sim/configs/method/update')
api.add_resource(MartensiteStart, '/api/v1/sim/configs/ms')
api.add_resource(BainiteStart, '/api/v1/sim/configs/bs')
api.add_resource(Austenite, '/api/v1/sim/configs/ae')
