# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# routes.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.10.15'

"""routes.py: 

This module defines all the routes for every Resource which can be used to 
get route URL with a prefix.
"""

import enum

PREFIX = '/v1/arc'


class Routes(enum.Enum):
    Root = '/'
    UserNerdyData = f'{PREFIX}/users/stats'
    UserLoginLocationData = f'{PREFIX}/users/login/map'
    UserProfileData = f'{PREFIX}/users/profile'
    LiveLoginData = f'{PREFIX}/app/logged_in_data'
