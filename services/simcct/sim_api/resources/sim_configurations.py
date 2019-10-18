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
__version__ = '2.0.0'
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
from sim_api.extensions.utilities import (DuplicateElementError, ElementInvalid,
                                          ElementSymbolInvalid,
                                          ElementWeightInvalid,
                                          MissingElementError)
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.routes import Routes
from sim_api.schemas import AlloyStoreSchema
from simulation.simconfiguration import SimConfiguration as SimConfig
from simulation.utilities import ConfigurationError, Method

configs_blueprint = Blueprint('sim_configurations', __name__)
logger = AppLogger(__name__)


# noinspection PyMethodMayBeStatic,DuplicatedCode
class Martensite(Resource):
    """
    The Resource to accomplish calculations for Martensite limits, `ms`.
    """

    method_decorators = {
        'post': [authenticate_user_cookie_restful],
        'put': [authenticate_user_cookie_restful]
    }

    def post(self, _):
        """This POST view method auto calculates the `Ms` as the user has
        selected the auto calculate feature. We are required to receive in
        the request body a `method` which must be a valid one as either
        "Li98" or "Kirkaldy83" and an `alloy_store` object.

        Args:
            _: a `sim_api.models.User` that is not used.

        Returns:
            A response object with appropriate status and message strings as
            well as the calculated Bs temperature.
        """

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()

        if not post_data:
            return response, 400

        alloy_store = post_data.get('alloy_store', None)
        method = post_data.get('method', None)

        # ===== # Validation Checks of POST BODY # ===== #
        if not alloy_store:
            response.update({'message': 'Alloy store required.'})
            return response, 400

        if not method:
            response.update({'message': 'Method required.'})
            return response, 400

        if method not in {'Li98', 'Kirkaldy83'}:
            response.update(
                {'message': 'Method must be one of ["Li98" | "Kirkaldy83"].'}
            )
            return response, 400

        # We need to validate the Alloy Store that matches our expected schema
        try:
            valid_store = AlloyStoreSchema().load(alloy_store)
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
        except ElementWeightInvalid as e:
            # If `C` weight is more than 0.8
            response['error'] = str(e)
            response['message'] = 'Invalid element weight error.'
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
            response['error'] = str(e.messages)
            response['message'] = 'Model schema validation error.'
            apm.capture_exception()
            return response, 400

        # We need to convert them to our enums as required by the calculations.
        transformation_method = Method.Li98
        if method == 'Kirkaldy83':
            transformation_method = Method.Kirkaldy83

        comp_list: list = []
        if valid_store['alloy_option'] == 'single':
            comp_list = valid_store['alloys']['parent'].get(
                'compositions', None
            )
        elif valid_store['alloy_option'] == 'mix':
            # DECISION:
            # We will not implement this as it adds too much complexity to
            # the logical path of the system state. This was not a core
            # requirement and Dr. Bendeich often said he did not want this
            # implemented at all.
            response.update({'message': 'Mix option not allowed.'})
            return response, 400

        if comp_list is None or not comp_list:
            response['message'] = 'No alloy composition.'
            return response, 400

        try:
            comp_np_arr = SimConfig.get_compositions(comp_list)
        except ConfigurationError as e:
            response['error'] = str(e)
            response['message'] = str(e)
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500

        # We try to do the calculation with Dr. Bendeich's algorithm but we
        # need to ensure we capture any exception that can occur.
        try:
            ms_temp = SimConfig.get_ms(
                method=transformation_method, comp=comp_np_arr
            )
            ms_rate_param = SimConfig.get_ms_alpha(comp=comp_np_arr)
        except Exception as e:
            # This is to make sure the client knows there has been some
            # calculation error which is potentially something to do with
            # our back-end code or, more likely, a value in the alloy
            # composition that does not work with this algorithm.
            msg = 'Calculating Ms and Ms rate param error.'
            logger.exception(msg)
            apm.capture_exception(msg)
            response.update({'message': msg, 'error': str(e)})
            return response, 500

        # Just overwrite the response instead of changing it.
        response = {
            'status': 'success',
            'data': {
                'ms_temp': ms_temp,
                'ms_rate_param': ms_rate_param
            }
        }

        return response, 200

    # [DEPRECATED]
    def put(self, _):
        """DEPRECATED.

        Args:
            _: a `sim_api.models.User` that is not used.

        Returns:
            A valid HTTP Response with a 405 status.
        """
        return {'message': 'Method Not Allowed.', 'status': 'fail'}, 405


