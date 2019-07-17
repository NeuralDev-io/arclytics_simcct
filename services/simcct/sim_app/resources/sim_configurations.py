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
    sess_store['grain_size_type'] = configs['grain_size_type']
    sess_store['grain_size'] = configs['grain_size']
    sess_store['nucleation_start'] = configs['nucleation_start']
    sess_store['nucleation_finish'] = configs['nucleation_finish']
    sess_store['start_temp'] = configs['start_temp']
    sess_store['cct_cooling_rate'] = configs['cct_cooling_rate']
    session[f'{token}:configurations'] = sess_store

    return jsonify({}), 204


@configs_blueprint.route(rule='/configs/method/update', methods=['POST'])
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
        not session_configs['auto_calculate_ms_bs']
        and not session_configs['auto_calculate_ae']
        and not session_configs['auto_calculate_xfe']
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

    if session_configs['auto_calculate_ms_bs']:
        # We need to convert them to our enums as required by the calculations.
        _transformation_method = Method.Li98
        if session_configs['transformation_method'] == 'Kirkaldy83':
            _transformation_method = Method.Kirkaldy83

        ms_temp = SimConfig.get_ms(_transformation_method, comp=comp_np_arr)
        bs_temp = SimConfig.get_bs(_transformation_method, comp=comp_np_arr)

        session_configs['auto_calculate_ms_bs'] = True
        session_configs['ms_temp'] = ms_temp
        session_configs['bs_temp'] = bs_temp
        response['data']['ms_temp'] = ms_temp
        response['data']['bs_temp'] = bs_temp

    if session_configs['auto_calculate_ae']:
        ae1, ae3 = SimConfig.calc_ae1_ae3(comp_np_arr)

        session_configs['auto_calculate_ae'] = True
        session_configs['ae1_temp'] = ae1
        session_configs['ae3_temp'] = ae3
        response['data']['ae1_temp'] = ae1
        response['data']['ae3_temp'] = ae3

    if session_configs['auto_calculate_xfe']:
        ae1_temp = np.float64(session_configs['ae1_temp'])
        if ae1_temp <= 0:
            response['message'] = (
                'Ae1 must be more than zero to find the '
                'Equilibrium Phase Fraction.'
            )
            return jsonify(response), 400

        cf = np.float32(session_configs['cf_value'])
        xfe, ceut = SimConfig.xfe_method2(comp_np_arr, ae1_temp, cf)

        session_configs['auto_calculate_xfe'] = True
        session_configs['xfe_value'] = xfe
        session_configs['ceut_value'] = ceut
        response['data']['xfe_value'] = xfe
        response['data']['ceut_value'] = ceut
        response['data']['cf_value'] = float(cf)

    session[f'{token}:configurations'] = session_configs

    response['status'] = 'success'
    return jsonify(response), 200


@configs_blueprint.route(rule='/configs/auto/ms-bs', methods=['POST'])
@token_required
def auto_calculate_ms_bs(token):
    """This POST endpoint auto calculates the `MS` and `BS` as the user has
    selected the auto calculate feature without the need for sending the
    compositions as they are already stored in the session store.

    Args:
        token: a valid JWT token.

    Returns:
        A response object with appropriate status and message strings as well
        as the calculated MS and BS temperatures.
    """

    # - If user has logged in first time, then this endpoint should not be
    #   possible as they have no compositions.
    #   * Need to do the validation checks for this.

    response = {'status': 'fail', 'message': 'Invalid payload.'}

    post_data = request.get_json()
    if not post_data:
        return jsonify(response), 400

    # Let's do some validation of those arguments we really need.
    _auto_calc_ms_bs = post_data.get('auto_calculate_ms_bs', None)
    _post_trans_method = post_data.get('transformation_method', None)

    if not _auto_calc_ms_bs:
        response['message'] = 'Post data auto calculate for MS or BS is false.'
        return jsonify(response), 400

    # Ensure we have the transformation method to use for MS/BS Calculations
    if not _post_trans_method:
        response['message'] = 'You must provide a transformation method.'
        return jsonify(response), 400

    # We need to convert them to our enums as required by the calculations.
    _transformation_method = Method.Li98
    if _post_trans_method == 'Kirkaldy83':
        _transformation_method = Method.Kirkaldy83

    session_configs = session.get(f'{token}:configurations')

    session_configs['auto_calculate_ms_bs'] = True
    session_configs['transformation_method'] = _transformation_method.name

    comp_list = session.get(f'{token}:alloy')['compositions']
    comp_np_arr = SimConfig.get_compositions(comp_list)

    ms_temp = SimConfig.get_ms(method=_transformation_method, comp=comp_np_arr)
    bs_temp = SimConfig.get_bs(method=_transformation_method, comp=comp_np_arr)

    if ms_temp == -1 or bs_temp == -1:
        response['message'] = (
            'Something went wrong with the MS and BS '
            'calculations'
        )
        return jsonify(response), 418

    # Save the new calculated BS and MS to the Session store
    session_configs['ms_temp'] = ms_temp
    session_configs['bs_temp'] = bs_temp
    session[f'{token}:configurations'] = session_configs

    response['status'] = 'success'
    response.pop('message')
    response['data'] = {'ms_temp': ms_temp, 'bs_temp': bs_temp}

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
    session_configs['bs_temp'] = bs_temp

    return jsonify({}), 204


