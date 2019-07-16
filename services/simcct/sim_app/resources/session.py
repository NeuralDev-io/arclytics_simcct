# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# session.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.3.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.10'
"""session.py: 

This module defines the resources for session management. 
"""

import os

import requests
from marshmallow import ValidationError
from flask import Blueprint, session, request
from flask_restful import Resource
from bson import ObjectId

from sim_app.schemas import (ConfigurationsSchema, AlloySchema)
from sim_app.middleware import token_required_restful

session_blueprint = Blueprint('session', __name__)


class Session(Resource):
    method_decorators = {'post': [token_required_restful]}

    def post(self, token):
        post_data = request.get_json()

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        if not post_data:
            return response, 400

        user_id = post_data.get('_id', None)
        user_configs = post_data.get('last_configurations', None)
        user_comp = post_data.get('last_compositions', None)

        if not ObjectId.is_valid(user_id):
            response['message'] = 'User ObjectId must be provided.'
            return response, 401

        # TODO(andrew@neuraldev.io): Need to do some validation for some fields
        #  - Need to validate the auto_calculate bools
        #  - Need to ensure the method is provided.
        #  - Need to ensure the transformation_method is also provided if the
        #    auto_calculate_ms_bs is true
        #  - Need to ensure there is a value for ae1 and ae3 if
        #    auto_calculate_ae is not true

        configs = None
        if user_configs:
            try:
                configs = ConfigurationsSchema().load(user_configs)
            except ValidationError as e:
                response['errors'] = e.messages
        else:
            configs = {
                'method': 'Li98',
                'alloy': 'parent',
                'grain_size_type': 'ASTM',
                'grain_size': 0.0,
                'nucleation_start': 1.0,
                'nucleation_finish': 99.90,
                'auto_calculate_xfe': True,
                'xfe_value': 0.0,
                'cf_value': 0.0,
                'ceut_value': 0.0,
                'auto_calculate_ms_bs': True,
                'transformation_method': 'Li98',
                'ms_temp': 0.0,
                'ms_undercool': 0.0,
                'bs_temp': 0.0,
                'auto_calculate_ae': True,
                'ae1_temp': 0.0,
                'ae3_temp': 0.0,
                'start_temp': 0,
                'cct_cooling_rate': 0
            }

        # TODO(andrew@neuraldev.io): If auto_calculate on any of these are true
        #  we have to ensure there are at least the necessary elements.
        #  - get_bs() --> carbon, manganese, ni, chromium, molybdenum
        #  - get_ms() --> carbon, manganese, nickel, chromium, molybdenum,
        #                 cobalt, silicon
        #  - xfe_method2() --> carbon and iron
        #  - calc_ae1_ae3() --> carbon, nickel, silicon, tungsten, manganese,
        #                       manganese, chromium, arsenic, molybdenum
        comp_obj = None
        if user_comp:
            user_alloy = user_comp['alloy']
            try:
                # ElementSchema also validates each element because it is nested
                comp_obj = AlloySchema().load(user_alloy)
            except ValidationError as e:
                response['errors'] = e.messages
                return response, 400

        session['user'] = user_id
        session['token'] = token
        session[f'{token}:configurations'] = configs
        session[f'{token}:alloy'] = comp_obj

        response['status'] = 'success'
        response['message'] = 'User session initiated.'
        response['session_id'] = session.sid

        return response, 201


class UsersPing(Resource):
    """
    This is just a sanity check to ensure we can connect from this server to
    the users-server through Docker just fine.
    """

    def get(self):
        users_server = os.environ.get('USERS_HOST', None)
        # We use the built-in DNS server of Docker to resolve the correct
        # IP address of the other container [1].
        url = f'http://{users_server}/ping'
        res = requests.get(url)
        return res.json(), 200, {'Content-type': 'application/json'}
