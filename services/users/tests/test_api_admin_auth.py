# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_admin_auth.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'David Matthews <@tree1004>']

__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'
"""test_api_admin_auth.py: 

This script will run all tests on the Admin create and account disable 
endpoints.
"""

import json
import unittest

from flask import current_app
from itsdangerous import URLSafeTimedSerializer

from tests.test_api_base import BaseTestCase
from logger.arc_logger import AppLogger
from users_app.models import (User, AdminProfile)
from users_app.token import (
    generate_confirmation_token, generate_url,
    generate_promotion_confirmation_token
)

logger = AppLogger(__name__)


# TODO(davidmatthews1004@gmail.com) If possible, import this so its not
#  repeated.
def log_test_user_in(self, user: User, password: str) -> str:
    """Log in a test user and return their token"""
    with self.client:
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps({
                'email': user.email,
                'password': password
            }),
            content_type='application/json'
        )
        token = json.loads(resp_login.data.decode())['token']
        return token


class TestAdminCreateService(BaseTestCase):
    """Tests for Admin creation and disable account endpoints"""

    def test_disable_account(self):
        """Test disable account is successful"""
        kylo = User(
            email='kyloren@gmail.com', first_name='Kylo', last_name='Ren'
        )
        kylo.set_password('LetStarWarsDie')
        kylo.save()

        vader = User(
            email='vader@sith.com', first_name='Darth', last_name='Vader'
        )
        vader.set_password('AllTooEasy')
        # vader.is_admin = True
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        vader.save()

        token = log_test_user_in(self, vader, 'AllTooEasy')

        with self.client:
            resp_disable = self.client.put(
                '/user/disable',
                data=json.dumps({'email': 'kyloren@gmail.com'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp_attempt_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'kyloren@gmail.com',
                        'password': 'LetStarWarsDie'
                    }
                ),
                content_type='application/json'
            )

            disable_data = json.loads(resp_disable.data.decode())
            self.assertEqual(resp_disable.status_code, 200)
            self.assertEqual(disable_data['status'], 'success')
            self.assertEqual(
                disable_data['message'],
                f'The account for User {kylo.email} has been disabled.'
            )

            login_data = json.loads(resp_attempt_login.data.decode())
            self.assertEqual(resp_attempt_login.status_code, 401)
            self.assertEqual(login_data['status'], 'fail')
            self.assertEqual(
                login_data['message'], 'Your Account has been disabled.'
            )

    def test_disable_account_no_data(self):
        """Test empty disable request is unsuccessful"""
        jarjar = User(
            first_name='Jar Jar', last_name='Binks', email='jarjar@binks.com'
        )
        jarjar.set_password('MeesaMakePassword')
        # jarjar.is_admin = True
        jarjar.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        jarjar.save()

        token = log_test_user_in(self, jarjar, 'MeesaMakePassword')

        with self.client:
            resp = self.client.put(
                '/user/disable',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_disable_account_dne(self):
        """Test disable non-existent account is unsuccessful."""
        r2d2 = User(
            first_name='R2', last_name='D2', email='r2d2@astromech.com'
        )
        r2d2.set_password('Weeeeeew')
        # r2d2.is_admin = True
        r2d2.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        r2d2.save()

        token = log_test_user_in(self, r2d2, 'Weeeeeew')

        with self.client:
            resp = self.client.put(
                '/user/disable',
                data=json.dumps({'email': 'c3p0@protocol.com'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 404)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User does not exist.')

    def test_disable_account_no_email(self):
        """
        Ensure a disable request is rejected when no email is provided.
        """
        vader = User(
            email='vader@sith.com', first_name='Darth', last_name='Vader'
        )
        vader.set_password('AllTooEasy')
        # vader.is_admin = True
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        vader.save()

        token = log_test_user_in(self, vader, 'AllTooEasy')

        with self.client:
            resp_disable = self.client.put(
                '/user/disable',
                data=json.dumps({'invalid_key': 'invalid_data'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp_disable.data.decode())
            self.assertEqual(resp_disable.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No email provided.')

    def test_disable_account_invalid_email(self):
        """
        Ensure a disable request is rejected if an invalid email is provided.
        """
        vader = User(
            email='vader@sith.com', first_name='Darth', last_name='Vader'
        )
        vader.set_password('AllTooEasy')
        # vader.is_admin = True
        vader.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        vader.save()

        token = log_test_user_in(self, vader, 'AllTooEasy')

        with self.client:
            resp_disable = self.client.put(
                '/user/disable',
                data=json.dumps({'email': 'invalid_email.com'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp_disable.data.decode())
            self.assertEqual(resp_disable.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid email.')

    def test_use_disable_account(self):
        """Ensure a disabled user is not able to interact with the system."""
        grevious = User(
            first_name='General',
            last_name='Grevious',
            email='grevious@separatists.com'
        )
        grevious.set_password('YouAreABoldOne')
        # grevious.is_admin = True
        grevious.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        grevious.save()

        droid = User(
            first_name='Idiot', last_name='Droid', email='idiot@droids.com'
        )
        droid.set_password('ButIJustGotPromoted')
        droid.save()

        grevious_token = log_test_user_in(self, grevious, 'YouAreABoldOne')

        droid_token = log_test_user_in(self, droid, 'ButIJustGotPromoted')

        with self.client:
            grevious_disable = self.client.put(
                '/user/disable',
                data=json.dumps({'email': 'idiot@droids.com'}),
                headers={'Authorization': 'Bearer {}'.format(grevious_token)},
                content_type='application/json'
            )

            droid_action = self.client.get(
                '/user',
                headers={'Authorization': 'Bearer {}'.format(droid_token)},
                content_type='application/json'
            )

            disable_data = json.loads(grevious_disable.data.decode())
            self.assertEqual(grevious_disable.status_code, 200)
            self.assertEqual(disable_data['status'], 'success')
            self.assertEqual(
                disable_data['message'],
                f'The account for User {droid.email} has been disabled.'
            )

            action_data = json.loads(droid_action.data.decode())
            self.assertEqual(droid_action.status_code, 401)
            self.assertEqual(action_data['status'], 'fail')
            self.assertEqual(
                action_data['message'], 'This user account has been disabled.'
            )

    def test_create_admin_success(self):
        """Test create admin is successful"""
        quigon = User(
            first_name='Qui-Gon',
            last_name='Jinn',
            email="davidmatthews1004@gmail.com"
        )
        # quigon.is_admin = True
        quigon.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        quigon.set_password('ShortNegotiations')
        quigon.save()

        obiwan = User(
            first_name='Obi-Wan',
            last_name='Kenobi',
            email='brickmatic479@gmail.com'
        )
        obiwan.verified = True
        obiwan.set_password('FromACertainPointOfView')
        obiwan.save()

        token = log_test_user_in(self, quigon, 'ShortNegotiations')

        with self.client:
            resp = self.client.post(
                '/admin/create',
                data=json.dumps(
                    {
                        'email': 'brickmatic479@gmail.com',
                        'position': 'Jedi Knight.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(resp.status_code, 202)

    def test_create_admin_invalid_email(self):
        """Test create admin with invalid email is unsuccessful"""
        luke = User(
            first_name='Luke',
            last_name='Skywalker',
            email="lukeskywalker@gmail.com"
        )
        # luke.is_admin = True
        luke.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        luke.set_password('IAmAJediLikeMyFatherBeforeMe')
        luke.save()

        biggs = User(
            first_name='Biggs',
            last_name='Darklighter',
            email='invalidbiggs@dot.com'
        )
        biggs.set_password('LukePullUp')
        biggs.save()

        token = log_test_user_in(self, luke, 'IAmAJediLikeMyFatherBeforeMe')

        with self.client:
            resp = self.client.post(
                '/admin/create',
                data=json.dumps(
                    {
                        'email': 'invalidbiggs@abcdefghijklmopqrstuvwxyz.com',
                        'position': 'Red Three'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['message'], 'Invalid email.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)

    def test_create_unverified_admin(self):
        """Test create admin from unverified user is unsuccessful"""
        ackbar = User(
            first_name='Admiral',
            last_name='Ackbar',
            email='admiralackbar@gmail.com'
        )
        ackbar.set_password('ITSATRAP')
        # ackbar.is_admin = True
        ackbar.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        ackbar.save()

        jyn = User(
            first_name='Jyn',
            last_name='Erso',
            email='brickmatic479@gmail.com'
        )
        jyn.set_password('RebellionsAreBuiltOnHope')
        jyn.save()

        token = log_test_user_in(self, ackbar, 'ITSATRAP')

        with self.client:
            resp = self.client.post(
                '/admin/create',
                data=json.dumps(
                    {
                        'email': 'brickmatic479@gmail.com',
                        'position': 'Rogue Leader'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 401)
            self.assertEqual(
                data['message'], 'The user must verify their email.'
            )

    def test_create_admin_already_admin(self):
        """
        Ensure an error comes up when trying to make an Admin an Admin
        """
        aayla = User(
            first_name='Aayla',
            last_name='Secura',
            email='aaylasecura@gmail.com'
        )
        aayla.set_password('KilledByBly')
        aayla.verified = True
        # aayla.is_admin = True
        aayla.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        aayla.save()

        luminara = User(
            first_name='Luminara',
            last_name='Unduli',
            email='luminaraunduli@gmail.com'
        )
        luminara.set_password('DiesOffscreen')
        luminara.verified = True
        # luminara.is_admin = True
        luminara.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        luminara.save()

        token = log_test_user_in(self, aayla, 'KilledByBly')

        with self.client:
            resp = self.client.post(
                '/admin/create',
                data=json.dumps(
                    {
                        'email': 'luminaraunduli@gmail.com',
                        'position': 'Jedi Master'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(
                data['message'], 'User is already an Administrator.'
            )

    def test_create_admin_no_data(self):
        """
        Ensure a create admin request with no request body is rejected.
        """
        quigon = User(
            first_name='Qui-Gon',
            last_name='Jinn',
            email="davidmatthews1004@gmail.com"
        )
        # quigon.is_admin = True
        quigon.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        quigon.set_password('ShortNegotiations')
        quigon.save()

        token = log_test_user_in(self, quigon, 'ShortNegotiations')

        with self.client:
            resp = self.client.post(
                '/admin/create',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_create_admin_no_email(self):
        """
        Ensure a create admin request with no email is rejected.
        """
        quigon = User(
            first_name='Qui-Gon',
            last_name='Jinn',
            email="davidmatthews1004@gmail.com"
        )
        # quigon.is_admin = True
        quigon.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        quigon.set_password('ShortNegotiations')
        quigon.save()

        token = log_test_user_in(self, quigon, 'ShortNegotiations')

        with self.client:
            resp = self.client.post(
                '/admin/create',
                data=json.dumps({'position': 'Jedi Knight.'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'No email provided.')

    def test_create_admin_no_position(self):
        """
        Ensure a create admin request with no position is rejected.
        """
        quigon = User(
            first_name='Qui-Gon',
            last_name='Jinn',
            email="davidmatthews1004@gmail.com"
        )
        # quigon.is_admin = True
        quigon.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        quigon.set_password('ShortNegotiations')
        quigon.save()

        token = log_test_user_in(self, quigon, 'ShortNegotiations')

        with self.client:
            resp = self.client.post(
                '/admin/create',
                data=json.dumps({'email': 'brickmatic479@gmail.com'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'No position provided.')

    def test_create_admin_user_dne(self):
        """
        Ensure a create admin request for a user that does not exist is
        rejected.
        """
        quigon = User(
            first_name='Qui-Gon',
            last_name='Jinn',
            email="davidmatthews1004@gmail.com"
        )
        # quigon.is_admin = True
        quigon.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        quigon.set_password('ShortNegotiations')
        quigon.save()

        token = log_test_user_in(self, quigon, 'ShortNegotiations')

        with self.client:
            resp = self.client.post(
                '/admin/create',
                data=json.dumps(
                    {
                        'email': 'brickmatic479@gmail.com',
                        'position': 'Invisible.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 404)
            self.assertEqual(data['message'], 'User does not exist.')

    def test_cancel_promotion_success(self):
        admin = User(
            email='davidmatthews1004@gmail.com',
            first_name='David',
            last_name='Matthews'
        )
        admin.set_password('testing123')
        admin.verified = True
        admin.is_admin = True
        admin_profile = AdminProfile(
            position='Jedi Master', mobile_number=None, verified=True
        )
        admin.admin_profile = admin_profile
        admin.save()

        user = User(
            email='brickmatic479@gmail.com',
            first_name='David',
            last_name='Jnr'
        )
        user.set_password('testing123')
        user.verified = True
        user.save()

        token = generate_promotion_confirmation_token(admin.email, user.email)
        url = generate_url('admin.cancel_promotion', token)
        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            self.assertEquals(resp.status_code, 302)
            self.assertTrue(resp.headers['Location'])
            redirect_url = 'http://localhost:3000/signin'
            self.assertRedirects(resp, redirect_url)

            updated_user = User.objects.get(email=user.email)
            self.assertTrue(not updated_user.is_admin)
            self.assertEqual(updated_user.admin_profile, None)

    def test_cancel_promotion_invalid_token(self):
        token = generate_confirmation_token('arclyticstest@gmail.com')
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            data = json.loads(resp.data.decode())
            self.assertEquals(resp.status_code, 400)
            self.assertEqual(data['message'], 'Invalid Token.')

    def test_cancel_promotion_invalid_token_list(self):
        token = generate_promotion_confirmation_token(
            'arclyticstest@gmail.com',
            '',
        )
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            data = json.loads(resp.data.decode())
            self.assertEquals(resp.status_code, 400)
            self.assertEqual(data['message'], 'Missing information in Token.')

    def test_cancel_promotion_token_list_missing_data(self):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(
            [
                'arclyticstestadmin@gmail.com',
            ],
            salt=current_app.config['SECURITY_PASSWORD_SALT']
        )
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            data = json.loads(resp.data.decode())
            self.assertEquals(resp.status_code, 400)
            self.assertEqual(data['message'], 'Invalid data in Token.')

    def test_cancel_promotion_promoter_not_admin(self):
        admin = User(
            email='davidmatthews1004@gmail.com',
            first_name='David',
            last_name='Matthews'
        )
        admin.set_password('testing123')
        admin.verified = True
        admin.save()

        user = User(
            email='brickmatic479@gmail.com',
            first_name='David',
            last_name='Jnr'
        )
        user.set_password('testing123')
        user.verified = True
        user.save()

        token = generate_promotion_confirmation_token(admin.email, user.email)
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            data = json.loads(resp.data.decode())
            self.assertEquals(resp.status_code, 401)
            self.assertEqual(
                data['message'],
                'User is not authorised to promote other users.'
            )

    def test_cancel_promotion_admin_dne(self):
        token = generate_promotion_confirmation_token(
            'arclyticstestadmin@gmail.com', 'arclyticstestuser@gmail.com'
        )
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            data = json.loads(resp.data.decode())
            self.assertEquals(resp.status_code, 400)
            self.assertEqual(data['message'], 'Administrator does not exist.')

    def test_cancel_promotion_user_dne(self):
        test_admin = User(
            email='arclyticstestadmin@gmail.com',
            first_name='Arclytics',
            last_name='Testadmin'
        )
        test_admin.set_password('testing123'),
        test_admin.save()
        token = generate_promotion_confirmation_token(
            'arclyticstestadmin@gmail.com', 'arclyticstestuser@gmail.com'
        )
        url = generate_url('admin.cancel_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            data = json.loads(resp.data.decode())
            self.assertEquals(resp.status_code, 400)
            self.assertEqual(data['message'], 'Target User does not exist.')

    def test_verify_promotion_success(self):
        admin = User(
            email='davidmatthews1004@gmail.com',
            first_name='David',
            last_name='Matthews'
        )
        admin.set_password('testing123')
        admin.verified = True
        # admin.is_admin = True
        admin_profile = AdminProfile(
            position='Jedi Master', mobile_number=None, verified=True
        )
        admin.admin_profile = admin_profile
        admin.save()

        user = User(
            email='brickmatic479@gmail.com',
            first_name='David',
            last_name='Jnr'
        )
        user.set_password('testing123')
        user.verified = True
        # user.is_admin=True
        user_admin_profile = AdminProfile(
            position='Jedi Knight.', mobile_number=None, verified=False
        )
        user.admin_profile = user_admin_profile
        user.admin_profile.promoted_by = admin.id
        user.save()

        token = generate_confirmation_token(user.email)
        url = generate_url('admin.verify_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            self.assertEquals(resp.status_code, 302)
            self.assertTrue(resp.headers['Location'])
            redirect_url = 'http://localhost:3000/signin'
            self.assertRedirects(resp, redirect_url)

            updated_user = User.objects.get(email=user.email)
            self.assertTrue(updated_user.is_admin)
            self.assertEqual(
                updated_user.admin_profile.position, 'Jedi Knight.'
            )
            self.assertEqual(updated_user.admin_profile.mobile_number, None)
            self.assertEqual(updated_user.admin_profile.verified, True)

    def test_verify_promotion_user_dne(self):
        token = generate_confirmation_token('arclyticstestuser@gmail.com')
        url = generate_url('admin.verify_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            data = json.loads(resp.data.decode())
            self.assertEquals(resp.status_code, 400)
            self.assertEqual(data['message'], 'User does not exist.')

    def test_verify_promotion_user_not_verified(self):
        test_user = User(
            email='arclyticstestuser@gmail.com',
            first_name='Arclytics',
            last_name='Testuser'
        )
        test_user.set_password('testing123')
        test_user.save()

        token = generate_confirmation_token(test_user.email)
        url = generate_url('admin.verify_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            data = json.loads(resp.data.decode())
            self.assertEquals(resp.status_code, 400)
            self.assertEqual(data['message'], 'User is not verified.')

    def test_verify_promotion_user_is_not_admin(self):
        test_user = User(
            email='arclyticstestuser@gmail.com',
            first_name='Arclytics',
            last_name='Testuser'
        )
        test_user.set_password('testing123')
        test_user.verified = True
        test_user.save()

        token = generate_confirmation_token(test_user.email)
        url = generate_url('admin.verify_promotion', token)

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            data = json.loads(resp.data.decode())
            self.assertEquals(resp.status_code, 400)
            self.assertEqual(data['message'], 'User is not an Admin.')


if __name__ == '__main__':
    unittest.main()
