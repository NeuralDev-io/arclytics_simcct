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
from flask import Blueprint, session, request, jsonify, Response, json
from bson import ObjectId

from sim_app.sim_session import SimSessionService
from sim_app.schemas import (ConfigurationsSchema, AlloyStoreSchema)
from sim_app.middleware import token_required
from simulation.utilities import validate_comp_elements
from logger.arc_logger import AppLogger

logger = AppLogger(__name__)

session_blueprint = Blueprint('session', __name__)


@session_blueprint.route('/session/login', methods=['POST'])
@token_required
def session_login(token):
    post_data = request.get_json()

    response = {'status': 'fail', 'message': 'Invalid payload.'}

    if not post_data:
        return jsonify(response), 400

    # We take what's currently stored in the User's document and then we
    # validate it.
    user_id = post_data.get('_id', None)
    user_is_admin = post_data.get('is_admin', False)
    user_configs = post_data.get('last_configurations', None)
    user_alloy_store = post_data.get('last_alloy_store', None)

    if not ObjectId.is_valid(user_id):
        response['message'] = 'User ObjectId must be provided.'
        return jsonify(response), 401

    # TODO(andrew@neuraldev.io): Need to do some validation for some fields
    #  - Need to validate the auto_calculate bools
    #  - Need to ensure the method is provided.
    #  - Need to ensure there is a value for ae1 and ae3 if
    #    auto_calculate_ae is not true

    if user_configs:
        try:
            configs = ConfigurationsSchema().load(user_configs)
        except ValidationError as e:
            response['errors'] = e.messages
            return jsonify(response), 400
    else:
        configs = {
            'is_valid': False,
            'method': 'Li98',
            'grain_size': 0.0,
            'nucleation_start': 1.0,
            'nucleation_finish': 99.90,
            'auto_calculate_ms': True,
            'ms_temp': 0.0,
            'ms_rate_param': 0.0,
            'auto_calculate_bs': True,
            'bs_temp': 0.0,
            'auto_calculate_ae': True,
            'ae1_temp': 0.0,
            'ae3_temp': 0.0,
            'start_temp': 0,
            'cct_cooling_rate': 0
        }

    if user_alloy_store:
        try:
            # The schema now validates elements and passes back any errors
            # with the element symbol. We still need to validate missing
            # elements below.
            alloy_store = AlloyStoreSchema().load(user_alloy_store)

            if alloy_store['alloy_option'] == 'single':
                # Validate the alloy has all the elements that we need
                comp = alloy_store['alloys'].get('parent')
                valid, missing_elem = validate_comp_elements(comp)
                if not valid:
                    response['message'] = f'Missing elements {missing_elem}'
                    return response, 400
            # TODO(andrew@neuraldev.io): Implement the other alloy options.
        except ValidationError as e:
            response['errors'] = e.messages
            return jsonify(response), 400
    else:
        alloy_store = {
            'alloy_option': 'single',
            'alloys': {
                'parent': None,
                'weld': None,
                'mix': None
            }
        }

    # TODO(andrew)
    session['user_id'] = user_id
    session['is_admin'] = user_is_admin
    session['token'] = token
    session['configurations'] = configs
    session['alloy_store'] = alloy_store

    logger.info('session_login : POST')
    logger.pprint(session)

    response['status'] = 'success'
    response['message'] = 'User session initiated.'

    resp = Response(
        response=json.dumps(response), status=201, mimetype='application/json'
    )
    resp.headers['Access-Control-Allow-Headers'] = (
        'Origin, X-Requested-With, Content-Type, Accept, x-auth'
    )
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'

    return resp


@session_blueprint.route('/session/logout', methods=['GET'])
@token_required
def session_logout(token):
    """We need to destroy the Session store of the user's configurations and
    other storage matters if the user has logged out from the users.

    Args:
        token: a valid JWT token associated with the user.

    Returns:
        A JSON response and a status code.
    """
    response = {'status': 'fail', 'message': 'Invalid session.'}
    sess_user = session.get('user')

    # FIXME(andrew@neuraldev.io): This seems to not be working as signing in
    #  does not store the user OR your testing method is screwed up.
    # sess_token = session.get(f'{sess_user}:token')
    # response['session_user'] = sess_user
    # response['session_token'] = sess_token

    # if token != sess_token:
    #     response['session_user'] = sess_user
    #     return jsonify(response), 401

    # session.pop(f'{token}:user')
    # session.pop(f'{sess_user}:token')
    # session.pop(f'{token}:configurations')
    # session.pop(f'{token}:alloy')

    response['status'] = 'success'
    response.pop('message')
    return jsonify(response), 200


@session_blueprint.route('/users/ping', methods=['GET'])
def ping_users_server():
    """
    This is just a sanity check to ensure we can connect from this server to
    the users through Docker just fine.
    """
    users_server = os.environ.get('USERS_HOST', None)
    # We use the built-in DNS server of Docker to resolve the correct
    # IP address of the other container [1].
    url = f'http://{users_server}/ping'
    res = requests.get(url)
    return (
        jsonify(res.json()), res.status_code, {
            'Content-type': 'application/json'
        }
    )