# noinspection PyMethodMayBeStatic,DuplicatedCode
class Bainite(Resource):
    """
    The Resource to accomplish calculations for Bainite limits, `bs`.
    """

    method_decorators = {
        'post': [authenticate_user_cookie_restful],
        'put': [authenticate_user_cookie_restful]
    }

    def post(self, _):
        """This POST view method auto calculates the `Bs` as the user has
        selected the auto calculate feature. We are required to receive in
        the request body a `method` which must be a valid one as either
        "Li98" or "Kirkaldy83" and an `alloy_store` object.

        Args:
            _: a `sim_api.models.User` that is not used.

        Returns:
            A response object with appropriate status and message strings as
            well as the calculated Bs temperature.
        """

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()

        if not post_data:
            return response, 400

        alloy_store = post_data.get('alloy_store', None)
        method = post_data.get('method', None)

        # ===== # Validation Checks of POST BODY # ===== #
        if not alloy_store:
            response.update({'message': 'Alloy store required.'})
            return response, 400

        if not method:
            response.update({'message': 'Method required.'})
            return response, 400

        if method not in {'Li98', 'Kirkaldy83'}:
            response.update(
                {'message': 'Method must be one of ["Li98" | "Kirkaldy83"].'}
            )
            return response, 400

        # We need to validate the Alloy Store that matches our expected schema
        try:
            valid_store = AlloyStoreSchema().load(alloy_store)
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
        except ElementWeightInvalid as e:
            # If `C` weight is more than 0.8
            response['error'] = str(e)
            response['message'] = 'Invalid element weight error.'
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
            response['error'] = str(e.messages)
            response['message'] = 'Model schema validation error.'
            apm.capture_exception()
            return response, 400

        # We need to convert them to our enums as required by the calculations.
        transformation_method = Method.Li98
        if method == 'Kirkaldy83':
            transformation_method = Method.Kirkaldy83

        comp_list: list = []
        if valid_store['alloy_option'] == 'single':
            comp_list = valid_store['alloys']['parent'].get(
                'compositions', None
            )
        elif valid_store['alloy_option'] == 'mix':
            # DECISION:
            # We will not implement this as it adds too much complexity to
            # the logical path of the system state. This was not a core
            # requirement and Dr. Bendeich often said he did not want this
            # implemented at all.
            response.update({'message': 'Mix option not allowed.'})
            return response, 400

        if comp_list is None or not comp_list:
            response['message'] = 'No alloy composition.'
            return response, 400

        try:
            comp_np_arr = SimConfig.get_compositions(comp_list)
        except ConfigurationError as e:
            response['error'] = str(e)
            response['message'] = str(e)
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500

        # We try to do the calculation with Dr. Bendeich's algorithm but we
        # need to ensure we capture any exception that can occur.
        try:
            bs_temp = SimConfig.get_bs(
                method=transformation_method, comp=comp_np_arr
            )
        except Exception as e:
            # This is to make sure the client knows there has been some
            # calculation error which is potentially something to do with
            # our back-end code or, more likely, a value in the alloy
            # composition that does not work with this algorithm.
            msg = 'Calculating Bs error.'
            logger.exception(msg)
            apm.capture_exception(msg)
            response.update({'message': msg, 'error': str(e)})
            return response, 500

        # Just overwrite the response instead of changing it.
        return {'status': 'success', 'data': {'bs_temp': bs_temp}}, 200

    # [DEPRECATED]
    def put(self, _):
        """DEPRECATED.

        Args:
            _: a `sim_api.models.User` that is not used.

        Returns:
            A valid HTTP Response with a 405 status.
        """
        return {'message': 'Method Not Allowed.', 'status': 'fail'}, 405


