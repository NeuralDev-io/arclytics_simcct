# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_sim_configs.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.13'

import json
import unittest
import numpy as np
from pathlib import Path

from bson import ObjectId
from flask import session, current_app

from tests.test_api_base import BaseTestCase
from sim_app.app import BASE_DIR
from sim_app.schemas import ConfigurationsSchema, AlloyStoreSchema

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'


class TestSimConfigurations(BaseTestCase):

    # NOTE:
    #  - We can treat the session stores of the compositions and configurations
    #    as always being the one that's displayed on the Client UI.

    def login_client(self, client):
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

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

        token = 'ABCDEFGHIJKLMOPQRSTUVWXYZ123'
        _id = ObjectId()

        sess_res = client.post(
            '/session/login',
            data=json.dumps(
                {
                    '_id': str(_id),
                    'last_configurations': configs,
                    'last_alloy_store': alloy_store
                }
            ),
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        data = json.loads(sess_res.data.decode())
        session_store = session.get(f'{token}:alloy_store')
        self.assertEqual(data['status'], 'success')
        self.assertTrue(sess_res.status_code == 201)
        self.assertEqual(alloy_store, session_store)

        return configs, alloy_store, token

    def test_on_method_change(self):
        """Ensure we can change the method in the session store."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            method = 'Kirkaldy83'
            res = client.put(
                '/configs/method/update',
                data=json.dumps({'method': method}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            session_store = session.get(f'{token}:configurations')
            self.assertEqual(data['message'], f'Changed to {method} method.')
            self.assertEqual(data['status'], 'success')
            self.assert200(res)
            self.assertEqual(session_store['method'], 'Kirkaldy83')

            method = 'Li98'
            res = client.put(
                '/configs/method/update',
                data=json.dumps({'method': method}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            session_store = session.get(f'{token}:configurations')
            self.assertEqual(data['message'], f'Changed to {method} method.')
            self.assertEqual(data['status'], 'success')
            self.assert200(res)
            self.assertEqual(session_store['method'], method)

    def test_auto_update_ms(self):
        """Ensure we get the correct calculations for MS given the alloy."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            res = client.get(
                '/configs/ms',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_store['auto_calculate_ms'])
            ms_temp = np.float32(data['data']['ms_temp'])
            ms_rate_param = np.float32(data['data']['ms_rate_param'])
            self.assertAlmostEqual(sess_store['ms_temp'], 464.1960, 4)
            self.assertAlmostEqual(sess_store['ms_rate_param'], 0.020691, 4)
            self.assertAlmostEqual(ms_temp, 464.1960, 4)
            self.assertAlmostEqual(ms_rate_param, 0.020691, 4)

    def test_auto_update_bs(self):
        """Ensure we get the correct calculations for BS given the alloy."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            res = client.get(
                '/configs/bs',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_store['auto_calculate_bs'])
            ms_temp = np.float32(data['data']['bs_temp'])
            self.assertAlmostEqual(sess_store['bs_temp'], 563.2380, 4)
            self.assertAlmostEqual(ms_temp, 563.2380, 4)

    def test_auto_update_ae(self):
        """Ensure we get the correct calculations for Ae1 and Ae3 given the
        testing configs and the testing compositions.
        """
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            res = client.get(
                '/configs/ae',
                data=json.dumps({'auto_calculate_ae': True}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_store['auto_calculate_ae'])
            ae1 = np.float64(data['data']['ae1_temp'])
            ae3 = np.float64(data['data']['ae3_temp'])
            self.assertAlmostEqual(sess_store['ae1_temp'], 700.90196, 4)
            self.assertAlmostEqual(sess_store['ae3_temp'], 845.83721, 4)
            self.assertAlmostEqual(ae1, 700.90196, 4)
            self.assertAlmostEqual(ae3, 845.83721, 4)

    def test_configurations_no_auth_header(self):
        """Ensure it fails with no header."""
        with current_app.test_client() as client:
            method = 'Kirkaldy83'
            res = client.put(
                '/configs/method/update',
                data=json.dumps({'method': method}),
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert401(res)
            self.assertEqual(
                data['message'], 'No valid Authorization in header.'
            )
            self.assertEqual(data['status'], 'fail')

    def test_configurations_bad_auth_header(self):
        """Ensure it fails with a bad header."""
        with current_app.test_client() as client:
            token = 'EncodedHelloWorld!'
            method = 'Kirkaldy83'
            res = client.put(
                '/configs/method/update',
                data=json.dumps({'method': method}),
                headers={'Authorization': 'Bearer '},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert401(res)
            self.assertEqual(data['message'], 'Invalid JWT token in header.')
            self.assertEqual(data['status'], 'fail')

    def test_configurations_empty_payload(self):
        """Ensure you miss 100% of the shots you don't take."""
        with current_app.test_client() as client:
            token = 'EncodedHelloWorld!'
            res = client.put(
                '/configs/method/update',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

            res = client.patch(
                '/alloys/update',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

            res = client.patch(
                '/configs/update',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

    def test_on_method_change_no_method_payload(self):
        with current_app.test_client() as client:
            token = 'EncodedHelloWorld!'
            res = client.put(
                '/configs/method/update',
                data=json.dumps({'method': ''}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'No method was provided.')
            self.assertEqual(data['status'], 'fail')

    def test_on_method_change_incorrect_method_payload(self):
        with current_app.test_client() as client:
            token = 'EncodedHelloWorld!'
            res = client.put(
                '/configs/method/update',
                data=json.dumps({'method': 'AndrewMethod!'}),
                headers={'Authorization': f'Bearer {token}'},
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
        with current_app.test_client() as client:
            token = 'EncodedHelloWorld!'
            res = client.put(
                '/configs/method/update',
                data=json.dumps({'method': 'Kirkaldy83'}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert404(res)
            self.assertEqual(
                data['message'], 'No previous session configurations was set.'
            )
            self.assertEqual(data['status'], 'fail')

    def test_auto_update_ms_kirkaldy_method(self):
        """Ensure we get the correct calculations for MS and BS given Kirkaldy83
        method testing configs and the testing compositions.
        """
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            res_method_update = client.put(
                'configs/method/update',
                data=json.dumps({'method': 'Kirkaldy83'}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            self.assert200(res_method_update)

            res = client.get(
                '/configs/ms',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_store['auto_calculate_ms'])
            ms_temp = np.float32(data['data']['ms_temp'])
            ms_rate_param = np.float32(data['data']['ms_rate_param'])
            self.assertAlmostEqual(sess_store['ms_temp'], 477.5940, 4)
            self.assertAlmostEqual(sess_store['ms_rate_param'], 0.02069, 4)
            self.assertAlmostEqual(ms_temp, 477.5940, 4)
            self.assertAlmostEqual(ms_rate_param, 0.02069, 4)

    def test_auto_update_bs_kirkaldy_method(self):
        """Ensure we get the correct calculations for BS given Kirkaldy83
        method testing configs and the testing compositions.
        """
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            res_method_update = client.put(
                'configs/method/update',
                data=json.dumps({'method': 'Kirkaldy83'}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            self.assert200(res_method_update)

            res = client.get(
                '/configs/bs',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            sess_store = session[f'{token}:configurations']
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(sess_store['auto_calculate_bs'])
            bs_temp = np.float32(data['data']['bs_temp'])
            self.assertAlmostEqual(sess_store['bs_temp'], 565.738, 3)
            self.assertAlmostEqual(bs_temp, 565.738, 4)

    def test_on_configs_change(self):
        """Ensure that if we send new configurations we store it in session."""
        with current_app.test_client() as client:
            configs, _, token = self.login_client(client)
            # Since login stores the configs already, we need to make some
            # changes to see if it updates.

            # Since this is a patch method and we only want to change 1 thing
            res = client.patch(
                '/configs/update',
                data=json.dumps({'start_temp': 901}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            self.assertEqual(res.status_code, 202)
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            session_store = session.get(f'{token}:configurations')
            # This is just for ensuring they're the same overall
            setup_configs = {
                'grain_size': configs['grain_size'],
                'nucleation_start': configs['nucleation_start'],
                'nucleation_finish': configs['nucleation_finish'],
                'start_temp': 901,
                'cct_cooling_rate': configs['cct_cooling_rate']
            }
            sess_setup_configs = {
                'grain_size': session_store['grain_size'],
                'nucleation_start': session_store['nucleation_start'],
                'nucleation_finish': session_store['nucleation_finish'],
                'start_temp': session_store['start_temp'],
                'cct_cooling_rate': session_store['cct_cooling_rate']
            }
            self.assertEqual(setup_configs, sess_setup_configs)

    def test_on_configs_change_empty_json(self):
        """Ensure that if we send an empty JSON we get an error."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)
            res = client.patch(
                '/configs/update',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

    def test_on_configs_change_before_login(self):
        """Ensure if the user has not logged in, they have no previous store."""
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        configs = test_json['configurations']
        token = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123'
        configs.pop('nucleation_start')
        configs.pop('nucleation_finish')

        with current_app.test_client() as client:
            res = client.patch(
                '/configs/update',
                data=json.dumps(configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert404(res)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(
                data['message'], 'No previous session configurations was set.'
            )

    def test_on_configs_change_invalid_schema(self):
        """Ensure if we send no valid data we get an error response."""
        with current_app.test_client() as client:
            _, _, token = self.login_client(client)
            res = client.patch(
                '/configs/update',
                data=json.dumps({'nuc_start': 123}),
                headers={'Authorization': f'Bearer {token}'},
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
        with current_app.test_client() as client:
            res = client.put(
                '/configs/ms',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer abcde'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'Invalid payload.')

    def test_update_bs_empty_payload(self):
        """Ensure an empty payload for BS does not pass."""
        with current_app.test_client() as client:
            res = client.put(
                '/configs/bs',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer abcde'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'Invalid payload.')

    def test_update_ms_missing_ms_payload(self):
        """Ensure an missing ms_temp payload does not pass."""
        with current_app.test_client() as client:
            _, _, token = self.login_client(client)
            ms_configs = {'ms_rate_param': 0.9}

            res = client.put(
                '/configs/ms',
                data=json.dumps(ms_configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'MS temperature is required.')

    def test_update_ms_no_prev_configs(self):
        """Ensure if there is no prev. configs MS payload does not pass."""
        with current_app.test_client() as client:
            # We don't login to set the previous configs
            # _, _, token = self.login_client(client)
            ms_configs = {
                'ms_temp': 464.196,
                'ms_rate_param': 0.0168,
            }

            token = 'BoGuSToKeN'
            res = client.put(
                '/configs/ms',
                data=json.dumps(ms_configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert404(res)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(
                data['message'], 'No previous session configurations was set.'
            )

    def test_update_bs_no_prev_configs(self):
        """Ensure if there is no prev. configs BS payload does not pass."""
        with current_app.test_client() as client:
            # We don't login to set the previous configs
            # _, _, token = self.login_client(client)
            bs_configs = {'bs_temp': 563.238}

            token = 'BoGuSToKeN'
            res = client.put(
                '/configs/bs',
                data=json.dumps(bs_configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert404(res)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(
                data['message'], 'No previous session configurations was set.'
            )

    def test_update_ms(self):
        """Ensure a valid payload of MS will do just as we expect."""
        with current_app.test_client() as client:
            _, _, token = self.login_client(client)
            configs = {
                'ms_temp': 464.196,
                'ms_rate_param': 0.0168,
            }

            res = client.put(
                '/configs/ms',
                data=json.dumps(configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)
            sess = session.get(f'{token}:configurations')
            self.assertEquals(sess['ms_temp'], configs['ms_temp'])
            self.assertEquals(sess['ms_rate_param'], configs['ms_rate_param'])

    def test_update_bs(self):
        """Ensure a valid payload of BS will do just as we expect."""
        with current_app.test_client() as client:
            _, _, token = self.login_client(client)

            res = client.put(
                '/configs/bs',
                data=json.dumps({'bs_temp': 563.238}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)
            sess = session.get(f'{token}:configurations')
            self.assertEquals(sess['bs_temp'], 563.238)

    def test_update_ae_empty_payload(self):
        """Ensure an empty payload does not pass."""
        with current_app.test_client() as client:
            res = client.put(
                '/configs/ae',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer abcde'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'Invalid payload.')

    def test_update_ae_missing_ae1_payload(self):
        """Ensure an missing ms_temp payload does not pass."""
        with current_app.test_client() as client:
            _, _, token = self.login_client(client)
            bad_ae_configs = {
                'ae3_temp': 700.902,
            }

            res = client.put(
                '/configs/ae',
                data=json.dumps(bad_ae_configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'Ae1 temperature is required.')

    def test_update_ae_missing_ae3_payload(self):
        """Ensure an missing bs_temp payload does not pass."""
        with current_app.test_client() as client:
            _, _, token = self.login_client(client)
            bad_ae_configs = {
                'ae1_temp': 700.902,
            }

            res = client.put(
                '/configs/ae',
                data=json.dumps(bad_ae_configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'Ae3 temperature is required.')

    def test_update_ae_no_prev_configs(self):
        """Ensure an missing bs_temp payload does not pass."""
        with current_app.test_client() as client:
            # We don't login to set the previous configs
            # _, _, token = self.login_client(client)
            ae_configs = {'ae1_temp': 700.902, 'ae3_temp': 845.838}

            token = 'BoGuSToKeN'
            res = client.put(
                '/configs/ae',
                data=json.dumps(ae_configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert404(res)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(
                data['message'], 'No previous session configurations was set.'
            )

    def test_update_ae(self):
        """Ensure a valid payload of MS and BS will do just as we expect."""
        with current_app.test_client() as client:
            _, _, token = self.login_client(client)
            new_ae = {'ae1_temp': 700.902, 'ae3_temp': 845.838}

            res = client.put(
                '/configs/ae',
                data=json.dumps(new_ae),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 202)
            sess = session.get(f'{token}:configurations')
            self.assertEquals(sess['ae1_temp'], new_ae['ae1_temp'])
            self.assertEquals(sess['ae3_temp'], new_ae['ae3_temp'])


if __name__ == '__main__':
    unittest.main()
