# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# __init__.py.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.09.08'
"""__init__.py: 

Simulation Session.
"""

from dataclasses import dataclass

from .sim_session_service import SimSessionService


@dataclass
class SimSession(object):
    is_valid: bool = False
    method: str = 'Li98'
    grain_size: float = 0.0
    nucleation_start: float = 0.0
    nucleation_finish: float = 0.0
    ms_temp: float = 0.0
    ms_rate_param: float = 0.0
    auto_calculate_ms: bool = True
    bs_temp: float = 0.0
    auto_calculate_bs: bool = True
    ae1_temp: float = 0.0
    ae3_temp: float = 0.0
    auto_calculate_ae: bool = True
    start_temp: float = 0.0
    cct_cooling_rate: float = 0.0
    # xfe: float = 0.0

    # TODO(andrew@neuraldev.io): THIS CLASS NEEDS TO BE SOMETHING CONCRETE
    #  - We can then use it to serialize and deserialise from the Session
    #    store as a concrete object to pass around rather than a Dictionary.
    #  - Gives us the opportunity to include internal error checking via
    #    decorators and other methods.
    #  - Can potentially use a Factory method to alloy serialization.
