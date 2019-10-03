# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# utilities.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__status__ = 'development'
__date__ = '2019.07.31'

from datetime import datetime

from flask import json

from sim_api.extensions.Session.redis_session import SESSION_COOKIE_NAME
from simulation.periodic import PeriodicTable

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
        '/v1/sim/auth/login',
        data=json.dumps({
            'email': email,
            'password': password
        }),
        content_type='application/json',
        environ_base={'REMOTE_ADDR': '127.0.0.1'}
    )

    cookie = next(
        (
            cookie for cookie in client.cookie_jar
            if cookie.name == SESSION_COOKIE_NAME
        ), None
    )

    resp_set_cookie = resp_login.headers.get('Set-Cookie').split(';')
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
        'key': cookie.name,
        'value': cookie.value,
        'expires': expiry_date.strftime(GMT_DATETIME_FORMAT),
        'domain': domain[1]
    }

    return cookie


class FlaskTestClientProxy(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response, *args, **kwargs):
        environ['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', '127.0.0.1')
        return self.app(environ, start_response, *args, **kwargs)
