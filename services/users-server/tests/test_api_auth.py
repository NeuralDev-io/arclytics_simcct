# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# test_api_auth.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.05'
"""test_api_auth.py: 

{Description}
"""

import json
import unittest

from flask import current_app

from api.models import User
from tests.test_api_base import BaseTestCase


class TestAuthEndpoints(BaseTestCase):
    def test_user_registration(self):
        """Ensure we can register a user."""
        resp = self.client.post('/auth/register',
                                data=json.dumps({
                                    'username': 'black_widow',
                                    'email': 'natasha@avengers.io',
                                    'password': 'RedInMyLedger'
                                }),
                                content_type='application/json')
        data = json.loads(resp.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == 'User has been registered.')
        self.assertTrue(data['auth_token'])
        self.assertTrue(resp.content_type == 'application/json')
        self.assertEqual(resp.status_code, 201)

    def test_user_registration_duplicate_email(self):
        user = User(username='test', email='test@test.com')
        user.set_password('test123')
        user.save()
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'username': 'ansto_joe',
                    'email': 'test@test.com',
                    'password': 'test123'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('This user already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_duplicate_username(self):
        user = User(username='ansto_joe', email='test@test.com')
        user.set_password('test123')
        user.save()
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'username': 'ansto_joe',
                    'email': 'test@test2.com',
                    'password': 'test123'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('The users details already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json(self):
        with self.client:
            response = self.client.post('/auth/register',
                                        data=json.dumps({}),
                                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_no_email(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'username': 'ansto_joe',
                    'password': 'test123'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('A user account must have an email.',
                          data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_invalid_email(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'username': 'ansto_joe',
                    'email': 'joe@mistakenemail',
                    'password': 'test123'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('The user cannot be validated.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_no_password(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'username': 'insecure_user',
                    'email': 'test@yahoo.com'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('A user account must have a password.',
                          data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_bad_password(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'username': 'insecure_user',
                    'email': 'test@yahoo.com',
                    'password': 'test'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('The password is invalid.', data['message'])
            self.assertIn('fail', data['status'])

    def test_registered_user_login(self):
        with self.client:
            user = User(username='test', email='test@test.com')
            user.set_password('test123')
            user.save()
            response = self.client.post('/auth/login',
                                        data=json.dumps({
                                            'email': 'test@test.com',
                                            'password': 'test123'
                                        }),
                                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertIn(data['message'], 'Successfully logged in.')
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_empty_user_login(self):
        with self.client:
            user = User(username='test', email='test@test.com')
            user.set_password('test123')
            user.save()
            response = self.client.post('/auth/login',
                                        data=json.dumps({}),
                                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertEqual('Invalid payload.', data['message'])
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual(response.status_code, 400)

    def test_bad_login_details(self):
        user = User(username='test', email='test@test.com')
        user.set_password('test123')
        user.save()
        with self.client:
            resp_1 = self.client.post('/auth/login',
                                      data=json.dumps({
                                          'username': 'test',
                                          'password': 'test123'
                                      }),
                                      content_type='application/json')
            data = json.loads(resp_1.data.decode())
            self.assertEqual('You must provide an email.', data['message'])
            self.assertTrue(data['status'] == 'fail')
            self.assertNotIn('auth_token', data)
            self.assertTrue(resp_1.content_type == 'application/json')
            self.assertEqual(resp_1.status_code, 400)

            resp_2 = self.client.post('/auth/login',
                                      data=json.dumps({
                                          'email': 'test@test.com',
                                      }),
                                      content_type='application/json')
            data = json.loads(resp_2.data.decode())
            self.assertEqual('You must provide a password.', data['message'])
            self.assertTrue(data['status'] == 'fail')
            self.assertNotIn('auth_token', data)
            self.assertEqual(resp_2.status_code, 400)

            resp_3 = self.client.post('/auth/login',
                                      data=json.dumps({
                                          'email': 'test@test.com',
                                          'password': 'short'
                                      }),
                                      content_type='application/json')
            data = json.loads(resp_3.data.decode())
            self.assertEqual('Email or password combination incorrect.',
                             data['message'])
            self.assertTrue(data['status'] == 'fail')
            self.assertNotIn('auth_token', data)
            self.assertEqual(resp_3.status_code, 400)

    def test_invalid_user_login(self):
        with self.client:
            user = User(username='test', email='test@test.com')
            user.set_password('test123')
            user.save()
            response = self.client.post('/auth/login',
                                        data=json.dumps({
                                            'email':
                                            'test@test.com',
                                            'password':
                                            'wrongpassword'
                                        }),
                                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertEqual('Email or password combination incorrect.',
                             data['message'])
            self.assertTrue(data['status'] == 'fail')
            self.assertNotIn('auth_token', data)
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_not_registered_user_login(self):
        with self.client:
            response = self.client.post('/auth/login',
                                        data=json.dumps({
                                            'email': 'test@test.com',
                                            'password': 'test123'
                                        }),
                                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User does not exist.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_bad_auth_token_encoding(self):
        user = User(username='test', email='test@test.com', user_type='2')
        user.set_password('wrongpassword')
        user.save()
        with self.client:
            response = self.client.post('/auth/login',
                                        data=json.dumps({
                                            'email':
                                            'test@test.com',
                                            'password':
                                            '<html>wrongpassword</html>'
                                        }),
                                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertEqual('Email or password combination incorrect.',
                             data['message'])
            self.assertTrue(data['status'] == 'fail')
            self.assertNotIn('auth_token', data)
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_valid_logout(self):
        user = User(username='test', email='test@test.com')
        user.set_password('test123')
        user.save()
        with self.client:
            # user login
            resp_login = self.client.post('/auth/login',
                                          data=json.dumps({
                                              'email': 'test@test.com',
                                              'password': 'test123'
                                          }),
                                          content_type='application/json')
            # valid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get('/auth/logout',
                                       headers={
                                           'Authorization':
                                           'Bearer {token}'.format(token=token)
                                       })
            data = json.loads(response.data.decode())
            self.assertIn(
                'success',
                data['status'],
            )
            self.assertIn('Successfully logged out.', data['message'])
            self.assertEqual(response.status_code, 200)

    def test_invalid_logout_expired_token(self):
        user = User(username='test', email='test@test.com')
        user.set_password('test123')
        user.save()
        current_app.config['TOKEN_EXPIRATION_SECONDS'] = -1
        with self.client:
            resp_login = self.client.post('/auth/login',
                                          data=json.dumps({
                                              'email': 'test@test.com',
                                              'password': 'test123'
                                          }),
                                          content_type='application/json')
            # invalid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get('/auth/logout',
                                       headers={
                                           'Authorization':
                                           'Bearer {token}'.format(token=token)
                                       })
            data = json.loads(response.data.decode())
            self.assertEqual('fail', data['status'])
            self.assertEqual('Signature expired. Please login again.',
                             data['message'])
            self.assertEqual(response.status_code, 401)

    def test_invalid_logout(self):
        with self.client:
            response = self.client.get(
                '/auth/logout', headers={'Authorization': 'Bearer invalid'})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual('Invalid token. Please log in again.',
                             data['message'])
            self.assertEqual(response.status_code, 401)

    def test_invalid_auth_header(self):
        with self.client:
            response = self.client.get('/auth/logout', headers={})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual('Provide a valid JWT auth token.',
                             data['message'])
            self.assertEqual(response.status_code, 403)

    def test_user_status(self):
        user = User(username='test', email='test@test.com')
        user.set_password('test123')
        user.save()
        with self.client:
            resp_login = self.client.post('/auth/login',
                                          data=json.dumps({
                                              'email': 'test@test.com',
                                              'password': 'test123'
                                          }),
                                          content_type='application/json')
            token = json.loads(resp_login.data.decode())['auth_token']
            resp_status = self.client.get(
                '/auth/status',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token)
                })
            data = json.loads(resp_status.data.decode())
            self.assertIn('success', data['status'])
            self.assertTrue(data['data'] is not None)
            self.assertIn('test', data['data']['username'])
            self.assertIn('test@test.com', data['data']['email'])
            self.assertTrue(data['data']['active'] is True)
            self.assertEqual(resp_status.status_code, 200)

    def test_invalid_status(self):
        with self.client:
            response = self.client.get(
                '/auth/status', headers={'Authorization': 'Bearer invalid'})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual('Invalid token. Please log in again.',
                             data['message'])
            self.assertEqual(response.status_code, 401)

    def test_invalid_logout_inactivate(self):
        user = User(username='test', email='test@test.com')
        user.set_password('test123')
        user.active = False
        user.save()
        with self.client:
            resp_login = self.client.post('/auth/login',
                                          data=json.dumps({
                                              'email': 'test@test.com',
                                              'password': 'test123'
                                          }),
                                          content_type='application/json')
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get('/auth/logout',
                                       headers={
                                           'Authorization':
                                           'Bearer {token}'.format(token=token)
                                       })
            data = json.loads(response.data.decode())
            self.assertEqual('fail', data['status'])
            self.assertEqual('Provide a valid JWT auth token.',
                             data['message'])
            self.assertEqual(response.status_code, 401)

    def test_invalid_status_inactive(self):
        user = User(username='test', email='test@test.com')
        user.set_password('test123')
        user.active = False
        user.save()
        with self.client:
            resp_login = self.client.post('/auth/login',
                                          data=json.dumps({
                                              'email': 'test@test.com',
                                              'password': 'test123'
                                          }),
                                          content_type='application/json')
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format(token)})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Provide a valid JWT auth token.')
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
