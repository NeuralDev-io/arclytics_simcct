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

from threading import Thread

from flask import Blueprint, session
from flask_restful import Resource

from sim_app.extensions import api
from sim_app.middleware import token_required_restful
from simulation.simconfiguration import SimConfiguration
from simulation.phasesimulation import PhaseSimulation

sim_blueprint = Blueprint('simulation', __name__)


class Simulation(Resource):

    method_decorators = {'get': [token_required_restful]}

    def get(self, token):
        response = {'status': 'fail'}

        # First we need to make sure they logged in and are in a current session
        session_configs = session.get(f'{token}:configurations')
        if session_configs is None:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        # By default, the session alloy store is single and parent but the
        # parent alloy is set to none.
        sess_alloy_store = session.get(f'{token}:alloy_store')
        if (
            not sess_alloy_store['alloys']['parent']
            and not sess_alloy_store['alloys']['weld']
            and not sess_alloy_store['alloys']['mix']
        ) or not sess_alloy_store:
            response['message'] = 'No previous session alloy was set.'
            return response, 404

        # We need to validate ae1, ae3, ms, and bs temperatures because if we do
        # the calculations for CCT/TTT will cause many problems.
        if (
            not session_configs['ae1_temp'] > 0.0
            or not session_configs['ae3_temp'] > 0.0
        ):
            response['message'] = 'Ae1 and Ae3 value cannot be less than 0.0.'
            return response, 400

        if (
            not session_configs['ms_temp'] > 0.0
            or not session_configs['bs_temp'] > 0.0
        ):
            response['message'] = 'MS and BS value cannot be less than 0.0.'
            return response, 400

        # TODO(andrew@neuraldev.io): Implement the other options
        alloy = None
        if sess_alloy_store.get('alloy_option') == 'single':
            alloy = sess_alloy_store['alloys']['parent']

        # No we can do the calculations for CCT and TTT
        sim_configs = SimConfiguration(
            configs=session_configs, compositions=alloy['compositions']
        )

        sim = PhaseSimulation(sim_configs=sim_configs)

        # Running these in parallel with threading
        ttt_process = Thread(sim.ttt())
        cct_process = Thread(sim.cct())
        # Starting CCT first because it takes longer.
        cct_process.start()
        ttt_process.start()

        # Now we stop the main thread to wait for them to finish.
        ttt_process.join()
        cct_process.join()

        data = {
            'TTT': sim.plots_data.get_ttt_plot_data(),
            'CCT': sim.plots_data.get_cct_plot_data()
        }

        response['status'] = 'success'
        response['data'] = data
        return response, 200


api.add_resource(Simulation, '/simulate')
