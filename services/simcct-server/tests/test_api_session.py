# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_session.py
# 
# Attributions: 
# [1] 
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.12'
"""test_api_session.py: 

{Description}
"""

import os
import json
import requests

import flask
from flask import current_app
from tests.test_api_base import BaseTestCase, app


class TestSessionService(BaseTestCase):
    users_host = os.environ.get('USERS_HOST')
    base_url = f'http://{users_host}'

    # def test_session_user_ping(self):
    #     with self.client:
    #         res = self.client.get('/users/ping')
    #         data = json.loads(res.data.decode())
    #         self.assertEqual(res.status_code, 200)
    #         self.assertEqual(data['message'], 'pong')
    #         self.assertEqual(data['status'], 'success')

    def test_session_post(self):
        resp = requests.post(
            url=f'{self.base_url}/auth/register',
            json={
                'email': 'eric@shield.gov.us',
                'first_name': 'Eric',
                'last_name': 'Selvig',
                'password': 'BifrostIsReal'
            }
        )
        data = resp.json()
        token = data['token']
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'User has been registered.')
        self.assertTrue(token)

        user_resp = requests.get(
            f'{self.base_url}/auth/status',
            headers={
                'Content-type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        data = user_resp.json()
        self.assertEqual(data['status'], 'success')
        user_id = data['data']['_id']

        with self.app.test_client() as client:
            login_res = client.post(
                '/session',
                data=json.dumps({
                    '_id': user_id,
                    'token': token
                }),
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(data['message'], 'User session initiated.')

    def test_session(self):
        with current_app.test_client() as client:
            login_res = client.post(
                '/session',
                data=json.dumps({
                    '_id': "joi2i3po4ipo2i34",
                    'token': "lkajsdlkjlkasjd"
                }),
                content_type='application/json'
            )
            data = json.loads(login_res.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertEqual(data['message'], 'User session initiated.')

            with client.session_transaction() as sess:
                sess['TEST'] = "HELLO WORLD!"
                print(sess.sid)
            flask.session['TEST2'] = 'HELLO WORLD AGAIN!'
            print(flask.session.sid)
