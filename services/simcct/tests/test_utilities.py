# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# utilities.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.31'
"""utilities.py: 

{Description}
"""

from datetime import datetime
from simulation.periodic import PeriodicTable
from flask import json

GMT_DATETIME_FORMAT = "%a, %d-%b-%Y %H:%M:%S GMT"


def convert_json_to_comp(comp_list):
    test_comp = {}
    for el in comp_list:
        try:
            idx = PeriodicTable[el['symbol']].value.atomic_num
        except NotImplementedError as e:
            raise NotImplementedError('Symbol not found error.')
        test_comp[str(idx)] = el
    return test_comp


def test_login(client, email: str, password: str):
    resp_login = client.post(
        '/api/v1/sim/auth/login',
        data=json.dumps({
            'email': email,
            'password': password
        }),
        content_type='application/json'
    )

    resp_set_cookie = resp_login.headers.get('Set-Cookie').split(';')
    session_key = str(resp_set_cookie[0]).split('=', 1)
    expiry_str = str(resp_set_cookie[1]).split('=', 1)
    expiry_date = datetime.strptime(expiry_str[1], GMT_DATETIME_FORMAT)
    domain = str(resp_set_cookie[3]).split('=', 1)

    # This is how the response cookie is set. Copy this.
    # response.set_cookie(
    #       SESSION_COOKIE_NAME, session_key, expires=expiry_date,
    #        httponly=True, domain=self.get_cookie_domain(app)
    # )

    # THIS IS JUST FOR VISUALS. CLIENT AUTOMATICALLY SETS IT.
    cookie = {
        'SESSION_COOKIE_NAME': session_key[0],
        'value': session_key[1],
        'expires': expiry_date.strftime(GMT_DATETIME_FORMAT),
        'domain': domain[1]
    }

    return cookie
