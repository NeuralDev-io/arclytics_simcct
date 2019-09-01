# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_auth.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.05'
"""test_api_auth.py: 

{Description}
"""

import os
import json
import unittest

from pymongo import MongoClient
from flask import current_app

from tests.test_api_base import BaseTestCase
from arc_app.models import User
from arc_app.resources.auth import SimCCTBadServerLogout
from arc_app.resources.auth import register_session
from arc_app.token import generate_confirmation_token, generate_url
from tests.test_api_users import log_test_user_in


class TestAuthEndpoints(BaseTestCase):
    """This module tests all the authentication endpoints and middleware."""

    user = None

    def setUp(self) -> None:
        self.user = User(
            **{
                'first_name': 'Nick',
                'last_name': 'Fury',
                'email': 'fury@arclytics.io'
            }
        )
        self.user.set_password('BothEyesOpen!')
        self.user.verified = True
        self.user.save()

    def tearDown(self) -> None:
        self.user.delete()

    @staticmethod
    def login(client, email='fury@arclytics.io', password='BothEyesOpen!'):
        resp_login = client.post(
            '/auth/login',
            data=json.dumps({
                'email': email,
                'password': password
            }),
            content_type='application/json'
        )
        token = json.loads(resp_login.data.decode())['token']
        return token

    def test_user_registration(self):
        """Ensure we can register a user."""
        resp = self.client.post(
            '/auth/register',
            data=json.dumps(
                {
                    'email': 'andrew@neuraldev.io',
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
            **{
                'email': 'green_machine@avengers.io',
                'first_name': 'Bruce',
                'last_name': 'Banner'
            }
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
                data=json.dumps({'email': 'test@yahoo.com'}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'A user account must have a password.', data['message']
            )
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_bad_password(self):
        """Ensure registration fails with a generic <6 char password."""
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

    def test_user_confirm_email_successful_redirect(self):
        mandolorian = User(
            email='themandolorian@arclytics.io',
            first_name='The',
            last_name='Mandolorian'
        )
        mandolorian.set_password('BountyHuntingIsComplicated')
        mandolorian.save()

        confirm_token = generate_confirmation_token(mandolorian.email)
        confirm_url = generate_url('auth.confirm_email', confirm_token)

        with self.client:
            resp = self.client.get(
                confirm_url, content_type='application/json'
            )
            mongo_client = MongoClient(os.environ.get('MONGO_URI'))
            db = mongo_client['arc_test']
            user = db.users.find_one({'email': mandolorian.email})
            print(f'User.verified: {user["verified"]}')

            client_host = os.environ.get('CLIENT_HOST')
            self.assertEquals(resp.status_code, 302)
            self.assertTrue(resp.headers['Location'])
            redirect_url = f'http://{client_host}/signin'
            self.assertRedirects(resp, redirect_url)

    # FIXME(davidmatthews1004@gmail.com) Pleas fix
    # def test_user_confirm_email_token_expired(self):
    #     mandolorian = User(
    #         email='mandolorian@arclytics.io',
    #         first_name='The',
    #         last_name='Mandolorian'
    #     )
    #     mandolorian.set_password('BountyHuntingIsComplicated')
    #     mandolorian.save()
    #
    #     confirm_token = (
    #         'InRoZW1hbmRvbG9yaWFuQGFyY2x5dGljcy5pbyI.XWIuAQ.fTJHBkmUa8rMqUbLm-J'
    #         'MjNIcQi0'
    #     )
    #     confirm_url = generate_url('auth.confirm_email', confirm_token)
    #
    #     with self.client:
    #         resp = self.client.get(
    #             confirm_url, content_type='application/json'
    #         )
    #
    #         data = json.loads(resp.data.decode())
    #         print(data)
    #
    #         client_host = os.environ.get('CLIENT_HOST')
    #         self.assertEquals(resp.status_code, 302)
    #         self.assertTrue(resp.headers['Location'])
    #         redirect_url = \
    #             f'http://{client_host}/signin/tokenexpired?=true'
    #         self.assertRedirects(resp, redirect_url)

    def test_registered_user_login(self):
        """Ensure we can login as users after they have registered."""
        with self.client:
            peter = User(
                **{
                    'email': 'spiderman@newavenger.io',
                    'first_name': 'Peter',
                    'last_name': 'Parker'
                }
            )
            peter.set_password('SpideySenses')
            peter.save()
            tony = User(
                **{
                    'email': 'tony@avengers.io',
                    'first_name': 'Tony',
                    'last_name': 'Stark'
                }
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
            **{
                'email': 'war_machine@avengers.io',
                'first_name': 'James',
                'last_name': 'Rhodey'
            }
        )
        user.set_password('test123')
        user.save()
        with self.client:
            resp_1 = self.client.post(
                '/auth/login',
                data=json.dumps({'password': 'test123'}),
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
                **{
                    'email': 'ant_man@avengers.io',
                    'first_name': 'Scott',
                    'last_name': 'Lang'
                }
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
            **{
                'email': 'metal_arm@newavengers.io',
                'first_name': 'Bucky',
                'last_name': 'Barnes'
            }
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
            **{
                'email': 'falcon@newavengers.io',
                'first_name': 'Sam',
                'last_name': 'Wilson'
            }
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
            session_key = register_session(user, str(token))

            response = self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token),
                    'Session': session_key
                }
            )
            data = json.loads(response.data.decode())
            self.assertIn(
                'success',
                data['status'],
            )
            self.assertIn('Successfully logged out.', data['message'])
            self.assertEqual(response.status_code, 202)

    def test_invalid_logout_expired_token(self):
        user = User(
            **{
                'email': 'tchalla@newavengers.io',
                'first_name': "T'challa",
                'last_name': 'Wakandan'
            }
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
            self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token)
                }
            )
            self.assertRaises(SimCCTBadServerLogout)

    def test_invalid_logout(self):
        with self.client:
            self.client.get(
                '/auth/logout', headers={'Authorization': 'Bearer invalid'}
            )
            self.assertRaises(SimCCTBadServerLogout)

    def test_invalid_auth_header(self):
        with self.client:
            self.client.get('/auth/logout', headers={})
            self.assertRaises(SimCCTBadServerLogout)

    def test_user_status(self):
        user = User(
            **{
                'email': 'scarlet_witch@avengers.io',
                'first_name': 'Wanda',
                'last_name': 'Maximoff'
            }
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
            **{
                'email': 'most_hated_avenger@disney.com',
                'first_name': 'Carol',
                'last_name': 'Danvers'
            }
        )
        user.set_password('OnlyHereBecauseOfFeminism')
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
            user.reload()
            user.active = False
            user.save()

            session_key = register_session(user, str(token))

            response = self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token),
                    'Session': session_key
                }
            )
            data = json.loads(response.data.decode())
            self.assertEqual('This user does not exist.', data['message'])
            self.assertEqual('fail', data['status'])
            self.assertEqual(response.status_code, 401)

    def test_invalid_status_inactive(self):
        """Ensure if user is not active they can't get a status."""
        user = User(
            **{
                'email': 'daredevil@marvel.io',
                'first_name': 'Matthew',
                'last_name': 'Murdock'
            }
        )
        user.set_password('BlindLawyer')
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
            user.reload()
            user.active = False
            user.save()
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'This user account has been disabled.'
            )
            self.assertEqual(response.status_code, 401)

    def test_change_pw_empty_json(self):
        with current_app.test_client() as client:
            token = self.login(client)

            res = client.put(
                '/auth/password/change',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_change_pw_no_old_pw(self):
        with current_app.test_client() as client:
            token = self.login(client)

            res = client.put(
                '/auth/password/change',
                data=json.dumps({'password': ''}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Must provide the current password.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert401(res)

    def test_change_pw_missing_other_pw(self):
        with current_app.test_client() as client:
            token = self.login(client)

            res = client.put(
                '/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'BothEyesOpen!',
                        'new_password': 'LastTimeITrustedSomeone'
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'],
                'Must provide a password and confirm password.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            res = client.put(
                '/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'BothEyesOpen!',
                        'confirm_password': 'LastTimeITrustedSomeone'
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'],
                'Must provide a password and confirm password.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_change_pw_invalid_pw(self):
        with current_app.test_client() as client:
            token = self.login(client)

            res = client.put(
                '/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'BothEyesOpen!',
                        'new_password': 'bad',
                        'confirm_password': 'bad'
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'The password is invalid.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_change_pw_not_matching_pw(self):
        with current_app.test_client() as client:
            token = self.login(client)

            res = client.put(
                '/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'BothEyesOpen!',
                        'new_password': 'Justascratch',
                        'confirm_password': 'JustaScratch!'
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Passwords do not match.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_change_pw_bad_current_pw(self):
        with current_app.test_client() as client:
            token = self.login(client)

            res = client.put(
                '/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'WhosACutie..',
                        'new_password': 'JustaScratch!',
                        'confirm_password': 'JustaScratch!'
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Password is not correct.')
            self.assertEqual(data['status'], 'fail')
            self.assert401(res)

    def test_change_pw_inactive_user(self):
        hill = User(
            **{
                'first_name': 'Maria',
                'last_name': 'Hill',
                'email': 'mariahill@arclytics.io'
            }
        )
        hill.set_password('#EyeCandy')
        hill.verified = True
        hill.save()

        with current_app.test_client() as client:
            token = self.login(client, email=hill.email, password='#EyeCandy')

            hill.reload()
            hill.active = False
            hill.save()

            res = client.put(
                '/auth/password/change',
                data=json.dumps(
                    {
                        'password': '#EyeCandy',
                        'new_password': 'RogerThat',
                        'confirm_password': 'RogerThat'
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'This user account has been disabled.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert401(res)

    def test_change_pw_unverified_user(self):
        sif = User(
            **{
                'first_name': 'Lady',
                'last_name': 'Sif',
                'email': 'sif@arclytics.io'
            }
        )
        sif.set_password('WarriorsThree$')
        sif.verified = False
        sif.save()

        with current_app.test_client() as client:
            token = self.login(
                client, email=sif.email, password='WarriorsThree$'
            )

            res = client.put(
                '/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'WarriorsThree$',
                        'new_password': 'Charge!!!',
                        'confirm_password': 'Charge!!!'
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'User needs to verify account.')
            self.assertEqual(data['status'], 'fail')
            self.assert401(res)

    def test_change_pw_success(self):
        fury = User(
            **{
                'first_name': 'Nick',
                'last_name': 'Fury',
                'email': 'admin@arclytics.io'
            }
        )
        fury.set_password('RealFury!')
        fury.verified = True
        fury.save()

        with current_app.test_client() as client:
            token = self.login(client, email=fury.email, password='RealFury!')

            res = client.put(
                '/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'RealFury!',
                        'new_password': 'BothEyesOpen!',
                        'confirm_password': 'BothEyesOpen!'
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Successfully changed password.')
            self.assertEqual(data['status'], 'success')
            self.assert200(res)

    def test_change_email_success(self):
        obiwan = User(
            email='obiwankenobi@arclytics.com',
            first_name='Obi-Wan',
            last_name='Kenobi'
        )
        obiwan.set_password('TVShowPlease')
        obiwan.save()

        token = log_test_user_in(self, obiwan, 'TVShowPlease')

        with self.client:
            resp = self.client.put(
                '/auth/email/change',
                # data=json.dumps({'new_email': 'brickmatic479@gmail.com'}),
                data=json.dumps({'new_email': 'obiwan@arclytics.io'}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Email changed.')
            self.assertEqual(data['new_email'], 'obiwan@arclytics.io')
            # self.assertEqual(data['new_email'], 'brickmatic479@gmail.com')

            obi_updated = User.objects.get(id=obiwan.id)
            self.assertEqual(obi_updated.email, 'obiwan@arclytics.io')
            # self.assertEqual(obi_updated.email, 'brickmatic479@gmail.com')

    def test_change_email_empty_payload(self):
        obiwan = User(
            email='obiwankenobi@arclytics.io',
            first_name='Obi-Wan',
            last_name='Kenobi'
        )
        obiwan.set_password('TVShowPlease')
        obiwan.save()

        token = log_test_user_in(self, obiwan, 'TVShowPlease')

        with self.client:
            resp = self.client.put(
                '/auth/email/change',
                data=json.dumps(''),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_change_email_no_email(self):
        vader = User(
            email='darthvader@arclytics.io',
            first_name='Darth',
            last_name='Vader'
        )
        vader.set_password('AllTooEasy')
        vader.save()

        token = log_test_user_in(self, vader, 'AllTooEasy')

        with self.client:
            resp = self.client.put(
                '/auth/email/change',
                data=json.dumps({'some_invalid_key': 'some_value'}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No new email given.')

    def test_change_email_invalid_email(self):
        jabba = User(
            email='jabba@arclytics.io',
            first_name='Jabba',
            last_name='The Hutt'
        )
        jabba.set_password('AllTooEasy')
        jabba.save()

        token = log_test_user_in(self, jabba, 'AllTooEasy')

        with self.client:
            resp = self.client.put(
                '/auth/email/change',
                data=json.dumps({'new_email': 'invalid_hutt.com'}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid email.')

    def test_resend_confirm_email_success(self):
        obiwan = User(
            # email='davidmatthews1004@gmail.com',
            email='benkenobi@arclytics.io',
            first_name='Obi-Wan',
            last_name='Kenobi'
        )
        obiwan.set_password('helloThere')
        obiwan.save()
        token = log_test_user_in(self, obiwan, 'helloThere')

        with self.client:
            resp = self.client.get(
                '/confirm/resend',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(
                data['message'], 'Another confirmation email has been sent.'
            )

    def test_resend_confirm_email_already_verified(self):
        obiwan = User(
            email='oldmanben@arclytics.io',
            first_name='Obi-Wan',
            last_name='Kenobi'
        )
        obiwan.set_password('helloThere')
        obiwan.verified = True
        obiwan.save()
        token = log_test_user_in(self, obiwan, 'helloThere')

        with self.client:
            resp = self.client.get(
                '/confirm/resend',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User is already verified.')

    def test_check_password_success(self):
        luke = User(
            email='luke@arclytics.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('IAmAJedi')
        luke.save()

        token = log_test_user_in(self, luke, 'IAmAJedi')

        with self.client:
            resp = self.client.post(
                '/auth/password/check',
                data=json.dumps({'password': 'IAmAJedi'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(resp.status_code, 200)

    def test_check_password_incorrect_password(self):
        luke = User(
            email='lukeskywalker@arclytics.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('IAmAJedi')
        luke.save()

        token = log_test_user_in(self, luke, 'IAmAJedi')

        with self.client:
            resp = self.client.post(
                '/auth/password/check',
                data=json.dumps({'password': 'IAmNotAJedi'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'Password incorrect.')

    def test_geolocation_data_on_login(self):
        jyn = User(
            first_name='Jyn', last_name='Erso', email='jynerso@arclytics.io'
        )
        jyn.set_password('stardust')
        jyn.save()

        token = log_test_user_in(self, jyn, 'stardust')
        with self.client:
            session_key = register_session(jyn, str(token))

            self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token),
                    'Session': session_key
                }
            )

        token_2 = log_test_user_in(self, jyn, 'stardust')
        with self.client:
            session_key_2 = register_session(jyn, str(token_2))

            self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token_2),
                    'Session': session_key_2
                }
            )

        token_3 = log_test_user_in(self, jyn, 'stardust')
        with self.client:
            session_key_3 = register_session(jyn, str(token_3))

            self.client.get(
                '/auth/logout',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token_3),
                    'Session': session_key_3
                }
            )

            jyn_updated = User.objects.get(email=jyn.email)
            self.assertEqual(jyn_updated.login_data.count(), 3)


if __name__ == '__main__':
    unittest.main()
