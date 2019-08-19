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

import time
from threading import Thread

from flask import Blueprint
from flask_restful import Resource

from sim_app.extensions import api
from sim_app.middleware import token_and_session_required
from sim_app.sim_session import SimSessionService
from simulation.simconfiguration import SimConfiguration
from simulation.phasesimulation import PhaseSimulation
from simulation.utilities import ConfigurationError, SimulationError
from sim_app.schemas import ConfigurationsSchema, AlloyStoreSchema
from logger.arc_logger import AppLogger

logger = AppLogger(__name__)

sim_blueprint = Blueprint('simulation', __name__)


class Simulation(Resource):

    method_decorators = {'get': [token_and_session_required]}

    # noinspection PyMethodMayBeStatic
    def get(self, _, session_key):
        response = {'status': 'fail'}

        # First we need to make sure they logged in and are in a current session
        sid, session_store = SimSessionService().load_session(session_key)

        logger.debug('Session Store')
        logger.debug(session_store)

        if sid is None:
            response['errors'] = session_store
            response['message'] = 'Unable to load session from Redis.'
            return response, 401

        if not session_store:
            response['message'] = 'Unable to retrieve data from Redis.'
            return response, 500

        session_configs = session_store.get('configurations')
        if session_configs is None:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        configs = ConfigurationsSchema().load(session_configs)

        # By default, the session alloy store is single and parent but the
        # parent alloy is set to none.
        sess_alloy_store = session_store.get('alloy_store')
        if (
            not sess_alloy_store['alloys']['parent']
            and not sess_alloy_store['alloys']['weld']
            and not sess_alloy_store['alloys']['mix']
        ) or not sess_alloy_store:
            response['message'] = 'No previous session alloy was set.'
            return response, 404

        alloy_store = AlloyStoreSchema().load(sess_alloy_store)

        # We need to validate ae1, ae3, ms, and bs temperatures because if we do
        # the calculations for CCT/TTT will cause many problems.
        if (not configs['ae1_temp'] > 0.0 or not configs['ae3_temp'] > 0.0):
            response['message'] = 'Ae1 and Ae3 value cannot be less than 0.0.'
            return response, 400

        if (not configs['ms_temp'] > 0.0 or not configs['bs_temp'] > 0.0):
            response['message'] = 'MS and BS value cannot be less than 0.0.'
            return response, 400

        # TODO(andrew@neuraldev.io): Implement the other options
        alloy = None
        if alloy_store.get('alloy_option') == 'single':
            alloy = alloy_store['alloys']['parent']

        # No we can do the calculations for CCT and TTT
        sim_configs = SimConfiguration(
            configs=configs, compositions=alloy['compositions']
        )

        logger.debug('Simulation Configurations')
        logger.pprint(sim_configs.__dict__)

        try:
            sim = PhaseSimulation(sim_configs=sim_configs)
        except ConfigurationError as e:
            response['errors'] = str(e)
            response['message'] = 'Configuration error.'
            return response, 400

        # TODO(andrew@neuraldev.io): add a Division by Zero check here or find
        #  out what is causing it and raise a custom Exception.

        # TIMER START
        start = time.time()
        # Running these in parallel with threading
        ttt_process = Thread(sim.ttt())
        cct_process = Thread(sim.cct())
        user_cooling_process = Thread(sim.user_cooling_curve())
        # Starting CCT first because it takes longer.
        cct_process.start()
        ttt_process.start()
        user_cooling_process.start()

        # Now we stop the main thread to wait for them to finish.
        user_cooling_process.join()
        user_cooling_time = time.time()
        ttt_process.join()
        ttt_time = time.time()
        cct_process.join()
        total_time = time.time()

        # TODO(andrew@neuraldev.io): We need to store the results in the Session
        #  store at some point as well.

        logger.debug(
            f'User Cooling Curve Simulation Time: {user_cooling_time - start}'
        )
        logger.debug(f'TTT Simulation Time: {ttt_time - start}')
        logger.debug(f'CCT Simulation Time: {total_time - start}')
        logger.debug('Total Simulation Time: {}'.format(total_time - start))

        data = {
            'TTT': sim.plots_data.get_ttt_plot_data(),
            'CCT': sim.plots_data.get_cct_plot_data(),
            'user_cooling_curve': sim.plots_data.get_user_cool_plot_data()
        }

        response['status'] = 'success'
        response['data'] = data
        return response, 200


api.add_resource(Simulation, '/simulate')
