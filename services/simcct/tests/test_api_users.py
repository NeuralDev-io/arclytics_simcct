# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_users.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'David Matthews <@tree1004>']
__status__ = 'development'
__date__ = '2019.07.03'

import json
import unittest

from mongoengine import get_db

from arc_logging import AppLogger
from sim_api.models import (AdminProfile, User, UserProfile)
from tests.test_api_base import BaseTestCase, app
from tests.test_utilities import test_login

logger = AppLogger(__name__)


def log_test_user_in(self, user: User, password: str) -> str:
    """Log in a test user and return their token"""
    with self.client:
        resp_login = self.client.post(
            '/v1/sim/auth/login',
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
    _email = None
    _tony_pw = 'IAmIronMan!!!'
    mongo = None

    def setUp(self) -> None:
        assert app.config['TESTING'] is True
        self.mongo = get_db('default')

        # Tony is an admin
        self.tony = User(
            **{
                'email': 'ironman@avengers.com',
                'first_name': 'Tony',
                'last_name': 'Stark'
            }
        )
        self.tony.set_password(self._tony_pw)
        self.tony.verified = True

        self.tony.profile = UserProfile(
            *{
                'aim': 'Save the world',
                'highest_education': 'Genius',
                'sci_tech_exp': 'Invented J.A.R.V.I.S.',
                'phase_transform_exp': 'More than you'
            }
        )

        self.tony.admin_profile = AdminProfile(
            **{
                'position': 'Billionaire Playboy Philanthropist',
                'mobile_number': None,
                'verified': True,
                'promoted_by': None
            }
        )
        self.tony.disable_admin = False
        self.tony.save()

        user_tony = self.mongo.users.find_one(
            {'email': 'ironman@avengers.com'}
        )
        assert user_tony is not None
        assert user_tony['admin'] is True

        self._email = self.tony.email

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

    def test_ping(self):
        """Ensure the /ping route behaves correctly."""
        res = self.client.get('/v1/sim/ping')
        data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn('pong', data['message'])

    def test_single_user(self):
        """Ensure we can get a single user works as expected."""
        tony = User(
            **{
                'email': 'tony@starkindustries.com',
                'first_name': 'Tony',
                'last_name': 'Stark'
            }
        )
        tony.set_password('IAmTheRealIronMan')
        tony.save()

        with self.client as client:
            # ALREADY SET BUT HERE IT IS FOR PRINTING IF YOU WANT
            test_login(client, tony.email, 'IAmTheRealIronMan')

            resp = client.get(
                '/v1/sim/user',
                content_type='application/json',
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertIn('tony@starkindustries.com', data['data']['email'])

    def test_user_status(self):
        with self.client:
            test_login(self.client, self.tony.email, self._tony_pw)
            response = self.client.get('/v1/sim/auth/status')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(data.get('message', None))
            self.assertEqual(data.get('status'), 'success')
            self.assertTrue(data['active'])
            self.assertTrue(data['admin'])
            self.assertTrue(data['isProfile'])
            self.assertTrue(data['verified'])

    def test_single_user_not_active(self):
        """
        Ensure if user is not active they can't use authenticated endpoints
        like get: /v1/sim/user
        """
        clint = User(
            **{
                'email': 'hawkeye@avengers.io',
                'first_name': 'Clint',
                'last_name': 'Barton'
            }
        )
        clint.set_password('GoneRogue!!!')
        clint.save()

        with self.client:
            test_login(self.client, clint.email, 'GoneRogue!!!')
            # Update Tony to be inactive
            clint.reload()
            clint.active = False
            clint.save()

            resp = self.client.get(
                '/v1/sim/user',
                content_type='application/json',
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 403)
            self.assertEqual(
                data['message'], 'This user account has been disabled.'
            )
            self.assertEqual('fail', data['status'])

    def test_single_user_no_cookie(self):
        """Ensure error is thrown if there is no cookie provided."""
        with self.client:
            response = self.client.get('/v1/sim/user')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertIn('Session token is not valid.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_no_session(self):
        with self.client as client:
            # If we don't login, we have no cookie
            # We also assert there is no cookie with the current client
            # The cookie_jar is a MultiDict
            test_login(client, self.tony.email, self._tony_pw)

            # Save the cookie from login
            cookie = next(
                (
                    cookie for cookie in client.cookie_jar
                    if cookie.name == 'SESSION_TOKEN'
                ), None
            )

            # Logging out should clear the session
            client.get('/v1/sim/auth/logout', content_type='application/json')

            # Clear the cookie from previously although it should be
            # cleared by logout
            client.cookie_jar.clear()
            self.assertEqual(len(client.cookie_jar), 0)

            # We set the old Cookie back and see if it works
            client.set_cookie('localhost', 'SESSION_TOKEN', cookie.value)

            res = client.get('/v1/sim/user', content_type='application/json')
            data = json.loads(res.data.decode())

            self.assertEqual(data['message'], 'Session is invalid.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(res.status_code, 401)

    # TODO(andrew@neuraldev.io) Figure this one out.
    # def test_single_user_no_jwt(self):
    #     with app.test_client() as client:
    #         # If we don't login, we have no cookie
    #         # We also assert there is no cookie with the current client
    #         # The cookie_jar is a MultiDict
    #         test_login(client, self.tony.email, self._tony_pw)
    #
    #         # Save the cookie from login
    #         cookie = next(
    #             (cookie for cookie in client.cookie_jar if
    #              cookie.name == 'SESSION_TOKEN'),
    #             None
    #         )
    #
    #         with client.session_transaction() as sess:
    #             sess['jwt'] = None
    #             sess['ip_address'] = '127.0.0.1'
    #             sess['signed_in'] = True
    #             logger.debug(f'Client Transaction: {sess}')
    #
    #         # # Clear the cookie from previously although it should be
    #         # # cleared by logout
    #         # # client.cookie_jar.clear()
    #         # self.assertEqual(len(client.cookie_jar), 0)
    #         #
    #         # # We set the old Cookie back and see if it works
    #         # client.set_cookie('localhost', 'SESSION_TOKEN', cookie.value)
    #         #
    #         res = client.get(
    #             '/v1/sim/user',
    #             content_type='application/json',
    #             environ_base={
    #                 'HTTP_USER_AGENT': 'Chrome',
    #                 'REMOTE_ADDR': '127.0.0.1'
    #             }
    #         )
    #         data = res.json
    #         print(data)
    #         #
    #         # self.assertEqual(data['message'], 'Session is invalid.')
    #         # self.assertEqual(data['status'], 'fail')
    #         # self.assertEqual(res.status_code, 401)

    def test_unauthorized_get_all_users(self):
        """Ensure we can't get all users because we are not authorized."""
        tony = User(
            **{
                'email': 'tony@starkindustries.com',
                'first_name': 'Tony',
                'last_name': 'Stark'
            }
        )
        tony.set_password('IAmTheRealIronMan')
        tony.save()
        nat = User(
            **{
                'email': 'nat@shield.gov.us',
                'first_name': 'Natasha',
                'last_name': 'Romanoff'
            }
        )
        nat.set_password('IveGotRedInMyLedger')
        nat.save()

        with self.client:
            test_login(self.client, tony.email, 'IAmTheRealIronMan')
            resp = self.client.get(
                '/v1/sim/users',
                content_type='application/json',
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 403)
            self.assertIn('fail', data['status'])
            self.assertNotIn('data', data)
            self.assertIn('Not authorized.', data['message'])

    def test_get_all_users_bad_cookie(self):
        thor = User(
            **{
                'email': 'thor@avengers.io',
                'first_name': 'Thor',
                'last_name': 'Odinson'
            }
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
        with self.client as client:
            test_login(client, thor.email, 'StrongestAvenger')

            cookie = next(
                (
                    cookie for cookie in client.cookie_jar
                    if cookie.name == 'SESSION_TOKEN'
                ), None
            )

            cookie_value = str(cookie.value)[3:-1]
            client.cookie_jar.clear()
            client.set_cookie('localhost', 'BAD_KEY', cookie_value)

            resp = self.client.get('/v1/sim/users')
            data = json.loads(resp.data.decode())
            self.assertEqual('fail', data['status'])
            self.assertNotIn('data', data)
            self.assertEqual('Session token is not valid.', data['message'])
            self.assertEqual(resp.status_code, 401)

    def test_get_all_users(self):
        """Ensure we can get all users if logged in and authorized."""
        tony = User(
            **{
                'email': 'tony@starkindustries.com',
                'first_name': 'Tony',
                'last_name': 'Stark'
            }
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
            **{
                'email': 'steve@avengers.io',
                'first_name': 'Steve',
                'last_name': 'Rogers'
            }
        )
        steve.set_password('ICanDoThisAllDay')
        steve.save()
        nat = User(
            **{
                'email': 'nat@shield.gov.us',
                'first_name': 'Natasha',
                'last_name': 'Romanoff'
            }
        )
        nat.set_password('IveGotRedInMyLedger')
        nat.verified = True
        nat.save()
        thor = User(
            **{
                'email': 'thor@avengers.io',
                'first_name': 'Thor',
                'last_name': 'Odinson'
            }
        )
        thor.set_password('BringMeThanos')
        thor.save()
        hulk = User(
            **{
                'email': 'hulk@avengers.io',
                'first_name': 'Bruce',
                'last_name': 'Banner'
            }
        )
        hulk.set_password('HulkOut')
        hulk.save()
        hawkeye = User(
            **{
                'email': 'hawkeye@avengers.io',
                'first_name': 'Clint',
                'last_name': 'Barton'
            }
        )
        hawkeye.set_password('AndIHaveABowAndArrow')
        hawkeye.save()

        db = get_db('default')
        self.assertEqual(db.name, 'arc_test')
        num_users = len([u for u in db.users.find()])

        with self.client as client:
            test_login(client, self.tony.email, self._tony_pw)
            self.assertTrue(tony.active)
            resp = client.get(
                '/v1/sim/users',
                data=json.dumps({
                    'sort_on': 'email',
                    'limit': 2,
                    'offset': 3
                }),
                content_type='application/json',
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data['sort_on'], 'email')
            self.assertEqual(data['next_offset'], 5)
            self.assertEqual(data['prev_offset'], 1)
            self.assertEqual(data['limit'], 2)
            self.assertEqual(data['current_page'], 2)
            self.assertEqual(data['total_pages'], 4)
            self.assertEqual(data['data'][0]['email'], 'ironman@avengers.com')
            self.assertEqual(data['data'][1]['email'], 'nat@shield.gov.us')

    def test_patch_user(self):
        """Test update user details"""
        obiwan = User(
            **{
                'email': 'obiwan@arclytics.io',
                'first_name': 'Obi Wan',
                'last_name': 'Kenobi'
            }
        )
        obiwan.set_password('HelloThere')
        obiwan.save()

        with self.client as client:
            test_login(client, obiwan.email, 'HelloThere')
            resp = self.client.patch(
                '/v1/sim/user',
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
        yoda = User(
            **{
                'email': 'yoda@jedi.io',
                'first_name': 'Yoda',
                'last_name': 'Smith'
            }
        )
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

        with self.client as client:
            test_login(client, yoda.email, 'DoOrDoNot')
            resp = self.client.patch(
                '/v1/sim/user',
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
            **{
                'email': 'sheev@arclytics.io',
                'first_name': 'Sheev',
                'last_name': 'Palpatine'
            }
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

        with self.client as client:
            test_login(client, sheev.email, 'IAmTheSenate')
            resp = client.patch(
                '/v1/sim/user',
                data=json.dumps(
                    {
                        'first_name': 'Emperor',
                        'aim': 'Rule the Galaxy.',
                        'phase_transform_exp': 'Sith Lord.',
                    }
                ),
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
        maul = User(
            **{
                'email': 'maul@arclytics.io',
                'first_name': 'Darth',
                'last_name': 'Maul'
            }
        )
        maul.set_password('AtLastWeWillHaveRevenge')
        maul.save()

        with self.client as client:
            test_login(client, maul.email, 'AtLastWeWillHaveRevenge')
            resp = self.client.patch(
                '/v1/sim/user',
                data=json.dumps(''),
                content_type='application/json'
            )
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')

    def test_patch_user_existing_profile(self):
        """Test update user details if there is existing outdated data"""
        ahsoka = User(
            **{
                'email': 'ahsoka@tano.io',
                'first_name': 'Ahsoka',
                'last_name': 'tano'
            }
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

        with self.client as client:
            test_login(client, ahsoka.email, 'IAmNoJedi')

            resp = client.patch(
                '/v1/sim/user',
                data=json.dumps(
                    {
                        'last_name': 'Tano',
                        'aim': 'Follow the will of the force.',
                        'highest_education': 'Rogue.',
                        'sci_tech_exp': 'Greater.',
                        'phase_transform_exp': 'Great.',
                    }
                ),
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
            **{
                'email': 'obiwan@arclytics.io',
                'first_name': 'Obi Wan',
                'last_name': 'Kenobi'
            }
        )
        obiwan.set_password('HelloThere')
        obiwan.save()

        with self.client as client:
            test_login(client, obiwan.email, 'HelloThere')

            resp = client.patch(
                '/v1/sim/user',
                data=json.dumps(
                    {
                        'lightsaber_colour': 'blue',
                        'movie_appearances': 'I, II, III, IV, V, VI, VII',
                        'best_star_wars_character': 'Yes'
                    }
                ),
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
            **{
                'email': 'obiwan@arclytics.io',
                'first_name': 'Obi Wan',
                'last_name': 'Kenobi'
            }
        )
        obiwan.set_password('HelloThere')
        obiwan.save()

        with self.client as client:
            test_login(client, obiwan.email, 'HelloThere')

            resp = client.patch(
                '/v1/sim/user',
                data=json.dumps(
                    {
                        'first_name': 'Obi-Wan',
                        'last_name': 'Kenobi',
                        'aim': 'Train Skywalkers.',
                        'highest_education': 'Jedi Council Member.'
                    }
                ),
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
            **{
                'email': 'rex@clone.io',
                'first_name': 'Rex',
                'last_name': 'Republic'
            }
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

        with self.client as client:
            test_login(client, rex.email, 'ExperienceOutranksEverything')

            resp = client.patch(
                '/v1/sim/user',
                data=json.dumps(
                    {
                        'mobile_number': '1234567890',
                        'position': 'Discharged.'
                    }
                ),
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
            **{
                'email': 'rex@clone.io',
                'first_name': 'Rex',
                'last_name': 'Republic'
            }
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

        with self.client as client:
            test_login(client, rex.email, 'ExperienceOutranksEverything')

            resp = self.client.patch(
                '/v1/sim/user',
                data=json.dumps(
                    {
                        'mobile_number': '1234567890',
                        'position': 'Discharged.'
                    }
                ),
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
            **{
                'email': 'jabba@hutt.io',
                'first_name': 'Jabba',
                'last_name': 'The Hutt'
            }
        )
        jabba.set_password('ThereWillBeNoBargain')
        jabba.save()

        with self.client as client:
            test_login(client, jabba.email, 'ThereWillBeNoBargain')

            resp = self.client.post(
                '/v1/sim/user/profile',
                data=json.dumps(
                    {
                        'aim': 'Find Han Solo.',
                        'highest_education': 'Hutt school of fatness.',
                        'sci_tech_exp': 'PHD.',
                        'phase_transform_exp': 'PHD.'
                    }
                ),
                content_type='application/json'
            )

            data = resp.json
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
            **{
                'email': 'lando@arclytics.io',
                'first_name': 'Lando',
                'last_name': 'Calrissian'
            }
        )
        lando.set_password('TheShieldIsStillUp')
        lando.save()

        with self.client as client:
            test_login(client, lando.email, 'TheShieldIsStillUp')
            resp = client.post(
                '/v1/sim/user/profile',
                data=json.dumps(''),
                content_type='application/json'
            )

            data = json.loads(resp.data.decode())
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(data['status'], 'fail')

    def test_post_user_profile_missing_data(self):
        """Test incomplete post is unsuccessful"""
        boba = User(
            **{
                'email': 'boba@fett.com',
                'first_name': 'Boba',
                'last_name': 'Fett'
            }
        )
        boba.set_password('NoGoodToMeDead')
        boba.save()

        with self.client as client:
            test_login(client, boba.email, 'NoGoodToMeDead')

            resp = client.post(
                '/v1/sim/user/profile',
                data=json.dumps(
                    {
                        'highest_education': 'Bounty Hunter Academy.',
                        'sci_tech_exp': 'Weapons Expert.',
                        'phase_transform_exp': 'Limited.'
                    }
                ),
                content_type='application/json'
            )

            data = resp.json
            err = (
                f"ValidationError (User:{boba.id}) (aim.Field is "
                f"required: ['profile'])"
            )
            self.assertEqual(data['error'], err)
            self.assertEqual(data['message'], 'Validation error.')
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(resp.status_code, 400)

    def test_disable_account(self):
        """Test disable account is successful"""
        kylo = User(
            **{
                'email': 'kyloren@gmail.com',
                'first_name': 'Kylo',
                'last_name': 'Ren'
            }
        )
        kylo.set_password('LetStarWarsDie')
        kylo.save()

    # def test_search_users_no_search_on(self):
    #     """Ensure a search request with no search_on value fails"""
    #     vos = User(
    #         **{
    #             'email': 'quinlan@arclytics.io',
    #             'first_name': 'Quinlan',
    #             'last_name': 'Vos'
    #         }
    #     )
    #     vos.set_password('expertTracker')
    #     vos.admin_profile = AdminProfile(
    #         position='Position',
    #         mobile_number=None,
    #         verified=True,
    #         promoted_by=None
    #     )
    #     vos.verified = True
    #     vos.save()
    #
    #     with self.client as client:
    #         test_login(client, vos.email, 'expertTracker')
    #         resp = client.get(
    #             '/v1/sim/users/search',
    #             data=json.dumps({
    #                 'sort_on': '-fullname'
    #             }),
    #             content_type='application/json'
    #         )
    #         data = json.loads(resp.data.decode())
    #         self.assertEqual(resp.status_code, 400)
    #         self.assertEqual(data['message'], 'No search parameters provided.')
    #
    # def test_search_users_invalid_search_on(self):
    #     """Ensure a search request with an invalid search_on value fails"""
    #     vos = User(
    #         **{
    #             'email': 'quinlan@arclytics.io',
    #             'first_name': 'Quinlan',
    #             'last_name': 'Vos'
    #         }
    #     )
    #     vos.set_password('expertTracker')
    #     vos.admin_profile = AdminProfile(
    #         position='Position',
    #         mobile_number=None,
    #         verified=True,
    #         promoted_by=None
    #     )
    #     vos.verified = True
    #     vos.save()
    #
    #     with self.client as client:
    #         test_login(client, vos.email, 'expertTracker')
    #         resp = client.get(
    #             '/v1/sim/users/search',
    #             data=json.dumps({
    #                 'search_on': 'force abilities',
    #                 'search_for': 'Force Speed'
    #             }),
    #             content_type='application/json'
    #         )
    #         data = json.loads(resp.data.decode())
    #         self.assertEqual(resp.status_code, 400)
    #         self.assertEqual(
    #             data['message'], 'Invalid search on attribute: force abilities.'
    #         )
    #
    # def test_search_users_success(self):
    #     """Ensure valid search requests on the users database are successful"""
    #     vos = User(
    #         **{
    #             'email': 'quinlan@arclytics.io',
    #             'first_name': 'Quinlan',
    #             'last_name': 'Vos'
    #         }
    #     )
    #     vos.set_password('expertTracker')
    #     vos.admin_profile = AdminProfile(
    #         position='Position',
    #         mobile_number=None,
    #         verified=True,
    #         promoted_by=None
    #     )
    #     vos.verified = True
    #     vos.save()
    #     kenobi = User(
    #         **{
    #             'email': 'obiwan@arclytics.io',
    #             'first_name': 'Obi Wan',
    #             'last_name': 'Kenobi'
    #         }
    #     )
    #     kenobi.set_password('HelloThere')
    #     kenobi.save()
    #     skywalker = User(
    #         **{
    #             'email': 'anakin@arclytics.io',
    #             'first_name': 'Anakin',
    #             'last_name': 'Skywalker'
    #         }
    #     )
    #     skywalker.set_password('YouUnderestimateMyPower')
    #     skywalker.save()
    #     ahsoka = User(
    #         **{
    #             'email': 'ahsoka@gmail.com',
    #             'first_name': 'Ahsoka',
    #             'last_name': 'Tano'
    #         }
    #     )
    #     ahsoka.set_password('YouAlwaysBlameTheShip')
    #     ahsoka.save()
    #     plo = User(
    #         **{
    #             'email': 'plokoon@gmail.com',
    #             'first_name': 'Plo',
    #             'last_name': 'Koon'
    #         }
    #     )
    #     plo.set_password('WhenYouAskForTrouble')
    #     plo.save()
    #     aayla = User(
    #         **{
    #             'email': 'aalya@arclytics.io',
    #             'first_name': 'Aayla',
    #             'last_name': 'Secura'
    #         }
    #     )
    #     aayla.set_password('AStrongBelief')
    #     aayla.save()
    #     yoda = User(
    #         **{
    #             'email': 'yoda@gmail.com',
    #             'first_name': 'Master',
    #             'last_name': 'Yoda'
    #         }
    #     )
    #     yoda.set_password('DoOrDoNot')
    #     yoda.save()
    #     mace = User(
    #         **{
    #             'email': 'mace@arclytics.io',
    #             'first_name': 'Mace',
    #             'last_name': 'Windu'
    #         }
    #     )
    #     mace.set_password('ThisPartysOver')
    #     mace.save()
    #
    #     with self.client as client:
    #         test_login(client, vos.email, 'expertTracker')
    #         resp = client.get(
    #             '/v1/sim/users/search',
    #             data=json.dumps({
    #                 'search_on': 'email',
    #                 'search_for': 'arclytics',
    #                 'sort_on': 'fullname',
    #                 'limit': 2
    #             }),
    #             content_type='application/json'
    #         )
    #         data = json.loads(resp.data.decode())
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertEqual(data['status'], 'success')
    #         self.assertEqual(data['data'][0]['email'], 'obiwan@arclytics.io')
    #         self.assertEqual(data['sort_on'], 'fullname')
    #         self.assertEqual(data['search_on'], 'email')
    #         self.assertEqual(data['search_for'], 'arclytics')
    #         self.assertEqual(data['next_offset'], 3)
    #         self.assertEqual(data['prev_offset'], None)
    #         self.assertEqual(data['limit'], 2)
    #         self.assertEqual(data['current_page'], 1)
    #         self.assertEqual(data['total_pages'], 3)
    #
    #         resp2 = client.get(
    #             '/v1/sim/users/search',
    #             data=json.dumps({
    #                 'search_on': 'first_name',
    #                 'search_for': 'o',
    #                 'sort_on': 'fullname',
    #                 'limit': 2,
    #                 'offset': 3
    #             }),
    #             content_type='application/json'
    #         )
    #         data2 = json.loads(resp2.data.decode())
    #         self.assertEqual(resp2.status_code, 200)
    #         self.assertEqual(data2['status'], 'success')
    #         self.assertEqual(data2['data'][1]['email'], 'ahsoka@gmail.com')
    #         self.assertEqual(data2['sort_on'], 'fullname')
    #         self.assertEqual(data2['search_on'], 'first_name')
    #         self.assertEqual(data2['search_for'], 'o')
    #         self.assertEqual(data2['next_offset'], None)
    #         self.assertEqual(data2['prev_offset'], 1)
    #         self.assertEqual(data2['limit'], 2)
    #         self.assertEqual(data2['current_page'], 2)
    #         self.assertEqual(data2['total_pages'], 2)
    #

if __name__ == '__main__':
    unittest.main()
