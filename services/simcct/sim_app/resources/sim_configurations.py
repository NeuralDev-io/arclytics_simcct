# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# sim_configurations.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['Dr. Philip Bendeich', 'Dr. Ondrej Muransky']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.13'
"""sim_configurations.py: 

This module deals with all the endpoints for setting and updating the 
configurations for the main simulations page. 
"""

import numpy as np

from flask import Blueprint, session, request, jsonify
from marshmallow import ValidationError

from simulation.simconfiguration import SimConfiguration as SimConfig
from simulation.utilities import Method
from sim_app.middleware import token_required
from sim_app.schemas import (
    AlloySchema, ConfigurationsSchema, NonLimitConfigsSchema
)

configs_blueprint = Blueprint('configs', __name__)


@configs_blueprint.route(rule='/configs/update', methods=['PUT'])
@token_required
def update_configurations(token):
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    post_data = request.get_json()
    if not post_data:
        return jsonify(response), 400

    session_configs = session.get(f'{token}:configurations')
    if session_configs is None:
        response['message'] = 'No previous session configurations was set.'
        return jsonify(response), 404

    # validate the configurations again
    try:
        configs = NonLimitConfigsSchema().load(post_data)
    except ValidationError as e:
        response['errors'] = e.messages
        return jsonify(response), 400

    sess_store = session.get(f'{token}:configurations')
    sess_store['grain_size'] = configs['grain_size']
    sess_store['nucleation_start'] = configs['nucleation_start']
    sess_store['nucleation_finish'] = configs['nucleation_finish']
    sess_store['start_temp'] = configs['start_temp']
    sess_store['cct_cooling_rate'] = configs['cct_cooling_rate']
    session[f'{token}:configurations'] = sess_store

    response['status'] = 'success'
    response['message'] = 'Setup configurations values have been updated.'
    return jsonify(response), 202


@configs_blueprint.route(rule='/configs/method/update', methods=['PUT'])
@token_required
def method_change(token):
    """This POST endpoint simply updates the `method` for CCT and TTT
    calculations
    in the session store

    Args:
        token: a valid JWT token.

    Returns:
        A response object with appropriate status and message strings.
    """
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    post_data = request.get_json()
    if not post_data:
        return jsonify(response), 400
    # Extract the method from the post request body
    method = post_data.get('method', None)

    if not method:
        response['message'] = 'No method was provided.'
        return jsonify(response), 400

    if not method == Method.Li98.name and not method == Method.Kirkaldy83.name:
        response['message'] = (
            'Invalid method provided (must be Li98 or '
            'Kirkaldy83).'
        )
        return jsonify(response), 400

    session_configs = session.get(f'{token}:configurations')

    if session_configs is None:
        response['message'] = 'No previous session configurations was set.'
        return jsonify(response), 404

    session_configs['method'] = Method.Li98.name
    if method == 'Kirkaldy83':
        session_configs['method'] = Method.Kirkaldy83.name

    response['status'] = 'success'
    response['message'] = f'Changed to {method} method.'
    return jsonify(response), 200


