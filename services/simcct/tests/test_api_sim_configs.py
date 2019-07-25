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

from sim_app.app import BASE_DIR
from tests.test_api_base import BaseTestCase
from sim_app.schemas import AlloySchema, ConfigurationsSchema

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'


class TestSimConfigurations(BaseTestCase):

    # NOTE:
    #  - We can treat the session stores of the compositions and configurations
    #    as always being the one that's displayed on the Client UI.

    def login_client(self, client):
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        configs = ConfigurationsSchema().load(test_json['configurations'])
        alloy = AlloySchema().load(
            {
                'name': 'Arc_Stark',
                'compositions': test_json['compositions']
            }
        )
        comp = {'alloy': alloy, 'alloy_type': 'parent'}

        token = 'ABCDEFGHIJKLMOPQRSTUVWXYZ123'
        _id = ObjectId()

        sess_res = client.post(
            '/session/login',
            data=json.dumps(
                {
                    '_id': str(_id),
                    'last_configurations': configs,
                    'last_compositions': comp
                }
            ),
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        data = json.loads(sess_res.data.decode())
        session_store = session.get(f'{token}:alloy')
        self.assertEqual(data['status'], 'success')
        self.assertTrue(sess_res.status_code == 201)
        self.assertEqual(comp['alloy'], session_store)

        return configs, comp, token

    def test_on_compositions_change(self):
        """Ensure if we update the compositions it changes in session store."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            # By default the auto calculate bools are all true so we need to
            # set them to false to get this working.

            client.put(
                '/configs/update/ms-bs',
                data=json.dumps(
                    {
                        'ms_temp': 464.196,
                        'ms_rate_param': 0.0168,
                        'bs_temp': 563.238
                    }
                ),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            client.put(
                '/configs/update/ae',
                data=json.dumps({
                    'ae1_temp': 700.902,
                    'ae3_temp': 845.838
                }),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            self.assertFalse(
                session[f'{token}:configurations']['auto_calculate_ms']
            )
            self.assertFalse(
                session[f'{token}:configurations']['auto_calculate_bs']
            )
            self.assertFalse(
                session[f'{token}:configurations']['auto_calculate_ae']
            )

            new_comp = comp
            new_comp['alloy']['compositions'][0]['weight'] = 0.050

            res = client.put(
                '/configs/comp/update',
                data=json.dumps(new_comp),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(data['message'], 'Compositions updated.')
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            session_comp = session.get(f'{token}:alloy')
            self.assertEqual(session_comp, new_comp['alloy'])

    def test_on_comp_change_invalid_comp_schema(self):
        """Ensure if we send a bad alloy schema we get errors."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            new_comp = {
                'alloy': {
                    'name': 'Bad_Alloy',
                    'compositions': 'It has stuff inside'
                },
                'alloy_type': 'parent'
            }

            res = client.put(
                '/configs/comp/update',
                data=json.dumps(new_comp),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(
                data['message'], 'Alloy failed schema validation.'
            )
            self.assert400(res)
            self.assertEqual(data['status'], 'fail')
            self.assertTrue(data['errors'])
            session_comp = session.get(f'{token}:alloy')
            self.assertNotEqual(session_comp, new_comp)

    def test_on_comp_change_auto_update_temps(self):
        """Ensure if we update compositions schema we also auto update."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            # We need to make auto_calculate true by using the endpoints
            client.get(
                '/configs/auto/ms',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            client.get(
                '/configs/auto/ae',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            client.get(
                '/configs/auto/bs',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )

            sess_store = session.get(f'{token}:configurations')
            self.assertAlmostEqual(sess_store['ms_temp'], 464.1960, 4)
            self.assertAlmostEqual(sess_store['ms_rate_param'], 0.02069, 4)
            self.assertAlmostEqual(sess_store['bs_temp'], 563.2380, 4)
            self.assertAlmostEqual(sess_store['ae1_temp'], 700.90196, 4)
            self.assertAlmostEqual(sess_store['ae3_temp'], 845.83721, 4)

            # Now we change the compositions and make sure it's all updated
            # with the composition change
            new_comp = comp
            new_comp['alloy']['compositions'][0]['weight'] = 0.050
            new_comp['alloy']['compositions'][1]['weight'] = 1.6

            res = client.put(
                '/configs/comp/update',
                data=json.dumps(new_comp),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(
                data['message'], 'Compositions and other values updated.'
            )
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'])

            # ANSTO SimCCT results
            ms_temp = 465.6100
            ms_rate_param = 0.02069
            bs_temp = 567.44
            ae1_temp = 702.7388
            ae3_temp = 847.103836

            self.assertAlmostEqual(data['data']['ms_temp'], ms_temp, 4)
            self.assertAlmostEqual(
                data['data']['ms_rate_param'], ms_rate_param, 4
            )
            self.assertAlmostEqual(data['data']['bs_temp'], bs_temp, 2)
            self.assertAlmostEqual(data['data']['ae1_temp'], ae1_temp, 4)
            self.assertAlmostEqual(data['data']['ae3_temp'], ae3_temp, 4)
            sess_store = session.get(f'{token}:configurations')
            self.assertAlmostEqual(sess_store['ms_temp'], ms_temp, 4)
            self.assertAlmostEqual(
                sess_store['ms_rate_param'], ms_rate_param, 4
            )
            self.assertAlmostEqual(sess_store['bs_temp'], bs_temp, 2)
            self.assertAlmostEqual(sess_store['ae1_temp'], ae1_temp, 4)
            self.assertAlmostEqual(sess_store['ae3_temp'], ae3_temp, 4)

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
                '/configs/auto/ms',
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
                '/configs/auto/bs',
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
                '/configs/auto/ae',
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

            res = client.put(
                '/configs/comp/update',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['message'], 'Invalid payload.')
            self.assertEqual(data['status'], 'fail')

            res = client.put(
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

    def test_on_comp_change_bad_comp_payload(self):
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)

            prev_sess_comp = session.get(f'{token}:alloy')
            res = client.put(
                '/configs/comp/update',
                data=json.dumps({'compositions': []}),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(
                data['message'], 'No composition list was provided.'
            )
            self.assert400(res)
            self.assertEqual(data['status'], 'fail')
            after_sess_comp = session.get(f'{token}:alloy')
            self.assertEqual(prev_sess_comp, after_sess_comp)

    # def test_on_comp_change_only_auto_ms_bs(self):
    #     with current_app.test_client() as client:
    #         configs, comp, token = self.login_client(client)
    #
    #         # We need to make auto_calculate true by using the endpoints
    #         client.put(
    #             '/configs/auto/ae',
    #             data=json.dumps({'auto_calculate_ae': True}),
    #             headers={'Authorization': f'Bearer {token}'},
    #             content_type='application/json'
    #         )
    #
    #         sess_store = session.get(f'{token}:configurations')
    #         self.assertTrue(sess_store['auto_calculate_ae'])
    #         self.assertFalse(sess_store['auto_calculate_ms_bs'])
    #
    #         # Now we change the compositions and make sure it's all updated
    #         # with the composition change
    #         new_comp = comp
    #         new_comp['alloy']['compositions'][0]['weight'] = 0.05
    #         new_comp['alloy']['compositions'][1]['weight'] = 1.6
    #
    #         res = client.put(
    #             '/configs/comp/update',
    #             data=json.dumps(new_comp),
    #             headers={'Authorization': f'Bearer {token}'},
    #             content_type='application/json'
    #         )
    #         data = json.loads(res.data.decode())
    #         sess_store = session.get(f'{token}:configurations')
    #
    #         self.assertEqual(
    #             data['message'], 'Compositions and other values updated.'
    #         )
    #         self.assert200(res)
    #         self.assertEqual(data['status'], 'success')
    #         self.assertTrue(data['data'])
    #         self.assertAlmostEqual(sess_store['ae1_temp'], 702.7388, 4)
    #         self.assertAlmostEqual(sess_store['ae3_temp'], 847.10445, 4)
    #         with self.assertRaises(KeyError):
    #             self.assertFalse(data['data']['ms_temp'])
    #             self.assertFalse(data['data']['bs_temp'])

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
                '/configs/auto/ms',
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
                '/configs/auto/bs',
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
            configs, comp, token = self.login_client(client)
            # Since login stores the configs already, we need to make some
            # changes to see if it updates.
            non_limit_configs = {
                'grain_size': configs['grain_size'],
                'nucleation_start': configs['nucleation_start'],
                'nucleation_finish': configs['nucleation_finish'],
                'start_temp': 901,
                'cct_cooling_rate': configs['cct_cooling_rate']
            }

            res = client.put(
                '/configs/update',
                data=json.dumps(non_limit_configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            self.assertEqual(res.status_code, 202)
            data = json.loads(res.data.decode())
            self.assertEqual(data['status'], 'success')
            session_store = session.get(f'{token}:configurations')
            sess_non_limit_configs = {
                'grain_size': session_store['grain_size'],
                'nucleation_start': session_store['nucleation_start'],
                'nucleation_finish': session_store['nucleation_finish'],
                'start_temp': session_store['start_temp'],
                'cct_cooling_rate': session_store['cct_cooling_rate']
            }
            self.assertEqual(non_limit_configs, sess_non_limit_configs)

    def test_on_configs_change_empty_json(self):
        """Ensure that if we send an empty JSON we get an error."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)
            res = client.put(
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
            res = client.put(
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

    def test_on_configs_invalid_schema_configs(self):
        """Ensure if we send invalid data we get an error response."""
        with current_app.test_client() as client:
            configs, comp, token = self.login_client(client)
            configs.pop('nucleation_finish')
            configs.pop('nucleation_start')
            res = client.put(
                '/configs/update',
                data=json.dumps(configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert400(res)
            self.assertEqual(data['status'], 'fail')
            self.assertEqual(data['message'], 'Invalid payload.')
            errors = {
                'nucleation_finish': ['Missing data for required field.'],
                'nucleation_start': ['Missing data for required field.']
            }
            self.assertTrue(data['errors'])
            self.assertEqual(data['errors'], errors)

    def test_update_ms_bs_empty_payload(self):
        """Ensure an empty payload does not pass."""
        with current_app.test_client() as client:
            res = client.put(
                '/configs/update/ms-bs',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer abcde'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'Invalid payload.')

    def test_update_ms_bs_missing_ms_payload(self):
        """Ensure an missing ms_temp payload does not pass."""
        with current_app.test_client() as client:
            _, _, token = self.login_client(client)
            non_limit_configs = {'bs_temp': 563.238}

            res = client.put(
                '/configs/update/ms-bs',
                data=json.dumps(non_limit_configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'MS temperature is required.')

    def test_update_ms_bs_missing_bs_payload(self):
        """Ensure an missing bs_temp payload does not pass."""
        with current_app.test_client() as client:
            _, _, token = self.login_client(client)
            non_limit_configs = {'ms_temp': 563.238, 'ms_rate_param': 0.0168}

            res = client.put(
                '/configs/update/ms-bs',
                data=json.dumps(non_limit_configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(res.status_code, 400)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(data['message'], 'BS temperature is required.')

    def test_update_ms_bs_no_prev_configs(self):
        """Ensure if there is no prev. configs payload does not pass."""
        with current_app.test_client() as client:
            # We don't login to set the previous configs
            # _, _, token = self.login_client(client)
            non_limit_configs = {
                'ms_temp': 464.196,
                'ms_rate_param': 0.0168,
                'bs_temp': 563.238
            }

            token = 'BoGuSToKeN'
            res = client.put(
                '/configs/update/ms-bs',
                data=json.dumps(non_limit_configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assert404(res)
            self.assertEquals(data['status'], 'fail')
            self.assertEquals(
                data['message'], 'No previous session configurations was set.'
            )

    def test_update_ms_bs(self):
        """Ensure a valid payload of MS and BS will do just as we expect."""
        with current_app.test_client() as client:
            _, _, token = self.login_client(client)
            configs = {
                'ms_temp': 464.196,
                'ms_rate_param': 0.0168,
                'bs_temp': 563.238
            }

            res = client.put(
                '/configs/update/ms-bs',
                data=json.dumps(configs),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            self.assertEqual(res.status_code, 204)
            self.assertFalse(res.data)
            sess = session.get(f'{token}:configurations')
            self.assertEquals(sess['ms_temp'], configs['ms_temp'])
            self.assertEquals(sess['ms_rate_param'], configs['ms_rate_param'])
            self.assertEquals(sess['bs_temp'], configs['bs_temp'])

    def test_update_ae_empty_payload(self):
        """Ensure an empty payload does not pass."""
        with current_app.test_client() as client:
            res = client.put(
                '/configs/update/ae',
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
            non_limit_configs = {
                'ae3_temp': 700.902,
            }

            res = client.put(
                '/configs/update/ae',
                data=json.dumps(non_limit_configs),
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
            non_limit_configs = {
                'ae1_temp': 700.902,
            }

            res = client.put(
                '/configs/update/ae',
                data=json.dumps(non_limit_configs),
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
            non_limit_configs = {'ae1_temp': 700.902, 'ae3_temp': 845.838}

            token = 'BoGuSToKeN'
            res = client.put(
                '/configs/update/ae',
                data=json.dumps(non_limit_configs),
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
                '/configs/update/ae',
                data=json.dumps(new_ae),
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            self.assertEqual(res.status_code, 204)
            self.assertFalse(res.data)
            sess = session.get(f'{token}:configurations')
            self.assertEquals(sess['ae1_temp'], new_ae['ae1_temp'])
            self.assertEquals(sess['ae3_temp'], new_ae['ae3_temp'])


if __name__ == '__main__':
    unittest.main()
