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
__version__ = '2.0.0'
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


# noinspection PyMethodMayBeStatic
class Simulation(Resource):
    """
    This Resource is used to call the main simulation algorithm which uses
    the `arc_simulation.simulation` package to run the Algorithm provided by
    Dr. Bendeich and optimized by the NeuralDev team.
    """

    method_decorators = {'post': [authenticate_user_cookie_restful]}

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

        if not alloy_store.get('alloy_option') in {'single', 'mix'}:
            response.update(
                {'message': 'Alloy option must be one of ["single" | "mix"]'}
            )
            return response, 400

        if not configurations:
            response.update({'message': 'Configurations required.'})
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
        except ZeroDivisionError as e:
            # We know that a zero division error can occur during the
            # calculations so we need to catch it and return to the client
            # to deal with it.
            response['error'] = str(e)
            response['message'] = 'Zero division error.'
            logger.exception(response['message'], exc_info=True)
            apm.capture_exception()
            return response, 500
        except Exception as e:
            response['error'] = str(e)
            response['message'] = 'Exception.'
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

        logger.debug('Simulation Total Time: {}'.format(finish - start))

        # Just overwrite the response instead of changing it.
        return {'status': 'success', 'data': data}, 200


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
