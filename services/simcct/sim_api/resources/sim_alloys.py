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
__version__ = '1.0.0'
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
from sim_api.extensions.utilities import (
    DuplicateElementError, ElementInvalid, ElementSymbolInvalid,
    MissingElementError, ElementWeightInvalid
)
from sim_api.extensions.SimSession.sim_session_service import SimSessionService
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.schemas import (
    AlloySchema, AlloyStoreSchema, ConfigurationsSchema
)
from simulation import SimConfiguration as SimConfig
from simulation import Method

logger = AppLogger(__name__)

sim_alloys_blueprint = Blueprint('sim_alloys', __name__)


class AlloyStore(Resource):
    method_decorators = {
        'patch': [authenticate_user_cookie_restful],
        'post': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
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
        if alloy_option not in {'single', 'mix'}:
            response['message'] = (
                'Alloy option not one of '
                '["single" | "mix"].'
            )
            return response, 400

        if not alloy_type or not isinstance(alloy_type, str):
            response['message'] = 'No alloy type was provided.'
            return response, 400

        if alloy_type not in {'parent', 'mix'}:
            response['message'] = (
                'Alloy type not one of ["parent" | "mix"].'
            )
            return response, 400

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
            # If no "symbol" or "weight" passed as an Element object.
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
            response['error'] = str(e.messages)
            response['message'] = 'Alloy failed schema validation.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
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
                # DECISION:
                # We will not implement this as it adds too much complexity to
                # the logical path of the system state. This was not a core
                # requirement and Dr. Bendeich often said he did not want this
                # implemented at all.
                pass
        except ValidationError as e:
            response['error'] = e.messages
            response['message'] = 'Alloy failed schema validation.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 400

        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            logger.info(response['message'])
            apm.capture_message(response['message'])
            return response, 500

        session_store['alloy_store'] = valid_store

        session_configs = session_store['configurations']

        if not session_configs:
            response['message'] = (
                'Cannot retrieve configurations from session.'
            )
            logger.error(response['message'], stack_info=True)
            apm.capture_message(response['message'])
            return response, 500

        try:
            valid_configs = ConfigurationsSchema().load(session_configs)
        except ValidationError as e:
            response['error'] = e.messages
            response['message'] = (
                'Validation error for session configurations.'
            )
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
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

        # See Decision above.
        # else:
        # comp_list = (
        #     sess_alloy_store['mix']['compositions']
        # )
        # pass

        comp_np_arr = SimConfig.get_compositions(comp_list)

        if comp_np_arr is False:
            response['message'] = 'Compositions conversion error.'
            logger.error(response['message'])
            apm.capture_message(response['message'])
            return response, 500

        # We need to store some results so let's prepare an empty dict
        response['message'] = (
            'Compositions and Configurations in Session '
            'initiated.'
        )
        data = {}

        # We need to convert them to our enums as required by the Sim
        # package - by default we always use Li98
        method = Method.Li98

        if valid_configs['auto_calculate_ms']:
            ms_temp = SimConfig.get_ms(method, comp=comp_np_arr)
            ms_rate_param = SimConfig.get_ms_alpha(comp=comp_np_arr)
            valid_configs['ms_temp'] = ms_temp
            valid_configs['ms_rate_param'] = ms_rate_param
            data.update({'ms_temp': ms_temp, 'ms_rate_param': ms_rate_param})

        if valid_configs['auto_calculate_bs']:
            bs_temp = SimConfig.get_bs(method, comp=comp_np_arr)
            valid_configs['bs_temp'] = bs_temp
            data.update({'bs_temp': bs_temp})

        if valid_configs['auto_calculate_ae']:
            ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)
            valid_configs['ae1_temp'] = ae1
            valid_configs['ae3_temp'] = ae3
            data.update({'ae1_temp': ae1, 'ae3_temp': ae3})

        valid_configs['is_valid'] = False
        session_store['configurations'] = valid_configs

        SimSessionService().save_session(session_store)

        response.update({'data': data})
        response['status'] = 'success'
        return response, 201

    # noinspection PyMethodMayBeStatic
    def patch(self, _):
        """This PATCH endpoint simply updates the `alloys` in the session
        store so that we can update all the other transformation temperature.

        Args:
            _: a `sim_api.models.User` that is not used.

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

        if alloy_option not in {'single', 'mix'}:
            response['message'] = (
                'Alloy option not one of '
                '["single" | "mix"].'
            )
            return response, 400

        # We have a couple of ways the Alloy is stored in both Session and
        # Database based on what is available with the alloy_option and
        # alloy_type. From the client, we expect these two keys to at the
        # very least be in the request body. Otherwise we won't do anything.

        if not alloy_type or not isinstance(alloy_type, str):
            response['message'] = 'No alloy type was provided.'
            return response, 400

        if alloy_type not in {'parent', 'weld', 'mix'}:
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
            response['message'] = 'No valid key in the alloy was provided.'
            return response, 400

        if not isinstance(alloy.get('compositions'), list):
            response['message'] = (
                'Valid compositions must be provided as a list.'
            )
            return response, 400

        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            logger.error(response['message'])
            apm.capture_message(response['message'])
            return response, 500

        # We get what's currently stored in the session and we update it
        sess_alloy_store = session_store.get('alloy_store')

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
            else:
                # DECISION:
                # We will not implement this as it adds too much complexity to
                # the logical path of the system state. This was not a core
                # requirement and Dr. Bendeich often said he did not want this
                # implemented at all.
                pass
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
            # If no "symbol" or "weight" passed as an Element object.
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
            response['error'] = e.messages
            response['message'] = 'Alloy failed schema validation.'
            return response, 400

        # We also need to do auto update fixes if necessary
        session_store['alloy_store'] = sess_alloy_store
        sess_configs = session_store.get('configurations')

        # Well, if we don't need to auto calc. anything, let's get out of here
        if (
            not sess_configs['auto_calculate_ms']
            and not sess_configs['auto_calculate_bs']
            and not sess_configs['auto_calculate_ae']
        ):
            # If we are only updating the alloy_store in the session, we access
            # Redis at this point and save it.
            SimSessionService().save_session(session_store)

            response['status'] = 'success'
            response['message'] = 'Compositions updated.'
            return response, 200

        # Since we do need to calculate, must get the compositions first in
        # numpy.ndarray structured format and type

        # We update the transformation limits based on which option is chosen
        comp_list: list = []
        if alloy_option == 'single':
            comp_list = sess_alloy_store['alloys']['parent']['compositions']

        # See above.
        # else:
        # comp_list = (
        #     sess_alloy_store['mix']['compositions']
        # )
        # pass

        comp_np_arr = SimConfig.get_compositions(comp_list)

        if comp_np_arr is False:
            response['message'] = 'Compositions conversion error.'
            logger.error(response['message'])
            apm.capture_message(response['message'])
            return response, 500

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

        sess_configs['is_valid'] = False
        session_store['configurations'] = sess_configs

        SimSessionService().save_session(session_store)

        response['status'] = 'success'
        return response, 200


api.add_resource(AlloyStore, '/v1/sim/alloys/update')
