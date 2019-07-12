# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_auth.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
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

from users_api.models.models import User
from tests.test_api_base import BaseTestCase


class TestAuthEndpoints(BaseTestCase):
    """This module tests all the authentication endpoints and middleware."""

    def test_user_registration(self):
        """Ensure we can register a user."""
        resp = self.client.post(
            '/auth/register',
            data=json.dumps(
                {
                    'email': 'natasha@avengers.io',
                    'first_name': 'Natasha',
                    'last_name': 'Romanoff',
                    'password': 'RedInMyLedger'
                }
            ),
            content_type='application/json'
        )
        data = json.loads(resp.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == 'User has been registered.')
        self.assertTrue(data['token'])
        self.assertTrue(resp.content_type == 'application/json')
        self.assertEqual(resp.status_code, 201)

    def test_user_registration_duplicate_email(self):
        user = User(
            email='green_machine@avengers.io',
            first_name='Bruce',
            last_name='Banner'
        )
        user.set_password('HulkSmash!')
        user.save()
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps(
                    {
                        'email': 'green_machine@avengers.io',
                        'first_name': 'Bruce',
                        'last_name': 'Banner',
                        'password': 'HulkSmash!'
                    }
                ),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('This user already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_no_email(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps(
                    {
                        'first_name': 'Joe',
                        'last_name': 'Blow',
                        'password': 'test123'
                    }
                ),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'A user account must have an email.', data['message']
            )
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_invalid_email(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps(
                    {
                        'email': 'joe@mistakenemail',
                        'password': 'test123'
                    }
                ),
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
                data=json.dumps(
                    {
                        'email': 'test@yahoo.com'
                    }
                ),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'A user account must have a password.', data['message']
            )
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_bad_password(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps(
                    {
                        'email': 'test@yahoo.com',
                        'password': 'test'
                    }
                ),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('The password is invalid.', data['message'])
            self.assertIn('fail', data['status'])

    def test_registered_user_login(self):
        """Ensure we can login as users after they have registered."""
        with self.client:
            peter = User(
                email='spiderman@newavenger.io',
                first_name='Peter',
                last_name='Parker'
            )
            peter.set_password('SpideySenses')
            peter.save()
            tony = User(
                email='tony@avengers.io',
                first_name='Tony',
                last_name='Stark'
            )
            tony.set_password('IAmIronMan')
            tony.save()

            response_peter = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'spiderman@newavenger.io',
                        'password': 'SpideySenses'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(response_peter.data.decode())
            self.assertIn(data['message'], 'Successfully logged in.')
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['token'])
            self.assertTrue(response_peter.content_type == 'application/json')
            self.assertEqual(response_peter.status_code, 200)

            response_tony = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'tony@avengers.io',
                        'password': 'IAmIronMan'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(response_tony.data.decode())
            self.assertIn(data['message'], 'Successfully logged in.')
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['token'])
            self.assertTrue(response_tony.content_type == 'application/json')
            self.assertEqual(response_tony.status_code, 200)

    def test_empty_user_login(self):
        """Ensure if no request body provided it returns appropriate message."""
        with self.client:
            response = self.client.post(
                '/auth/login',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual('Invalid payload.', data['message'])
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual(response.status_code, 400)

    def test_bad_login_details(self):
        """
        Ensure if bad details are given, it will fail with appropriate messages.
        """
        user = User(
            email='war_machine@avengers.io',
            first_name='James',
            last_name='Rhodey'
        )
        user.set_password('test123')
        user.save()
        with self.client:
            resp_1 = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'password': 'test123'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(resp_1.data.decode())
            self.assertEqual('You must provide an email.', data['message'])
            self.assertTrue(data['status'] == 'fail')
            self.assertNotIn('token', data)
            self.assertTrue(resp_1.content_type == 'application/json')
            self.assertEqual(resp_1.status_code, 400)

            resp_2 = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'war_machine@avengers.io',
                }),
                content_type='application/json'
            )
            data = json.loads(resp_2.data.decode())
            self.assertEqual('You must provide a password.', data['message'])
            self.assertTrue(data['status'] == 'fail')
            self.assertNotIn('token', data)
            self.assertEqual(resp_2.status_code, 400)

            resp_3 = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'test@test.com',
                        'password': 'short'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(resp_3.data.decode())
            self.assertEqual(
                'Email or password combination incorrect.', data['message']
            )
            self.assertTrue(data['status'] == 'fail')
            self.assertNotIn('token', data)
            self.assertEqual(resp_3.status_code, 400)

    def test_invalid_user_login(self):
        with self.client:
            user = User(
                email='ant_man@avengers.io',
                first_name='Scott',
                last_name='Lang'
            )
            user.set_password('ILoveCassie')
            user.save()
            response = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'ant_man@avengers.io',
                        'password': 'wrongpassword'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(
                'Email or password combination incorrect.', data['message']
            )
            self.assertTrue(data['status'] == 'fail')
            self.assertNotIn('token', data)
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_not_registered_user_login(self):
        with self.client:
            response = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'test@test.com',
                        'password': 'test123'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User does not exist.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_bad_auth_token_encoding(self):
        user = User(
            email='metal_arm@newavengers.io',
            first_name='Bucky',
            last_name='Barnes'
        )
        user.set_password('badpassword')
        user.save()
        with self.client:
            response = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'metal_arm@newavengers.io',
                        'password': '<html>wrongpassword</html>'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(
                'Email or password combination incorrect.', data['message']
            )
            self.assertTrue(data['status'] == 'fail')
            self.assertNotIn('token', data)
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_valid_logout(self):
        user = User(
            email='falcon@newavengers.io',
            first_name='Sam',
            last_name='Wilson'
        )
        user.set_password('NewCaptainAmerica')
        user.save()
        with self.client:
            # user login
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'falcon@newavengers.io',
                        'password': 'NewCaptainAmerica'
                    }
                ),
                content_type='application/json'
            )
            # valid token logout
            token = json.loads(resp_login.data.decode())['token']
            response = self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token)
                }
            )
            data = json.loads(response.data.decode())
            self.assertIn(
                'success',
                data['status'],
            )
            self.assertIn('Successfully logged out.', data['message'])
            self.assertEqual(response.status_code, 200)

    def test_invalid_logout_expired_token(self):
        user = User(
            email='tchalla@newavengers.io',
            first_name='Tchalla',
            last_name='Wakandan'
        )
        user.set_password('SomebodyGetThatManAShield!')
        user.save()
        current_app.config['TOKEN_EXPIRATION_SECONDS'] = -1
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'tchalla@newavengers.io',
                        'password': 'SomebodyGetThatManAShield!'
                    }
                ),
                content_type='application/json'
            )
            # invalid token logout
            token = json.loads(resp_login.data.decode())['token']
            response = self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token)
                }
            )
            data = json.loads(response.data.decode())
            self.assertEqual('fail', data['status'])
            self.assertEqual(
                'Signature expired. Please login again.', data['message']
            )
            self.assertEqual(response.status_code, 401)

    def test_invalid_logout(self):
        with self.client:
            response = self.client.get(
                '/auth/logout', headers={'Authorization': 'Bearer invalid'}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual(
                'Invalid token. Please log in again.', data['message']
            )
            self.assertEqual(response.status_code, 401)

    def test_invalid_auth_header(self):
        with self.client:
            response = self.client.get('/auth/logout', headers={})
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertEqual(
                'Provide a valid JWT auth token.', data['message']
            )
            self.assertEqual(response.status_code, 400)

    def test_user_status(self):

        user = User(
            email='scarlet_witch@avengers.io',
            first_name='Wanda',
            last_name='Maximoff'
        )
        user.set_password('YouTookEverythingFromMe!')
        user.save()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'scarlet_witch@avengers.io',
                        'password': 'YouTookEverythingFromMe!'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']
            resp_status = self.client.get(
                '/auth/status',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token)
                }
            )
            data = json.loads(resp_status.data.decode())
            self.assertIn('success', data['status'])
            self.assertTrue(data['data'] is not None)
            self.assertIn('scarlet_witch@avengers.io', data['data']['email'])
            self.assertTrue(data['data']['active'] is True)
            self.assertEqual(resp_status.status_code, 200)

    def test_invalid_status(self):
        with self.client:
            response = self.client.get(
                '/auth/status', headers={'Authorization': 'Bearer invalid'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(
                'Invalid token. Please log in again.', data['message']
            )
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(response.status_code, 401)

    def test_invalid_logout_inactive(self):
        """Ensure if user is not active, they cannot logout."""
        user = User(
            email='most_hated_avenger@disney.com',
            first_name='Carol',
            last_name='Danvers'
        )
        user.set_password('OnlyHereBecauseOfFeminism')
        user.active = False
        user.save()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'most_hated_avenger@disney.com',
                        'password': 'OnlyHereBecauseOfFeminism'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']
            response = self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token)
                }
            )
            data = json.loads(response.data.decode())
            self.assertEqual(
                'This user does not exist.', data['message']
            )
            self.assertEqual('fail', data['status'])
            self.assertEqual(response.status_code, 401)

    def test_invalid_status_inactive(self):
        """Ensure if user is not active they can't get a status."""
        user = User(
            email='daredevil@marvel.io',
            first_name='Matthew',
            last_name='Murdock'
        )
        user.set_password('BlindLawyer')
        user.active = False
        user.save()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'daredevil@marvel.io',
                        'password': 'BlindLawyer'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'This user does not exist.'
            )
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
