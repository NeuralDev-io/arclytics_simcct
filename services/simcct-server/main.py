# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# main.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.06.24'
"""main.py: 

{Description}
"""

from simulation.simconfiguration import *
from simulation.phasesimulation import PhaseSimulation

if __name__ == '__main__':
    # logger = AppLogger(__name__)
    # logger.info('SimConfiguration Start - Alpha version')
    configs = SimConfiguration(debug=True)
    print(configs)
    sim = PhaseSimulation(configs, debug=True)
    # sim.cct()
    print(sim.plots_data.to_string('CCT'))
    # logger.info('SimConfiguration Complete - Alpha version')
