# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# __init__.py.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------

__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.09.08'

"""__init__.py: 

Simulation Session.
"""

from .sim_session_service import SimSessionService
from dataclasses import dataclass


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





