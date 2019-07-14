# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# sim_configurations.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
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

from simulation.simconfiguration import SimConfiguration
from simulation.utilities import Method

configurations_blueprint = Blueprint('configurations', __name__)


@configurations_blueprint.route(
    rule='/configs/method/update', methods=['POST']
)
def method_change():
    # Just change the session store method.
    pass


@configurations_blueprint.route(rule='/configs/comp/update', methods=['POST'])
def composition_change():
    # - Combined method for changing the sessions compositions
    # - Check if the compositions are valid
    # -
    # - Check if auto calculate is selected for ms_bs, ae, or xfe
    # - Compute for the calculations that auto_calculate_x is True
    # - Save the value to session store.
    # - Return the values

    pass


@configurations_blueprint.route(rule='/configs/auto/ms-bs', methods=['POST'])
def auto_calculate_ms_bs():
    # - If user has logged in first time, then this endpoint should not be
    #   possible as they have no compositions.
    #   * Need to do the validation checks for this.
    #
    # - If they have a session store of compositions, use that.
    # - Check if the compositions has valid elements required.
    # - Compute the MS and BS
    # - Update the MS and BS for session store
    # - Return the values

    # Get the post data
    post_data = request.get_json()

    response = {'status': 'fail', 'message': 'Invalid payload.'}

    if not post_data:
        return jsonify(response), 400

    # Extract the needed request data
    auth_header = request.headers.get('Authorization', None)

    if not auth_header:
        response['message'] = 'You must provide a valid Authorization header.'
        return jsonify(response), 400

    token = auth_header.split(' ')[1]

    # Let's do some validation of those arguments we really need.
    _auto_calc_ms_bs = post_data['auto_calculate_ms_bs']
    _post_trans_method = post_data['transformation_method']

    # Ensure we have the transformation method to use for MS/BS Calculations
    if not _post_trans_method:
        response['message'] = 'You must provide a transformation method.'
        return jsonify(response), 400

    # We need to convert them to our enums as required by the calculations.
    _transformation_method = None
    if _post_trans_method == 'Li98':
        _transformation_method = Method.Li98
    elif _post_trans_method == 'Kirkaldy83':
        _transformation_method = Method.Kirkaldy83

    session_configs = session.get(f'{token}:configurations')

    if not _auto_calc_ms_bs:
        response['message'] = 'Auto calculate for MS or BS is false.'
        return jsonify(response), 400

    session_configs['auto_calculate_ms_bs'] = True

    comp_list = session.get(f'{token}:compositions')['comp']
    comp_np_arr = SimConfiguration.get_compositions(comp_list)

    ms_temp = SimConfiguration.get_ms(
        method=_transformation_method, comp=comp_np_arr
    )
    bs_temp = SimConfiguration.get_bs(
        method=_transformation_method, comp=comp_np_arr
    )

    if ms_temp == -1 or bs_temp == -1:
        response['message'] = (
            'Something went wrong with the MS and BS '
            'calculations'
        )
        return jsonify(response), 400

    # Save the new calculated BS and MS to the Session store
    session_configs['ms_temp'] = ms_temp
    session_configs['bs_temp'] = bs_temp

    response['status'] = 'success'
    response.pop('message')
    response['data'] = {'ms_temp': ms_temp, 'bs_temp': bs_temp}

    return jsonify(response), 200


@configurations_blueprint.route(rule='/configs/auto/ae', methods=['POST'])
def auto_calculate_ae():
    # - If user has logged in first time, then this endpoint should not be
    #   possible as they have no compositions.
    #   * Need to do the validation checks for this.
    #
    # - If they have a session store of compositions, use that.
    # - Check if the compositions has valid elements required.
    # - Compute the xfe (and others) values
    # - Update the xfe (and others) values for session store
    # - Return the values

    # Get the post data
    post_data = request.get_json()

    response = {'status': 'fail', 'message': 'Invalid payload.'}

    if not post_data:
        return jsonify(response), 400

    # Extract the needed request data
    auth_header = request.headers.get('Authorization', None)

    if not auth_header:
        response['message'] = 'You must provide a valid Authorization header.'
        return jsonify(response), 400

    token = auth_header.split(' ')[1]

    # Let's do some validation of those arguments we really need.
    _auto_calc_ae = post_data['auto_calculate_ae']

    session_configs = session.get(f'{token}:configurations')

    if not _auto_calc_ae:
        response['message'] = 'Auto calculate for Austenite is false.'
        return jsonify(response), 400

    session_configs['auto_calculate_ae'] = True

    comp_list = session.get(f'{token}:compositions')['comp']
    comp_np_arr = SimConfiguration.get_compositions(comp_list)

    ae1, ae3 = SimConfiguration.calc_ae1_ae3(comp_np_arr)

    # Save the new calculated Ae1 and Ae3 to the Session store
    session_configs['ae1_temp'] = ae1
    session_configs['ae3_temp'] = ae3

    response['status'] = 'success'
    response.pop('message')
    response['data'] = {'ae1_temp': ae1, 'ae3_temp': ae3}

    return jsonify(response), 200


@configurations_blueprint.route(rule='/configs/auto/xfe', methods=['POST'])
def auto_calculate_xfe():
    # - If user has logged in first time, then this endpoint should not be
    #   possible as they have no compositions.
    #   * Need to do the validation checks for this.
    #
    # - If they have a session store of compositions, use that.
    # - Check if the compositions has valid elements required.
    # - Compute the Ae1 and Ae3
    # - Update the Ae1 and Ae3 for session store
    # - Return the values

    # Get the post data
    post_data = request.get_json()

    response = {'status': 'fail', 'message': 'Invalid payload.'}

    if not post_data:
        return jsonify(response), 400

    # Extract the needed request data
    auth_header = request.headers.get('Authorization', None)

    if not auth_header:
        response['message'] = 'You must provide a valid Authorization header.'
        return jsonify(response), 400

    token = auth_header.split(' ')[1]

    # Let's do some validation of those arguments we really need.
    _auto_calc_xfe = post_data['auto_calculate_xfe']

    if not _auto_calc_xfe:
        response['message'] = 'Auto calculate for Equilibrium Phase is false.'
        return jsonify(response), 400

    session_configs = session.get(f'{token}:configurations')
    session_configs['auto_calculate_xfe'] = True

    comp_list = session.get(f'{token}:compositions')['comp']
    comp_np_arr = SimConfiguration.get_compositions(comp_list)

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

    xfe, ceut = SimConfiguration.xfe_method2(comp_np_arr, ae1_temp, cf)

    # Save the new calculated Xfe and Ceut to the Session store
    session_configs['xfe_value'] = xfe
    session_configs['ceut_value'] = ceut

    response['status'] = 'success'
    response.pop('message')
    response['data'] = {'xfe_value': xfe, 'cf_value': cf, 'ceut_value': ceut}

    return jsonify(response), 200
