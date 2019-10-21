# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_arc_utilities.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__status__ = 'development'
__date__ = '2019.10.03'

import requests
from os import environ as env
from datetime import datetime
from flask import json

from arc_api.extensions import API_TOKEN_NAME

GMT_DATETIME_FORMAT = "%a, %d-%b-%Y %H:%M:%S GMT"
URL_PREFIX = env.get('SIMCCT_HOST', 'http://localhost:8000/v1/sim')


def get_mongo_uri():
    host = env.get('MONGO_HOST')
    port = int(env.get('MONGO_PORT'))
    db = str(env.get('MONGO_APP_DB'))
    if env.get('FLASK_ENV', 'development') == 'production':
        username = str(env.get('MONGO_APP_USER'))
        password = str(env.get('MONGO_APP_USER_PASSWORD'))
        return f'mongodb://{username}:{password}@{host}:{port}/{db}'
    else:
        return f'mongodb://{host}:{port}/{db}'


def test_register_user(
        client, first_name: str, last_name: str, email: str, password: str
):
    session = requests.Session()
    res = session.post(
        f'{URL_PREFIX}/auth/register',
        json={
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password
        },
        headers={
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
    )
    print(res.json())
    print(res.cookies.get_dict())

    # client.set_cookie(
    #     API_TOKEN_NAME, jwt, expires=expiry_date,
    # )


def test_login(client, email: str, password: str):

    session = requests.Session()

    res = session.post(
        f'{URL_PREFIX}/auth/login',
        json={
            'email': email,
            'password': password
        },
        headers={
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
    )

    cookie = session.cookies.get_dict()
    print(cookie)

    # Extract the token from the header and set the cookie on the
    # client.
    resp_set_cookie = res.headers['Set-Cookie'].split(';')
    domain = str(resp_set_cookie[3]).split('=', 1)
    expiry_str = resp_set_cookie[1].split('=')[1]
    expiry_date = datetime.strptime(expiry_str, GMT_DATETIME_FORMAT)
    auth_token = resp_set_cookie[3].split('=')[2]
    client.set_cookie(
        API_TOKEN_NAME, auth_token, expires=expiry_date, httponly=True
    )

    # THIS IS JUST FOR VISUALS. CLIENT AUTOMATICALLY SETS IT.
    cookie = {
        'key': cookie.name,
        'value': cookie.value,
        'expires': expiry_date.strftime(GMT_DATETIME_FORMAT),
        'domain': domain[1]
    }

    return cookie
