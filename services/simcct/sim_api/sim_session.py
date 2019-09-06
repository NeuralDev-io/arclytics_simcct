# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# sim_session.py
#
# Attributions:
# [1] https://gist.github.com/wushaobo/52be20bc801243dddf52a8be4c13179a
# [2] https://github.com/mrichman/flask-redis
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.08'
"""sim_session.py: 

This module defines the class to create a RedisSession instance and the
interface to validate and operate on the Redis store of this session. 
"""

import json
from typing import Union

from flask import session
from sim_api.models import User
from sim_api.extensions import JSONEncoder
from logger.arc_logger import AppLogger

logger = AppLogger(__name__)


class SimSession(object):
    def __init__(
            self,
            is_valid=False,
            method='Li98'
    ):
        self.is_valid = is_valid
        self.method = method


class SimSessionService(object):
    """The interface defines how a service for Simulation Session works."""
    SESSION_PREFIX = 'simulation'

    def new_session(self, user: User) -> None:
        if user.last_configuration is not None:
            configs = user.last_configuration.to_dict()
        else:
            # These are based of defaults in the front-end as agreed to by
            # Andrew
            # and Dalton.
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
            alloy_store = user.last_alloy_store.to_dict()
        else:
            alloy_store = {
                'alloy_option': 'single',
                'alloys': {
                    'parent': None,
                    'weld': None,
                    'mix': None
                }
            }
        # if user.last_results is not None:
        #     last_results = user.last_results

        # This dict defines what we store in Redis for the session
        session_data_store = {
            'configurations': configs,
            'alloy_store': alloy_store,
            # TODO(davidmatthews1004@gmail.com) Update this to get from last in
            #  user doc
            'results': None
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

        # We access the Session from Redis and get the Session data
        session_data_store = session.get(self.SESSION_PREFIX, None)
        if not session_data_store:
            return 'Cannot retrieve data from Redis.'

        sess_data = json.loads(session_data_store)
        # Return the data as a dict and the sid to be used later for saving
        return sess_data

    def clean_simulation_session(self) -> None:
        session.pop(self.SESSION_PREFIX)
