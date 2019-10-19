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
    """
    A Routes Enum that ensure we can centrally control all of the routes
    which is particularly important if we need to change any of the prefixes.
    Each route must be below a comment that tells us which file it comes from.

    Note:
      - Routes from RESTful endpoints will use the ClassName.
      - Routes from Flask endpoints will use the function_name.
    """

    # root.py
    index = '/'
    readiness_probe = '/healthy'

    # user_analytics.py
    UserNerdyData = f'{PREFIX}/users/stats'
    UserLoginLocationData = f'{PREFIX}/users/login/map'
    UserProfileData = f'{PREFIX}/users/profile'

    # app_analytics.py
    GeneralData = f'{PREFIX}/app/stats'
    LiveLoginData = f'{PREFIX}/app/logged_in_data'
