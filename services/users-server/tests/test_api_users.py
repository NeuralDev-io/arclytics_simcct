# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_api_users.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'
"""test_api_users.py: 

{Description}
"""

import json
import unittest

from bson import ObjectId
from flask import current_app

from tests.test_api_base import BaseTestCase
from logger.arc_logger import AppLogger
from api.models import User

logger = AppLogger(__name__)


class TestUserService(BaseTestCase):
    """Tests for the User API service."""

    def test_ping(self):
        """Ensure the /ping route behaves correctly."""
        res = self.client.get('/ping')
        data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn('pong', data['message'])

    def test_single_user(self):
        """Ensure we can get a single user works as expected."""
        tony = User(username='iron_man', email='tony@starkindustries.com')
        tony.set_password('IAmTheRealIronMan')
        tony.save()

        with self.client:
            resp_login = self.client.post('/auth/login',
                                          data=json.dumps({
                                              'email':
                                              'tony@starkindustries.com',
                                              'password':
                                              'IAmTheRealIronMan'
                                          }),
                                          content_type='application/json')
            token = json.loads(resp_login.data.decode())['auth_token']

            resp = self.client.get(
                '/users/{user_id}'.format(user_id=tony.id),
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)})
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertIn('iron_man', data['username'])
            self.assertIn('tony@starkindustries.com', data['email'])

    def test_single_user_not_active(self):
        tony = User(username='iron_man', email='tony@starkindustries.com')
        tony.set_password('IAmTheRealIronMan')
        tony.save()

        with self.client:
            resp_login = self.client.post('/auth/login',
                                          data=json.dumps({
                                              'email':
                                              'tony@starkindustries.com',
                                              'password':
                                              'IAmTheRealIronMan'
                                          }),
                                          content_type='application/json')
            token = json.loads(resp_login.data.decode())['auth_token']

            # Update Tony to be inactive
            tony.active = False
            tony.save()

            resp = self.client.get(
                '/users/{user_id}'.format(user_id=tony.id),
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)})

            data = json.loads(resp.data.decode())
            self.assertEqual(data['message'], 'User must sign in again.')
            self.assertEqual('fail', data['status'])
            self.assertEqual(resp.status_code, 401)

    def test_single_user_invalid_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Provide a valid JWT auth token.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            _id = ObjectId()
            response = self.client.get(f'/users/{_id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Provide a valid JWT auth token.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_expired_token(self):
        tony = User(username='iron_man', email='tony@starkindustries.com')
        tony.set_password('IAmTheRealIronMan')
        tony.save()
        current_app.config['TOKEN_EXPIRATION_SECONDS'] = -1
        with self.client:
            resp_login = self.client.post('/auth/login',
                                          data=json.dumps({
                                              'email':
                                              'tony@starkindustries.com',
                                              'password':
                                              'IAmTheRealIronMan'
                                          }),
                                          content_type='application/json')
            # invalid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get('/users/{}'.format(tony.id),
                                       headers={
                                           'Authorization':
                                           'Bearer {token}'.format(token=token)
                                       })
            data = json.loads(response.data.decode())
            self.assertEqual('fail', data['status'])
            self.assertEqual('Signature expired. Please login again.',
                             data['message'])
            self.assertEqual(response.status_code, 401)

    def test_get_all_users_no_header(self):
        with self.client:
            resp = self.client.get('/users',
                                   content_type='application/json',
                                   headers={})
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 403)
            self.assertIn('fail', data['status'])
            self.assertNotIn('data', data)
            self.assertIn('Provide a valid JWT auth token.', data['message'])

    def test_unauthorized_get_all_users(self):
        """Ensure we can't get all users because we are not authorized."""
        tony = User(username='iron_man', email='tony@starkindustries.com')
        tony.set_password('IAmTheRealIronMan')
        tony.is_admin = False
        tony.save()
        nat = User(username='black_widow', email='nat@shield.gov.us')
        nat.set_password('IveGotRedInMyLedger')
        nat.save()

        with self.client:
            resp_login = self.client.post('/auth/login',
                                          data=json.dumps({
                                              'email':
                                              'tony@starkindustries.com',
                                              'password':
                                              'IAmTheRealIronMan'
                                          }),
                                          content_type='application/json')
            token = json.loads(resp_login.data.decode())['auth_token']

            resp = self.client.get(
                '/users',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)})
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 403)
            self.assertIn('fail', data['status'])
            self.assertNotIn('data', data)
            self.assertIn('Not authorized.', data['message'])

    def test_get_all_users_expired_token(self):
        thor = User(username='thor', email='thor@avengers.io')
        thor.set_password('StrongestAvenger')
        thor.is_admin = True
        thor.save()
        with self.client:
            resp_login = self.client.post('/auth/login',
                                          data=json.dumps({
                                              'email':
                                              'thor@avengers.io',
                                              'password':
                                              'StrongestAvenger'
                                          }),
                                          content_type='application/json')
            # token = json.loads(resp_login.data.decode())['auth_token']
            token = 'KJASlkdjlkajsdlkjlkasjdlkjalosd'
            resp = self.client.get('/users',
                                   headers={
                                       'Authorization':
                                       'Bearer {token}'.format(token=token)
                                   })
            data = json.loads(resp.data.decode())
            self.assertEqual('fail', data['status'])
            self.assertNotIn('data', data)
            self.assertEqual('Invalid token. Please log in again.',
                             data['message'])
            self.assertEqual(resp.status_code, 401)

    def test_get_all_users(self):
        """Ensure we can get all users if logged in ant authorized."""
        tony = User(username='iron_man', email='tony@starkindustries.com')
        tony.set_password('IAmTheRealIronMan')
        tony.is_admin = True
        tony.save()
        steve = User(username='cap', email='steve@avengers.io')
        steve.set_password('ICanDoThisAllDay')
        steve.save()
        nat = User(username='black_widow', email='nat@shield.gov.us')
        nat.set_password('IveGotRedInMyLedger')
        nat.save()

        with self.client:
            resp_login = self.client.post('/auth/login',
                                          data=json.dumps({
                                              'email':
                                              'tony@starkindustries.com',
                                              'password':
                                              'IAmTheRealIronMan'
                                          }),
                                          content_type='application/json')
            token = json.loads(resp_login.data.decode())['auth_token']

            resp = self.client.get(
                '/users',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)})
            data = json.loads(resp.data.decode())

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(data['data']['users']), 3)
            self.assertIn('iron_man', data['data']['users'][0]['username'])
            self.assertTrue(data['data']['users'][0]['admin'])
            self.assertIn('cap', data['data']['users'][1]['username'])
            self.assertFalse(data['data']['users'][1]['admin'])
            self.assertIn('black_widow', data['data']['users'][2]['username'])
            self.assertIn('success', data['status'])


if __name__ == '__main__':
    unittest.main()
