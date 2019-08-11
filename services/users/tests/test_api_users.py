# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_users.py
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
"""test_api_users.py: 

This script will run all tests on the Users endpoints.
"""

import json
import unittest
from datetime import datetime

from bson import ObjectId
from flask import current_app
from itsdangerous import URLSafeTimedSerializer

from tests.test_api_base import BaseTestCase
from logger.arc_logger import AppLogger
from users_app.models import (
    User, UserProfile, AdminProfile, Element, Alloy, Configuration,
    SharedSimulation, AlloyType, AlloyStore
)
from users_app.token import (
    generate_confirmation_token, generate_url,
    generate_promotion_confirmation_token,
    generate_shared_simulation_signature,
    generate_url_with_signature, confirm_signature
)

logger = AppLogger(__name__)


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
            self.assertEqual(
                data['message'], 'This user account has been disabled.'
            )
            self.assertEqual('fail', data['status'])

    def test_single_user_invalid_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/user')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertIn('Provide a valid JWT auth token.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            _id = ObjectId()
            response = self.client.get('/user')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
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
            self.assertEqual(resp.status_code, 401)
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
        # thor.is_admin = True
        thor.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
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
        # tony.is_admin = True
        tony.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
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
            email='obiwan@kenobi.io', first_name='Obi Wan', last_name='kenobi'
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
            self.assertEqual(data['data']['first_name'], 'Obi-Wan')
            self.assertEqual(data['data']['last_name'], 'Kenobi')
            self.assertEqual(
                data['data']['profile']['aim'], 'Train Skywalkers.'
            )
            self.assertEqual(
                data['data']['profile']['highest_education'],
                'Jedi Council Member.'
            )
            self.assertEqual(
                data['data']['profile']['sci_tech_exp'],
                'Flying is for Droids.'
            )
            self.assertEqual(
                data['data']['profile']['phase_transform_exp'], 'Prequels.'
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
                updated_user['profile']['sci_tech_exp'],
                'Flying is for Droids.'
            )
            self.assertEqual(
                updated_user['profile']['phase_transform_exp'], 'Prequels.'
            )

    def test_patch_admin_user(self):
        """Test update admin user details"""
        yoda = User(email='yoda@jedi.io', first_name='Yoda', last_name='Smith')
        yoda.set_password('DoOrDoNot')
        # yoda.is_admin = True
        yoda.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        admin_profile = AdminProfile(
            position='Filler', mobile_number=None, verified=True
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
            self.assertEqual(data['data']['first_name'], 'Yoda')
            self.assertEqual(data['data']['last_name'], 'Smith')
            self.assertEqual(
                data['data']['profile']['aim'], 'Pass on what I have learned.'
            )
            self.assertEqual(
                data['data']['profile']['highest_education'],
                'Jedi Temple Professor.'
            )
            self.assertEqual(
                data['data']['profile']['sci_tech_exp'],
                'Much to learn, I still have.'
            )
            self.assertEqual(
                data['data']['profile']['phase_transform_exp'],
                'I am a puppet.'
            )
            self.assertEqual(
                data['data']['admin_profile']['mobile_number'], '1234567890'
            )
            self.assertEqual(
                data['data']['admin_profile']['position'], 'Grand Jedi Master.'
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
                updated_user['admin_profile']['mobile_number'], '1234567890'
            )
            self.assertEqual(
                updated_user['admin_profile']['position'], 'Grand Jedi Master.'
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
            self.assertEqual(data['data']['first_name'], 'Emperor')
            self.assertEqual(
                data['data']['profile']['aim'], 'Rule the Galaxy.'
            )
            self.assertEqual(
                data['data']['profile']['phase_transform_exp'], 'Sith Lord.'
            )

            updated_user = User.objects.get(email=sheev.email)
            self.assertEqual(updated_user['first_name'], 'Emperor')
            self.assertEqual(updated_user['last_name'], 'Palpatine')
            self.assertEqual(
                updated_user['profile']['aim'], 'Rule the Galaxy.'
            )
            self.assertEqual(updated_user['profile']['sci_tech_exp'], 'filler')
            self.assertEqual(
                updated_user['profile']['highest_education'], 'filler'
            )
            self.assertEqual(
                updated_user['profile']['phase_transform_exp'], 'Sith Lord.'
            )

    def test_patch_user_no_data(self):
        """Try update a user without any data for the update"""
        maul = User(email='maul@sith.io', first_name='Darth', last_name='Maul')
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
            email='ahsoka@tano.io', first_name='Ahsoka', last_name='tano'
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
            self.assertEqual(data['data']['last_name'], 'Tano')
            self.assertEqual(
                data['data']['profile']['aim'], 'Follow the will of the force.'
            )
            self.assertEqual(
                data['data']['profile']['highest_education'], 'Rogue.'
            )
            self.assertEqual(
                data['data']['profile']['sci_tech_exp'], 'Greater.'
            )
            self.assertEqual(
                data['data']['profile']['phase_transform_exp'], 'Great.'
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
            email='obiwan@kenobi.io', first_name='Obi Wan', last_name='kenobi'
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
            email='obiwan@kenobi.io', first_name='Obi Wan', last_name='kenobi'
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
                data['message'], (
                    'User profile cannot be updated as there is no existing '
                    'profile.'
                )
            )

    def test_patch_admin_existing_admin_profile(self):
        """Test update user details if there is existing outdated data"""
        rex = User(
            email='rex@clone.io', first_name='Rex', last_name='Republic'
        )
        rex.set_password('ExperienceOutranksEverything')
        profile = UserProfile(
            aim='Serve the Republic',
            highest_education='Clone Captain',
            sci_tech_exp='Limited',
            phase_transform_exp='Limited'
        )
        rex.profile = profile
        # rex.is_admin = True
        rex.admin_profile = AdminProfile(
            position='Position',
            mobile_number=None,
            verified=True,
            promoted_by=None
        )
        admin_profile = AdminProfile(
            mobile_number='0987654321', position='Captain', verified=True
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
                data['data']['admin_profile']['mobile_number'], '1234567890'
            )
            self.assertEqual(
                data['data']['admin_profile']['position'], 'Discharged.'
            )

            updated_user = User.objects.get(email=rex.email)
            self.assertEqual(
                updated_user['admin_profile']['mobile_number'], '1234567890'
            )
            self.assertEqual(
                updated_user['admin_profile']['position'], 'Discharged.'
            )

    def test_patch_unverified_admin(self):
        """Test update user details if there is existing outdated data"""
        rex = User(
            email='rex@clone.io', first_name='Rex', last_name='Republic'
        )
        rex.set_password('ExperienceOutranksEverything')
        profile = UserProfile(
            aim='Serve the Republic',
            highest_education='Clone Captain',
            sci_tech_exp='Limited',
            phase_transform_exp='Limited'
        )
        rex.profile = profile
        rex.admin_profile = AdminProfile(
            mobile_number='0987654321', position='Captain', verified=False
        )
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
            self.assertEqual(resp.status_code, 401)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'User is not verified as an admin.'
            )

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
<<<<<<< Updated upstream

        with self.client:
            resp = self.client.put(
                '/user/disable',
                data=json.dumps(''),
=======

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
                        'email': 'invalidbiggs@dot.com',
                        'position': 'Red Three'
                    }
                ),
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            self.assertEqual(data['message'], 'Invalid payload.')
=======
            self.assertEqual(resp.status_code, 401)
            self.assertEqual(
                data['message'], 'The user must verify their email.'
            )
