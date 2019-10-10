# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# routes.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.10.07'
"""routes.py: 

This module defines all the routes for every Resource which can be used to 
get route URL with a prefix.
"""

import enum

PREFIX = '/v1/sim'


class Routes(enum.Enum):
    root = '/'
    ping = f'{PREFIX}/ping'
    healthy = f'{PREFIX}/healthy'
    alloy_store = f'{PREFIX}/alloys/update'
