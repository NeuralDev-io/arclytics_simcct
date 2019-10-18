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
    """
    A Routes Enum that ensure we can centrally control all of the routes which
    is particularly important if we need to change any of the prefixes. Each
    route must be below a comment that tells us which file it comes from.

    Note:
      - Routes from RESTful endpoints will use the ClassName.
      - Routes from Flask endpoints will use the function_name.
    """
    # root.py
    root = '/'
    ping = f'{PREFIX}/ping'
    healthy = f'{PREFIX}/healthy'

    # auth.py
    confirm_email = f'{PREFIX}/confirm/<token>'
    confirm_email_resend = f'{PREFIX}/confirm/resend'
    confirm_email_resend_after_registration = (
        f'{PREFIX}/confirm/register/resend'
    )
    confirm_email_admin = f'{PREFIX}/confirmadmin/<token>'
    register_user = f'{PREFIX}/auth/register'
    check_password = f'{PREFIX}/auth/password/check'
    reset_password = f'{PREFIX}/auth/password/reset'
    confirm_reset_password = f'{PREFIX}/reset/password/confirm/<token>'
    reset_password_email = f'{PREFIX}/reset/password'
    change_password = f'{PREFIX}/auth/password/change'
    change_email = f'{PREFIX}/auth/email/change'
    login = f'{PREFIX}/auth/login'
    logout = f'{PREFIX}/auth/logout'
    get_user_status = f'{PREFIX}/auth/status'

    # users.py
    UserList = f'{PREFIX}/users'
    UserListQuery = f'{PREFIX}/users/query'
    SearchUsers = f'{PREFIX}/users/search'
    Users = f'{PREFIX}/user'
    UserProfiles = f'{PREFIX}/user/profile'

    save_simulation_list = f'{PREFIX}/user/simulation'
    save_simulation_detail = f'{PREFIX}/user/simulation/<sim_id>'

    user_rating = f'{PREFIX}/user/rating'
    user_feedback = f'{PREFIX}/user/feedback'
    feedback_list = f'{PREFIX}/admin/feedback/list'
    subscribe_feedback = f'{PREFIX}/admin/feedback/list/subscribe'

    # share.py
    ShareSimulationLink = f'{PREFIX}/user/share/simulation/link'
    ShareSimulationEmail = f'{PREFIX}/user/share/simulation/email'
    request_shared_simulation = (
        f'{PREFIX}/user/share/simulation/request/<token>'
    )
    view_shared_simulation = f'{PREFIX}/user/share/simulation/view/<token>'

    user_alloy_list = f'{PREFIX}/user/alloys'
    user_alloy = f'{PREFIX}/user/alloys/<alloy_id>'
    last_simulation = f'{PREFIX}/user/last/simulation'

    # simulation.py
    Simulation = f'{PREFIX}/simulate'
    Ae3Equilibrium = f'{PREFIX}/ae3equilibrium'

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

    # sim_alloys.py
    AlloyStore = f'{PREFIX}/alloys/update'
