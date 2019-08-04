# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# sim_alloys.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.03'
"""sim_alloys.py: 

{Description}
"""

from flask import Blueprint, request, session
from flask_restful import Resource
from marshmallow import ValidationError

from sim_app.extensions import api
from sim_app.schemas import AlloySchema, AlloyStoreSchema
from sim_app.middleware import token_required_restful
from simulation.simconfiguration import SimConfiguration as SimConfig
from simulation.utilities import Method

sim_alloys_blueprint = Blueprint('sim_alloys', __name__)


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

        alloy_name = alloy.get('name', None)
        alloy_comp = alloy.get('compositions', None)

        if not alloy_name and not alloy_comp:
            response['message'] = ('No valid keys was provided for alloy '
                                   '(i.e. must be "name" or "compositions")')
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
        except ValidationError as e:
            response['errors'] = str(e)
            response['message'] = 'Alloy failed schema validation.'
            return response, 400

        # TODO(andrew@neuraldev.io): Need to also validate every element is
        #  a valid symbol.
        # Validate the alloy has all the elements that we need by using a
        # hashed dictionary which is must faster than iterating a list
        valid_elements = {
            'C': False,
            'Mn': False,
            'Ni': False,
            'Cr': False,
            'Mo': False,
            'Si': False,
            'Co': False,
            'W': False,
            'As': False,
            'Fe': False
        }

        for el in alloy_comp:
            if el['symbol'] in valid_elements.keys():
                valid_elements[el['symbol']] = True

        # all() returns True if all values in the dict are True
        # If it does not pass, we build up a message and respond.
        if not all(el is True for el in valid_elements.values()):
            # We build up a list of missing elements for the response.
            missing_elem = []
            for k, v in valid_elements.items():
                if not v:
                    missing_elem.append(k)

            response['message'] = f'Missing elements {missing_elem}'
            return response, 400
        # Otherwise we have all the elements we need

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
        return response, 201

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
            response['message'] = 'No valid key in the alloy was provided.'
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


api.add_resource(AlloyStore, '/alloys/update')
