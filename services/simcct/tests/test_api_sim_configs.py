# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_sim_configs.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__status__ = 'development'
__date__ = '2019.07.13'

import json
import unittest
from pathlib import Path

import numpy as np
from mongoengine import get_db

from arc_logging import AppLogger
from manage import BASE_DIR
from sim_api.extensions.SimSession import SimSessionService
from sim_api.models import AlloyStore, Configuration, User
from sim_api.schemas import AlloyStoreSchema, ConfigurationsSchema
from tests.test_api_base import BaseTestCase, app
from tests.test_utilities import test_login

logger = AppLogger(__name__)

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'tests' / 'sim_configs.json'
with open(_TEST_CONFIGS_PATH, 'r') as f:
    test_json = json.load(f)


# noinspection PyTypeChecker
class TestSimConfigurations(BaseTestCase):

    # NOTE:
    #  - We can treat the session stores of the compositions and configurations
    #    as always being the one that's displayed on the Client UI.

    _email = None
    _user_pw = 'IllShowYouFerocity!@!@'
    mongo = None

    @classmethod
    def setUpClass(cls) -> None:
        assert app.config['TESTING'] is True

        # Tony is an admin
        cls.user = User(
            **{
                'email': 'antman@pymindustries.io',
                'first_name': 'Hank',
                'last_name': 'Pym'
            }
        )
        cls.user.set_password(cls._user_pw)
        cls.user.verified = True

        configs = ConfigurationsSchema().load(test_json['configurations'])
        store_dict = {
            'alloy_option': 'single',
            'alloys': {
                'parent': {
                    'name': 'Arc_Stark',
                    'compositions': test_json['compositions']
                },
                'weld': None,
                'mix': None
            }
        }
        alloy_store = AlloyStoreSchema().load(store_dict)

        cls.user.last_alloy_store = alloy_store
        cls.user.last_configuration = configs

        cls.user.save()
        cls._email = cls.user.email

        mongo = get_db('default')
        user = mongo.users.find_one({'email': 'antman@pymindustries.io'})
        assert user is not None

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete users collection so no conflict."""
        db = get_db('default')
        assert db.name == 'arc_test'
        db.users.drop()

    def login_client(self, client):
        """Set up a User for the simulation."""
        test_login(client, self._email, self._user_pw)

        session_store: dict = SimSessionService().load_session()
        configs: dict = session_store['configurations']
        alloy_store: dict = session_store['alloy_store']

        return configs, alloy_store

    def logout_client(self, client):
        resp_login = client.get(
            '/api/v1/sim/auth/logout',
            content_type='application/json',
            environ_base={'REMOTE_ADDR': '127.0.0.1'}
        )
        self.assertStatus(resp_login, 202)

    def test_sim_configs_no_session_key(self):
        """Ensure if we don't pass a session key it fails."""
        with app.test_client() as client:
            self.login_client(client)

            client.cookie_jar.clear()

            # Don't need data in any of these as Middleware should go first.
            res = client.patch(
                '/api/v1/sim/configs/update',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assert401(res)

            res = client.put(
                '/api/v1/sim/configs/method/update',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assert401(res)

            res = client.get(
                '/api/v1/sim/configs/ms',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assert401(res)

            res = client.put(
                '/api/v1/sim/configs/ms',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assert401(res)

            res = client.get(
                '/api/v1/sim/configs/bs',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assert401(res)

            res = client.put(
                '/api/v1/sim/configs/bs',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assert401(res)

            res = client.get(
                '/api/v1/sim/configs/ae',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assert401(res)

            res = client.put(
                '/api/v1/sim/configs/ae',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assert401(res)

    def test_on_method_change(self):
        """Ensure we can change the method in the session store."""
        with app.test_client() as client:
            self.login_client(client)

            method = 'Kirkaldy83'
            res = client.put(
                '/api/v1/sim/configs/method/update',
                data=json.dumps({'method': method}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            session_store = SimSessionService().load_session()
            session_configs = session_store.get('configurations')
            self.assertEqual(data['message'], f'Changed to {method} method.')
            self.assertEqual(data['status'], 'success')
            self.assert200(res)
            self.assertEqual(session_configs['method'], 'Kirkaldy83')

            method = 'Li98'
            res = client.put(
                '/api/v1/sim/configs/method/update',
                data=json.dumps({'method': method}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            session_store = SimSessionService().load_session()
            session_configs = session_store.get('configurations')
            self.assertEqual(data['message'], f'Changed to {method} method.')
            self.assertEqual(data['status'], 'success')
            self.assert200(res)
            self.assertEqual(session_configs['method'], method)

    def test_auto_update_ms(self):
        """Ensure we get the correct calculations for MS given the alloy."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.get(
                '/api/v1/sim/configs/ms', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            session_store = SimSessionService().load_session()
            sess_configs = session_store.get('configurations')
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_configs['auto_calculate_ms'])
            ms_temp = np.float32(data['data']['ms_temp'])
            ms_rate_param = np.float32(data['data']['ms_rate_param'])
            self.assertAlmostEqual(sess_configs['ms_temp'], 464.1792, 2)
            self.assertAlmostEqual(sess_configs['ms_rate_param'], 0.020691, 2)
            self.assertAlmostEqual(ms_temp, 464.1792, 2)
            self.assertAlmostEqual(ms_rate_param, 0.020691, 2)

    def test_auto_update_bs(self):
        """Ensure we get the correct calculations for BS given the alloy."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.get(
                '/api/v1/sim/configs/bs', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            session_store = SimSessionService().load_session()
            sess_configs = session_store.get('configurations')
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_configs['auto_calculate_bs'])
            ms_temp = np.float32(data['data']['bs_temp'])
            self.assertAlmostEqual(sess_configs['bs_temp'], 563.2208, 2)
            self.assertAlmostEqual(ms_temp, 563.2208, 2)

    def test_auto_update_ae(self):
        """Ensure we get the correct calculations for Ae1 and Ae3 given the
        testing configs and the testing compositions.
        """
        with app.test_client() as client:
            self.login_client(client)

            res = client.get(
                '/api/v1/sim/configs/ae',
                data=json.dumps({'auto_calculate_ae': True}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            session_store = SimSessionService().load_session()
            sess_configs = session_store['configurations']
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_configs['auto_calculate_ae'])
            ae1 = np.float64(data['data']['ae1_temp'])
            ae3 = np.float64(data['data']['ae3_temp'])
            self.assertAlmostEqual(sess_configs['ae1_temp'], 700.8947, 2)
            self.assertAlmostEqual(sess_configs['ae3_temp'], 845.8189, 2)
            self.assertAlmostEqual(ae1, 700.8947, 2)
            self.assertAlmostEqual(ae3, 845.8189, 2)

    def test_configurations_no_session(self):
        """Ensure it fails with no header."""
        with app.test_client() as client:
            # We login to get a valid cookie
            cookie = test_login(client, self.user.email, self._user_pw)
            # Logout should clear the Cookie and Session from being valid
            self.logout_client(client)

            # Reset the cookie for the next request but it should not
            # be the one that retrieves a valid session.
            client.set_cookie('localhost', cookie['key'], cookie['value'])

            method = 'Kirkaldy83'
            res = client.put(
                '/api/v1/sim/configs/method/update',
                data=json.dumps({'method': method}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert401(res)
            self.assertEqual(data['message'], 'Session is invalid.')
            self.assertEqual(data['status'], 'fail')

    def test_configurations_bad_cookie(self):
        """Ensure it fails with a bad header."""
        with app.test_client() as client:
            cookie = test_login(client, self.user.email, self._user_pw)
            self.logout_client(client)

            client.set_cookie('localhost', 'BAD_KEY', cookie['value'])

            method = 'Kirkaldy83'
            res = client.put(
                '/api/v1/sim/configs/method/update',
                data=json.dumps({'method': method}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert401(res)
            self.assertEqual(data['message'], 'Session token is not valid.')
            self.assertEqual(data['status'], 'fail')

    def test_configurations_empty_payload(self):
        """Ensure you miss 100% of the shots you don't take."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.put(
                '/api/v1/sim/configs/method/update',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

            res = client.patch(
                '/api/v1/sim/alloys/update',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

            res = client.patch(
                '/api/v1/sim/configs/update',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

    def test_on_method_change_no_method_payload(self):
        with app.test_client() as client:
            self.login_client(client)

            res = client.put(
                '/api/v1/sim/configs/method/update',
                data=json.dumps({'method': ''}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'No method was provided.')
            self.assertEqual(data['status'], 'fail')

    def test_on_method_change_incorrect_method_payload(self):
        with app.test_client() as client:
            self.login_client(client)

            res = client.put(
                '/api/v1/sim/configs/method/update',
                data=json.dumps({'method': 'AndrewMethod!'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(
                data['message'],
                'Invalid method provided (must be Li98 or Kirkaldy83).'
            )
            self.assertEqual(data['status'], 'fail')

    def test_on_method_change_empty_session_store(self):
        with app.test_client() as client:
            cookie = test_login(client, self.user.email, self._user_pw)
            self.logout_client(client)

            client.set_cookie('localhost', cookie['key'], cookie['value'])

            res = client.put(
                '/api/v1/sim/configs/method/update',
                data=json.dumps({'method': 'Kirkaldy83'}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Session is invalid.')
            self.assert401(res)
            self.assertEqual(data['status'], 'fail')

    def test_auto_update_ms_kirkaldy_method(self):
        """Ensure we get the correct calculations for MS and BS given Kirkaldy83
        method testing configs and the testing compositions.
        """
        with app.test_client() as client:
            self.login_client(client)

            res_method_update = client.put(
                '/api/v1/sim/configs/method/update',
                data=json.dumps({'method': 'Kirkaldy83'}),
                content_type='application/json'
            )
            self.assert200(res_method_update)

            res = client.get(
                '/api/v1/sim/configs/ms', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            session_store = SimSessionService().load_session()
            sess_configs = session_store.get('configurations')
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_configs['auto_calculate_ms'])
            ms_temp = np.float32(data['data']['ms_temp'])
            ms_rate_param = np.float32(data['data']['ms_rate_param'])
            self.assertAlmostEqual(sess_configs['ms_temp'], 477.5753, 3)
            self.assertAlmostEqual(sess_configs['ms_rate_param'], 0.02069, 2)
            self.assertAlmostEqual(ms_temp, 477.5753, 2)
            self.assertAlmostEqual(ms_rate_param, 0.02069, 2)

    def test_auto_update_bs_kirkaldy_method(self):
        """Ensure we get the correct calculations for BS given Kirkaldy83
        method testing configs and the testing compositions.
        """
        with app.test_client() as client:
            self.login_client(client)

            res_method_update = client.put(
                '/api/v1/sim/configs/method/update',
                data=json.dumps({'method': 'Kirkaldy83'}),
                content_type='application/json'
            )
            self.assert200(res_method_update)

            res = client.get(
                '/api/v1/sim/configs/bs', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            session_store = SimSessionService().load_session()
            sess_configs = session_store['configurations']
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_configs['auto_calculate_bs'])
            bs_temp = np.float32(data['data']['bs_temp'])
            self.assertAlmostEqual(sess_configs['bs_temp'], 565.723, 2)
            self.assertAlmostEqual(bs_temp, 565.723, 2)

    def test_on_configs_change(self):
        """Ensure that if we send new configurations we store it in session."""
        with app.test_client() as client:
            configs, _ = self.login_client(client)
            # Since login stores the configs already, we need to make some
            # changes to see if it updates.

            # Since this is a patch method and we only want to change 1 thing
            res = client.patch(
                '/api/v1/sim/configs/update',
                data=json.dumps({'start_temp': 901}),
                content_type='application/json'
            )
            self.assertEqual(res.status_code, 202)
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            session_store = SimSessionService().load_session()
            sess_configs = session_store.get('configurations')
            # This is just for ensuring they're the same overall
            setup_configs = {
                'grain_size': configs['grain_size'],
                'nucleation_start': configs['nucleation_start'],
                'nucleation_finish': configs['nucleation_finish'],
                'start_temp': 901,
                'cct_cooling_rate': configs['cct_cooling_rate']
            }
            sess_setup_configs = {
                'grain_size': sess_configs['grain_size'],
                'nucleation_start': sess_configs['nucleation_start'],
                'nucleation_finish': sess_configs['nucleation_finish'],
                'start_temp': sess_configs['start_temp'],
                'cct_cooling_rate': sess_configs['cct_cooling_rate']
            }
            self.assertEqual(setup_configs, sess_setup_configs)

    def test_on_configs_change_empty_json(self):
        """Ensure that if we send an empty JSON we get an error."""
        with app.test_client() as client:
            self.login_client(client)
            res = client.patch(
                '/api/v1/sim/configs/update',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

    def test_on_configs_change_before_login(self):
        """Ensure if the user has not logged in, they have no previous store."""

        configs = test_json['configurations']
        configs.pop('nucleation_start')
        configs.pop('nucleation_finish')

        with app.test_client() as client:
            cookie = test_login(client, self.user.email, self._user_pw)
            self.logout_client(client)

            client.set_cookie('localhost', cookie['key'], cookie['value'])

            res = client.patch(
                '/api/v1/sim/configs/update',
                data=json.dumps(configs),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['message'], 'Session is invalid.')
            self.assertEqual(data['status'], 'fail')
            self.assert401(res)

    def test_on_configs_change_invalid_schema(self):
        """Ensure if we send no valid data we get an error response."""
        with app.test_client() as client:
            self.login_client(client)
            res = client.patch(
                '/api/v1/sim/configs/update',
                data=json.dumps({'nuc_start': 123}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'Payload does not have any valid keys.'
            )

    def test_update_ms_empty_payload(self):
        """Ensure an empty payload for MS does not pass."""
        with app.test_client() as client:
            self.login_client(client)
            res = client.put(
                '/api/v1/sim/configs/ms',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['message'], 'Invalid payload.')
            self.assertEquals(data['status'], 'fail')

    def test_update_bs_empty_payload(self):
        """Ensure an empty payload for BS does not pass."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.put(
                '/api/v1/sim/configs/bs',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'Invalid payload.')

    def test_update_ms_missing_ms_payload(self):
        """Ensure an missing ms_temp payload does not pass."""
        with app.test_client() as client:
            self.login_client(client)
            ms_configs = {'ms_rate_param': 0.9}

            res = client.put(
                '/api/v1/sim/configs/ms',
                data=json.dumps(ms_configs),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'MS temperature is required.')

    def test_update_ms_no_prev_configs(self):
        """Ensure if there is no prev. configs MS payload does not pass."""
        with app.test_client() as client:
            # We login to get a cookie
            _, _ = self.login_client(client)

            # We change the session by making a transaction on it within context
            # Note: ENSURE that `environ_overrides={'REMOTE_ADDR': '127.0.0.1'}`
            #  is set because otherwise opening a transaction will not use
            #  a standard HTTP request environ_base.
            with client.session_transaction(
                environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ) as session:
                session['simulation'] = None
            with client.session_transaction(
                environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ):
                # At this point the session transaction has been updated so
                # we can check the session within the context
                session_store = SimSessionService().load_session()
                self.assertIsInstance(session_store, str)
                self.assertEqual(session_store, 'Session is empty.')

            ms_configs = {
                'ms_temp': 464.196,
                'ms_rate_param': 0.0168,
            }

            res = client.put(
                '/api/v1/sim/configs/ms',
                data=json.dumps(ms_configs),
                content_type='application/json',
                environ_base={'REMOTE_ADDR': '127.0.0.1'}
            )
            data = json.loads(res.data.decode())
            self.assertEquals(
                data['message'], 'Cannot retrieve data from Session store.'
            )
            self.assertEqual(res.status_code, 500)
            self.assertEquals(data['status'], 'fail')

    def test_update_bs_no_prev_configs(self):
        """Ensure if there is no prev. configs BS payload does not pass."""
        with app.test_client() as client:
            # We login to get a cookie
            _, _ = self.login_client(client)

            # We change the session by making a transaction on it within context
            # Note: ENSURE that `environ_overrides={'REMOTE_ADDR': '127.0.0.1'}`
            #  is set because otherwise opening a transaction will not use
            #  a standard HTTP request environ_base.
            with client.session_transaction(
                environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ) as session:
                session['simulation'] = None
            with client.session_transaction(
                environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ):
                # At this point the session transaction has been updated so
                # we can check the session within the context
                session_store = SimSessionService().load_session()
                self.assertIsInstance(session_store, str)
                self.assertEqual(session_store, 'Session is empty.')

            bs_configs = {'bs_temp': 563.238}

            res = client.put(
                '/api/v1/sim/configs/bs',
                data=json.dumps(bs_configs),
                content_type='application/json',
                environ_base={'REMOTE_ADDR': '127.0.0.1'}
            )
            data = json.loads(res.data.decode())
            self.assertEquals(
                data['message'], 'Cannot retrieve data from Session store.'
            )
            self.assertEquals(data['status'], 'fail')
            self.assertEqual(res.status_code, 500)

    def test_update_ms(self):
        """Ensure a valid payload of MS will do just as we expect."""
        with app.test_client() as client:
            self.login_client(client)
            configs = {
                'ms_temp': 464.196,
                'ms_rate_param': 0.0168,
            }

            res = client.put(
                '/api/v1/sim/configs/ms',
                data=json.dumps(configs),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)
            session_store = SimSessionService().load_session()
            sess = session_store.get('configurations')
            self.assertEquals(sess['ms_temp'], configs['ms_temp'])
            self.assertEquals(sess['ms_rate_param'], configs['ms_rate_param'])

    def test_update_bs(self):
        """Ensure a valid payload of BS will do just as we expect."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.put(
                '/api/v1/sim/configs/bs',
                data=json.dumps({'bs_temp': 563.238}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)
            session_store = SimSessionService().load_session()
            sess = session_store.get('configurations')
            self.assertEquals(sess['bs_temp'], 563.238)

    def test_update_ae_empty_payload(self):
        """Ensure an empty payload does not pass."""
        with app.test_client() as client:
            self.login_client(client)

            res = client.put(
                '/api/v1/sim/configs/ae',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEquals(data['message'], 'Invalid payload.')
            self.assertEquals(data['status'], 'fail')
            self.assertEqual(res.status_code, 400)

    def test_update_ae_missing_ae1_payload(self):
        """Ensure an missing ms_temp payload does not pass."""
        with app.test_client() as client:
            self.login_client(client)
            bad_ae_configs = {
                'ae3_temp': 700.902,
            }

            res = client.put(
                '/api/v1/sim/configs/ae',
                data=json.dumps(bad_ae_configs),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'Ae1 temperature is required.')

    def test_update_ae_missing_ae3_payload(self):
        """Ensure an missing bs_temp payload does not pass."""
        with app.test_client() as client:
            self.login_client(client)
            bad_ae_configs = {
                'ae1_temp': 700.902,
            }

            res = client.put(
                '/api/v1/sim/configs/ae',
                data=json.dumps(bad_ae_configs),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'Ae3 temperature is required.')

    def test_update_ae_no_prev_configs(self):
        """Ensure an missing bs_temp payload does not pass."""
        with app.test_client() as client:
            # We login to get a cookie
            _, _ = self.login_client(client)

            # We change the session by making a transaction on it within context
            # Note: ENSURE that `environ_overrides={'REMOTE_ADDR': '127.0.0.1'}`
            #  is set because otherwise opening a transaction will not use
            #  a standard HTTP request environ_base.
            with client.session_transaction(
                environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ) as session:
                session['simulation'] = None
            with client.session_transaction(
                environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ):
                # At this point the session transaction has been updated so
                # we can check the session within the context
                session_store = SimSessionService().load_session()
                self.assertIsInstance(session_store, str)
                self.assertEqual(session_store, 'Session is empty.')

            ae_configs = {'ae1_temp': 700.902, 'ae3_temp': 845.838}

            res = client.put(
                '/api/v1/sim/configs/ae',
                data=json.dumps(ae_configs),
                content_type='application/json',
                environ_base={'REMOTE_ADDR': '127.0.0.1'}
            )
            data = json.loads(res.data.decode())
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(
                data['message'], 'Cannot retrieve data from Session store.'
            )
            self.assertEqual(res.status_code, 500)

    def test_update_ae(self):
        """Ensure a valid payload of MS and BS will do just as we expect."""
        with app.test_client() as client:
            self.login_client(client)
            new_ae = {'ae1_temp': 700.902, 'ae3_temp': 845.838}

            res = client.put(
                '/api/v1/sim/configs/ae',
                data=json.dumps(new_ae),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)
            session_store = SimSessionService().load_session()
            sess = session_store.get('configurations')
            self.assertEquals(sess['ae1_temp'], new_ae['ae1_temp'])
            self.assertEquals(sess['ae3_temp'], new_ae['ae3_temp'])


if __name__ == '__main__':
    unittest.main()
