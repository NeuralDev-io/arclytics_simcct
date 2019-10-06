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

from flask import Blueprint, request
from flask_restful import Resource
from marshmallow import ValidationError

from arc_logging import AppLogger
from sim_api.extensions import api, apm
from sim_api.extensions.utilities import (
    DuplicateElementError, ElementInvalid, ElementSymbolInvalid,
    ElementWeightInvalid, MissingElementError
)
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.schemas import AlloyStoreSchema, ConfigurationsSchema
from simulation.phasesimulation import PhaseSimulation
from simulation.simconfiguration import SimConfiguration
from simulation.utilities import ConfigurationError, SimulationError

logger = AppLogger(__name__)

sim_blueprint = Blueprint('simulation', __name__)


class Simulation(Resource):

    method_decorators = {'post': [authenticate_user_cookie_restful]}

    # noinspection PyMethodMayBeStatic
    def post(self, _):
        response = {'status': 'fail'}

        post_data = request.get_json()

        if not post_data:
            return response, 400

        alloy_store = post_data.get('alloy_store', None)
        configurations = post_data.get('configurations', None)

        # ===== # Validation Checks of POST BODY # ===== #
        if not alloy_store:
            response.update({'message': 'Alloy store required.'})
            return response, 400

        # We need to validate the Configurations matches our expected schema
        try:
            valid_configs = ConfigurationsSchema().load(configurations)
        except ValidationError as e:
            # All other validation errors
            response['error'] = str(e.messages)
            response['message'] = 'Model schema validation error.'
            apm.capture_exception()
            return response, 400

        # We need to validate the Alloy Store that matches our expected schema
        try:
            valid_store = AlloyStoreSchema().load(alloy_store)
        except ElementSymbolInvalid as e:
            # Where the symbol used for the element is not valid meaning it
            # does not exist in a Periodic Table.
            response['error'] = str(e)
            response['message'] = 'Invalid element symbol error.'
            return response, 400
        except ElementInvalid as e:
            # If no "symbol" or "weight" passed as an Element object.
            response['error'] = str(e)
            response['message'] = 'Invalid element error.'
            return response, 400
        except ElementWeightInvalid as e:
            # If `C` weight is more than 0.8
            response['error'] = str(e)
            response['message'] = 'Invalid element weight error.'
            return response, 400
        except MissingElementError as e:
            # Where the alloy is missing elements we expect to always be
            # available as they are required downstream in the algorithm.
            response['error'] = str(e)
            response['message'] = 'Missing element error.'
            return response, 400
        except DuplicateElementError as e:
            # One of the alloys contains two or more elements with the same
            # chemical symbol.
            response['error'] = str(e)
            response['message'] = 'Alloy contains a duplicate element.'
            return response, 400
        except ValidationError as e:
            # All other validation errors
            response['error'] = str(e.messages)
            response['message'] = 'Model schema validation error.'
            apm.capture_exception()
            return response, 400

        alloy = None
        if alloy_store.get('alloy_option') == 'single':
            alloy = alloy_store['alloys']['parent']
        elif valid_store['alloy_option'] == 'mix':
            # DECISION:
            # We will not implement this as it adds too much complexity to
            # the logical path of the system state. This was not a core
            # requirement and Dr. Bendeich often said he did not want this
            # implemented at all.
            response.update({'message': 'Mix option not allowed.'})
            return response, 400

        # TIMER START
        start = time.time()

        # Here we need to create a `SimConfiguration` instance that does some
        # more checks of the values and converts the compositions to a
        # structured `numpy.ndarray` that the simulation package users.
        # It also prepares a Integral matrix for the simulation algorithm.
        try:
            sim_configs = SimConfiguration(
                configs=valid_configs, compositions=alloy['compositions']
            )
        except ValueError as e:
            # We know that at certain times, the algorithms cannot calculate
            # the integral matrix because there can be a Math Domain Error
            # with trying to a log of a negative number. This mostly occurs
            # when Carbon weight content is less than 0.8 in certain cases.
            # Whilst we have already checked for this in validating the alloy,
            # it is possible the error might occur again for other weight
            # values so we want to catch it appropriately and let the frontend
            # know that we cannot do the calculation.
            msg = 'ValueError in preparing SimConfiguration instance.'
            logger.exception(msg)
            apm.capture_exception(msg)
            response.update({'message': msg, 'error': str(e)})
            return response, 500
        except ConfigurationError as e:
            # Both of these are raised manually if any error occurs that
            # we have specifically caught.
            response['error'] = str(e)
            response['message'] = 'Configuration error.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 400
        except Exception as e:
            # This is to make sure the client knows there has been some
            # calculation error which is potentially something to do with
            # our back-end code or, more likely, a value in the alloy
            # composition that does not work with this algorithm.
            msg = 'SimConfiguration intialisation error.'
            logger.exception(msg)
            apm.capture_exception(msg)
            response.update({'message': msg, 'error': str(e)})
            return response, 500

        try:
            sim = PhaseSimulation(sim_configs=sim_configs)
        except ConfigurationError as e:
            # Both of these are raised manually if any error occurs that
            # we have specifically caught.
            response['error'] = str(e)
            response['message'] = 'Configuration error.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 400
        except SimulationError as e:
            # Both of these are raised manually if any error occurs that
            # we have specifically caught.
            response['error'] = str(e)
            response['message'] = 'Simulation error.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 400
        except Exception as e:
            # This is to make sure the client knows there has been some
            # calculation error which is potentially something to do with
            # our back-end code or, more likely, a value in the alloy
            # composition that does not work with this algorithm.
            msg = 'PhaseSimulation intialisation error.'
            logger.exception(msg)
            apm.capture_exception(msg)
            response.update({'message': msg, 'error': str(e)})
            return response, 500

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
            # We know that a zero division error can occur during the
            # calculations so we need to catch it and return to the client
            # to deal with it.
            response['error'] = str(e)
            response['message'] = 'Zero division error.'
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

        # Just overwrite the response instead of changing it.
        response = {'status': 'success', 'data': data}
        return response, 200


api.add_resource(Simulation, '/v1/sim/simulate')