@configs_blueprint.route(rule='/configs/comp/update', methods=['POST'])
@token_required
def composition_change(token):
    """This POST endpoint simply updates the `compositions` in the session
    store so that we can update all the other methods.

    Args:
        token: a valid JWT token.

    Returns:
        A response object with appropriate status and message strings.
    """
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    post_data = request.get_json()
    if not post_data:
        return jsonify(response), 400
    # Extract the method from the post request body
    comp = post_data.get('alloy', None)
    alloy_type = post_data.get('alloy_type', None)

    if not comp:
        response['message'] = 'No composition list was provided.'
        return jsonify(response), 400

    try:
        comp_obj = AlloySchema().load(comp)
    except ValidationError as e:
        response['errors'] = e.messages
        response['message'] = 'Alloy failed schema validation.'
        return jsonify(response), 400

    session[f'{token}:alloy'] = comp_obj
    session[f'{token}:configurations']['alloy'] = alloy_type

    session_configs = session.get(f'{token}:configurations')

    # Well, if we don't need to auto calculate anything, let's get out of here
    if (
        not session_configs['auto_calculate_ms']
        and not session_configs['auto_calculate_bs']
        and not session_configs['auto_calculate_ae']
    ):
        response['status'] = 'success'
        response['message'] = 'Compositions updated.'
        return jsonify(response), 200

    # Since we do need to calculate, must get the compositions first in
    # numpy.ndarray structured format and type
    comp_list = session.get(f'{token}:alloy')['compositions']
    comp_np_arr = SimConfig.get_compositions(comp_list)

    # We need to store some results so let's prepare an empty dict
    response['message'] = 'Compositions and other values updated.'
    response['data'] = {}

    method = Method.Li98
    if session_configs['method'] == 'Kirkaldy83':
        method = Method.Kirkaldy83

    if session_configs['auto_calculate_ms']:
        # We need to convert them to our enums as required by the calculations.

        ms_temp = SimConfig.get_ms(method, comp=comp_np_arr)
        ms_rate_param = SimConfig.get_ms_alpha(comp=comp_np_arr)

        session_configs['auto_calculate_ms'] = True
        session_configs['ms_temp'] = ms_temp
        session_configs['ms_rate_param'] = ms_rate_param
        response['data']['ms_temp'] = ms_temp
        response['data']['ms_rate_param'] = ms_rate_param

    if session_configs['auto_calculate_bs']:
        # We need to convert them to our enums as required by the calculations.

        bs_temp = SimConfig.get_bs(method, comp=comp_np_arr)

        session_configs['auto_calculate_bs'] = True
        session_configs['bs_temp'] = bs_temp
        response['data']['bs_temp'] = bs_temp

    if session_configs['auto_calculate_ae']:
        ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)

        session_configs['auto_calculate_ae'] = True
        session_configs['ae1_temp'] = ae1
        session_configs['ae3_temp'] = ae3
        response['data']['ae1_temp'] = ae1
        response['data']['ae3_temp'] = ae3

    session[f'{token}:configurations'] = session_configs

    response['status'] = 'success'
    return jsonify(response), 200


@configs_blueprint.route(rule='/configs/auto/ms', methods=['GET'])
@token_required
def auto_calculate_ms(token):
    """This POST endpoint auto calculates the `MS` and `MS Rate Param` as the
    user has selected the auto calculate feature without the need for sending
    the compositions as they are already stored in the session store.

    Args:
        token: a valid JWT token.

    Returns:
        A response object with appropriate status and message strings as well
        as the calculated MS temperature and MS Rate Parameter.
    """

    # - If user has logged in first time, then this endpoint should not be
    #   possible as they have no compositions.
    #   * Need to do the validation checks for this.

    response = {'status': 'fail', 'message': 'Invalid payload.'}

    session_configs = session.get(f'{token}:configurations')

    # We need to convert them to our enums as required by the calculations.
    _transformation_method = Method.Li98
    if session_configs['method'] == 'Kirkaldy83':
        _transformation_method = Method.Kirkaldy83

    session_configs['auto_calculate_ms'] = True

    comp_list = session.get(f'{token}:alloy')['compositions']
    comp_np_arr = SimConfig.get_compositions(comp_list)

    ms_temp = SimConfig.get_ms(method=_transformation_method, comp=comp_np_arr)
    ms_rate_param = SimConfig.get_ms_alpha(comp=comp_np_arr)

    # Save the new calculated BS and MS to the Session store
    session_configs['ms_temp'] = ms_temp
    session_configs['ms_rate_param'] = ms_rate_param
    session[f'{token}:configurations'] = session_configs

    response['status'] = 'success'
    response.pop('message')
    response['data'] = {'ms_temp': ms_temp, 'ms_rate_param': ms_rate_param}

    return jsonify(response), 200


