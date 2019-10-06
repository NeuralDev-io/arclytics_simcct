# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# simulation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__credits__ = ['Dr. Philip Bendeich', 'Dr. Ondrej Muransky']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.17'
"""simulation.py: 

This module defines and implements the endpoints for CCT and TTT simulations.
"""

import time
from os import environ as env
# import threading
import concurrent.futures

from flask import Blueprint, json
from flask_restful import Resource
from arc_logging import AppLogger

from sim_api.extensions import api, apm
from sim_api.extensions.SimSession import SimSessionService
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.schemas import AlloyStoreSchema, ConfigurationsSchema
from simulation.phasesimulation import PhaseSimulation
from simulation.simconfiguration import SimConfiguration
from simulation.utilities import ConfigurationError, SimulationError

logger = AppLogger(__name__)

sim_blueprint = Blueprint('simulation', __name__)


class Simulation(Resource):

    method_decorators = {'get': [authenticate_user_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def get(self, _):
        response = {'status': 'fail'}

        # First we need to make sure they logged in and are in a current session
        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            logger.error(response['message'])
            apm.capture_message(response['message'])
            return response, 500

        log_msg = json.dumps(
            {
                'message': 'Session Store',
                **session_store['configurations']
            }
        )
        logger.debug(log_msg)

        session_configs = session_store.get('configurations')
        if not session_configs:
            response['message'] = 'No previous session configurations was set.'
            return response, 404

        configs = ConfigurationsSchema().load(session_configs)

        # If the configs are considered valid, then they must have run a
        # previous Simulation successfully.
        # if configs.get('is_valid', False):
        #     response['status'] = 'success'
        #     response['data'] = session_store['results']
        #     return response, 200

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
        if not configs['ae1_temp'] > 0.0 or not configs['ae3_temp'] > 0.0:
            response['message'] = 'Ae1 and Ae3 value cannot be less than 0.0.'
            return response, 400

        if not configs['ms_temp'] > 0.0 or not configs['bs_temp'] > 0.0:
            response['message'] = 'MS and BS value cannot be less than 0.0.'
            return response, 400

        alloy = None
        if alloy_store.get('alloy_option') == 'single':
            alloy = alloy_store['alloys']['parent']
        else:
            # DECISION:
            # We will not implement this as it adds too much complexity to
            # the logical path of the system state. This was not a core
            # requirement and Dr. Bendeich often said he did not want this
            # implemented at all.
            pass

        # dask_client = Client(
        #     address=env.get('DASK_SCHEDULER_ADDRESS'), processes=False
        # )

        # TIMER START
        start = time.time()

        # No we can do the calculations for CCT and TTT
        sim_configs = SimConfiguration(
            configs=configs, compositions=alloy['compositions']
        )

        # stop_configs_time = time.time()
        # sim_configs_time = stop_configs_time - start

        # TODO(andrew@neuraldev.io) Validate for Carbon < 0.7

        try:
            sim = PhaseSimulation(sim_configs=sim_configs)
        except ConfigurationError as e:
            response['error'] = str(e)
            response['message'] = 'Configuration error.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 400
        except SimulationError as e:
            response['error'] = str(e)
            response['message'] = 'Simulation error.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 400

        log_msg = json.dumps(
            {
                'message': 'SimConfigs Instance',
                **sim.configs.__dict__
            }
        )
        logger.debug(log_msg)

        # Now we do the simulation part but catch all exceptions and return it
        try:
            ttt_results = sim.ttt()
            user_cooling_curve_results = sim.user_cooling_profile()
            cct_results = sim.cct()
            # with concurrent.futures.ThreadPoolExecutor() as executor:
            #     ttt_future = executor.submit(sim.ttt)
            #     user_future = executor.submit(sim.user_cooling_profile)
            #     cct_future = executor.submit(sim.cct)

            # We send the three simulation functions off to a Dask Worker to
            # compute as a background thread.
            # cct_future = dask_client.submit(sim.cct)
            # ttt_future = dask_client.submit(sim.ttt)
            # user_cc_future = dask_client.submit(sim.user_cooling_profile)
        except ZeroDivisionError as e:
            response['error'] = str(e)
            response['message'] = 'Zero Division Error.'
            response['configs'] = sim.configs.__dict__
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500
        except Exception as e:
            response['error'] = str(e)
            response['message'] = 'Exception.'
            response['configs'] = sim.configs.__dict__
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500

        # Converting the TTT and CCT `numpy.ndarray` will raise an
        # AssertionError if the shape of the ndarray is not correct.
        try:
            data = {
                'TTT': ttt_results,
                'CCT': cct_results,
                'USER': user_cooling_curve_results
            }
            # data = {
            #     'TTT': ttt_future.result(),
            #     'CCT': cct_future.result(),
            #     'USER': user_future.result()
            # }
        except AssertionError as e:
            response['error'] = str(e)
            response['message'] = 'Assertion error building response data.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500

        finish = time.time()

        # logger.debug(f'Configurations Setup Time: {sim_configs_time}')
        # logger.debug(f'Integral Matrix Time: {integral_mat_time}')
        # logger.debug(f'Total Simulation Time: {simulation_time}')
        logger.debug('Simulation Total Time: {}'.format(finish - start))

        # If a valid simulation has been run, the configurations are now valid.
        session_store['configurations']['is_valid'] = True
        session_store['results'] = data
        SimSessionService().save_session(session_store)

        response['status'] = 'success'
        response['data'] = data
        return response, 200


class Ae3Equilibrium(Resource):

    method_decorators = {'get': [authenticate_user_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def get(self, _):
        response = {'status': 'fail'}

        # First we need to make sure they logged in and are in a current session
        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            logger.error(response['message'])
            apm.capture_message(response['message'])
            return response, 500

        session_configs = session_store.get('configurations')
        if not session_configs:
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
        if not configs['ae1_temp'] > 0.0 or not configs['ae3_temp'] > 0.0:
            response['message'] = 'Ae1 and Ae3 value cannot be less than 0.0.'
            return response, 400

        if not configs['ms_temp'] > 0.0 or not configs['bs_temp'] > 0.0:
            response['message'] = 'MS and BS value cannot be less than 0.0.'
            return response, 400

        alloy = None
        if alloy_store.get('alloy_option') == 'single':
            alloy = alloy_store['alloys']['parent']
        else:
            # DECISION:
            # We will not implement this as it adds too much complexity to
            # the logical path of the system state. This was not a core
            # requirement and Dr. Bendeich often said he did not want this
            # implemented at all.
            pass

        # Create a configuration object based off the session config and comp
        # so we can perform ae3 equilibrium calculations on it.
        sim_configs = SimConfiguration(
            configs=configs, compositions=alloy['compositions']
        )

        # Call the xfe_method2 function to calculate the ae3 equilibrium
        # graph data.
        try:
            # xfe is ferrite_phase_frac and ceut is eutectic_composition_carbon
            results_plot, results_mat, xfe, ceut = \
                sim_configs.xfe_method2(
                    comp_list=alloy['compositions'], ae1=configs['ae1_temp'],
                    plot=True
                )
        except ZeroDivisionError as e:
            response['error'] = str(e)
            response['message'] = 'Zero Division Error.'
            response['configs'] = sim_configs.__dict__
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500
        # TODO(davidmatthews1004@gmail.com) Find if its possible for any other
        #  kind of exceptions to occur and handle them appropriately.
        except Exception as e:
            response['error'] = str(e)
            response['message'] = 'Exception.'
            response['configs'] = sim_configs.__dict__
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500

        try:
            data = {
                'ferrite_phase_frac': xfe,
                'eutectic_composition_carbon': ceut,
                'results_plot': results_plot
                # 'results_mat': results_mat.tolist()
            }
        # Not sure if this is possible for the ae3 equilibrium results but
        # putting it in just in case.
        # This is to try and catch the following:
        # Converting the TTT and CCT `numpy.ndarray` will raise an
        # AssertionError if the shape of the ndarray is not correct.
        except AssertionError as e:
            response['error'] = str(e)
            response['message'] = 'Assertion error building response data.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500

        response['status'] = 'success'
        response['data'] = data
        return response, 200


api.add_resource(Simulation, '/v1/sim/simulate')
api.add_resource(Ae3Equilibrium, '/v1/sim/ae3equilibrium')
