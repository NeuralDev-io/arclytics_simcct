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
from flask import Blueprint, request, jsonify
from bson import ObjectId

from sim_app.sim_session import SimSessionService
from sim_app.schemas import (ConfigurationsSchema, AlloyStoreSchema)
from sim_app.middleware import token_required_flask, session_key_required_flask
from simulation.utilities import MissingElementError
from logger.arc_logger import AppLogger

logger = AppLogger(__name__)

session_blueprint = Blueprint('session', __name__)


@session_blueprint.route('/session/login', methods=['POST'])
@token_required_flask
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
    user_results = post_data.get('last_results', None)

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
        # These are based of defaults in the front-end as agreed to by Andrew
        # and Dalton.
        configs = {
            'is_valid': False,
            'method': 'Li98',
            'grain_size': 8.0,
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
            'start_temp': 900,
            'cct_cooling_rate': 10
        }

    if user_alloy_store:
        try:
            # The schema now validates elements and passes back any errors
            # with the element symbol. We still need to validate missing
            # elements below.
            alloy_store = AlloyStoreSchema().load(user_alloy_store)
        except MissingElementError as e:
            response['message'] = str(e)
            return jsonify(response), 400
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

    # This dict defines what we store in Redis for the session
    session_data_store = {
        'user_id': user_id,
        'is_admin': user_is_admin,
        'token': token,
        'configurations': configs,
        'alloy_store': alloy_store,
        # TODO(andrew@neuraldev.io) Update this to get from last in user doc
        'results': None
    }
    session_key = SimSessionService().new_session(token, session_data_store)

    response['status'] = 'success'
    response['message'] = 'User session initiated.'
    response['session_key'] = session_key

    return jsonify(response), 201


@session_blueprint.route('/session/logout', methods=['GET'])
@session_key_required_flask
def session_logout(session_key):
    """We need to destroy the Session store of the user's configurations and
    other storage matters if the user has logged out from the users.

    Args:
        session_key: a valid TimedJSONWebSignature token.

    Returns:
        A JSON response and a status code.
    """
    response = {'status': 'fail', 'message': 'Invalid session.'}

    # Delete this from the Redis datastore
    SimSessionService().clean_redis_session(session_key)

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
