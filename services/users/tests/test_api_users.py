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

from bson import ObjectId
from flask import current_app

from tests.test_api_base import BaseTestCase
from logger.arc_logger import AppLogger
from users_app.models import (User, UserProfile, AdminProfile)

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

    def test_post_user_profile(self):
        """Test post to user profile is successful"""
        jabba = User(
            email='jabba@hutt.io', first_name='Jabba', last_name='The Hutt'
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
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['data']['aim'], 'Find Han Solo.')
            self.assertEqual(
                data['data']['highest_education'], 'Hutt school of fatness.'
            )
            self.assertEqual(data['data']['sci_tech_exp'], 'PHD.')
            self.assertEqual(data['data']['phase_transform_exp'], 'PHD.')

            updated_user = User.objects.get(email=jabba.email)
            profile_obj = json.loads(updated_user.profile.to_json())
            self.assertEqual(profile_obj['aim'], 'Find Han Solo.')
            self.assertEqual(
                profile_obj['highest_education'], 'Hutt school of fatness.'
            )
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
        boba = User(email='boba@fett.com', first_name='Boba', last_name='Fett')
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
            email='kyloren@gmail.com', first_name='Kylo', last_name='Ren'
        )
        kylo.set_password('LetStarWarsDie')
        kylo.save()


if __name__ == '__main__':
    unittest.main()
