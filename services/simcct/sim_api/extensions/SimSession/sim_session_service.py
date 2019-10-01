# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# sim_session_service.py
#
# Attributions:
# [1] https://gist.github.com/wushaobo/52be20bc801243dddf52a8be4c13179a
# [2] https://github.com/mrichman/flask-redis
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.08.08'
"""sim_session_service.py: 

This module defines the class to create a session for simulation data that is 
stored in the user's Flask Session instance. This service makes it simpler 
to do the regular actions of `new_session`, `save_session`, and `load_session`.
"""

import json
from typing import Union

from flask import session

from sim_api.extensions import JSONEncoder, apm
from sim_api.models import User

from arc_logging import AppLogger

logger = AppLogger(__name__)


class SimSessionService(object):
    """The interface defines how a service for Simulation Session works."""
    SESSION_PREFIX = 'simulation'

    def new_session(self, user: User) -> None:
        if user.last_configuration is not None:
            configs = user.last_configuration
        else:
            # These are based of defaults in the front-end as agreed to by
            # Andrew and Dalton.
            configs = {
                'is_valid': False,
                'method': 'Li98',
                'grain_size': 8.0,
                'nucleation_start': 1.0,
                'nucleation_finish': 99.90,
                'auto_calculate_ms': True,
                'ms_temp': 0.0,
                'ms_rate_param': 0.0,
                'auto_calculate_bs': True,
                'bs_temp': 0.0,
                'auto_calculate_ae': True,
                'ae1_temp': 0.0,
                'ae3_temp': 0.0,
                'start_temp': 900,
                'cct_cooling_rate': 10
            }

        if user.last_alloy_store is not None:
            alloy_store = user.last_alloy_store
        else:
            alloy_store = {
                'alloy_option': 'single',
                'alloys': {
                    'parent': None,
                    'weld': None,
                    'mix': None
                }
            }
        if user.last_simulation_results is not None:
            last_results = user.last_simulation_results
        else:
            last_results = {}

        # This dict defines what we store in Redis for the session
        session_data_store = {
            'configurations': configs,
            'alloy_store': alloy_store,
            'results': last_results
        }

        # The storage value dumped to JSON format. We use our custom JSON
        # Encoder to ensure that numpy.floats get serialized properly
        sim_session_data = JSONEncoder().encode(session_data_store)
        session[self.SESSION_PREFIX] = sim_session_data

    def save_session(self, session_data: dict) -> None:
        # We use our custom JSON Encoder to ensure that numpy.floats get
        # serialized properly
        session_data_store = JSONEncoder().encode(session_data)
        session[self.SESSION_PREFIX] = session_data_store

    def load_session(self) -> Union[str, dict]:
        if not session:
            logger.info('Session is empty.')
            # Must capture message because there is no exception in this
            # case which is a bug if Python APM Agent.
            # https://github.com/elastic/apm-agent-python/issues/599
            apm.capture_message('Unauthorised access.')
            return 'Session is empty.'

        # We access the Session from Redis and get the Session data
        session_data_store = session.get(self.SESSION_PREFIX, None)
        if not session_data_store:
            message = 'Cannot retrieve data from Session store.'
            logger.info(message, stack_info=True)
            # Must capture message because there is no exception in this
            # case which is a bug if Python APM Agent.
            # https://github.com/elastic/apm-agent-python/issues/599
            apm.capture_message('Unauthorised access.')
            return message

        sess_data: dict = json.loads(session_data_store)
        # Return the data as a dict
        return sess_data

    def clean_simulation_session(self) -> None:
        session.pop(self.SESSION_PREFIX)
