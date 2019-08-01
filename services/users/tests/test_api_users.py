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
from users_app.models import User, UserProfile, AdminProfile, Element, Alloy, \
    Configuration

logger = AppLogger(__name__)


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
            token = json.loads(resp_login.data.decode())['token']

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
            token = json.loads(resp_login.data.decode())['token']

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
            token = json.loads(resp_login.data.decode())['token']

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
            token = json.loads(resp_login.data.decode())['token']
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

    def test_put_user(self):
        """Test update user details"""
        obiwan = User(
            email='obiwan@kenobi.io', first_name='Obi Wan', last_name='kenobi'
        )
        obiwan.set_password('HelloThere')
        obiwan.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'obiwan@kenobi.io',
                        'password': 'HelloThere'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.put(
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

    def test_put_admin_user(self):
        """Test update admin user details"""
        yoda = User(email='yoda@jedi.io', first_name='Yoda', last_name='Smith')
        yoda.set_password('DoOrDoNot')
        yoda.is_admin = True
        yoda.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'yoda@jedi.io',
                        'password': 'DoOrDoNot'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.put(
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

    def test_put_user_partial(self):
        """Test update only some of the user's details"""
        sheev = User(
            email='sheev@palpatine.io',
            first_name='Sheev',
            last_name='Palpatine'
        )
        sheev.set_password('IAmTheSenate')
        sheev.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'sheev@palpatine.io',
                        'password': 'IAmTheSenate'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.put(
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

            updated_user = User.objects.get(email=sheev.email)
            self.assertEqual(updated_user['first_name'], 'Emperor')
            self.assertEqual(updated_user['last_name'], 'Palpatine')
            self.assertEqual(
                updated_user['profile']['aim'], 'Rule the Galaxy.'
            )
            self.assertEqual(
                updated_user['profile']['highest_education'], None
            )
            self.assertEqual(updated_user['profile']['sci_tech_exp'], None)
            self.assertEqual(
                updated_user['profile']['phase_transform_exp'], 'Sith Lord.'
            )

    def test_put_user_no_data(self):
        """Try update a user without any data for the update"""
        maul = User(email='maul@sith.io', first_name='Darth', last_name='Maul')
        maul.set_password('AtLastWeWillHaveRevenge')
        maul.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'maul@sith.io',
                        'password': 'AtLastWeWillHaveRevenge'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.put(
                '/user',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_put_user_existing_profile(self):
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

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'ahsoka@tano.io',
                        'password': 'IAmNoJedi'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.put(
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

            updated_user = User.objects.get(email=ahsoka.email)
            self.assertEqual(updated_user['first_name'], 'Ahsoka')
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

    def test_put_admin_existing_admin_profile(self):
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
        rex.is_admin = True
        admin_profile = AdminProfile(
            mobile_number='0987654321', position='Captain'
        )
        rex.admin_profile = admin_profile
        rex.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'rex@clone.io',
                        'password': 'ExperienceOutranksEverything'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.put(
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

            updated_user = User.objects.get(email=rex.email)
            self.assertEqual(updated_user['first_name'], 'Rex')
            self.assertEqual(updated_user['last_name'], 'Republic')
            self.assertEqual(
                updated_user['admin_profile']['mobile_number'], '1234567890'
            )
            self.assertEqual(
                updated_user['admin_profile']['position'], 'Discharged.'
            )

    def test_get_user_last(self):
        """Test get the user's last used alloy and config"""
        fives = User(
            email='fives@clone.io', first_name='Five', last_name='Republic'
        )
        config = Configuration(
            is_valid=True,
            method='Li98',
            grain_size=0.0,
            nucleation_start=1.0,
            nucleation_finish=99.9,
            auto_calculate_ms=False,
            ms_temp=1.0,
            ms_rate_param=1.0,
            auto_calculate_bs=False,
            bs_temp=1.0,
            auto_calculate_ae=False,
            ae1_temp=1.0,
            ae3_temp=1.0,
            start_temp=1.0,
            cct_cooling_rate=1
        )
        fives.last_configuration = config
        hydrogen = Element(symbol='H', weight=1.0)
        helium = Element(symbol='He', weight=4.0)
        lithium = Element(symbol='Li', weight=1.9)
        alloy = Alloy(
            name='TestAlloy', composition=[hydrogen, helium, lithium]
        )
        fives.last_alloy = alloy
        fives.set_password('NotJustAnotherNumber')
        fives.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'fives@clone.io',
                        'password': 'NotJustAnotherNumber'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.get(
                '/user/last',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['configuration']['is_valid'], True)
            self.assertEqual(
                data['composition']['composition'][0]['symbol'], 'H'
            )
            self.assertEqual(
                data['composition']['composition'][0]['weight'], 1.0
            )
            self.assertEqual(
                data['composition']['composition'][1]['symbol'], 'He'
            )
            self.assertEqual(
                data['composition']['composition'][1]['weight'], 4.0
            )

    def test_get_user_last_no_last_config(self):
        """Test get last alloy and config with no config data"""
        bly = User(
            email='bly@clone.io', first_name='Bly', last_name='Republic'
        )
        hydrogen = Element(symbol='H', weight=1.0)
        helium = Element(symbol='He', weight=4.0)
        lithium = Element(symbol='Li', weight=1.9)
        alloy = Alloy(
            name='TestAlloy', composition=[hydrogen, helium, lithium]
        )
        bly.last_alloy = alloy
        bly.set_password('IHateSecura')
        bly.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'bly@clone.io',
                        'password': 'IHateSecura'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.get(
                '/user/last',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'No last configuration was found.'
            )

    def test_get_user_last_no_alloy(self):
        """Test get last alloy and config with no alloy data"""
        cody = User(
            email='cody@clone.io', first_name='Cody', last_name='Republic'
        )
        config = Configuration(
            is_valid=True,
            method='Li98',
            grain_size=0.0,
            nucleation_start=1.0,
            nucleation_finish=99.9,
            auto_calculate_ms=False,
            ms_temp=1.0,
            ms_rate_param=1.0,
            auto_calculate_bs=False,
            bs_temp=1.0,
            auto_calculate_ae=False,
            ae1_temp=1.0,
            ae3_temp=1.0,
            start_temp=1.0,
            cct_cooling_rate=1
        )
        cody.last_configuration = config
        cody.set_password('YouMightBeNeedingThis')
        cody.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'cody@clone.io',
                        'password': 'YouMightBeNeedingThis'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.get(
                '/user/last',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No last composition was found.')

    def test_get_user_saved_alloys(self):
        """Test get user's list of saved alloys"""
        fox = User(
            email='fox@clone.io', first_name='Fox', last_name='Republic'
        )
        hydrogen = Element(symbol='H', weight=1.0)
        helium = Element(symbol='He', weight=4.0)
        lithium = Element(symbol='Li', weight=1.9)
        berylium = Element(symbol='Be', weight=9.0)
        alloy1 = Alloy(
            name='TestAlloy1', composition=[hydrogen, helium, lithium]
        )
        alloy2 = Alloy(
            name='TestAlloy2', composition=[helium, lithium, berylium]
        )
        saved_alloys = [alloy1, alloy2]
        fox.saved_alloys = saved_alloys
        fox.set_password('ShootToKill')
        fox.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'fox@clone.io',
                        'password': 'ShootToKill'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.get(
                '/user/alloys',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['alloys'][0]['name'], 'TestAlloy1')
            self.assertEqual(
                data['alloys'][0]['composition'][0]['symbol'], 'H'
            )
            self.assertEqual(data['alloys'][1]['name'], 'TestAlloy2')
            self.assertEqual(
                data['alloys'][1]['composition'][0]['symbol'], 'He'
            )

    def test_get_user_saved_alloys_no_alloys(self):
        """Test get user's list of alloys with no saved alloys"""
        wolffe = User(
            email='wolffe@clone.io', first_name='Wolffe', last_name='Republic'
        )
        wolffe.set_password('HaveWeGotAChance')
        wolffe.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'wolffe@clone.io',
                        'password': 'HaveWeGotAChance'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.get(
                '/user/alloys',
                content_type='application/json',
                headers={'Authorization': 'Bearer {}'.format(token)}
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'No alloys found.')

    def test_get_user_profile(self):
        """Test get request on user profile"""
        gree = User(
            email='gree@clone.io', first_name='Gree', last_name='Clone'
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

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'gree@clone.io',
                        'password': 'WhydYouDoIt'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

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

    def test_put_user_profile(self):
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

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'luke@skywalker.io',
                        'password': 'NeverJoinYou'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.put(
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

            updated_user = User.objects.get(email=luke.email)
            profile_obj = json.loads(updated_user.profile.to_json())
            self.assertEqual(profile_obj['aim'], 'Redeem my father.')
            self.assertEqual(
                profile_obj['highest_education'],
                'Graduated Dagobah Highschool.'
            )
            self.assertEqual(profile_obj['sci_tech_exp'], 'Limited.')
            self.assertEqual(profile_obj['phase_transform_exp'], 'Limited.')

    def test_put_user_profile_no_data(self):
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

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'anakin@skywalker.io',
                        'password': 'IAmYourFather'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.put(
                '/user/profile',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

    def test_put_user_profile_partial_data(self):
        """
        Ensure user profile can be updated even if not all fields are provided.
        """
        han = User(email='han@solo.io', first_name='Han', last_name='Solo')
        han.set_password('BadFeelingAboutThis')
        han.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'han@solo.io',
                        'password': 'BadFeelingAboutThis'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.put(
                '/user/profile',
                data=json.dumps(
                    {
                        'aim': 'Pay Jabba.',
                        'phase_transform_exp': 'Limited'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')

            updated_user = User.objects.get(email=han.email)
            profile_obj = json.loads(updated_user.profile.to_json())
            self.assertEqual(profile_obj['aim'], 'Pay Jabba.')
            self.assertEqual(profile_obj['phase_transform_exp'], 'Limited')
            self.assertEqual(profile_obj['highest_education'], None)
            self.assertEqual(profile_obj['sci_tech_exp'], None)

    def test_put_user_profile_two_partial_data(self):
        """
        Ensure a profile can be updated through multiple update requests that
        each update different parts of the profile.
        """
        leia = User(
            email='leia@organa.io', first_name='Leia', last_name='Organa'
        )
        leia.set_password('ShortForAStormtrooper')
        leia.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'leia@organa.io',
                        'password': 'ShortForAStormtrooper'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp_1 = self.client.put(
                '/user/profile',
                data=json.dumps(
                    {
                        'aim': 'Defeat the Empire',
                        'phase_transform_exp': 'Expert'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp_2 = self.client.put(
                '/user/profile',
                data=json.dumps(
                    {
                        'highest_education': 'University of Alderaan',
                        'sci_tech_exp': 'Expert'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data_1 = json.loads(resp_1.data.decode())
            self.assertEqual(resp_1.status_code, 200)
            self.assertEqual(data_1['status'], 'success')

            data_2 = json.loads(resp_2.data.decode())
            self.assertEqual(resp_2.status_code, 200)
            self.assertEqual(data_2['status'], 'success')

            updated_user = User.objects.get(email=leia.email)
            profile_obj = json.loads(updated_user.profile.to_json())
            self.assertEqual(profile_obj['aim'], 'Defeat the Empire')
            self.assertEqual(profile_obj['phase_transform_exp'], 'Expert')
            self.assertEqual(
                profile_obj['highest_education'], 'University of Alderaan'
            )
            self.assertEqual(profile_obj['sci_tech_exp'], 'Expert')

    def test_put_user_profile_override(self):
        """
        Ensure updates to an existing user profile are successfull.
        """
        mace = User(email='mace@jedi.io', first_name='Mace', last_name='Windu')
        mace.set_password('ThisPartysOver')
        mace.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'mace@jedi.io',
                        'password': 'ThisPartysOver'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp_1 = self.client.put(
                '/user/profile',
                data=json.dumps(
                    {
                        'aim': 'Stop the Sif from returning.',
                        'highest_education': 'Jedi Council Member',
                        'sci_tech_exp': 'Limited',
                        'phase_transform_exp': 'Limted'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp_2 = self.client.put(
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

            data_2 = json.loads(resp_2.data.decode())
            self.assertEqual(resp_2.status_code, 200)
            self.assertEqual(data_2['status'], 'success')

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

    def test_post_user_profile(self):
        jabba = User(
            email='jabba@hutt.io', first_name='Jabba', last_name='The Hutt'
        )
        jabba.set_password('ThereWillBeNoBargain')
        jabba.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'jabba@hutt.io',
                        'password': 'ThereWillBeNoBargain'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

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

            updated_user = User.objects.get(email=jabba.email)
            profile_obj = json.loads(updated_user.profile.to_json())
            self.assertEqual(profile_obj['aim'], 'Find Han Solo.')
            self.assertEqual(
                profile_obj['highest_education'], 'Hutt school of fatness.'
            )
            self.assertEqual(profile_obj['sci_tech_exp'], 'PHD.')
            self.assertEqual(profile_obj['phase_transform_exp'], 'PHD.')

    def test_post_user_profile_no_data(self):
        lando = User(
            email='lando@calrissian.io',
            first_name='Lando',
            last_name='Calrissian'
        )
        lando.set_password('TheShieldIsStillUp')
        lando.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'lando@calrissian.io',
                        'password': 'TheShieldIsStillUp'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

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
        boba = User(email='boba@fett.com', first_name='Boba', last_name='Fett')
        boba.set_password('NoGoodToMeDead')
        boba.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'boba@fett.com',
                        'password': 'NoGoodToMeDead'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

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
            self.assertEqual(data['message'], 'Missing aim.')

    def test_disable_account(self):
        kylo = User(email='kylo@ren.com', first_name='Kylo', last_name='Ren')
        kylo.set_password('LetStarWarsDie')
        kylo.save()

        vader = User(
            email='vader@sith.com', first_name='Darth', last_name='Vader'
        )
        vader.set_password('AllTooEasy')
        vader.is_admin = True
        vader.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'vader@sith.com',
                        'password': 'AllTooEasy'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp_disable = self.client.post(
                '/disableaccount',
                data=json.dumps({'email': 'kylo@ren.com'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp_attempt_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'kylo@ren.com',
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
        jarjar = User(
            first_name='Jar Jar', last_name='Binks', email='jarjar@binks.com'
        )
        jarjar.set_password('MeesaMakePassword')
        jarjar.is_admin = True
        jarjar.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'jarjar@binks.com',
                        'password': 'MeesaMakePassword'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.post(
                '/disableaccount',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User does not exist.')

    def test_disable_account_dne(self):
        r2d2 = User(
            first_name='R2', last_name='D2', email='r2d2@astromech.com'
        )
        r2d2.set_password('Weeeeeew')
        r2d2.is_admin = True
        r2d2.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'r2d2@astromech.com',
                        'password': 'Weeeeeew'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp = self.client.post(
                '/disableaccount',
                data=json.dumps({'email': 'c3p0@protocol.com'}),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User does not exist.')


if __name__ == '__main__':
    unittest.main()
