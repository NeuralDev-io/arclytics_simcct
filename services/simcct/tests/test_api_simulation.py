# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_simulation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__status__ = 'development'
__date__ = '2019.07.17'

import os
import unittest
from copy import deepcopy
from pathlib import Path

from flask import json
from mongoengine import get_db

from arc_logging import AppLogger
from sim_api.models import User
from tests.test_api_base import BaseTestCase, app
from tests.test_utilities import test_login

logger = AppLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir))
_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'sim_configs.json'
with open(_TEST_CONFIGS_PATH, 'r') as f:
    test_json = json.load(f)

ALLOY_STORE = {
    'alloy_option': 'single',
    'alloys': {
        'parent': {
            'name': 'Arc_Stark',
            'compositions': test_json['compositions']
        }
    }
}

CONFIGS = test_json['configurations']


class TestSimulationService(BaseTestCase):
    _email = None
    _user_pw = 'IMissThor!!!'
    mongo = None

    @classmethod
    def setUpClass(cls) -> None:
        assert app.config['TESTING'] is True

        cls.user = User(
            **{
                'email': 'jane@culver.edu.us',
                'first_name': 'Jane',
                'last_name': 'Foster',
            }
        )
        cls.user.set_password(cls._user_pw)
        cls.user.verified = True
        cls.user.save()
        cls._email = cls.user.email

        mongo = get_db('default')
        user = mongo.users.find_one({'email': 'jane@culver.edu.us'})
        assert user is not None

    @classmethod
    def tearDownClass(cls) -> None:
        """On finishing, we should delete users collection so no conflict."""
        db = get_db('default')
        assert db.name == 'arc_test'
        db.users.drop()

    def test_simulate_with_login(self):
        """Ensure there is a successful simulation get request."""
        configs = deepcopy(CONFIGS)
        with app.test_client() as client:
            test_login(client, self._email, self._user_pw)

            # We need to update Ae, MS, and BS in the configs
            res = client.post(
                '/v1/sim/configs/ae',
                data=json.dumps(
                    {
                        'alloy_store': ALLOY_STORE,
                        'method': 'Li98'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assert200(res)

            configs.update(
                {
                    'ae1_temp': data['data']['ae1_temp'],
                    'ae3_temp': data['data']['ae3_temp'],
                }
            )

            res = client.post(
                '/v1/sim/configs/ms',
                data=json.dumps(
                    {
                        'alloy_store': ALLOY_STORE,
                        'method': 'Li98'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assert200(res)

            configs.update(
                {
                    'ms_temp': data['data']['ms_temp'],
                    'ms_rate_param': data['data']['ms_rate_param'],
                }
            )

            res = client.post(
                '/v1/sim/configs/bs',
                data=json.dumps(
                    {
                        'alloy_store': ALLOY_STORE,
                        'method': 'Li98'
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assert200(res)

            configs.update({'bs_temp': data['data']['bs_temp']})

            # Now we can run
            res = client.post(
                '/v1/sim/simulate',
                data=json.dumps(
                    {
                        'alloy_store': ALLOY_STORE,
                        'configurations': configs
                    }
                ),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            logger.debug(data)
            self.assertFalse(data.get('message', None))
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])
            self.assertEqual(
                len(data['data']['CCT']['ferrite_nucleation']['time']),
                len(data['data']['CCT']['ferrite_nucleation']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['ferrite_completion']['time']),
                len(data['data']['CCT']['ferrite_completion']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['pearlite_nucleation']['time']),
                len(data['data']['CCT']['pearlite_nucleation']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['pearlite_completion']['time']),
                len(data['data']['CCT']['pearlite_completion']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['bainite_nucleation']['time']),
                len(data['data']['CCT']['bainite_nucleation']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['bainite_completion']['time']),
                len(data['data']['CCT']['bainite_completion']['temp'])
            )
            self.assertEqual(
                len(data['data']['CCT']['martensite']['time']),
                len(data['data']['CCT']['martensite']['temp'])
            )

    def test_ae3equilibrium_no_prev_configs(self):
        """
        Ensure that a request for the ae3euquilibrium data fails if no prev
        config is available.
        """
        with app.test_client() as client:
            self.login_client(client)

            # We change the session by making a transaction on it within context
            # Note: ENSURE that `environ_overrides={'REMOTE_ADDR': '127.0.0.1'}`
            #  is set because otherwise opening a transaction will not use
            #  a standard HTTP request environ_base.
            with client.session_transaction(
                environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ) as session:
                # Setting the `simulation` key in the session to None will clear
                # out any config data so we can test the behaviour of the
                # endpoint when it is unable to retrieve the config data from
                # the session.
                session['simulation'] = None
            with client.session_transaction(
                environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ):
                # At this point the session transaction has been updated so
                # we can check the session within the context
                session_store = SimSessionService().load_session()
                self.assertIsInstance(session_store, str)
                self.assertEqual(session_store, 'Session is empty.')

            res = client.get(
                '/v1/sim/ae3equilibrium', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'Cannot retrieve data from Session store.'
            )
            self.assertEqual(data['status'], 'fail')
            self.assertStatus(res, 500)

    def test_ae3equilibrium_no_prev_alloy(self):
        """
        Ensure that a request for the ae3equilibrium data fails if no prev alloy
        is available.
        """
        with app.test_client() as client:
            self.login_client(client)

            # We change the session by making a transaction on it within context
            # Note: ENSURE that `environ_overrides={'REMOTE_ADDR': '127.0.0.1'}`
            #  is set because otherwise opening a transaction will not use
            #  a standard HTTP request environ_base.
            with client.session_transaction(
                environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            ) as session:
                # Override the session data and set the alloy information to
                # None.
                session_store = json.loads(session['simulation'])
                session_store['alloy_store']['alloys']['parent'] = None
                ser_session_data = json.dumps(session_store)
                prefix = SimSessionService.SESSION_PREFIX
                session[prefix] = ser_session_data

            res = client.get(
                '/v1/sim/ae3equilibrium', content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'], 'No previous session alloy was set.'
            )
            self.assert404(res)
            self.assertEqual(data['status'], 'fail')

    def test_ae3equilibrium_with_login(self):
        with app.test_client() as client:
            self.login_client(client)

            # MUST have AE and MS/BS > 0.0 before we can run simulate
            res = client.get(
                '/v1/sim/configs/ae', content_type='application/json'
            )
            self.assert200(res)

            res = client.get(
                '/v1/sim/configs/ms', content_type='application/json'
            )
            self.assert200(res)
            res = client.get(
                '/v1/sim/configs/bs', content_type='application/json'
            )
            self.assert200(res)

            res = client.get(
                '/v1/sim/ae3equilibrium', content_type='application/json'
            )
            data = json.loads(res.data.decode())


if __name__ == '__main__':
    unittest.main()
