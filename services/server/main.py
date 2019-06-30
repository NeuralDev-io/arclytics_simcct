# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# main.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.06.24'

"""main.py: 

{Description}
"""

# Built-in/Generic Imports
import os

from logger.arc_logger import AppLogger
from simulation.simconfiguration import *
from simulation.simulations import Simulation

if __name__ == '__main__':
    logger = AppLogger(__name__)
    logger.info('SimConfiguration Start - Alpha version')
    configs = SimConfiguration(debug=True)
    print(configs)
    sim = Simulation(configs, debug=True)
    sim.cct()
    logger.info('SimConfiguration Complete - Alpha version')
