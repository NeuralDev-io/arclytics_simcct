# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_users.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'David Matthews <@davidjmatthews>']

__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.2.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'
"""test_api_users.py: 

This script will run all tests on the Users endpoints.
"""

import json
import unittest
import time

from bson import ObjectId
from flask import current_app

from tests.test_api_base import BaseTestCase
from logger.arc_logger import AppLogger
from users_app.models import (
    User, UserProfile, AdminProfile, Element, Alloy, Configuration
)
from users_app.token import generate_confirmation_token, generate_url

logger = AppLogger(__name__)


def log_test_user_in(self, user: User, password: str) -> str:
    """Log in a test user and return their token"""
    with self.client:
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps(
                {
                    'email': user.email,
                    'password': password
                }
            ),
            content_type='application/json'
        )
        token = json.loads(resp_login.data.decode())['token']
        return token


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
        tony = User(
            email='tony@starkindustries.com',
            first_name='Tony',
            last_name='Stark'
        )
        tony.set_password('IAmTheRealIronMan')
        tony.save()

        token = log_test_user_in(self, tony, 'IAmTheRealIronMan')

        with self.client:
            resp = self.client.get(
                '/user',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertIn('tony@starkindustries.com', data['data']['email'])

    def test_single_user_not_active(self):
        """
        Ensure if user is not active they can't use authenticated endpoints
        like get: /users/<id>
        """
        tony = User(
            email='tony@starkindustries.com',
            first_name='Tony',
            last_name='Stark'
        )
        tony.set_password('IAmTheRealIronMan')
        tony.save()

        token = log_test_user_in(self, tony, 'IAmTheRealIronMan')

        with self.client:
            # Update Tony to be inactive
            tony.reload()
            tony.active = False
            tony.save()

            resp = self.client.get(
                '/user',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 401)
            self.assertEqual(data['message'], 'This user does not exist.')
            self.assertEqual('fail', data['status'])

    def test_single_user_invalid_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/user')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Provide a valid JWT auth token.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            _id = ObjectId()
            response = self.client.get('/user')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Provide a valid JWT auth token.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_expired_token(self):
        tony = User(
            email='tony@starkindustries.com',
            first_name='Tony',
            last_name='Stark'
        )
        tony.set_password('IAmTheRealIronMan')
        tony.save()
        current_app.config['TOKEN_EXPIRATION_SECONDS'] = -1
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'tony@starkindustries.com',
                        'password': 'IAmTheRealIronMan'
                    }
                ),
                content_type='application/json'
            )
            # invalid token logout
            token = json.loads(resp_login.data.decode())['token']
            response = self.client.get(
                '/user'.format(tony.id),
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

    def test_get_all_users_no_header(self):
        with self.client:
            resp = self.client.get(
                '/users', content_type='application/json', headers={}
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertIn('fail', data['status'])
            self.assertNotIn('data', data)
            self.assertIn('Provide a valid JWT auth token.', data['message'])

    def test_unauthorized_get_all_users(self):
        """Ensure we can't get all users because we are not authorized."""
        tony = User(
            email='tony@starkindustries.com',
            first_name='Tony',
            last_name='Stark'
        )
        tony.set_password('IAmTheRealIronMan')
        tony.is_admin = False
        tony.save()
        nat = User(
            email='nat@shield.gov.us',
            first_name='Natasha',
            last_name='Romanoff'
        )
        nat.set_password('IveGotRedInMyLedger')
        nat.save()

        token = log_test_user_in(self, tony, 'IAmTheRealIronMan')

        with self.client:
            resp = self.client.get(
                '/users',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 403)
            self.assertIn('fail', data['status'])
            self.assertNotIn('data', data)
            self.assertIn('Not authorized.', data['message'])

    def test_get_all_users_expired_token(self):
        thor = User(
            email='thor@avengers.io', first_name='Thor', last_name='Odinson'
        )
        thor.set_password('StrongestAvenger')
        thor.is_admin = True
        thor.save()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'thor@avengers.io',
                        'password': 'StrongestAvenger'
                    }
                ),
                content_type='application/json'
            )
            # token = json.loads(resp_login.data.decode())['token']
            token = 'KJASlkdjlkajsdlkjlkasjdlkjalosd'
            resp = self.client.get(
                '/users',
                headers={
                    'Authorization': 'Bearer {token}'.format(token=token)
                }
            )
            data = json.loads(resp.data.decode())
            self.assertEqual('fail', data['status'])
            self.assertNotIn('data', data)
            self.assertEqual(
                'Invalid token. Please log in again.', data['message']
            )
            self.assertEqual(resp.status_code, 401)

    def test_get_all_users(self):
        """Ensure we can get all users if logged in and authorized."""
        tony = User(
            email='tony@starkindustries.com',
            first_name='Tony',
            last_name='Stark'
        )
        tony.set_password('IAmTheRealIronMan')
        tony.is_admin = True
        tony.verified = True
        tony.save()
        steve = User(
            email='steve@avengers.io', first_name='Steve', last_name='Rogers'
        )
        steve.set_password('ICanDoThisAllDay')
        steve.save()
        nat = User(
            email='nat@shield.gov.us',
            first_name='Natasha',
            last_name='Romanoff'
        )
        nat.set_password('IveGotRedInMyLedger')
        nat.verified = True
        nat.save()

        token = log_test_user_in(self, tony, 'IAmTheRealIronMan')

        with self.client:
            tony.reload()
            self.assertTrue(tony.active)
            resp = self.client.get(
                '/users',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(data['data']['users']), 3)
            self.assertTrue(data['data']['users'][0]['admin'])
            self.assertFalse(data['data']['users'][1]['admin'])
            self.assertIn('success', data['status'])

    def test_patch_user(self):
        """Test update user details"""
        obiwan = User(
            email='obiwan@kenobi.io',
            first_name='Obi Wan',
            last_name = 'kenobi'
        )
        obiwan.set_password('HelloThere')
        obiwan.save()

        token = log_test_user_in(self, obiwan, 'HelloThere')

        with self.client:
            resp = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'first_name': 'Obi-Wan',
                        'last_name': 'Kenobi',
                        'aim': 'Train Skywalkers.',
                        'highest_education': 'Jedi Council Member.',
                        'sci_tech_exp': 'Flying is for Droids.',
                        'phase_transform_exp': 'Prequels.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['first_name'], 'Obi-Wan')
            self.assertEqual(data['last_name'], 'Kenobi')
            self.assertEqual(data['profile']['aim'], 'Train Skywalkers.')
            self.assertEqual(
                data['profile']['highest_education'], 'Jedi Council Member.'
            )
            self.assertEqual(
                data['profile']['sci_tech_exp'], 'Flying is for Droids.'
            )
            self.assertEqual(
                data['profile']['phase_transform_exp'], 'Prequels.'
            )

            updated_user = User.objects.get(email=obiwan.email)
            self.assertEqual(updated_user['first_name'], 'Obi-Wan')
            self.assertEqual(updated_user['last_name'], 'Kenobi')
            self.assertEqual(
                updated_user['profile']['aim'], 'Train Skywalkers.'
            )
            self.assertEqual(
                updated_user['profile']['highest_education'],
                'Jedi Council Member.'
            )
            self.assertEqual(
                updated_user['profile']['sci_tech_exp'], 'Flying is for Droids.'
            )
            self.assertEqual(
                updated_user['profile']['phase_transform_exp'], 'Prequels.'
            )

    def test_patch_admin_user(self):
        """Test update admin user details"""
        yoda = User(
            email='yoda@jedi.io',
            first_name='Yoda',
            last_name='Smith'
        )
        yoda.set_password('DoOrDoNot')
        yoda.is_admin = True
        admin_profile = AdminProfile(
            position='Filler',
            mobile_number=None,
            verified=True
        )
        yoda.admin_profile = admin_profile
        yoda.save()

        token = log_test_user_in(self, yoda, 'DoOrDoNot')

        with self.client:
            resp = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'first_name': 'Yoda',
                        'last_name': 'Smith',
                        'aim': 'Pass on what I have learned.',
                        'highest_education': 'Jedi Temple Professor.',
                        'sci_tech_exp': 'Much to learn, I still have.',
                        'phase_transform_exp': 'I am a puppet.',
                        'mobile_number': '1234567890',
                        'position': 'Grand Jedi Master.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['first_name'], 'Yoda')
            self.assertEqual(data['last_name'], 'Smith')
            self.assertEqual(
                data['profile']['aim'], 'Pass on what I have learned.'
            )
            self.assertEqual(
                data['profile']['highest_education'],
                'Jedi Temple Professor.'
            )
            self.assertEqual(
                data['profile']['sci_tech_exp'],
                'Much to learn, I still have.'
            )
            self.assertEqual(
                data['profile']['phase_transform_exp'],
                'I am a puppet.'
            )
            self.assertEqual(
                data['admin_profile']['mobile_number'],
                '1234567890'
            )
            self.assertEqual(
                data['admin_profile']['position'],
                'Grand Jedi Master.'
            )

            updated_user = User.objects.get(email=yoda.email)
            self.assertEqual(updated_user['first_name'], 'Yoda')
            self.assertEqual(updated_user['last_name'], 'Smith')
            self.assertEqual(
                updated_user['profile']['aim'], 'Pass on what I have learned.'
            )
            self.assertEqual(
                updated_user['profile']['highest_education'],
                'Jedi Temple Professor.'
            )
            self.assertEqual(
                updated_user['profile']['sci_tech_exp'],
                'Much to learn, I still have.'
            )
            self.assertEqual(
                updated_user['profile']['phase_transform_exp'],
                'I am a puppet.'
            )
            self.assertEqual(
                updated_user['admin_profile']['mobile_number'],
                '1234567890'
            )
            self.assertEqual(
                updated_user['admin_profile']['position'],
                'Grand Jedi Master.'
            )

    def test_patch_user_partial(self):
        """Test update only some of the user's details"""
        sheev = User(
            email='sheev@palpatine.io',
            first_name='Sheev',
            last_name='Palpatine'
        )
        sheev.set_password('IAmTheSenate')
        profile = UserProfile(
            aim='filler',
            highest_education='filler',
            sci_tech_exp='filler',
            phase_transform_exp='filler'
        )
        sheev.profile = profile
        sheev.save()

        token = log_test_user_in(self, sheev, 'IAmTheSenate')

        with self.client:
            resp = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'first_name': 'Emperor',
                        'aim': 'Rule the Galaxy.',
                        'phase_transform_exp': 'Sith Lord.',
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['first_name'], 'Emperor')
            self.assertEqual(data['profile']['aim'], 'Rule the Galaxy.')
            self.assertEqual(
                data['profile']['phase_transform_exp'], 'Sith Lord.'
            )

            updated_user = User.objects.get(email=sheev.email)
            self.assertEqual(updated_user['first_name'], 'Emperor')
            self.assertEqual(updated_user['last_name'], 'Palpatine')
            self.assertEqual(updated_user['profile']['aim'], 'Rule the Galaxy.')
            self.assertEqual(
                updated_user['profile']['phase_transform_exp'], 'Sith Lord.'
            )

    def test_patch_user_no_data(self):
        """Try update a user without any data for the update"""
        maul = User(
            email='maul@sith.io',
            first_name='Darth',
            last_name='Maul'
        )
        maul.set_password('AtLastWeWillHaveRevenge')
        maul.save()

        token = log_test_user_in(self, maul, 'AtLastWeWillHaveRevenge')

        with self.client:
            resp = self.client.patch(
                '/user',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_patch_user_existing_profile(self):
        """Test update user details if there is existing outdated data"""
        ahsoka = User(
            email='ahsoka@tano.io',
            first_name='Ahsoka',
            last_name='tano'
        )
        ahsoka.set_password('IAmNoJedi')
        profile = UserProfile(
            aim='Protect my Master',
            highest_education='Jedi Knight',
            sci_tech_exp='Great',
            phase_transform_exp='Less Great'
        )
        ahsoka.profile = profile
        ahsoka.save()

        token = log_test_user_in(self, ahsoka, 'IAmNoJedi')

        with self.client:
            resp = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'last_name': 'Tano',
                        'aim': 'Follow the will of the force.',
                        'highest_education': 'Rogue.',
                        'sci_tech_exp': 'Greater.',
                        'phase_transform_exp': 'Great.',
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['last_name'], 'Tano')
            self.assertEqual(
                data['profile']['aim'], 'Follow the will of the force.'
            )
            self.assertEqual(
                data['profile']['highest_education'], 'Rogue.'
            )
            self.assertEqual(
                data['profile']['sci_tech_exp'], 'Greater.'
            )
            self.assertEqual(
                data['profile']['phase_transform_exp'], 'Great.'
            )

            updated_user = User.objects.get(email=ahsoka.email)
            self.assertEqual(updated_user['last_name'], 'Tano')
            self.assertEqual(
                updated_user['profile']['aim'], 'Follow the will of the force.'
            )
            self.assertEqual(
                updated_user['profile']['highest_education'], 'Rogue.'
            )
            self.assertEqual(
                updated_user['profile']['sci_tech_exp'], 'Greater.'
            )
            self.assertEqual(
                updated_user['profile']['phase_transform_exp'], 'Great.'
            )

    def test_patch_user_invalid_keys(self):
        """
        Send a patch request for user details with invalid keys and ensure it
        is rejected.
        """
        obiwan = User(
            email='obiwan@kenobi.io',
            first_name='Obi Wan',
            last_name='kenobi'
        )
        obiwan.set_password('HelloThere')
        obiwan.save()

        token = log_test_user_in(self, obiwan, 'HelloThere')

        with self.client:
            resp = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'lightsaber_colour': 'blue',
                        'movie_appearances': 'I, II, III, IV, V, VI, VII',
                        'best_star_wars_character': 'Yes'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'Payload does not have any valid keys.'
            )

    def test_patch_user_profile_no_existing_profile_missing_fields(self):
        """Test update user details"""
        obiwan = User(
            email='obiwan@kenobi.io',
            first_name='Obi Wan',
            last_name='kenobi'
        )
        obiwan.set_password('HelloThere')
        obiwan.save()

        token = log_test_user_in(self, obiwan, 'HelloThere')

        with self.client:
            resp = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'first_name': 'Obi-Wan',
                        'last_name': 'Kenobi',
                        'aim': 'Train Skywalkers.',
                        'highest_education': 'Jedi Council Member.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'],
                'User profile cannot be patched as there is no existing profile.'
            )

    def test_patch_admin_existing_admin_profile(self):
        """Test update user details if there is existing outdated data"""
        rex = User(
            email='rex@clone.io',
            first_name='Rex',
            last_name='Republic'
        )
        rex.set_password('ExperienceOutranksEverything')
        profile = UserProfile(
            aim='Serve the Republic',
            highest_education='Clone Captain',
            sci_tech_exp='Limited',
            phase_transform_exp='Limited'
        )
        rex.profile = profile
        rex.is_admin = True
        admin_profile = AdminProfile(
            mobile_number='0987654321',
            position='Captain',
            verified=True
        )
        rex.admin_profile = admin_profile
        rex.save()

        token = log_test_user_in(self, rex, 'ExperienceOutranksEverything')

        with self.client:
            resp = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'mobile_number': '1234567890',
                        'position': 'Discharged.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(
                data['admin_profile']['mobile_number'],
                '1234567890'
            )
            self.assertEqual(
                data['admin_profile']['position'],
                'Discharged.'
            )

            updated_user = User.objects.get(email=rex.email)
            self.assertEqual(
                updated_user['admin_profile']['mobile_number'],
                '1234567890'
            )
            self.assertEqual(
                updated_user['admin_profile']['position'],
                'Discharged.'
            )

    def test_patch_admin_missing_admin_data(self):
        """
        Test update admin user details without updating admin profile details
        """
        ezra = User(
            email='ezra@bridger.io',
            first_name='ezra',
            last_name='bridger'
        )
        ezra.set_password('IKnowWhatWeHaveToDo')
        ezra.is_admin = True
        admin_profile = AdminProfile(
            position='filler',
            mobile_number=None,
            verified=True
        )
        ezra.admin_profile = admin_profile
        ezra.save()

        token = log_test_user_in(self, ezra, 'IKnowWhatWeHaveToDo')

        with self.client:
            resp = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'first_name': 'Ezra',
                        'last_name': 'Bridger',
                        'aim': 'Learn the ways of the force.',
                        'highest_education': 'Lothal Highschool.',
                        'sci_tech_exp': 'Limited.',
                        'phase_transform_exp': 'Limited.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['first_name'], 'Ezra')
            self.assertEqual(data['last_name'], 'Bridger')
            self.assertEqual(
                data['profile']['aim'], 'Learn the ways of the force.'
            )
            self.assertEqual(
                data['profile']['highest_education'],
                'Lothal Highschool.'
            )
            self.assertEqual(
                data['profile']['sci_tech_exp'],
                'Limited.'
            )
            self.assertEqual(
                data['profile']['phase_transform_exp'],
                'Limited.'
            )

            updated_user = User.objects.get(email=ezra.email)
            self.assertEqual(updated_user['first_name'], 'Ezra')
            self.assertEqual(updated_user['last_name'], 'Bridger')
            self.assertEqual(
                updated_user['profile']['aim'], 'Learn the ways of the force.'
            )
            self.assertEqual(
                updated_user['profile']['highest_education'],
                'Lothal Highschool.'
            )
            self.assertEqual(
                updated_user['profile']['sci_tech_exp'],
                'Limited.'
            )
            self.assertEqual(
                updated_user['profile']['phase_transform_exp'],
                'Limited.'
            )

    def test_patch_admin_multiple_patches(self):
        """
        Ensure multiple patches on an admins details work and the final details
        match the final patch.
        """
        kanan = User(
            first_name='kanan',
            last_name='jarrus',
            email='kananjarrus@jediknight.com'
        )
        kanan.set_password('ICantSeeAnythingNow')
        kanan.is_admin=True
        profile = UserProfile(
            aim='filler',
            highest_education='filler',
            sci_tech_exp='filler',
            phase_transform_exp='filler'
        )
        kanan.profile = profile
        admin_profile = AdminProfile(
            position='filler',
            mobile_number=None,
            verified=True
        )
        kanan.admin_profile = admin_profile
        kanan.save()

        token = log_test_user_in(self, kanan, 'ICantSeeAnythingNow')

        with self.client:
            resp_1 = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'first_name': 'Kanan',
                        'last_name': 'Jarrus',
                        'aim': 'Help the Rebellion.',
                        'mobile_number': '1234567890',
                        'position': 'Freedom Fighter.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp_2 = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'highest_education': 'Jedi Padawan.',
                        'sci_tech_exp': 'Limited.',
                        'phase_transform_exp': 'Limited.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data_1 = json.loads(resp_1.data.decode())
            self.assertEqual(resp_1.status_code, 200)
            self.assertEqual(data_1['status'], 'success')
            self.assertEqual(data_1['first_name'], 'Kanan')
            self.assertEqual(data_1['last_name'], 'Jarrus')
            self.assertEqual(
                data_1['profile']['aim'], 'Help the Rebellion.'
            )
            self.assertEqual(
                data_1['admin_profile']['mobile_number'],
                '1234567890'
            )
            self.assertEqual(
                data_1['admin_profile']['position'],
                'Freedom Fighter.'
            )

            data_2 = json.loads(resp_2.data.decode())
            self.assertEqual(resp_2.status_code, 200)
            self.assertEqual(data_2['status'], 'success')
            self.assertEqual(
                data_2['profile']['highest_education'],
                'Jedi Padawan.'
            )
            self.assertEqual(
                data_2['profile']['sci_tech_exp'],
                'Limited.'
            )
            self.assertEqual(
                data_2['profile']['phase_transform_exp'],
                'Limited.'
            )

            updated_user = User.objects.get(email=kanan.email)
            self.assertEqual(updated_user['first_name'], 'Kanan')
            self.assertEqual(updated_user['last_name'], 'Jarrus')
            self.assertEqual(
                updated_user['profile']['aim'], 'Help the Rebellion.'
            )
            self.assertEqual(
                updated_user['profile']['highest_education'],
                'Jedi Padawan.'
            )
            self.assertEqual(
                updated_user['profile']['sci_tech_exp'],
                'Limited.'
            )
            self.assertEqual(
                updated_user['profile']['phase_transform_exp'],
                'Limited.'
            )
            self.assertEqual(
                updated_user['admin_profile']['mobile_number'],
                '1234567890'
            )
            self.assertEqual(
                updated_user['admin_profile']['position'],
                'Freedom Fighter.'
            )

    def test_patch_invalid_admin(self):
        """Test update user details"""
        obiwan = User(
            email='obiwan@kenobi.io',
            first_name='Obi Wan',
            last_name='kenobi'
        )
        obiwan.set_password('HelloThere')
        obiwan.is_admin=True
        obiwan.save()

        token = log_test_user_in(self, obiwan, 'HelloThere')

        with self.client:
            resp = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'first_name': 'Obi-Wan',
                        'last_name': 'Kenobi',
                        'aim': 'Train Skywalkers.',
                        'highest_education': 'Jedi Council Member.',
                        'sci_tech_exp': 'Flying is for Droids.',
                        'phase_transform_exp': 'Prequels.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'],
                'User admin profile is invalid and cannot be patched.'
            )

    def test_patch_unverified_admin(self):
        """Test update user details"""
        obiwan = User(
            email='obiwan@kenobi.io',
            first_name='Obi Wan',
            last_name='kenobi'
        )
        obiwan.set_password('HelloThere')
        obiwan.is_admin=True
        admin_profile = AdminProfile(
            position='Filler',
            mobile_number=None,
            verified=False
        )
        obiwan.admin_profile = admin_profile
        obiwan.save()

        token = log_test_user_in(self, obiwan, 'HelloThere')

        with self.client:
            resp = self.client.patch(
                '/user',
                data=json.dumps(
                    {
                        'first_name': 'Obi-Wan',
                        'last_name': 'Kenobi',
                        'aim': 'Train Skywalkers.',
                        'highest_education': 'Jedi Council Member.',
                        'sci_tech_exp': 'Flying is for Droids.',
                        'phase_transform_exp': 'Prequels.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'User is not verified as an admin.'
            )

    # TODO(andrew@neuraldev.io) Implement the following tests for /user/last
    # or tell davidmatthews1004@gmail.com to do them.

    # def test_get_user_last(self):
    #     """Test get the user's last used alloy and config"""
    #     fives = User(
    #         email='fives@clone.io',
    #         first_name='Five',
    #         last_name='Republic'
    #     )
    #     config = Configuration(
    #         is_valid=True,
    #         method='Li98',
    #         grain_size=0.0,
    #         nucleation_start=1.0,
    #         nucleation_finish=99.9,
    #         auto_calculate_ms=False,
    #         ms_temp=1.0,
    #         ms_rate_param=1.0,
    #         auto_calculate_bs=False,
    #         bs_temp=1.0,
    #         auto_calculate_ae=False,
    #         ae1_temp=1.0,
    #         ae3_temp=1.0,
    #         start_temp=1.0,
    #         cct_cooling_rate=1
    #     )
    #     fives.last_configuration = config
    #     hydrogen = Element(
    #         symbol='H',
    #         weight=1.0
    #     )
    #     helium = Element(
    #         symbol='He',
    #         weight=4.0
    #     )
    #     lithium = Element(
    #         symbol='Li',
    #         weight=1.9
    #     )
    #     alloy = Alloy(
    #         name='TestAlloy',
    #         composition=[
    #             hydrogen,
    #             helium,
    #             lithium
    #         ]
    #     )
    #     fives.last_alloy=alloy
    #     fives.set_password('NotJustAnotherNumber')
    #     fives.save()
    #
    #     with self.client:
    #         resp_login = self.client.post(
    #             '/auth/login',
    #             data=json.dumps(
    #                 {
    #                     'email': 'fives@clone.io',
    #                     'password': 'NotJustAnotherNumber'
    #                 }
    #             ),
    #             content_type='application/json'
    #         )
    #         token = json.loads(resp_login.data.decode())['token']
    #
    #         resp = self.client.get(
    #             '/user/last',
    #             content_type='application/json',
    #             headers={'Authorization': 'Bearer {}'.format(token)}
    #         )
    #         data = json.loads(resp.data.decode())
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertEqual(data['status'], 'success')
    #         self.assertEqual(data['configuration']['is_valid'], True)
    #         self.assertEqual(
    #             data['composition']['composition'][0]['symbol'], 'H'
    #         )
    #         self.assertEqual(
    #             data['composition']['composition'][0]['weight'], 1.0
    #         )
    #         self.assertEqual(
    #             data['composition']['composition'][1]['symbol'], 'He'
    #         )
    #         self.assertEqual(
    #             data['composition']['composition'][1]['weight'], 4.0
    #         )
    #
    # def test_get_user_last_no_last_config(self):
    #     """Test get last alloy and config with no config data"""
    #     bly = User(
    #         email='bly@clone.io',
    #         first_name='Bly',
    #         last_name='Republic'
    #     )
    #     hydrogen = Element(
    #         symbol='H',
    #         weight=1.0
    #     )
    #     helium = Element(
    #         symbol='He',
    #         weight=4.0
    #     )
    #     lithium = Element(
    #         symbol='Li',
    #         weight=1.9
    #     )
    #     alloy = Alloy(
    #         name='TestAlloy',
    #         composition=[
    #             hydrogen,
    #             helium,
    #             lithium
    #         ]
    #     )
    #     bly.last_alloy = alloy
    #     bly.set_password('IHateSecura')
    #     bly.save()
    #
    #     with self.client:
    #         resp_login = self.client.post(
    #             '/auth/login',
    #             data=json.dumps(
    #                 {
    #                     'email': 'bly@clone.io',
    #                     'password': 'IHateSecura'
    #                 }
    #             ),
    #             content_type='application/json'
    #         )
    #         token = json.loads(resp_login.data.decode())['token']
    #
    #         resp = self.client.get(
    #             '/user/last',
    #             content_type='application/json',
    #             headers={'Authorization': 'Bearer {}'.format(token)}
    #         )
    #         data = json.loads(resp.data.decode())
    #         self.assertEqual(resp.status_code, 400)
    #         self.assertEqual(data['status'], 'fail')
    #         self.assertEqual(
    #             data['message'], 'No last configuration was found.'
    #         )
    #
    # def test_get_user_last_no_alloy(self):
    #     """Test get last alloy and config with no alloy data"""
    #     cody = User(
    #         email='cody@clone.io',
    #         first_name='Cody',
    #         last_name='Republic'
    #     )
    #     config = Configuration(
    #         is_valid=True,
    #         method='Li98',
    #         grain_size=0.0,
    #         nucleation_start=1.0,
    #         nucleation_finish=99.9,
    #         auto_calculate_ms=False,
    #         ms_temp=1.0,
    #         ms_rate_param=1.0,
    #         auto_calculate_bs=False,
    #         bs_temp=1.0,
    #         auto_calculate_ae=False,
    #         ae1_temp=1.0,
    #         ae3_temp=1.0,
    #         start_temp=1.0,
    #         cct_cooling_rate=1
    #     )
    #     cody.last_configuration = config
    #     cody.set_password('YouMightBeNeedingThis')
    #     cody.save()
    #
    #     with self.client:
    #         resp_login = self.client.post(
    #             '/auth/login',
    #             data=json.dumps(
    #                 {
    #                     'email': 'cody@clone.io',
    #                     'password': 'YouMightBeNeedingThis'
    #                 }
    #             ),
    #             content_type='application/json'
    #         )
    #         token = json.loads(resp_login.data.decode())['token']
    #
    #         resp = self.client.get(
    #             '/user/last',
    #             content_type='application/json',
    #             headers={'Authorization': 'Bearer {}'.format(token)}
    #         )
    #         data = json.loads(resp.data.decode())
    #         self.assertEqual(resp.status_code, 400)
    #         self.assertEqual(data['status'], 'fail')
    #         self.assertEqual(
    #             data['message'], 'No last composition was found.'
    #         )
    #
    # def test_get_user_saved_alloys(self):
    #     """Test get user's list of saved alloys"""
    #     fox = User(
    #         email='fox@clone.io',
    #         first_name='Fox',
    #         last_name='Republic'
    #     )
    #     hydrogen = Element(
    #         symbol='H',
    #         weight=1.0
    #     )
    #     helium = Element(
    #         symbol='He',
    #         weight=4.0
    #     )
    #     lithium = Element(
    #         symbol='Li',
    #         weight=1.9
    #     )
    #     berylium = Element(
    #         symbol='Be',
    #         weight=9.0
    #     )
    #     alloy1 = Alloy(
    #         name='TestAlloy1',
    #         composition=[
    #             hydrogen,
    #             helium,
    #             lithium
    #         ]
    #     )
    #     alloy2 = Alloy(
    #         name='TestAlloy2',
    #         composition=[
    #             helium,
    #             lithium,
    #             berylium
    #         ]
    #     )
    #     saved_alloys = [alloy1, alloy2]
    #     fox.saved_alloys = saved_alloys
    #     fox.set_password('ShootToKill')
    #     fox.save()
    #
    #     with self.client:
    #         resp_login = self.client.post(
    #             '/auth/login',
    #             data=json.dumps(
    #                 {
    #                     'email': 'fox@clone.io',
    #                     'password': 'ShootToKill'
    #                 }
    #             ),
    #             content_type='application/json'
    #         )
    #         token = json.loads(resp_login.data.decode())['token']
    #
    #         resp = self.client.get(
    #             '/user/alloys',
    #             content_type='application/json',
    #             headers={'Authorization': 'Bearer {}'.format(token)}
    #         )
    #         data = json.loads(resp.data.decode())
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertEqual(data['status'], 'success')
    #         self.assertEqual(
    #             data['alloys'][0]['name'], 'TestAlloy1'
    #         )
    #         self.assertEqual(
    #             data['alloys'][0]['composition'][0]['symbol'], 'H'
    #         )
    #         self.assertEqual(
    #             data['alloys'][1]['name'], 'TestAlloy2'
    #         )
    #         self.assertEqual(
    #             data['alloys'][1]['composition'][0]['symbol'], 'He'
    #         )
    #
    # def test_get_user_saved_alloys_no_alloys(self):
    #     """Test get user's list of alloys with no saved alloys"""
    #     wolffe = User(
    #         email='wolffe@clone.io',
    #         first_name='Wolffe',
    #         last_name='Republic'
    #     )
    #     wolffe.set_password('HaveWeGotAChance')
    #     wolffe.save()
    #
    #     with self.client:
    #         resp_login = self.client.post(
    #             '/auth/login',
    #             data=json.dumps(
    #                 {
    #                     'email': 'wolffe@clone.io',
    #                     'password': 'HaveWeGotAChance'
    #                 }
    #             ),
    #             content_type='application/json'
    #         )
    #         token = json.loads(resp_login.data.decode())['token']
    #
    #         resp = self.client.get(
    #             '/user/alloys',
    #             content_type='application/json',
    #             headers={'Authorization': 'Bearer {}'.format(token)}
    #         )
    #         data = json.loads(resp.data.decode())
    #         self.assertEqual(resp.status_code, 400)
    #         self.assertEqual(data['status'], 'fail')
    #         self.assertEqual(data['message'], 'No alloys found.')

    def test_get_user_profile(self):
        """Test get request on user profile"""
        gree = User(
            email='gree@clone.io',
            first_name= 'Gree',
            last_name= 'Clone'
        )
        gree.set_password('WhydYouDoIt')
        profile = UserProfile(
            aim='Serve The Republic.',
            highest_education='Kamino Graduate.',
            sci_tech_exp='Student.',
            phase_transform_exp='Limited'
        )
        gree.profile = profile
        gree.save()

        token = log_test_user_in(self, gree, 'WhydYouDoIt')

        with self.client:
            resp = self.client.get(
                '/user/profile',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertIn(data['status'], 'success')
            self.assertIn(data['profile']['aim'], 'Serve The Republic.')
            self.assertIn(
                data['profile']['highest_education'], 'Kamino Graduate.'
            )
            self.assertIn(data['profile']['sci_tech_exp'], 'Student.')
            self.assertIn(data['profile']['phase_transform_exp'], 'Limited.')

    def test_patch_user_profile(self):
        """
        Ensure a user profile can be updated if all fields are provided.
        """
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.patch(
                '/user/profile',
                data=json.dumps(
                    {
                        'aim': 'Redeem my father.',
                        'highest_education': 'Graduated Dagobah Highschool.',
                        'sci_tech_exp': 'Limited.',
                        'phase_transform_exp': 'Limited.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['profile']['aim'], 'Redeem my father.')
            self.assertEqual(data['profile']['highest_education'],
                             'Graduated Dagobah Highschool.')
            self.assertEqual(data['profile']['sci_tech_exp'], 'Limited.')
            self.assertEqual(data['profile']['phase_transform_exp'], 'Limited.')

            updated_user = User.objects.get(email=luke.email)
            profile_obj = json.loads(updated_user.profile.to_json())
            self.assertEqual(profile_obj['aim'], 'Redeem my father.')
            self.assertEqual(profile_obj['highest_education'],
                             'Graduated Dagobah Highschool.')
            self.assertEqual(profile_obj['sci_tech_exp'], 'Limited.')
            self.assertEqual(profile_obj['phase_transform_exp'], 'Limited.')

    def test_patch_user_profile_no_data(self):
        """
        Ensure request fails if no data is provided.
        """
        anakin = User(
            email='anakin@skywalker.io',
            first_name='Anakin',
            last_name='Skywalker'
        )
        anakin.set_password('IAmYourFather')
        anakin.save()

        token = log_test_user_in(self, anakin, 'IAmYourFather')

        with self.client:
            resp = self.client.patch(
                '/user/profile',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type = 'application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

    def test_patch_user_profile_partial_data(self):
        """
        Ensure user profile can be updated even if not all fields are provided.
        """
        han = User(
            email='han@solo.io',
            first_name='Han',
            last_name='Solo'
        )
        han.set_password('BadFeelingAboutThis')
        profile = UserProfile(
            aim='filler',
            highest_education='filler',
            sci_tech_exp='filler',
            phase_transform_exp='filler'
        )
        han.profile = profile
        han.save()

        token = log_test_user_in(self, han, 'BadFeelingAboutThis')

        with self.client:
            resp = self.client.patch(
                '/user/profile',
                data=json.dumps(
                    {
                        'aim': 'Pay Jabba.',
                        'phase_transform_exp': 'Limited'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type = 'application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['profile']['aim'], 'Pay Jabba.')
            self.assertEqual(data['profile']['phase_transform_exp'], 'Limited')

            updated_user = User.objects.get(email=han.email)
            profile_obj = json.loads(updated_user.profile.to_json())
            self.assertEqual(profile_obj['aim'], 'Pay Jabba.')
            self.assertEqual(profile_obj['phase_transform_exp'], 'Limited')

    def test_patch_user_profile_two_partial_data(self):
        """
        Ensure a profile can be updated through multiple update requests that
        each update different parts of the profile.
        """
        leia = User(
            email='leia@organa.io',
            first_name='Leia',
            last_name='Organa'
        )
        leia.set_password('ShortForAStormtrooper')
        profile = UserProfile(
            aim='filler',
            highest_education='filler',
            sci_tech_exp='filler',
            phase_transform_exp='filler'
        )
        leia.profile = profile
        leia.save()

        token = log_test_user_in(self, leia, 'ShortForAStormtrooper')

        with self.client:
            resp_1 = self.client.patch(
                '/user/profile',
                data=json.dumps(
                    {
                        'aim' : 'Defeat the Empire',
                        'phase_transform_exp': 'Expert'
                    }
                ),
                headers = {'Authorization': 'Bearer {}'.format(token)},
                content_type = 'application/json'
            )

            resp_2 = self.client.patch(
                '/user/profile',
                data=json.dumps(
                    {
                        'highest_education' : 'University of Alderaan',
                        'sci_tech_exp' : 'Expert'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data_1 = json.loads(resp_1.data.decode())
            self.assertEqual(resp_1.status_code, 200)
            self.assertEqual(data_1['status'], 'success')
            self.assertEqual(data_1['profile']['aim'], 'Defeat the Empire')
            self.assertEqual(data_1['profile']['phase_transform_exp'], 'Expert')

            data_2 = json.loads(resp_2.data.decode())
            self.assertEqual(resp_2.status_code, 200)
            self.assertEqual(data_2['status'], 'success')
            self.assertEqual(
                data_2['profile']['highest_education'], 'University of Alderaan'
            )
            self.assertEqual(data_2['profile']['sci_tech_exp'], 'Expert')

            updated_user = User.objects.get(email=leia.email)
            profile_obj = json.loads(updated_user.profile.to_json())
            self.assertEqual(profile_obj['aim'], 'Defeat the Empire')
            self.assertEqual(profile_obj['phase_transform_exp'], 'Expert')
            self.assertEqual(
                profile_obj['highest_education'], 'University of Alderaan'
            )
            self.assertEqual(profile_obj['sci_tech_exp'], 'Expert')

    def test_patch_user_profile_override(self):
        """
        Ensure updates to an existing user profile are successful.
        """
        mace = User(
            email='mace@jedi.io',
            first_name='Mace',
            last_name='Windu'
        )
        mace.set_password('ThisPartysOver')
        mace.save()

        token = log_test_user_in(self, mace, 'ThisPartysOver')

        with self.client:
            resp_1 = self.client.patch(
                '/user/profile',
                data=json.dumps(
                    {
                        'aim' : 'Stop the Sif from returning.',
                        'highest_education' : 'Jedi Council Member',
                        'sci_tech_exp': 'Limited',
                        'phase_transform_exp': 'Limted'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp_2 = self.client.patch(
                '/user/profile',
                data=json.dumps(
                    {
                        'aim': 'Stop the Sith from returning.',
                        'phase_transform_exp': 'Limited'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data_1 = json.loads(resp_1.data.decode())
            self.assertEqual(resp_1.status_code, 200)
            self.assertEqual(data_1['status'], 'success')
            self.assertEqual(
                data_1['profile']['aim'], 'Stop the Sif from returning.'
            )
            self.assertEqual(data_1['profile']['phase_transform_exp'], 'Limted')
            self.assertEqual(
                data_1['profile']['highest_education'], 'Jedi Council Member'
            )
            self.assertEqual(data_1['profile']['sci_tech_exp'], 'Limited')

            data_2 = json.loads(resp_2.data.decode())
            self.assertEqual(resp_2.status_code, 200)
            self.assertEqual(data_2['status'], 'success')
            self.assertEqual(
                data_2['profile']['aim'], 'Stop the Sith from returning.'
            )
            self.assertEqual(
                data_2['profile']['phase_transform_exp'], 'Limited'
            )

            updated_user = User.objects.get(email=mace.email)
            profile_obj = json.loads(updated_user.profile.to_json())
            self.assertEqual(
                profile_obj['aim'], 'Stop the Sith from returning.'
            )
            self.assertEqual(profile_obj['phase_transform_exp'], 'Limited')
            self.assertEqual(
                profile_obj['highest_education'], 'Jedi Council Member'
            )
            self.assertEqual(profile_obj['sci_tech_exp'], 'Limited')

    def test_patch_user_profile_invalid_keys(self):
        """
        Ensure a patch request for user profile with no valid keys is rejected.
        """
        obiwan = User(
            email='obiwan@kenobi.io',
            first_name='Obi Wan',
            last_name='kenobi'
        )
        obiwan.set_password('HelloThere')
        obiwan.save()

        token = log_test_user_in(self, obiwan, 'HelloThere')

        with self.client:
            resp = self.client.patch(
                '/user/profile',
                data=json.dumps(
                    {
                        'lightsaber_colour': 'blue',
                        'movie_appearances': 'I, II, III, IV, V, VI, VII',
                        'best_star_wars_character': 'Yes'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'Payload does not have any valid keys.'
            )

    def test_patch_user_profile_missing_data_no_existing_profile(self):
        """
        Ensure a patch (without full profile details) on a user profile is
        rejected when no user profile already exists.
        """
        obiwan = User(
            email='obiwan@kenobi.io',
            first_name='Obi Wan',
            last_name='kenobi'
        )
        obiwan.set_password('HelloThere')
        obiwan.save()

        token = log_test_user_in(self, obiwan, 'HelloThere')

        with self.client:
            resp = self.client.patch(
                '/user/profile',
                data=json.dumps(
                    {
                        'aim': 'Redeem my father.',
                        'highest_education': 'Graduated Dagobah Highschool.',
                        'sci_tech_exp': 'Limited.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'],
                'User profile cannot be patched as there is no existing profile.'
            )

    def test_post_user_profile(self):
        """Test post to user profile is successful"""
        jabba = User(
            email='jabba@hutt.io',
            first_name='Jabba',
            last_name='The Hutt'
        )
        jabba.set_password('ThereWillBeNoBargain')
        jabba.save()

        token = log_test_user_in(self, jabba, 'ThereWillBeNoBargain')

        with self.client:
            resp = self.client.post(
                '/user/profile',
                data=json.dumps(
                    {
                        'aim': 'Find Han Solo.',
                        'highest_education': 'Hutt school of fatness.',
                        'sci_tech_exp': 'PHD.',
                        'phase_transform_exp': 'PHD.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(
                data['message'],
                f'Successfully updated User profile for {jabba.id}.'
            )
            self.assertEqual(data['profile']['aim'], 'Find Han Solo.')
            self.assertEqual(data['profile']['highest_education'],
                             'Hutt school of fatness.')
            self.assertEqual(data['profile']['sci_tech_exp'], 'PHD.')
            self.assertEqual(data['profile']['phase_transform_exp'], 'PHD.')

            updated_user = User.objects.get(email=jabba.email)
            profile_obj = json.loads(updated_user.profile.to_json())
            self.assertEqual(profile_obj['aim'], 'Find Han Solo.')
            self.assertEqual(profile_obj['highest_education'],
                             'Hutt school of fatness.')
            self.assertEqual(profile_obj['sci_tech_exp'], 'PHD.')
            self.assertEqual(profile_obj['phase_transform_exp'], 'PHD.')

    def test_post_user_profile_no_data(self):
        """Test empty post is unsuccessful"""
        lando = User(
            email='lando@calrissian.io',
            first_name='Lando',
            last_name='Calrissian'
        )
        lando.set_password('TheShieldIsStillUp')
        lando.save()

        token = log_test_user_in(self, lando, 'TheShieldIsStillUp')

        with self.client:
            resp = self.client.post(
                '/user/profile',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_post_user_profile_missing_data(self):
        """Test incomplete post is unsuccessful"""
        boba = User(
            email='boba@fett.com',
            first_name='Boba',
            last_name='Fett'
        )
        boba.set_password('NoGoodToMeDead')
        boba.save()

        token = log_test_user_in(self, boba, 'NoGoodToMeDead')

        with self.client:
            resp = self.client.post(
                '/user/profile',
                data=json.dumps(
                    {
                        'highest_education': 'Bounty Hunter Academy.',
                        'sci_tech_exp': 'Weapons Expert.',
                        'phase_transform_exp': 'Limited.'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')

    def test_disable_account(self):
        """Test disable account is successful"""
        kylo = User(
            email='kyloren@gmail.com',
            first_name='Kylo',
            last_name='Ren'
        )
        kylo.set_password('LetStarWarsDie')
        kylo.save()

        vader = User(
            email='vader@sith.com',
            first_name='Darth',
            last_name='Vader'
        )
        vader.set_password('AllTooEasy')
        vader.is_admin= True
        vader.save()

        token = log_test_user_in(self, vader, 'AllTooEasy')

        with self.client:
            resp_disable = self.client.put(
                '/user/disable',
                data=json.dumps(
                    {
                        'email': 'kyloren@gmail.com'
                    }
                ),
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
                f'The account for User {kylo.id} has been disabled.'
            )

            login_data = json.loads(resp_attempt_login.data.decode())
            self.assertEqual(resp_attempt_login.status_code, 400)
            self.assertEqual(login_data['status'], 'fail')
            self.assertEqual(
                login_data['message'], 'Your Account has been disabled.'
            )

    def test_disable_account_no_data(self):
        """Test empty disable request is unsuccessful"""
        jarjar = User(
            first_name='Jar Jar',
            last_name='Binks',
            email='jarjar@binks.com'
        )
        jarjar.set_password('MeesaMakePassword')
        jarjar.is_admin=True
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
            self.assertEqual(data['message'], 'User does not exist.')

    def test_disable_account_dne(self):
        """Test disable non-existent account is unsuccessful."""
        r2d2 = User(
            first_name='R2',
            last_name='D2',
            email='r2d2@astromech.com'
        )
        r2d2.set_password('Weeeeeew')
        r2d2.is_admin=True
        r2d2.save()

        token = log_test_user_in(self, r2d2, 'Weeeeeew')

        with self.client:
            resp = self.client.put(
                '/user/disable',
                data=json.dumps(
                    {
                        'email': 'c3p0@protocol.com'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User does not exist.')

    def test_disable_account_no_email(self):
        """
        Ensure a disable request is rejected when no email is provided.
        """
        vader = User(
            email='vader@sith.com',
            first_name='Darth',
            last_name='Vader'
        )
        vader.set_password('AllTooEasy')
        vader.is_admin = True
        vader.save()

        token = log_test_user_in(self, vader, 'AllTooEasy')

        with self.client:
            resp_disable = self.client.put(
                '/user/disable',
                data=json.dumps(
                    {
                        'invalid_key': 'invalid_data'
                    }
                ),
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
            email='vader@sith.com',
            first_name='Darth',
            last_name='Vader'
        )
        vader.set_password('AllTooEasy')
        vader.is_admin = True
        vader.save()

        token = log_test_user_in(self, vader, 'AllTooEasy')

        with self.client:
            resp_disable = self.client.put(
                '/user/disable',
                data=json.dumps(
                    {
                        'email': 'invalid_email.com'
                    }
                ),
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
        grevious.is_admin=True
        grevious.save()

        droid = User(
            first_name='Idiot',
            last_name='Droid',
            email='idiot@droids.com'
        )
        droid.set_password('ButIJustGotPromoted')
        droid.save()

        grevious_token = log_test_user_in(self, grevious, 'YouAreABoldOne')

        droid_token = log_test_user_in(self, droid, 'ButIJustGotPromoted')

        with self.client:
            grevious_disable = self.client.put(
                '/user/disable',
                data=json.dumps(
                    {
                        'email': 'idiot@droids.com'
                    }
                ),
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
                f'The account for User {droid.id} has been disabled.'
            )

            action_data = json.loads(droid_action.data.decode())
            self.assertEqual(droid_action.status_code, 401)
            self.assertEqual(action_data['status'], 'fail')
            self.assertEqual(
                action_data['message'], 'This user does not exist.'
            )

    def test_create_admin_success(self):
        """Test create admin is successful"""
        quigon = User(
            first_name='Qui-Gon',
            last_name='Jinn',
            email="davidmatthews1004@gmail.com"
        )
        quigon.is_admin=True
        quigon.set_password('ShortNegotiations')
        quigon.save()

        obiwan = User(
            first_name='Obi-Wan',
            last_name='Kenobi',
            email='brickmatic479@gmail.com'
        )
        obiwan.verified=True
        obiwan.set_password('FromACertainPointOfView')
        obiwan.save()

        token = log_test_user_in(self, quigon, 'ShortNegotiations')

        with self.client:
            resp = self.client.post(
                '/admincreate',
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

            user = User.objects.get(email=obiwan.email)
            self.assertEqual(user.is_admin, True)
            self.assertEqual(user.admin_profile.position, 'Jedi Knight.')
            self.assertEqual(user.admin_profile.mobile_number, None)
            self.assertEqual(user.admin_profile.verified, False)

    def test_create_admin_successful_redirect(self):
        """Test admin creation confirmation is successful"""
        promoter = User(
            email='brickmatic479@gmail.com',
            first_name='David',
            last_name='Test'
        )
        promoter.is_admin=True
        promoter.set_password('Testing123')
        promoter.save()

        email = 'test@test.com'
        user = User(email=email, first_name='Test', last_name='User')
        user.set_password('Testing123')
        user.is_admin=True
        user.admin_profile = AdminProfile(
            position='Test position.',
            mobile_number=None,
            verified=False,
            promoted_by=promoter.id
        )
        user.cascade_save()
        user.save()
        token = generate_confirmation_token(email)
        admin_url = generate_url('users.confirm_create_admin', token)
        with current_app.test_client() as client:
            res = client.get(
                admin_url,
                content_type='application/json',
            )
            self.assertEquals(res.status_code, 302)
            # self.assertTrue(res.headers['Authorization'])
            self.assertTrue(res.headers['Location'])
            # Every redirect will be different.
            redirect_url = f'http://localhost:3000/signin'
            self.assertRedirects(res, redirect_url)

            updated_user = User.objects.get(email=email)
            self.assertEqual(updated_user.is_admin, True)
            self.assertEqual(
                updated_user.admin_profile.position, 'Test position.'
            )
            self.assertEqual(updated_user.admin_profile.mobile_number, None)
            self.assertEqual(updated_user.admin_profile.verified, True)

    def test_create_admin_invalid_email(self):
        """Test create admin with invalid email is unsuccessful"""
        luke = User(
            first_name='Luke',
            last_name='Skywalker',
            email="lukeskywalker@gmail.com"
        )
        luke.is_admin=True
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
                '/admincreate',
                data=json.dumps(
                    {
                        'email': 'invalidbiggs@dot.com',
                        'position': 'Red Three'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'Invalid email.')

    def test_create_unverified_admin(self):
        """Test create admin from unverified user is unsuccessful"""
        ackbar = User(
            first_name='Admiral',
            last_name='Ackbar',
            email='admiralackbar@gmail.com'
        )
        ackbar.set_password('ITSATRAP')
        ackbar.is_admin=True
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
                '/admincreate',
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
            self.assertEqual(data['message'], 'The user must verify their email.')

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
        aayla.verified=True
        aayla.is_admin=True
        aayla.save()

        luminara = User(
            first_name='Luminara',
            last_name='Unduli',
            email='luminaraunduli@gmail.com'
        )
        luminara.set_password('DiesOffscreen')
        luminara.verified=True
        luminara.is_admin=True
        luminara.save()

        token = log_test_user_in(self, aayla, 'KilledByBly')

        with self.client:
            resp = self.client.post(
                '/admincreate',
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
            self.assertEqual(resp.status_code, 401)
            self.assertEqual(data['message'], 'User is already an Administrator.')

    def test_create_admin_no_data(self):
        """
        Ensure a create admin request with no request body is rejected.
        """
        quigon = User(
            first_name='Qui-Gon',
            last_name='Jinn',
            email="davidmatthews1004@gmail.com"
        )
        quigon.is_admin=True
        quigon.set_password('ShortNegotiations')
        quigon.save()

        token = log_test_user_in(self, quigon, 'ShortNegotiations')

        with self.client:
            resp = self.client.post(
                '/admincreate',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'Empty payload.')

    def test_create_admin_no_email(self):
        """
        Ensure a create admin request with no email is rejected.
        """
        quigon = User(
            first_name='Qui-Gon',
            last_name='Jinn',
            email="davidmatthews1004@gmail.com"
        )
        quigon.is_admin = True
        quigon.set_password('ShortNegotiations')
        quigon.save()

        token = log_test_user_in(self, quigon, 'ShortNegotiations')

        with self.client:
            resp = self.client.post(
                '/admincreate',
                data=json.dumps(
                    {
                        'position': 'Jedi Knight.'
                    }
                ),
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
        quigon.is_admin = True
        quigon.set_password('ShortNegotiations')
        quigon.save()

        token = log_test_user_in(self, quigon, 'ShortNegotiations')

        with self.client:
            resp = self.client.post(
                '/admincreate',
                data=json.dumps(
                    {
                        'email': 'brickmatic479@gmail.com'
                    }
                ),
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
        quigon.is_admin = True
        quigon.set_password('ShortNegotiations')
        quigon.save()

        token = log_test_user_in(self, quigon, 'ShortNegotiations')

        with self.client:
            resp = self.client.post(
                '/admincreate',
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
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'User does not exist.')

    # def test_create_admin_success_manual(self):
    #     david = User(
    #         first_name='David',
    #         last_name='Matthews',
    #         email="dgm999@uowmail.edu.au"
    #     )
    #     david.is_admin=True
    #     david.set_password('DestroyTheSith')
    #     david.save()
    #
    #     david2 = User(
    #         first_name='Dave',
    #         last_name='Matthews',
    #         email='davidmatthews1004@gmail.com'
    #     )
    #     david2.verified=True
    #     david2.set_password('OrDestroyTheJedi')
    #     david2.save()
    #
    #     with self.client:
    #         resp_login = self.client.post(
    #             '/auth/login',
    #             data=json.dumps(
    #                 {
    #                     'email': 'dgm999@uowmail.edu.au',
    #                     'password': 'DestroyTheSith'
    #                 }
    #             ),
    #             content_type='application/json'
    #         )
    #         token = json.loads(resp_login.data.decode())['token']
    #         resp = self.client.post(
    #             '/admincreate',
    #             data=json.dumps(
    #                 {
    #                     'email': 'davidmatthews1004@gmail.com'
    #                 }
    #             ),
    #             headers={'Authorization': 'Bearer {}'.format(token)},
    #             content_type='application/json'
    #         )
    #         data = json.loads(resp.data.decode())
    #         self.assertEqual(data['status'], 'success')
    #         self.assertEqual(resp.status_code, 202)

if __name__ == '__main__':
    unittest.main()