@configs_blueprint.route(rule='/configs/auto/bs', methods=['GET'])
@token_required
def auto_calculate_bs(token):
    """This POST endpoint auto calculates the `BS` as the user has
    selected the auto calculate feature without the need for sending the
    compositions as they are already stored in the session store.

    Args:
        token: a valid JWT token.

    Returns:
        A response object with appropriate status and message strings as well
        as the calculated BS temperature.
    """

    # - If user has logged in first time, then this endpoint should not be
    #   possible as they have no compositions.
    #   * Need to do the validation checks for this.

    response = {'status': 'fail', 'message': 'Invalid payload.'}

    session_configs = session.get(f'{token}:configurations')

    # We need to convert them to our enums as required by the calculations.
    _transformation_method = Method.Li98
    if session_configs['method'] == 'Kirkaldy83':
        _transformation_method = Method.Kirkaldy83

    session_configs['auto_calculate_bs'] = True

    comp_list = session.get(f'{token}:alloy')['compositions']
    comp_np_arr = SimConfig.get_compositions(comp_list)

    bs_temp = SimConfig.get_bs(method=_transformation_method, comp=comp_np_arr)

    # Save the new calculated BS and MS to the Session store
    session_configs['bs_temp'] = bs_temp
    session[f'{token}:configurations'] = session_configs

    response['status'] = 'success'
    response.pop('message')
    response['data'] = {'bs_temp': bs_temp}

    return jsonify(response), 200


@configs_blueprint.route(rule='/configs/update/ms-bs', methods=['PUT'])
@token_required
def update_ms_bs(token):
    """If the user manually updates the MS and BS temperatures in the client,
    we receive those and update the session cache.

    Args:
        token: a valid JWT token.

    Returns:
        Only the 204 status code with no response body.
    """
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    post_data = request.get_json()
    if not post_data:
        return jsonify(response), 400

    # Let's do some validation of those arguments we really need.
    ms_temp = post_data.get('ms_temp', None)
    bs_temp = post_data.get('bs_temp', None)
    ms_rate_param = post_data.get('ms_rate_param', None)

    if not ms_rate_param:
        response['message'] = 'MS Rate Parameter temperature is required.'
        return jsonify(response), 400

    if not ms_temp:
        response['message'] = 'MS temperature is required.'
        return jsonify(response), 400

    if not bs_temp:
        response['message'] = 'BS temperature is required.'
        return jsonify(response), 400

    session_configs = session.get(f'{token}:configurations')
    if session_configs is None:
        response['message'] = 'No previous session configurations was set.'
        return jsonify(response), 404

    session_configs['ms_temp'] = ms_temp
    session_configs['ms_rate_param'] = ms_rate_param
    session_configs['bs_temp'] = bs_temp

    return jsonify({}), 204


@configs_blueprint.route(rule='/configs/auto/ae', methods=['GET'])
@token_required
def auto_calculate_ae(token):
    """This POST endpoint auto calculates the `Ae1` and `Ae3` as the user has
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
    session_configs['auto_calculate_ae'] = True

    comp_list = session.get(f'{token}:alloy')['compositions']
    comp_np_arr = SimConfig.get_compositions(comp_list)

    ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)

    # Save the new calculated Ae1 and Ae3 to the Session store
    session_configs['ae1_temp'] = ae1
    session_configs['ae3_temp'] = ae3
    session[f'{token}:configurations'] = session_configs

    response['status'] = 'success'
    response.pop('message')
    response['data'] = {'ae1_temp': ae1, 'ae3_temp': ae3}

    return jsonify(response), 200


@configs_blueprint.route(rule='/configs/update/ae', methods=['PUT'])
@token_required
def update_ae(token):
    """If the user manually updates the Ae1 and Ae3 temperatures in the client,
        we receive those and update the session cache.

    Args:
        token: a valid JWT token.

    Returns:
        Only the 204 status code with no response body.
    """
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    post_data = request.get_json()
    if not post_data:
        return jsonify(response), 400

    # Let's do some validation of those arguments we really need.
    ae1_temp = post_data.get('ae1_temp', None)
    ae3_temp = post_data.get('ae3_temp', None)

    if not ae1_temp:
        response['message'] = 'Ae1 temperature is required.'
        return jsonify(response), 400

    if not ae3_temp:
        response['message'] = 'Ae3 temperature is required.'
        return jsonify(response), 400

    session_configs = session.get(f'{token}:configurations')
    if session_configs is None:
        response['message'] = 'No previous session configurations was set.'
        return jsonify(response), 404

    session_configs['ae1_temp'] = ae1_temp
    session_configs['ae3_temp'] = ae3_temp

    return jsonify({}), 204
