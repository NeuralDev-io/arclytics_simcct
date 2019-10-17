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
    user_list = f'{PREFIX}/users'
    search_users = f'{PREFIX}/users/search'
    users = f'{PREFIX}/user'
    user_profiles = f'{PREFIX}/user/profile'
    user_rating = f'{PREFIX}/user/rating'
    user_feedback = f'{PREFIX}/user/feedback'
    feedback_list = f'{PREFIX}/admin/feedback/list'
    subscribe_feedback = f'{PREFIX}/admin/feedback/list/subscribe'
    save_simulation_list = f'{PREFIX}/user/simulation'
    save_simulation_detail = f'{PREFIX}/user/simulation/<sim_id>'
    request_shared_simulation = (
        f'{PREFIX}/user/share/simulation/request/<token>'
    )
    view_shared_simulation = f'{PREFIX}/user/share/simulation/view/<token>'
    share_simulation_link = f'{PREFIX}/user/share/simulation/link'
    share_simulation_email = f'{PREFIX}/user/share/simulation/email'
    simulation = f'{PREFIX}/simulate'
    ae3_equilibrium = f'{PREFIX}/ae3equilibrium'
    user_alloy_list = f'{PREFIX}/user/alloys'
    user_alloy = f'{PREFIX}/user/alloys/<alloy_id>'
    last_simulation = f'{PREFIX}/user/last/simulation'
    cancel_promotion = f'{PREFIX}/admin/create/cancel/<token>'
    verify_promotion = f'{PREFIX}/admin/create/verify/<token>'
    confirm_disable_account = f'{PREFIX}/disable/user/confirm/<token>'
    admin_create = f'{PREFIX}/admin/create'
    disable_account = f'{PREFIX}/disable/user'
    enable_account = f'{PREFIX}/enable/user'
    martensite = f'{PREFIX}/configs/ms'
    bainite = f'{PREFIX}/configs/bs'
    austenite = f'{PREFIX}/configs/ae'
    alloys = f'{PREFIX}/global/alloys/<alloy_id>'
    alloys_list = f'{PREFIX}/global/alloys'
    # = f'{PREFIX}/'
    # = f'{PREFIX}/'
    # = f'{PREFIX}/'
    # = f'{PREFIX}/'
