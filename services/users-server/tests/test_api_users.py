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
from users_app.models import User

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

    def test_update_user_profile(self):
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

            resp = self.client.post(
                '/user/updateprofile',
                data=json.dumps(
                    {
                        'aim': 'Redeem my father.',
                        'highest_education': 'Graduated Dagobah Highschool.',
                        'sci_text_exp': 'Limited.',
                        'phase_transform_exp': 'Limited'
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
            self.assertEqual(profile_obj['highest_education'],
                             'Graduated Dagobah Highschool.')
            # Because you we spelt the key wrong -- "sci_text_exp"
            self.assertEqual(profile_obj['sci_tech_exp'], None)
            self.assertEqual(profile_obj['phase_transform_exp'], 'Limited.')

    def test_update_user_profile_no_data(self):
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

            resp = self.client.post(
                '/user/updateprofile',
                data=json.dumps(''),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type = 'application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

    def test_update_user_profile_partial_data(self):
        """
        Ensure user profile can be updated even if not all fields are provided.
        """
        han = User(
            email='han@solo.io',
            first_name='Han',
            last_name='Solo'
        )
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

            resp = self.client.post(
                '/user/updateprofile',
                data=json.dumps(
                    {
                        'aim': 'Pay Jabba.',
                        'phase_transform_exp': 'Limited'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type = 'application/json'
            )

            # data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            # TODO(davidmatthews1004@gmail.com -- Spring 6)
            # Need to validate that the profile data has been stored in the
            # database without using the get method.
            # TODO(andrew@neuraldev.io): Message to David:
            #  follow the code from above in the first User Profile test.

    def test_view_user_profile(self):
        """
        Ensure a user can view their own profile information.
        """
        obiwan = User(
            email='obiwan@jedi.io',
            first_name='Obiwan',
            last_name='Kenobi'
        )
        obiwan.set_password('HelloThere')
        obiwan.save()

        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(
                    {
                        'email': 'obiwan@jedi.io',
                        'password': 'HelloThere'
                    }
                ),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['token']

            resp_update = self.client.post(
                '/user/updateprofile',
                data=json.dumps(
                    {
                        'aim': 'Protect the Skywalker twins.',
                        'highest_education': 'Jedi Council Member',
                        'sci_text_exp': 'Flying is for droids.',
                        'phase_transform_exp': 'Limited'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp = self.client.get(
                '/user/viewprofile',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(
                data['data']['aim'], 'Protect the Skywalker twins.'
            )

    def test_update_user_profile_two_partial_data(self):
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

            resp_1 = self.client.post(
                '/user/updateprofile',
                data=json.dumps(
                    {
                        'aim' : 'Defeat the Empire',
                        'phase_transform_exp': 'Expert'
                    }
                ),
                headers = {'Authorization': 'Bearer {}'.format(token)},
                content_type = 'application/json'
            )

            resp_2 = self.client.post(
                '/user/updateprofile',
                data=json.dumps(
                    {
                        'highest_education' : 'University of Alderaan',
                        'sci_tech_exp' : 'Expert'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp = self.client.get(
                '/user/viewprofile',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp_1.status_code, 200)
            self.assertEqual(resp_2.status_code, 200)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['data']['aim'], 'Defeat the Empire')
            self.assertEqual(data['data']['phase_transform_exp'], 'Expert')
            self.assertEqual(
                data['data']['highest_education'], 'University of Alderaan'
            )
            self.assertEqual(data['data']['sci_tech_exp'], 'Expert')

    def test_view_user_profile_none(self):
        """
        Ensure view profile request fails if a user profile has not been set
        yet.
        """
        yoda = User(
            email='yoda@jedi.io',
            first_name='Yoda',
            last_name='NoLastName'
        )
        yoda.set_password('DoOrDoNot')
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

            resp = self.client.get(
                '/user/viewprofile',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'User Profile not set yet.')

    def test_update_user_profile_override(self):
        """
        Ensure updates to an existing user profile are successfull.
        """
        mace = User(
            email='mace@jedi.io',
            first_name='Mace',
            last_name='Windu'
        )
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

            resp_1 = self.client.post(
                '/user/updateprofile',
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

            resp_2 = self.client.post(
                '/user/updateprofile',
                data=json.dumps(
                    {
                        'aim': 'Stop the Sith from returning.',
                        'phase_transform_exp': 'Limited'
                    }
                ),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            resp = self.client.get(
                '/user/viewprofile',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp_1.status_code, 200)
            self.assertEqual(resp_2.status_code, 200)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['status'], 'success')
            # self.assertEqual(data['data']['aim'], 'Stop the Sith from returning.')
            self.assertEqual(data['data']['phase_transform_exp'], 'Limited')
            self.assertEqual(
                data['data']['highest_education'], 'Jedi Council Member'
            )
            self.assertEqual(data['data']['sci_tech_exp'], 'Limited')


if __name__ == '__main__':
    unittest.main()
