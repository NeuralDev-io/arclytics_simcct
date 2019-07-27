# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_forgot_password.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.26'
"""test_api_forgot_password.py: 

{Description}
"""

import unittest

from flask import current_app as app
from flask import json

from users_app.models import User
from tests.test_api_base import BaseTestCase
from users_app.token import generate_url, generate_confirmation_token


class MyTestCase(BaseTestCase):
    def test_invalid_json_body_reset_password_email(self):
        """Ensure an empty request body fails during reset password."""
        with app.test_client() as client:
            res = client.post(
                '/auth/resetpassword',
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
                '/auth/resetpassword',
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
                '/auth/resetpassword',
                data=json.dumps({'email': 'bademail@nodomain'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err_msg = (
                'The domain name nodomain is not valid. '
                'It should have a period.'
            )
            self.assertTrue(data['error'])
            self.assertEqual(data['error'], err_msg)
            self.assertEqual(data['message'], 'Invalid email.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

            res = client.post(
                '/auth/resetpassword',
                data=json.dumps({'email': 'bademail@nodomain.random'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err_msg = 'The domain name nodomain.random does not exist.'
            self.assertTrue(data['error'])
            self.assertEqual(data['error'], err_msg)
            self.assertEqual(data['message'], 'Invalid email.')

            res = client.post(
                '/auth/resetpassword',
                data=json.dumps({'email': 'bademailatyahoo.com'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            err_msg = (
                'The email address is not valid. It must have exactly '
                'one @-sign.'
            )
            self.assertTrue(data['error'])
            self.assertEqual(data['error'], err_msg)
            self.assertEqual(data['message'], 'Invalid email.')

    def test_reset_password_email_no_user_exists(self):
        """Ensure if the user does not exist we don't send an email."""
        with app.test_client() as client:
            res = client.post(
                '/auth/resetpassword',
                data=json.dumps({'email': 'carol@systemssecurity.com'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'User does not exist.')
            self.assertEqual(data['status'], 'fail')
            self.assert404(res)

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
                '/auth/resetpassword',
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
        email = 'happy@arclytics.neuraldev.io'
        user = User(email=email, first_name='Happy', last_name='Hogan')
        user.set_password('ImIronsManBodyguard')
        user.verified = True
        user.save()
        with app.test_client() as client:
            res = client.post(
                '/auth/resetpassword',
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
            res = client.get(
                reset_url,
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['error'], 'Bad signature.')
            self.assertEqual(data['message'], 'Invalid token.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

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
            self.assertEquals(res.status_code, 302)
            # self.assertTrue(res.headers['Authorization'])
            self.assertTrue(res.headers['Location'])
            # Every redirect will be different.
            token = res.headers['Location'].split('=')[1]
            redirect_url = f'http://localhost:3000/password/reset={token}'
            self.assertRedirects(res, redirect_url)

    def test_reset_password_no_token(self):
        """Ensure if no token is provided it fails."""
        with app.test_client() as client:
            res = client.put(
                '/auth/password/reset',
                data=json.dumps({}),  # token will fail before data
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Provide a valid JWT auth token.')
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_reset_password_invalid_token(self):
        """Ensure if we provide an invalid token we get the message."""
        token = ''
        with app.test_client() as client:
            res = client.put(
                '/auth/password/reset',
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
            # We do some setup first to get a valid token.
            email = 'punisher@arclytics.neuraldev.io'
            user = User(
                email=email, first_name='Frank', last_name='Castle'
            )
            original_pw = 'IAmThePunisher!!!'
            user.set_password(original_pw)
            user.verified = True
            user.save()

            # url_token = generate_confirmation_token(email)
            # reset_url = generate_url('auth.confirm_reset_password', url_token)

            # Shouldn't need to do this but just testing something for now
            # resp = client.post(
            #     '/auth/resetpassword',
            #     data=json.dumps({'email': user.email}),
            #     content_type='application/json'
            # )
            # data = json.loads(resp.data.decode())
            # print(data)

            # res = client.get(
            #     reset_url,
            #     content_type='application/json',
            # )
            # print(res.headers)
            # self.assertTrue(res.headers['Location'])
            # b_token = res.headers['Location'].split('=')[1]
            # str_token = str(b_token)
            token = User.encode_password_reset_token(user.id)
            print(token.__class__)

            res = client.put(
                '/auth/password/reset',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            print(data)
            self.assertEqual(
                data['message'], 'Invalid payload.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_reset_password_success(self):
        """Ensure we go through the whole reset password correctly."""
        with app.test_client() as client:
            # We do some setup first to get a valid token.
            email = 'punisher@marvel.io'
            user = User(
                email=email, first_name='Frank', last_name='Castle'
            )
            original_pw = 'IAmThePunisher!!!'
            user.set_password(original_pw)
            user.verified = True
            user.save()

            token = generate_confirmation_token(email)
            reset_url = generate_url('auth.confirm_reset_password', token)

            res = client.get(
                reset_url,
                content_type='application/json',
            )
            self.assertTrue(res.headers['Location'])
            # Every redirect will be different.
            token = res.headers['Location'].split('=')[1]

            # res = client.put(
            #     '/auth/password/reset',
            #     data=json.dumps({}),
            #     headers={'Authorization': f'Bearer {token}'},
            #     content_type='application/json'
            # )
            # data = json.loads(res.data.decode())

    # def test_valid_reset_password(self):
    #     """Ensure everything works correctly with sending a reset email."""
    #     debug = True
    #     test_email = ('help@arclytics.neuraldev.io'
    #                   if debug
    #                   else 'andrew@codeninja55.me')
    #     user = User(
    #         first_name='Andrew',
    #         last_name='Che',
    #         email=test_email
    #     )
    #     user.set_password('IAmIronManJr')
    #     user.verified = True
    #     user.save()
    #
    #     with app.test_client() as client:
    #         res = client.post(
    #             '/auth/resetpassword',
    #             data=json.dumps({
    #                 'email': test_email
    #             }),
    #             content_type='application/json'
    #         )
    #         data = json.loads(res.data.decode())
    #         self.assertEqual(res.status_code, 202)
    #         self.assertEqual(data['status'], 'success')


if __name__ == '__main__':
    unittest.main()

#