>>>>>>> Stashed changes

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

        token = log_test_user_in(self, r2d2, 'Weeeeeew')

        with self.client:
<<<<<<< Updated upstream
            resp = self.client.put(
                '/user/disable',
                data=json.dumps({'email': 'c3p0@protocol.com'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 404)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User cannot be found.')

    def test_disable_account_no_email(self):
        """
        Ensure a disable request is rejected when no email is provided.
        """
        vader = User(
            email='vader@sith.com', first_name='Darth', last_name='Vader'
        )
        vader.set_password('AllTooEasy')
        vader.is_admin = True
        vader.save()

        token = log_test_user_in(self, vader, 'AllTooEasy')

        with self.client:
            resp_disable = self.client.put(
                '/user/disable',
                data=json.dumps({'invalid_key': 'invalid_data'}),
=======
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
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
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
        vader.is_admin = True
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
        grevious.is_admin = True
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
                action_data['message'], 'This user does not exist.'
            )

    def test_create_admin_success(self):
        """Test create admin is successful"""
        quigon = User(
            first_name='Qui-Gon',
            last_name='Jinn',
            email="davidmatthews1004@gmail.com"
        )
        quigon.is_admin = True
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
        luke.is_admin = True
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
        ackbar.is_admin = True
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

<<<<<<< HEAD
<<<<<<< HEAD
    def test_disable_account_dne(self):
        r2d2 = User(
            first_name='R2', last_name='D2', email='r2d2@astromech.com'
        )
        r2d2.set_password('Weeeeeew')
        r2d2.is_admin = True
        r2d2.save()
=======
    def test_create_admin_already_admin(self):
        """
        Ensure an error comes up when trying to make an Admin an Admin
        """
        aayla = User(
            first_name='Aayla',
            last_name='Secura',
            email='aaylasecura@gmail.com'
        )
=======
    def test_create_admin_already_admin(self):
        """
        Ensure an error comes up when trying to make an Admin an Admin
        """
        aayla = User(
            first_name='Aayla',
            last_name='Secura',
            email='aaylasecura@gmail.com'
        )
>>>>>>> ARC-105
        aayla.set_password('KilledByBly')
        aayla.verified = True
        aayla.is_admin = True
        aayla.save()

        luminara = User(
            first_name='Luminara',
            last_name='Unduli',
            email='luminaraunduli@gmail.com'
        )
        luminara.set_password('DiesOffscreen')
        luminara.verified = True
        luminara.is_admin = True
        luminara.save()

        token = log_test_user_in(self, aayla, 'KilledByBly')
<<<<<<< HEAD
>>>>>>> ARC-105
=======
>>>>>>> ARC-105

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
        quigon.is_admin = True
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
<<<<<<< HEAD

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
<<<<<<< HEAD
                '/disableaccount',
                data=json.dumps({'email': 'c3p0@protocol.com'}),
=======
=======

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
>>>>>>> ARC-105
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
        quigon.is_admin = True
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
<<<<<<< HEAD
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

        token = generate_promotion_confirmation_token(
            admin.email, user.email
        )
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

        token = generate_promotion_confirmation_token(
            admin.email, user.email
        )
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
        url = generate_url(
            'admin.verify_promotion', token
        )

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
        url = generate_url(
            'admin.verify_promotion', token
        )

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
        url = generate_url(
            'admin.verify_promotion', token
        )

        with current_app.test_client() as client:
            resp = client.get(url, content_type='application/json')

            data = json.loads(resp.data.decode())
            self.assertEquals(resp.status_code, 400)
            self.assertEqual(data['message'], 'User is not an Admin.')

    def test_share_configuration_link_success(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified=True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name': 'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        },
                                        {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name': 'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        },
                                        {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name': 'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        },
                                        {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['status'], 'success')

    def test_share_configuration_link_no_data(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/link',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_share_configuration_link_key_error(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/link',
                data=json.dumps(
                    {
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name': 'Parent Name'
                                },
                                'weld': {
                                    'name': 'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        },
                                        {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Key error.')

    def test_share_configuration_single_email_success(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(
                    {
                        'email_list': 'davidmatthews1004@gmail.com',
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name': 'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        },
                                        {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name': 'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        },
                                        {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name': 'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        },
                                        {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Email(s) sent.')

    def test_share_configuration_multiple_emails_success(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(
                    {
                        'email_list': [
                            'davidmatthews1004@gmail.com',
                            'brickmatic479@gmail.com'
                        ],
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name': 'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        },
                                        {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name': 'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        },
                                        {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name': 'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        },
                                        {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['message'], 'Email(s) sent.')

    def test_share_configuration_email_no_data(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_share_configuration_email_no_email(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(
                    {
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name': 'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        },
                                        {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name': 'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        },
                                        {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name': 'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        },
                                        {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No email addresses provided.')

    def test_share_configuration_email_invalid_email_type(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(
                    {
                        'email_list': 1234,
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name': 'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        },
                                        {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name': 'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        },
                                        {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name': 'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        },
                                        {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'Invalid email address type.'
            )

    def test_share_configuration_email_invalid_email(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        with self.client:
            resp = self.client.post(
                '/user/share/simulation/email',
                data=json.dumps(
                    {
                        'email_list': 'invalidemail@com',
                        'configuration': {
                            'is_valid': True,
                            'method': 'Li98',
                            'grain_size': 0.1,
                            'nucleation_start': 1.1,
                            'nucleation_finish': 99.8,
                            'auto_calculate_ms': False,
                            'ms_temp': 0.2,
                            'ms_rate_param': 0.3,
                            'auto_calculate_bs': False,
                            'bs_temp': 0.4,
                            'auto_calculate_ae': False,
                            'ae1_temp': 0.5,
                            'ae3_temp': 0.6,
                            'start_temp': 7,
                            'cct_cooling_rate': 1
                        },
                        'alloy_store': {
                            'alloy_option': 'Option String',
                            'alloys': {
                                'parent': {
                                    'name': 'Parent Name',
                                    'compositions': [
                                        {
                                            'symbol': 'H',
                                            'weight': 1.008
                                        },
                                        {
                                            'symbol': 'He',
                                            'weight': 4.003
                                        }
                                    ]
                                },
                                'weld': {
                                    'name': 'Weld Name',
                                    'compositions': [
                                        {
                                            'symbol': 'Li',
                                            'weight': 6.941
                                        },
                                        {
                                            'symbol': 'Be',
                                            'weight': 9.012
                                        }
                                    ]
                                },
                                'mix': {
                                    'name': 'Mix Name',
                                    'compositions': [
                                        {
                                            'symbol': 'B',
                                            'weight': 10.811
                                        },
                                        {
                                            'symbol': 'C',
                                            'weight': 12.011
                                        }
                                    ]
                                },
                            }
                        }
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid email.')

    def test_view_shared_configuration_success(self):
        luke = User(
            email='luke@skywalker.io',
            first_name='Luke',
            last_name='Skywalker'
        )
        luke.set_password('NeverJoinYou')
        luke.verified = True
        luke.save()

        token = log_test_user_in(self, luke, 'NeverJoinYou')

        carbon = Element(symbol='C', weight=12.011)
        boron = Element(symbol='B', weight=10.811)
        berylium = Element(symbol='Be', weight=9.012)
        lithium = Element(symbol='Li', weight=6.941)
        helium = Element(symbol='He', weight=4.003)
        hydrogen = Element(symbol='H', weight=1.008)

        mix = Alloy(name='Mix Name', compositions=[boron, carbon])
        weld = Alloy(name='Weld Name', compositions=[lithium, berylium])
        parent = Alloy(name='Parent Name', compositions=[hydrogen, helium])
        alloy_type = AlloyType(parent=parent, weld=weld, mix=mix)
        alloy_store = AlloyStore(
            alloy_option='Option String',
            alloys=alloy_type
        )
        configuration = Configuration(
            is_valid=True,
            method='Li98',
            grain_size = 0.1,
            nucleation_start = 1.1,
            nucleation_finish = 99.8,
            auto_calculate_ms = False,
            ms_temp = 0.2,
            ms_rate_param = 0.3,
            auto_calculate_bs = False,
            bs_temp = 0.4,
            auto_calculate_ae = False,
            ae1_temp = 0.5,
            ae3_temp = 0.6,
            start_temp = 7,
            cct_cooling_rate = 1
        )

        shared_config = SharedSimulation(
            owner_email=luke.email,
            created_date=datetime.utcnow(),
            configuration=configuration,
            alloy_store=alloy_store
        )

        shared_config.save()

        config_signature = generate_shared_simulation_signature(
            shared_config.to_dict()
        )
        config_url = generate_url_with_signature(
            'share.view_shared_simulation', config_signature
        )

        with self.client:
            resp = self.client.get(
                config_url,
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')

            self.assertEqual(data['data']['configuration']['is_valid'], True)
            self.assertEqual(data['data']['configuration']['method'], 'Li98')
            self.assertEqual(data['data']['configuration']['grain_size'], 0.1)
            self.assertEqual(
                data['data']['configuration']['nucleation_start'], 1.1
            )
            self.assertEqual(
                data['data']['configuration']['nucleation_finish'], 99.8
            )
            self.assertEqual(
                data['data']['configuration']['auto_calculate_ms'], False
            )
            self.assertEqual(data['data']['configuration']['ms_temp'], 0.2)
            self.assertEqual(
                data['data']['configuration']['ms_rate_param'], 0.3
            )
            self.assertEqual(
                data['data']['configuration']['auto_calculate_bs'], False
            )
            self.assertEqual(data['data']['configuration']['bs_temp'], 0.4)
            self.assertEqual(
                data['data']['configuration']['auto_calculate_ae'], False
            )
            self.assertEqual(data['data']['configuration']['ae1_temp'], 0.5)
            self.assertEqual(data['data']['configuration']['ae3_temp'], 0.6)
            self.assertEqual(data['data']['configuration']['start_temp'], 7)
            self.assertEqual(
                data['data']['configuration']['cct_cooling_rate'], 1
            )
            self.assertEqual(
                data['data']['alloy_store']['alloy_option'], 'Option String'
            )
            self.assertEqual(
                data['data']['alloy_store']['alloys']['parent']['name'],
                'Parent Name'
            )
            self.assertEqual(
                data['data']['alloy_store']['alloys']['parent']['compositions'][0]['symbol'],
                'H'
            )
            self.assertEqual(
                data['data']['alloy_store']['alloys']['parent']['compositions'][0]['weight'],
                1.008
            )

if __name__ == '__main__':
    unittest.main()
