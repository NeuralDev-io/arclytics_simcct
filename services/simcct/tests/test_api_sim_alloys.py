# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_sim_alloys.py
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
from pathlib import Path

from bson import ObjectId
from flask import current_app

import settings
from tests.test_api_base import BaseTestCase
from sim_api.schemas import (
    AlloyStoreRequestSchema, ConfigurationsSchema, AlloyStoreSchema
)
from sim_api.extensions.sim_session import SimSessionService

_TEST_CONFIGS_PATH = Path(
    settings.BASE_DIR
) / 'simulation' / 'sim_configs.json'


class TestSimAlloys(BaseTestCase):
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

        token = 'eykjhja098akjhkkhkwhekhlkalsjlasd'
        _id = ObjectId()

        sess_res = client.post(
            '/session/login',
            data=json.dumps(
                {
                    '_id': str(_id),
                    'is_admin': False,
                    'last_configurations': configs,
                    'last_alloy_store': alloy_store
                }
            ),
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        data = json.loads(sess_res.data.decode())
        session_key = data['session_key']
        _, session_store = SimSessionService().load_session(session_key)
        session_alloy = session_store.get('alloy_store')
        self.assertEqual(data['status'], 'success')
        self.assertTrue(sess_res.status_code == 201)
        self.assertEqual(alloy_store, session_alloy)

        return configs, alloy_store, token, session_key

    def test_post_alloy_missing_elements(self):
        with current_app.test_client() as client:
            configs, comp, token, session_key = self.login_client(client)

            res = client.post(
                '/alloys/update',
                data=json.dumps(
                    {
                        'alloy_option': 'single',
                        'alloy_type': 'parent',
                        'alloy': {
                            'name': 'Bad Alloy',
                            'compositions': [{
                                'symbol': 'C',
                                'weight': 1
                            }]
                        }
                    }
                ),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            msg = (
                "Missing elements ['Mn', 'Ni', 'Cr', 'Mo', 'Si', 'Co', 'W', "
                "'As', 'Fe']"
            )
            self.assertEqual(data['message'], msg)
            self.assertEqual(data['status'], 'fail')
            self.assert400(res)

    def test_post_alloy_all_elements(self):
        with current_app.test_client() as client:
            configs, comp, token, session_key = self.login_client(client)

            good_comp = [
                {
                    'symbol': 'C',
                    'weight': 0.044
                },
                {
                    'symbol': 'Mn',
                    'weight': 0.0
                },
                {
                    'symbol': 'Ni',
                    'weight': 0.0
                },
                {
                    'symbol': 'Cr',
                    'weight': 0.0
                },
                {
                    'symbol': 'Mo',
                    'weight': 0.0
                },
                {
                    'symbol': 'Si',
                    'weight': 0.0
                },
                {
                    'symbol': 'Co',
                    'weight': 0.0
                },
                {
                    'symbol': 'W',
                    'weight': 0.0
                },
                {
                    'symbol': 'As',
                    'weight': 0.0
                },
                {
                    'symbol': 'Fe',
                    'weight': 0.0
                },
            ]

            res = client.post(
                '/alloys/update',
                data=json.dumps(
                    {
                        'alloy_option': 'single',
                        'alloy_type': 'parent',
                        'alloy': {
                            'name': 'Bad Alloy',
                            'compositions': good_comp
                        }
                    }
                ),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())
            self.assertEqual(
                data['message'],
                'Compositions and Configurations in Session initiated.'
            )
            trans_temps = data['data']
            self.assertEqual(data['status'], 'success')
            self.assertEqual(res.status_code, 201)
            self.assertAlmostEqual(trans_temps['ms_temp'], 520.388, 3)
            self.assertAlmostEqual(trans_temps['ms_rate_param'], 0.0219292, 3)
            self.assertAlmostEqual(trans_temps['bs_temp'], 634.448, 3)
            self.assertAlmostEqual(trans_temps['ae1_temp'], 719.259259259, 4)
            self.assertAlmostEqual(trans_temps['ae3_temp'], 887.130506988, 4)

    def test_on_compositions_change(self):
        """Ensure if we update the compositions it changes in session store."""
        with current_app.test_client() as client:
            configs, alloy_store, token, session_key = self.login_client(
                client
            )

            # By default the auto calculate bools are all true so we need to
            # set them to false to get this working.
            client.put(
                '/configs/ms',
                data=json.dumps(
                    {
                        'ms_temp': 464.196,
                        'ms_rate_param': 0.0168,
                    }
                ),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
                content_type='application/json'
            )
            client.put(
                '/configs/bs',
                data=json.dumps({'bs_temp': 563.238}),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
                content_type='application/json'
            )
            client.put(
                '/configs/ae',
                data=json.dumps({
                    'ae1_temp': 700.902,
                    'ae3_temp': 845.838
                }),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
                content_type='application/json'
            )
            _, session_store = SimSessionService().load_session(session_key)
            self.assertFalse(
                session_store['configurations']['auto_calculate_ms']
            )
            self.assertFalse(
                session_store['configurations']['auto_calculate_bs']
            )
            self.assertFalse(
                session_store['configurations']['auto_calculate_ae']
            )

            new_alloy_store = {
                'alloy_option': 'single',
                'alloy_type': 'parent',
                'alloy': alloy_store['alloys']['parent']
            }
            new_parent_comp = dict(new_alloy_store.get('alloy'))
            new_parent_comp['compositions'][0] = {
                'symbol': 'C',
                'weight': 0.050
            }
            req_alloy = AlloyStoreRequestSchema().load(new_alloy_store)

            res = client.patch(
                '/alloys/update',
                data=json.dumps(req_alloy),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(data['message'], 'Compositions updated.')
            self.assert200(res)
            self.assertEqual(data['status'], 'success')
            _, session_store = SimSessionService().load_session(session_key)
            session_comp = session_store.get('alloy_store')
            self.assertDictEqual(
                session_comp['alloys']['parent'], new_alloy_store['alloy']
            )

    def test_on_comp_change_invalid_comp_schema(self):
        """Ensure if we send a bad alloy schema we get errors."""
        with current_app.test_client() as client:
            configs, comp, token, s_key = self.login_client(client)

            new_comp = {
                'alloy_option': 'single',
                'alloy': {
                    'name': 'Bad_Alloy',
                    'compositions': 'It has stuff inside'
                },
                'alloy_type': 'parent'
            }

            res = client.patch(
                '/alloys/update',
                data=json.dumps(new_comp),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': s_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(
                data['message'],
                'Valid compositions must be provided as a list.'
            )
            self.assert400(res)
            self.assertEqual(data['status'], 'fail')
            _, session_store = SimSessionService().load_session(s_key)
            session_comp = session_store.get('alloy_store')
            self.assertNotEqual(session_comp, new_comp)

    def test_on_comp_change_invalid_empty_schema(self):
        """Ensure if we send a bad alloy schema we get errors."""
        with current_app.test_client() as client:
            configs, comp, token, session_key = self.login_client(client)

            new_comp = {
                'alloy_option': 'single',
                'alloy': {
                    'name': '',
                    'compositions': []
                },
                'alloy_type': 'parent'
            }

            res = client.patch(
                '/alloys/update',
                data=json.dumps(new_comp),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(
                data['message'], 'No valid key in the alloy was provided.'
            )
            self.assert400(res)
            self.assertEqual(data['status'], 'fail')
            _, session_store = SimSessionService().load_session(session_key)
            session_comp = session_store.get('alloy_store')
            self.assertNotEqual(session_comp, new_comp)

    def test_on_comp_change_auto_update_temps(self):
        """Ensure if we update compositions schema we also auto update."""
        with current_app.test_client() as client:
            configs, alloy_store, token, session_key = self.login_client(
                client
            )

            # We need to make auto_calculate true by using the endpoints
            client.get(
                '/configs/ms',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
                content_type='application/json'
            )
            client.get(
                '/configs/ae',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
                content_type='application/json'
            )
            client.get(
                '/configs/bs',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
                content_type='application/json'
            )

            _, session_store = SimSessionService().load_session(session_key)
            sess_configs = session_store.get('configurations')
            self.assertAlmostEqual(sess_configs['ms_temp'], 464.1960, 4)
            self.assertAlmostEqual(sess_configs['ms_rate_param'], 0.02069, 4)
            self.assertAlmostEqual(sess_configs['bs_temp'], 563.2380, 4)
            self.assertAlmostEqual(sess_configs['ae1_temp'], 700.90196, 4)
            self.assertAlmostEqual(sess_configs['ae3_temp'], 845.83715, 4)

            # Now we change the compositions and make sure it's all updated
            # with the composition change
            new_alloy_store = {
                'alloy_option': 'single',
                'alloy_type': 'parent',
                'alloy': alloy_store['alloys']['parent']
            }

            new_parent_comp = new_alloy_store.get('alloy')
            new_parent_comp['compositions'][0]['weight'] = 0.050  # carbon
            new_parent_comp['compositions'][1]['weight'] = 1.6  # manganese
            req_alloy = AlloyStoreRequestSchema().load(new_alloy_store)

            res = client.patch(
                '/alloys/update',
                data=json.dumps(req_alloy),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
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
            _, session_store = SimSessionService().load_session(session_key)
            sess_configs = session_store.get('configurations')
            self.assertAlmostEqual(sess_configs['ms_temp'], ms_temp, 4)
            self.assertAlmostEqual(
                sess_configs['ms_rate_param'], ms_rate_param, 4
            )
            self.assertAlmostEqual(sess_configs['bs_temp'], bs_temp, 2)
            self.assertAlmostEqual(sess_configs['ae1_temp'], ae1_temp, 4)
            self.assertAlmostEqual(sess_configs['ae3_temp'], ae3_temp, 4)

    def test_on_comp_change_bad_comp_payload(self):
        """Ensure if we send no compositions to update it fails."""
        with current_app.test_client() as client:
            configs, comp, token, session_key = self.login_client(client)

            _, session_store = SimSessionService().load_session(session_key)
            prev_sess_comp = session_store.get('alloy_store')
            res = client.patch(
                '/alloys/update',
                data=json.dumps(
                    {
                        'alloy_option': 'single',
                        'alloy_type': 'parent',
                        'alloy': {
                            'compositions': {}
                        }
                    }
                ),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Session': session_key
                },
                content_type='application/json'
            )
            data = json.loads(res.data.decode())

            self.assertEqual(
                data['message'], 'No valid key in the alloy was provided.'
            )
            self.assert400(res)
            self.assertEqual(data['status'], 'fail')
            _, session_store = SimSessionService().load_session(session_key)
            after_sess_comp = session_store.get('alloy_store')
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


if __name__ == '__main__':
    unittest.main()
