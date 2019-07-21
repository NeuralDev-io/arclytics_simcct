# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# simulation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = '[Andrew Che <@codeninja55>]'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.17'
"""simulation.py: 

This module defines and implements the endpoints for CCT and TTT simulations.
"""

from flask import Blueprint, json, jsonify, session

from sim_app.middleware import token_required
from simulation.simconfiguration import SimConfiguration
from simulation.phasesimulation import PhaseSimulation

sim_blueprint = Blueprint('simulation', __name__)


@sim_blueprint.route('/simulate', methods=['GET'])
@token_required
def simulate(token):
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    # First we need to make sure they logged in and are in a current session
    session_configs = session.get(f'{token}:configurations')
    if session_configs is None:
        response['message'] = 'No previous session configurations was set.'
        return jsonify(response), 404

    session_alloy = session.get(f'{token}:alloy')
    if session_alloy is None:
        response['message'] = 'No previous session alloy was set.'
        return jsonify(response), 404

    if session_configs['ae1_temp'] < 0.0 or session_configs['ae3_temp'] < 0.0:
        response['message'] = 'Ae1 and Ae3 value cannot be less than 0.0.'
        return jsonify(response), 400

    # No we can do the calculations for CCT and TTT
    # FIXME(andrew@neuraldev.io): Note the auto calc is still being checked
    #  inside the SimConfiguration instance and recalculated. Find a better
    #  way to do this.
    sim_configs = SimConfiguration(
        configs=session.get(f'{token}:configurations'),
        compositions=session.get(f'{token}:alloy')['compositions']
    )

    sim = PhaseSimulation(sim_configs=sim_configs)
    sim.ttt()
    sim.cct()
    data = {
        'TTT': sim.plots_data.get_ttt_plot_data(),
        'CCT': sim.plots_data.get_cct_plot_data()
    }

    response['status'] = 'success'
    response['data'] = data
    response.pop('message')
    return jsonify(response), 200
