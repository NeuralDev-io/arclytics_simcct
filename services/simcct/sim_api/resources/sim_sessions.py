# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# sim_sessions.py
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
__status__ = 'development'
__date__ = '2019.10.03'
"""sim_sessions.py: 

This module deals with all the endpoints for updating the session with the 
user's current configuration and alloy_store 
"""

from flask import Blueprint, request
from flask_restful import Resource

from arc_logging import AppLogger
from sim_api.extensions import api, apm
from sim_api.extensions.SimSession import SimSessionService
from sim_api.middleware import authenticate_user_cookie_restful

sessions_blueprint = Blueprint('sim_sessions', __name__)

logger = AppLogger(__name__)


class SimulationSession(Resource):
    method_decorators = {'put': [authenticate_user_cookie_restful]}

    def put(self, _):
        """This PUT endpoint updates the redis session with the user's current
        simulation configurations and alloy_store information

        :param user: The user object returned by the authenticate middleware
        function
        :return:
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        put_data = request.get_json()
        if not put_data:
            return response, 400

        configuration = put_data.get('configuration', None)
        if not configuration:
            response['message'] = 'No configuration provided.'
            return response, 400

        if not isinstance(configuration, dict):
            response['message'] = 'Configuration must be of type dict.'
            return response, 400

        alloy_store = put_data.get('alloy_store', None)
        if not alloy_store:
            response['message'] = 'No alloy store provided.'
            return response, 400

        if not isinstance(alloy_store, dict):
            response['message'] = 'Alloy store must be of type dict.'
            return response, 400

        session_store = SimSessionService().load_session()

        if isinstance(session_store, str):
            response['message'] = session_store
            logger.error(response['message'])
            apm.capture_message(response['message'])
            return response, 500

        session_store['configuration'] = configuration
        session_store['alloy_store'] = alloy_store

        SimSessionService().save_session(session_store)
        response['status'] = 'success'
        response['message'] = 'Session updated.'
        return response, 200


class ResetSimulationSetting(Resource):
    method_decorators = {'delete': [authenticate_user_cookie_restful]}

    def delete(self, _):
        """This DELETE method resets the redis session to be empty."""
        session_store = SimSessionService().load_session()
        session_store['configuration'] = None
        session_store['alloy_store'] = None
        session_store['simulation_results'] = None
        session_store = SimSessionService().save_session(session_store)

        response = {'status': 'success', 'message': 'Session cleared.'}
        return response, 200


api.add_resource(SimulationSession, '/v1/sim/session/update')
api.add_resource(ResetSimulationSetting, '/v1/sim/session/reset')
