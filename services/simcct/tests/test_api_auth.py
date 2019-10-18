# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_auth.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'David Matthews <@tree1004>']
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
from sim_api.models import User
from sim_api.token import generate_confirmation_token, generate_url
from sim_api.extensions.utilities import get_mongo_uri
from tests.test_utilities import test_login


class TestAuthEndpoints(BaseTestCase):
    """This module tests all the authentication endpoints and middleware."""

    user = None

    # def setUp(self) -> None:
    #     self.user = User(
    #         **{
    #             'first_name': 'Nick',
    #             'last_name': 'Fury',
    #             'email': 'fury@arclytics.io'
    #         }
    #     )
    #     self.user.set_password('BothEyesOpen!')
    #     self.user.verified = True
    #     self.user.save()
    #
    # def tearDown(self) -> None:
    #     self.user.delete()
    #
    # @staticmethod
    # def login(client, email='fury@arclytics.io', password='BothEyesOpen!'):
    #     resp_login = client.post(
    #         '/auth/login',
    #         data=json.dumps({
    #             'email': email,
    #             'password': password
    #         }),
    #         content_type='application/json'
    #     )
    #     token = json.loads(resp_login.data.decode())['token']
    #     return token

    def test_user_registration(self):
        """Ensure we can register a user."""
        resp = self.client.post(
            '/v1/sim/auth/register',
            data=json.dumps(
                {
                    # 'email': 'andrew@neuraldev.io',
                    'email': 'natashas@arclytics.io',
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
                '/v1/sim/auth/register',
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
                '/v1/sim/auth/register',
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
                '/v1/sim/auth/register',
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
                '/v1/sim/auth/register',
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
            self.assertIn('Invalid email.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_no_password(self):
        with self.client:
            response = self.client.post(
                '/v1/sim/auth/register',
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
                '/v1/sim/auth/register',
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
            **{
                'email': 'themandolorian@arclytics.io',
                'first_name': 'The',
                'last_name': 'Mandolorian'
            }
        )
        mandolorian.set_password('BountyHuntingIsComplicated')
        mandolorian.save()

        confirm_token = generate_confirmation_token(mandolorian.email)
        confirm_url = generate_url('auth.confirm_email', confirm_token)

        with self.client:
            resp = self.client.get(
                confirm_url, content_type='application/json'
            )
            mongo_client = MongoClient(get_mongo_uri())
            db = mongo_client['arc_test']
            user = db.users.find_one({'email': mandolorian.email})
            print(f'User.verified: {user["verified"]}')

            self.assertEquals(resp.status_code, 302)
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = f"{protocol}://{client_host}:{client_port}"

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
                    'email': 'spiderman@avengers.io',
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
                '/v1/sim/auth/login',
                data=json.dumps(
                    {
                        'email': 'spiderman@avengers.io',
                        'password': 'SpideySenses'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(response_peter.data.decode())
            self.assertIn(data['message'], 'Successfully logged in.')
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(response_peter.content_type == 'application/json')
            self.assertEqual(response_peter.status_code, 200)

            response_tony = self.client.post(
                '/v1/sim/auth/login',
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
            self.assertTrue(response_tony.content_type == 'application/json')
            self.assertEqual(response_tony.status_code, 200)

    def test_empty_user_login(self):
        """Ensure if no request body provided it returns appropriate message."""
        with self.client:
            response = self.client.post(
                '/v1/sim/auth/login',
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
                '/v1/sim/auth/login',
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
                '/v1/sim/auth/login',
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
                '/v1/sim/auth/login',
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
                '/v1/sim/auth/login',
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
            self.assertEqual(response.status_code, 400)

    def test_not_registered_user_login(self):
        with self.client:
            response = self.client.post(
                '/v1/sim/auth/login',
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
            self.assertEqual(
                data['message'], 'Email or password combination incorrect.'
            )
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_bad_auth_token_encoding(self):
        user = User(
            **{
                'email': 'metal_arm@avengers.io',
                'first_name': 'Bucky',
                'last_name': 'Barnes'
            }
        )
        user.set_password('badpassword')
        user.save()
        with self.client:
            response = self.client.post(
                '/v1/sim/auth/login',
                data=json.dumps(
                    {
                        'email': 'metal_arm@avengers.io',
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
            self.assertEqual(response.status_code, 400)

    def test_valid_logout(self):
        user = User(
            **{
                'email': 'falcon@avengers.io',
                'first_name': 'Sam',
                'last_name': 'Wilson'
            }
        )
        user.set_password('NewCaptainAmerica')
        user.save()
        with self.client:
            _ = test_login(self.client, user.email, 'NewCaptainAmerica')

            # user login
            self.client.post(
                '/v1/sim/auth/login',
                data=json.dumps(
                    {
                        'email': 'falcon@avengers.io',
                        'password': 'NewCaptainAmerica'
                    }
                ),
                content_type='application/json'
            )
            # valid token logout

            response = self.client.get('/v1/sim/auth/logout', )
            data = json.loads(response.data.decode())
            self.assertIn(
                'success',
                data['status'],
            )
            self.assertIn('Successfully logged out.', data['message'])
            self.assertEqual(response.status_code, 202)

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
            cookie = test_login(
                self.client, user.email, 'YouTookEverythingFromMe!'
            )

            resp_login = self.client.post(
                '/v1/sim/auth/login',
                data=json.dumps(
                    {
                        'email': 'scarlet_witch@avengers.io',
                        'password': 'YouTookEverythingFromMe!'
                    }
                ),
                content_type='application/json'
            )
            resp_status = self.client.get(
                '/v1/sim/auth/status', content_type='application/json'
            )
            data = json.loads(resp_status.data.decode())
            self.assertIn('success', data['status'])
            # self.assertTrue(data['data'] is not None)
            # self.assertIn('scarlet_witch@avengers.io', data['data']['email'])
            self.assertTrue(data['active'] is True)
            self.assertEqual(resp_status.status_code, 200)

    def test_invalid_status(self):
        with self.client:
            response = self.client.get(
                '/v1/sim/auth/status',
                headers={'Authorization': 'Bearer invalid'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual('Session token is not valid.', data['message'])
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
            cookie = test_login(
                self.client, user.email, 'OnlyHereBecauseOfFeminism'
            )
            user.reload()
            user.active = False
            user.save()

            response = self.client.get('/v1/sim/auth/logout')
            data = json.loads(response.data.decode())
            self.assertEqual(
                'This user account has been disabled.', data['message']
            )
            self.assertEqual('fail', data['status'])
            self.assertEqual(response.status_code, 403)

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
            cookie = test_login(self.client, user.email, 'BlindLawyer')

            user.reload()
            user.active = False
            user.save()
            response = self.client.get('/v1/sim/auth/status')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'This user account has been disabled.'
            )
            self.assertEqual(response.status_code, 403)

    def test_change_pw_empty_json(self):
        vader = User(
            **{
                'first_name': 'Darth',
                'last_name': 'Vader',
                'email': 'darklordofthesith@arclytics.io'
            }
        )
        vader.set_password('IAmYourFather')
        vader.save()

        with current_app.test_client() as client:
            cookie = test_login(client, vader.email, 'IAmYourFather')

            res = client.put(
                '/v1/sim/auth/password/change',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_change_pw_no_old_pw(self):
        vader = User(
            **{
                'first_name': 'Darth',
                'last_name': 'Vader',
                'email': 'vader@arclytics.io'
            }
        )
        vader.set_password('IAmYourFather')
        vader.save()

        with current_app.test_client() as client:
            cookie = test_login(client, vader.email, 'IAmYourFather')

            res = client.put(
                '/v1/sim/auth/password/change',
                data=json.dumps({'password': ''}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Must provide the current password.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert401(res)

    def test_change_pw_missing_other_pw(self):
        vader = User(
            **{
                'first_name': 'Darth',
                'last_name': 'Vader',
                'email': 'darth@arclytics.io'
            }
        )
        vader.set_password('IAmYourFather')
        vader.save()

        with current_app.test_client() as client:
            cookie = test_login(client, vader.email, 'IAmYourFather')

            res = client.put(
                '/v1/sim/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'BothEyesOpen!',
                        'new_password': 'LastTimeITrustedSomeone'
                    }
                ),
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
                '/v1/sim/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'BothEyesOpen!',
                        'confirm_password': 'LastTimeITrustedSomeone'
                    }
                ),
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
        vader = User(
            **{
                'first_name': 'Darth',
                'last_name': 'Vader',
                'email': 'vaderscoming@arclytics.io'
            }
        )
        vader.set_password('IAmYourFather')
        vader.save()

        with current_app.test_client() as client:
            cookie = test_login(client, vader.email, 'IAmYourFather')

            res = client.put(
                '/v1/sim/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'BothEyesOpen!',
                        'new_password': 'bad',
                        'confirm_password': 'bad'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'The password is invalid.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_change_pw_not_matching_pw(self):
        vader = User(
            **{
                'first_name': 'Darth',
                'last_name': 'Vader',
                'email': 'lordvader@arclytics.io'
            }
        )
        vader.set_password('IAmYourFather')
        vader.save()

        with current_app.test_client() as client:
            cookie = test_login(client, vader.email, 'IAmYourFather')

            res = client.put(
                '/v1/sim/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'IAmYourFather',
                        'new_password': 'Justascratch',
                        'confirm_password': 'JustaScratch!'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Passwords do not match.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_change_pw_bad_current_pw(self):
        vader = User(
            **{
                'first_name': 'Darth',
                'last_name': 'Vader',
                'email': 'darthvaderisawesome@arclytics.io'
            }
        )
        vader.set_password('IAmYourFather')
        vader.verified = True
        vader.save()

        with current_app.test_client() as client:
            cookie = test_login(client, vader.email, 'IAmYourFather')

            res = client.put(
                '/v1/sim/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'WhosACutie..',
                        'new_password': 'JustaScratch!',
                        'confirm_password': 'JustaScratch!'
                    }
                ),
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
            cookie = test_login(client, hill.email, '#EyeCandy')

            hill.reload()
            hill.active = False
            hill.save()

            res = client.put(
                '/v1/sim/auth/password/change',
                data=json.dumps(
                    {
                        'password': '#EyeCandy',
                        'new_password': 'RogerThat',
                        'confirm_password': 'RogerThat'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'This user account has been disabled.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert403(res)

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
            cookie = test_login(client, sif.email, 'WarriorsThree$')

            res = client.put(
                '/v1/sim/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'WarriorsThree$',
                        'new_password': 'Charge!!!',
                        'confirm_password': 'Charge!!!'
                    }
                ),
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
            cookie = test_login(client, fury.email, 'RealFury!')

            res = client.put(
                '/v1/sim/auth/password/change',
                data=json.dumps(
                    {
                        'password': 'RealFury!',
                        'new_password': 'BothEyesOpen!',
                        'confirm_password': 'BothEyesOpen!'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Successfully changed password.')
            self.assertEqual(data['status'], 'success')
            self.assert200(res)

    def test_change_email_success(self):
        user = User(
            **{
                'email': 'obiwankenobi@arclytics.com',
                'first_name': 'Obi-Wan',
                'last_name': 'Kenobi'
            }
        )
        user.set_password('TVShowPlease')
        user.verified = True
        user.save()

        with self.client as client:
            cookie = test_login(client, user.email, 'TVShowPlease')

            resp = client.put(
                '/v1/sim/auth/email/change',
                # data=json.dumps({'new_email': 'brickmatic479@gmail.com'}),
                data=json.dumps({'new_email': 'obiwan@arclytics.com'}),
                content_type='application/json'
            )

            # obiwan.reload()
            # self.assertEqual(obiwan.email, 'obiwan@arclytics.io')
            # self.assertEqual(obiwan.verified, False)
            # # self.assertEqual(obi_updated.email, 'brickmatic479@gmail.com')

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Email changed.')
            self.assertEqual(data['new_email'], 'obiwan@arclytics.com')
            # self.assertEqual(data['new_email'], 'brickmatic479@gmail.com')

    def test_change_email_empty_payload(self):
        user = User(
            **{
                'email': 'obiwankenobi@arclytics.io',
                'first_name': 'Obi-Wan',
                'last_name': 'Kenobi'
            }
        )
        user.set_password('TVShowPlease')
        user.save()

        with self.client:
            cookie = test_login(self.client, user.email, 'TVShowPlease')

            resp = self.client.put(
                '/v1/sim/auth/email/change',
                data=json.dumps(''),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_change_email_no_email(self):
        vader = User(
            **{
                'email': 'darthvader@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Vader'
            }
        )
        vader.set_password('AllTooEasy')
        vader.save()

        with self.client:
            cookie = test_login(self.client, vader.email, 'AllTooEasy')

            resp = self.client.put(
                '/v1/sim/auth/email/change',
                data=json.dumps({'some_invalid_key': 'some_value'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No new email given.')

    def test_change_email_invalid_email(self):
        user = User(
            **{
                'email': 'jabba@arclytics.io',
                'first_name': 'Jabba',
                'last_name': 'The Hutt'
            }
        )
        user.set_password('HanMyBoy')
        user.save()

        with self.client:
            cookie = test_login(self.client, user.email, 'HanMyBoy')

            resp = self.client.put(
                '/v1/sim/auth/email/change',
                data=json.dumps({'new_email': 'invalid_hutt.com'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid email.')

    def test_resend_confirm_email_success(self):
        user = User(
            **{
                # 'email': 'davidmatthews1004@gmail.com',
                'email': 'benkenobi@arclytics.io',
                'first_name': 'Obi-Wan',
                'last_name': 'Kenobi'
            }
        )
        user.set_password('helloThere')
        user.save()

        with self.client as client:
            cookie = test_login(client, user.email, 'helloThere')

            resp = client.get(
                '/v1/sim/confirm/resend', content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(
                data['message'], 'Another confirmation email has been sent.'
            )

    def test_resend_confirm_email_already_verified(self):
        user = User(
            **{
                'email': 'oldmanben@arclytics.io',
                'first_name': 'Obi-Wan',
                'last_name': 'Kenobi'
            }
        )
        user.set_password('helloThere')
        user.verified = True
        user.save()

        with self.client as client:
            cookie = test_login(client, user.email, 'helloThere')

            resp = self.client.get(
                '/v1/sim/confirm/resend', content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User is already verified.')

    def test_check_password_success(self):
        luke = User(
            **{
                'email': 'luke@arclytics.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('IAmAJedi')
        luke.save()

        with self.client as client:
            cookie = test_login(client, luke.email, 'IAmAJedi')

            resp = self.client.post(
                '/v1/sim/auth/password/check',
                data=json.dumps({'password': 'IAmAJedi'}),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(resp.status_code, 200)

    def test_check_password_incorrect_password(self):
        luke = User(
            **{
                'email': 'lukeskywalker@arclytics.io',
                'first_name': 'Luke',
                'last_name': 'Skywalker'
            }
        )
        luke.set_password('IAmAJedi')
        luke.save()

        with self.client as client:
            cookie = test_login(client, luke.email, 'IAmAJedi')

            resp = self.client.post(
                '/v1/sim/auth/password/check',
                data=json.dumps({'password': 'IAmNotAJedi'}),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'Password incorrect.')

    # def test_geolocation_data_on_login(self):
    #     jyn = User(
    #         first_name='Jyn', last_name='Erso', email='jynerso@arclytics.io'
    #     )
    #     jyn.set_password('stardust')
    #     jyn.save()
    #
    #     token = log_test_user_in(self, jyn, 'stardust')
    #     with self.client:
    #         session_key = register_session(jyn, str(token))
    #
    #         self.client.get(
    #             '/auth/logout',
    #             headers={
    #                 'Authorization': 'Bearer {token}'.format(token=token),
    #                 'Session': session_key
    #             }
    #         )
    #
    #     token_2 = log_test_user_in(self, jyn, 'stardust')
    #     with self.client:
    #         session_key_2 = register_session(jyn, str(token_2))
    #
    #         self.client.get(
    #             '/auth/logout',
    #             headers={
    #                 'Authorization': 'Bearer {token}'.format(token=token_2),
    #                 'Session': session_key_2
    #             }
    #         )
    #
    #     token_3 = log_test_user_in(self, jyn, 'stardust')
    #     with self.client:
    #         session_key_3 = register_session(jyn, str(token_3))
    #
    #         self.client.get(
    #             '/auth/logout',
    #             headers={
    #                 'Authorization': 'Bearer {token}'.format(token=token_3),
    #                 'Session': session_key_3
    #             }
    #         )
    #
    #         jyn_updated = User.objects.get(email=jyn.email)
    #         self.assertEqual(jyn_updated.login_data.count(), 3)

    # TODO(davidmatthews1004@gmail.com) write tests for geolocation with
    #  external ip addresses.

    def test_resend_confirm_email_after_registration_user_dne(self):
        with self.client as client:
            resp = client.put(
                '/v1/sim/confirm/register/resend',
                data=json.dumps({'email': 'lordvader@arclytics.com'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            # self.assertEqual(
            #     data['message'], 'User does not exist.'
            # )

    def test_resend_confirm_email_after_registration_already_verified(self):
        user = User(
            **{
                'email': 'kenobi@arclytics.io',
                'first_name': 'Obi-Wan',
                'last_name': 'Kenobi'
            }
        )
        user.set_password('helloThere')
        user.verified = True
        user.save()

        with self.client as client:
            resp = client.put(
                '/v1/sim/confirm/register/resend',
                data=json.dumps({'email': 'kenobi@arclytics.io'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            # self.assertEqual(data['status'], 'success')
            # self.assertEqual(
            #     data['message'], 'User is already verified.'
            # )

    def test_resend_confirm_email_after_registration_success(self):
        user = User(
            **{
                'email': 'kenobi@arclytics.com',
                'first_name': 'Obi-Wan',
                'last_name': 'Kenobi'
            }
        )
        user.set_password('helloThere')
        user.save()

        with self.client as client:
            resp = client.put(
                '/v1/sim/confirm/register/resend',
                data=json.dumps({'email': 'kenobi@arclytics.com'}),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            # self.assertEqual(
            #     data['message'], 'Another confirmation email has been sent.'
            # )


if __name__ == '__main__':
    unittest.main()