@configs_blueprint.route(rule='/configs/auto/ae', methods=['POST'])
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

    # Get the post data
    post_data = request.get_json()
    if not post_data:
        return jsonify(response), 400

    # Let's do some validation of those arguments we really need.
    _auto_calc_ae = post_data.get('auto_calculate_ae', None)

    if not _auto_calc_ae:
        response['message'] = 'Auto calculate for Austenite is false.'
        return jsonify(response), 400

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


@configs_blueprint.route(rule='/configs/auto/xfe', methods=['POST'])
@token_required
def auto_calculate_xfe(token):
    """This POST endpoint auto calculates the `Xfe` and `Ceut` as the user has
    selected the auto calculate feature without the need for sending the
    compositions as they are already stored in the session store.

    Args:
        token: a valid JWT token.

    Returns:
        A response object with appropriate status and message strings as
        well as the calculated Xfe, Ceut and Cf values.
    """
    # - If user has logged in first time, then this endpoint should not be
    #   possible as they have no compositions.
    #   * Need to do the validation checks for this.

    response = {'status': 'fail', 'message': 'Invalid payload.'}

    post_data = request.get_json()
    if not post_data:
        return jsonify(response), 400

    # Let's do some validation of those arguments we really need.
    _auto_calc_xfe = post_data.get('auto_calculate_xfe', None)

    if not _auto_calc_xfe:
        response['message'] = 'Auto calculate for Equilibrium Phase is false.'
        return jsonify(response), 400

    session_configs = session.get(f'{token}:configurations')
    session_configs['auto_calculate_xfe'] = True

    comp_list = session.get(f'{token}:alloy')['compositions']
    comp_np_arr = SimConfig.get_compositions(comp_list)

    # TODO(andrew@neuraldev.io): We need to do an Ae check here because this
    #  requires the use of Ae1 to get ceut. No ae_check bool is currently set
    #  in the Session store.
    ae1_temp = np.float64(session_configs['ae1_temp'])
    if ae1_temp <= 0:
        response['message'] = (
            'Ae1 must be more than zero to find the '
            'Equilibrium Phase Fraction.'
        )
        return jsonify(response), 400

    cf = np.float32(session_configs['cf_value'])

    xfe, ceut = SimConfig.xfe_method2(comp_np_arr, ae1_temp, cf)

    # Save the new calculated Xfe and Ceut to the Session store
    session_configs['xfe_value'] = xfe
    session_configs['ceut_value'] = ceut
    session[f'{token}:configurations'] = session_configs

    response['status'] = 'success'
    response.pop('message')
    response['data'] = {'xfe_value': xfe, 'cf_value': cf, 'ceut_value': ceut}

    return jsonify(response), 200


@configs_blueprint.route(rule='/configs/update/xfe', methods=['PUT'])
@token_required
def update_xfe(token):
    """If the user manually updates the Xfe, Cf and Ceut temperatures in the
    client, we receive those and update the session cache.

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
    xfe_value = post_data.get('xfe_value', None)
    cf_value = post_data.get('cf_value', None)
    ceut_value = post_data.get('ceut_value', None)

    if not xfe_value:
        response['message'] = 'Xfe value is required.'
        return jsonify(response), 400

    if not cf_value:
        response['message'] = 'Cf value is required.'
        return jsonify(response), 400

    if not ceut_value:
        response['message'] = 'Ceut value is required.'
        return jsonify(response), 400

    session_configs = session.get(f'{token}:configurations')
    if session_configs is None:
        response['message'] = 'No previous session configurations was set.'
        return jsonify(response), 404

    session_configs['xfe_value'] = xfe_value
    session_configs['cf_value'] = cf_value
    session_configs['ceut_value'] = ceut_value

    return jsonify({}), 204
