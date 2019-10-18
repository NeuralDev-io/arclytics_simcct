# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_forgot_password.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__status__ = 'development'
__date__ = '2019.07.26'
"""test_api_forgot_password.py: 

{Description}
"""

import unittest
import os

from flask import current_app as app
from flask import json
from mongoengine import get_db

from sim_api.extensions import bcrypt
from sim_api.models import User, UserProfile, AdminProfile
from tests.test_api_base import BaseTestCase
from sim_api.token import generate_url, generate_confirmation_token


class TestForgotPassword(BaseTestCase):
    def tearDown(self) -> None:
        db = get_db('default')
        self.assertTrue(db.name, 'arc_test')
        db.users.drop()

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete users collection so no conflict."""
        db = get_db('default')
        assert db.name == 'arc_test'
        db.users.drop()

    def preprocess_reset_password(self, client):
        # We do some setup first to get a valid token.
        email = 'punisher@arclytics.neuraldev.io'
        user = User(email=email, first_name='Frank', last_name='Castle')
        user.set_password('IAmThePunisher!!!')
        user.verified = True
        user.save()

        url_token = generate_confirmation_token(email)
        reset_url = generate_url('auth.confirm_reset_password', url_token)

        res = client.get(
            reset_url,
            content_type='application/json',
        )
        self.assertTrue(res.headers['Location'])
        jwt_token = res.headers['Location'].split('=')[1]
        return url_token, jwt_token, user

    def test_invalid_json_body_reset_password_email(self):
        """Ensure an empty request body fails during reset password."""
        with app.test_client() as client:
            res = client.post(
                '/v1/sim/reset/password',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_invalid_json_body_no_email(self):
        """Ensure a request body without email fails."""
        with app.test_client() as client:
            res = client.post(
                '/v1/sim/reset/password',
                data=json.dumps(
                    {'address': '123 Forgetful Street, Old Town, 2222'}
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_reset_password_email_invalid_email(self):
        """Ensure if an invalid email we receive an error from validation."""
        with app.test_client() as client:
            res = client.post(
                '/v1/sim/reset/password',
                data=json.dumps({'email': 'bademail@nodomain'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err_msg = (
                'The domain name nodomain is not valid. '
                'It should have a period.'
            )
            self.assertEqual(data['error'], err_msg)
            # self.assertTrue(data['error'])
            self.assertEqual(data['message'], 'Invalid email.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            # This validation requires an internet access
            # res = client.post(
            #     '/reset/password',
            #     data=json.dumps({'email': 'bademail@nodomain.jhkfdf'}),
            #     content_type='application/json'
            # )
            # data = json.loads(res.data.decode())
            # err_msg = 'The domain name nodomain.random does not exist.'
            # self.assertTrue(data['error'])
            # self.assertEqual(data['error'], err_msg)
            # self.assertEqual(data['message'], 'Invalid email.')

            res = client.post(
                '/v1/sim/reset/password',
                data=json.dumps({'email': 'bademailatyahoo.com'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err_msg = (
                'The email address is not valid. It must have exactly '
                'one @-sign.'
            )
            # self.assertTrue(data['error'])
            self.assertEqual(data['error'], err_msg)
            self.assertEqual(data['message'], 'Invalid email.')

    def test_reset_password_email_no_user_exists(self):
        """Ensure if the user does not exist we don't send an email."""
        with app.test_client() as client:
            res = client.post(
                '/v1/sim/reset/password',
                data=json.dumps({'email': 'carol@systemssecurity.com'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            # For security reasons, the endpoint will return success even if the
            # user does not exist.
            # self.assertEqual(data['message'], 'User does not exist.')
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)

    def test_reset_password_email_not_verified_user(self):
        """Ensure if user has not confirmed email no reset password."""
        user = User(
            email='loki@asgard.space',
            first_name='Loki',
            last_name='Frostgiant'
        )
        user.set_password('GodOfTrickery')
        user.verified = False  # ensure they are not accidentally verified
        user.save()

        with app.test_client() as client:
            res = client.post(
                '/v1/sim/reset/password',
                data=json.dumps({'email': 'loki@asgard.space'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'The user must verify their email.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert401(res)

    def test_reset_password_email_success(self):
        """Ensure we get the response after sending email."""
        email = 'happy@arclytics.com'
        user = User(email=email, first_name='Happy', last_name='Hogan')
        user.set_password('ImIronsManBodyguard')
        user.verified = True
        user.save()
        with app.test_client() as client:
            res = client.post(
                '/v1/sim/reset/password',
                data=json.dumps({'email': email}),
                content_type='application/json',
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)

    def test_confirm_reset_password_bad_token(self):
        """Ensure if we send a bad token it will not be confirmed."""
        bad_token = 'test@test.com'
        reset_url = generate_url('auth.confirm_reset_password', bad_token)
        with app.test_client() as client:
            res = client.get(reset_url, content_type='application/json')
            # data = json.loads(res.data.decode())
            # self.assertEqual(data['error'], 'Bad signature.')
            # self.assertEqual(data['message'], 'Invalid token.')
            # self.assertEqual(data['status'], 'fail')
            # self.assert400(res)
            self.assertEquals(res.status_code, 302)
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = (
                f"{protocol}://{client_host}:{client_port}/password/"
                "reset?tokenexpired=true"
            )

    def test_confirm_reset_password_successful_redirect(self):
        """Ensure if we send a valid token it will redirect."""
        email = 'test@test.com'
        user = User(email=email, first_name='Test', last_name='User')
        user.set_password('Testing123')
        user.save()
        token = generate_confirmation_token(email)
        reset_url = generate_url('auth.confirm_reset_password', token)
        with app.test_client() as client:
            res = client.get(
                reset_url,
                content_type='application/json',
            )
            # self.assertEquals(res.status_code, 302)
            # self.assertTrue(res.headers['Authorization'])
            # self.assertTrue(res.headers['Location'])
            # Every redirect will be different.
            token = res.headers['Location'].split('=')[1]
            # redirect_url = f'http://localhost:3000/password/reset={token}'
            # self.assertRedirects(res, redirect_url)
            self.assertEquals(res.status_code, 302)
            protocol = os.environ.get('CLIENT_SCHEME')
            client_host = os.environ.get('CLIENT_HOST')
            client_port = os.environ.get('CLIENT_PORT')
            redirect_url = (
                f"{protocol}://{client_host}:{client_port}/rest/password/"
                f"{token}"
            )

    def test_reset_password_no_token(self):
        """Ensure if no token is provided it fails."""
        with app.test_client() as client:
            res = client.put(
                '/v1/sim/auth/password/reset',
                data=json.dumps({}),  # token will fail before data
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Provide a valid JWT auth token.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_reset_password_invalid_token(self):
        """Ensure if we provide an invalid token we get the message."""
        token = ''
        with app.test_client() as client:
            res = client.put(
                '/v1/sim/auth/password/reset',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Invalid token. Please get a new token.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert401(res)

    def test_reset_password_bad_json_data(self):
        """Ensure if we provide no json data we fail."""
        with app.test_client() as client:
            _, jwt_token, user = self.preprocess_reset_password(client)

            res = client.put(
                '/v1/sim/auth/password/reset',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {jwt_token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_reset_pass_bad_password_request(self):
        """Ensure we validate for bad passwords."""
        with app.test_client() as client:
            # We do some setup first to get a valid token.
            _, jwt_token, user = self.preprocess_reset_password(client)

            # Both requests have one or the other required request body
            res1 = client.put(
                '/v1/sim/auth/password/reset',
                data=json.dumps({
                    'password': 'IDontNeedToConfirm'
                }),
                headers={'Authorization': f'Bearer {jwt_token}'},
                content_type='application/json'
            )
            res2 = client.put(
                '/v1/sim/auth/password/reset',
                data=json.dumps({
                    'confirm_password': 'IDontNeedToConfirm'
                }),
                headers={'Authorization': f'Bearer {jwt_token}'},
                content_type='application/json'
            )
            data1 = json.loads(res1.data.decode())
            data2 = json.loads(res2.data.decode())
            msg = 'Must provide a password and confirm password.'
            self.assertEqual(data1['message'], msg)
            self.assertEqual(data2['message'], msg)
            self.assert400(res1)
            self.assert400(res2)

            res3 = client.put(
                '/v1/sim/auth/password/reset',
                data=json.dumps(
                    {
                        'password': 'short',
                        'confirm_password': 'short'
                    }
                ),
                headers={'Authorization': f'Bearer {jwt_token}'},
                content_type='application/json'
            )
            data3 = json.loads(res3.data.decode())
            self.assertEqual(data3['message'], 'The password is invalid.')
            self.assert400(res3)

    def test_reset_password_not_match_passwords(self):
        """Ensure if the passwords are not the same it doesn't succeed."""
        with app.test_client() as client:
            _, jwt_token, user = self.preprocess_reset_password(client)

            res = client.put(
                '/v1/sim/auth/password/reset',
                data=json.dumps(
                    {
                        'password': 'NewPassword',
                        'confirm_password': 'NewPasword'
                    }
                ),
                headers={'Authorization': f'Bearer {jwt_token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Passwords do not match.')
            self.assert400(res)

    def test_reset_password_not_active_user(self):
        """Ensure if the user is not active they can't reset."""
        with app.test_client() as client:
            _, jwt_token, user = self.preprocess_reset_password(client)
            user.active = False
            user.save()

            res = client.put(
                '/v1/sim/auth/password/reset',
                data=json.dumps(
                    {
                        'password': 'NewPassword',
                        'confirm_password': 'NewPassword'
                    }
                ),
                headers={'Authorization': f'Bearer {jwt_token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            # self.assertEqual(data['message'], 'User does not exist.')
            # self.assert401(res)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)

    def test_reset_password_success(self):
        """Ensure we go through the whole reset password correctly."""
        with app.test_client() as client:
            # We do some setup first to get a valid token.
            _, jwt_token, user = self.preprocess_reset_password(client)
            original_pw = 'IAmThePunisher!!!'
            new_pw = 'IAmFrankCastelleone'

            res = client.put(
                '/v1/sim/auth/password/reset',
                data=json.dumps(
                    {
                        'password': new_pw,
                        'confirm_password': new_pw
                    }
                ),
                headers={'Authorization': f'Bearer {jwt_token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)
            user.reload()
            self.assertFalse(
                bcrypt.check_password_hash(user.password, original_pw)
            )
            self.assertTrue(bcrypt.check_password_hash(user.password, new_pw))

    def test_valid_reset_password(self):
        """Ensure everything works correctly with sending a reset email."""
        debug = True
        test_email = (
            'help@arclytics.com' if debug else 'andrew@codeninja55.me'
        )
        user = User(first_name='Andrew', last_name='Che', email=test_email)
        user.set_password('IAmIronManJr')
        user.verified = True
        user.save()

        with app.test_client() as client:
            res = client.post(
                '/v1/sim/reset/password',
                data=json.dumps({'email': test_email}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 202)
            self.assertEqual(data['status'], 'success')


if __name__ == '__main__':
    unittest.main()

#