# noinspection PyMethodMayBeStatic
class Austenite(Resource):
    """
    The Resource to accomplish calculations for Austenite, particularly `ae1`
    and `ae3`.
    """

    method_decorators = {
        'post': [authenticate_user_cookie_restful],
        'put': [authenticate_user_cookie_restful]
    }

    def post(self, _):
        """This POST view method auto calculates the `Ae1` and `Ae3` as the
        user has selected the auto calculate feature. We are required to
        receive in the request body a `method` which must be a valid one
        as either "Li98" or "Kirkaldy83" and an `alloy_store` object.

        Args:
            _: a `sim_api.models.User` that is not used.

        Returns:
            A response object with appropriate status and message strings as
            well as the calculated Ae1 and Ae3 temperatures.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()

        if not post_data:
            return response, 400

        alloy_store = post_data.get('alloy_store', None)
        method = post_data.get('method', None)

        # ===== # Validation Checks of POST BODY # ===== #
        if not alloy_store:
            response.update({'message': 'Alloy store required.'})
            return response, 400

        if not method:
            response.update({'message': 'Method required.'})
            return response, 400

        if method not in {'Li98', 'Kirkaldy83'}:
            response.update(
                {'message': 'Method must be one of ["Li98" | "Kirkaldy83"].'}
            )
            return response, 400

        # We need to validate the Alloy Store that matches our expected schema
        try:
            valid_store = AlloyStoreSchema().load(alloy_store)
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
        except ElementWeightInvalid as e:
            # If `C` weight is more than 0.8
            response['error'] = str(e)
            response['message'] = 'Invalid element weight error.'
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
            response['error'] = str(e.messages)
            response['message'] = 'Model schema validation error.'
            apm.capture_exception()
            return response, 400

        # ===== # Check which alloy we are using # ===== #
        comp_list: list = []
        if valid_store['alloy_option'] == 'single':
            comp_list = valid_store['alloys']['parent'].get(
                'compositions', None
            )
        elif valid_store['alloy_option'] == 'mix':
            # DECISION:
            # We will not implement this as it adds too much complexity to
            # the logical path of the system state. This was not a core
            # requirement and Dr. Bendeich often said he did not want this
            # implemented at all.
            response.update({'message': 'Mix option not allowed.'})
            return response, 400

        if comp_list is None or not comp_list:
            response['message'] = 'No alloy composition.'
            return response, 400

        # ===== # Calculations # ===== #
        try:
            # Convert the Alloys list to a structured `numpy.ndarray` that
            # is used by the Simulation package.
            comp_np_arr = SimConfig.get_compositions(comp_list)
        except ConfigurationError as e:
            response['error'] = str(e)
            response['message'] = str(e)
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500

        # We try to do the calculation with Dr. Bendeich's algorithm but we
        # need to ensure we capture any exception that can occur.
        try:
            ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)
        except Exception as e:
            # This is to make sure the client knows there has been some
            # calculation error which is potentially something to do with
            # our back-end code or, more likely, a value in the alloy
            # composition that does not work with this algorithm.
            msg = 'Calculating Ae1 and Ae3 error.'
            logger.exception(msg)
            apm.capture_exception(msg)
            response.update({'message': msg, 'error': str(e)})
            return response, 500

        # Just overwrite the response instead of changing it.
        response = {
            'status': 'success',
            'data': {
                'ae1_temp': ae1,
                'ae3_temp': ae3
            }
        }
        return response, 200

    # [DEPRECATED]
    def put(self, _):
        """DEPRECATED.

        Args:
            _: a `sim_api.models.User` that is not used.

        Returns:
            A valid HTTP Response with a 405 status.
        """
        return {'message': 'Method Not Allowed.', 'status': 'fail'}, 405


api.add_resource(Martensite, Routes.Martensite.value)
api.add_resource(Bainite, Routes.Bainite.value)
api.add_resource(Austenite, Routes.Austenite.value)
