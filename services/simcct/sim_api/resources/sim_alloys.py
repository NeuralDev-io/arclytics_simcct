# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# sim_alloys.py
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
__date__ = '2019.08.03'
"""sim_alloys.py: 

This module defines the View methods for setting an Alloy in the frontend to
be stored in the Flask Session object. 
"""

from flask import Blueprint, request
from flask_restful import Resource
from marshmallow import ValidationError

from arc_logging import AppLogger
from sim_api.extensions import api, apm
from sim_api.routes import Routes
from sim_api.extensions.utilities import (
    DuplicateElementError, ElementInvalid, ElementSymbolInvalid,
    MissingElementError, ElementWeightInvalid
)
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.schemas import AlloyStoreSchema
from simulation import SimConfiguration as SimConfig
from simulation import Method
from simulation.utilities import ConfigurationError

logger = AppLogger(__name__)
sim_alloys_blueprint = Blueprint('sim_alloys', __name__)


# noinspection PyMethodMayBeStatic
class AlloyStore(Resource):
    """
    This Resource provides the method when the client has updated their Alloy
    and/or compositions for the alloy and we need to do auto calculation of
    Austenite, Martensite, or Bainite transformation limits.
    """

    method_decorators = {
        'patch': [authenticate_user_cookie_restful],
        'post': [authenticate_user_cookie_restful]
    }

    def post(self, _):
        """This POST endpoint initiates the Alloy Store by setting the alloy
        in the request body to the Session storage.

        Args:
            _: a `sim_api.models.User` that is not used.

        Returns:
            A response object with appropriate status and message
            strings.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()
        if not post_data:
            return response, 400

        # Extract the method from the post request body
        # REQUEST BODY SHOULD BE FOR ALLOY_STORE
        # {
        #     "alloy_option": "single",
        #     "alloy": {
        #           "name": "...",
        #           "compositions": [{"symbol": "C", "weight": 1}, ...]
        #     }
        # }

        alloy_store = post_data.get('alloy_store', None)
        method = post_data.get('method', None)
        auto_calc_ae = post_data.get('auto_calculate_ae', False)
        auto_calc_ms = post_data.get('auto_calculate_ms', False)
        auto_calc_bs = post_data.get('auto_calculate_bs', False)

        # ===== # Validation Checks of POST BODY # ===== #
        if not auto_calc_ae and not auto_calc_ms and not auto_calc_bs:
            response.update(
                {'message': 'No auto calculate booleans have been sent.'}
            )
            return response, 400

        if not method:
            response.update({'message': 'Method required.'})
            return response, 400

        if method not in {'Li98', 'Kirkaldy83'}:
            response.update(
                {'message': 'Method must be one of ["Li98" | "Kirkaldy83"].'}
            )
            return response, 400

        if not alloy_store:
            response.update({'message': 'Alloy store required.'})
            return response, 400

        # This is to ensure we know which alloy or mix to do the calculations
        # on even though we have yet to implement the `mix` option.
        if not alloy_store.get('alloy_option') in {'single', 'mix'}:
            response.update(
                {'message': 'Alloy option must be one of ["single" | "mix"]'}
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

        if comp_np_arr is False:
            response['message'] = 'Compositions conversion error.'
            logger.error(response['message'])
            apm.capture_message(response['message'])
            return response, 500

        # We need to store some results so let's prepare an empty dict
        data = {}

        # We need to convert them to our enums as required by the calculations.
        transformation_method = Method.Li98
        if method == 'Kirkaldy83':
            transformation_method = Method.Kirkaldy83

        if auto_calc_ms:
            # We try to do the calculation with Dr. Bendeich's algorithm but we
            # need to ensure we capture any exception that can occur.
            try:
                ms_temp = SimConfig.get_ms(
                    method=transformation_method, comp=comp_np_arr
                )
                ms_rate_param = SimConfig.get_ms_alpha(comp=comp_np_arr)
                data.update(
                    {
                        'ms_temp': ms_temp,
                        'ms_rate_param': ms_rate_param
                    }
                )
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

        if auto_calc_bs:
            try:
                bs_temp = SimConfig.get_bs(
                    method=transformation_method, comp=comp_np_arr
                )
                data.update({'bs_temp': bs_temp})
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

        if auto_calc_ae:
            # We try to do the calculation with Dr. Bendeich's algorithm but we
            # need to ensure we capture any exception that can occur.
            try:
                ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)
                data.update({'ae1_temp': ae1, 'ae3_temp': ae3})
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
        return {'status': 'success', 'data': data}, 200

    # noinspection PyMethodMayBeStatic
    def patch(self, _):
        """DEPRECATED.

        Args:
            _: a `sim_api.models.User` that is not used.

        Returns:
            A response object with appropriate status and message strings.
        """
        return {'message': 'Method Not Allowed.', 'status': 'fail'}, 405


api.add_resource(AlloyStore, Routes.AlloyStore.value)
