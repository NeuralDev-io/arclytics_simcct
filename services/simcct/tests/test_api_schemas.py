# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_schemas.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']

__status__ = 'development'
__date__ = '2019.07.18'

import unittest
from pathlib import Path

from flask import json
from marshmallow import ValidationError

from manage import BASE_DIR
from tests.test_api_base import BaseTestCase
from sim_api.schemas import (AlloySchema, ConfigurationsSchema)
from sim_api.extensions.utilities import ElementSymbolInvalid

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'tests' / 'sim_configs.json'


class TestSchemas(BaseTestCase):
    @staticmethod
    def import_test_configs():
        with open(_TEST_CONFIGS_PATH, 'r') as f:
            test_json = json.load(f)

        alloy = {
            'name': 'Arc_Stark',
            'compositions': test_json['compositions']
        }
        comp = {
            'alloy': alloy,
            'alloy_type': 'parent',
            'alloy_option': 'single'
        }

        return test_json['configurations'], comp

    def test_configurations_schema(self):
        """Ensure the configurations schema is as we expect."""
        configs, _ = self.import_test_configs()
        configs = ConfigurationsSchema().load(configs)
        self.assertTrue(configs['method'])
        self.assertIsInstance(configs['method'], str)

    def test_invalid_configurations_schema(self):
        """Ensure that if we pass it a bad dict it fails."""
        pass

    def test_string_floats_configurations_schema(self):
        """Ensure if we pass it a string for a float dict it still passes."""
        configs, _ = self.import_test_configs()
        configs['grain_size'] = "8.0"
        # Check grain_size is now a string
        self.assertIsInstance(configs['grain_size'], str)
        # Turn it to JSON first
        json_configs = json.dumps(configs)
        self.assertIsInstance(json_configs, str)
        # Parse it back from JSON then validate it
        valid_configs = ConfigurationsSchema().load(json.loads(json_configs))
        self.assertIsInstance(valid_configs, dict)
        # Check if grain_size is valid from string parsed to float.
        self.assertIsInstance(valid_configs['grain_size'], float)

    def test_bad_string_floats_configurations_schema(self):
        """Ensure if we pass it a string that cant be parsed it fails."""
        configs, _ = self.import_test_configs()
        configs['grain_size'] = "8.j"
        # Check grain_size is now a string
        self.assertIsInstance(configs['grain_size'], str)
        # Turn it to JSON first
        json_configs = json.dumps(configs)
        self.assertIsInstance(json_configs, str)
        # Parse it back from JSON then validate it and we should see it fail
        with self.assertRaises(ValidationError):
            try:
                ConfigurationsSchema().load(json.loads(json_configs))
            except ValidationError as e:
                self.assertEquals(
                    e.messages, {'grain_size': ['Not a valid number.']}
                )
                raise ValidationError(e.messages)

    def test_config_dump(self):
        configs, _ = self.import_test_configs()
        configs['grain_size'] = "8.0"
        self.assertIsInstance(json.dumps(configs), str)
        self.assertIsInstance(configs['grain_size'], str)
        valid_configs = ConfigurationsSchema().dump(configs)
        self.assertIsInstance(valid_configs, dict)

    def test_alloy_schema_compositions_invalid(self):
        """Ensure the schema validates the incorrect Periodic symbol."""
        alloy = {
            'name': 'Invalid Comp',
            'compositions': [{
                'symbol': 'Vb',
                'weight': 1
            }]
        }

        err = (
            'ValidationError (Element) (Field does not match a valid element'
            ' symbol in the Periodic Table: ["symbol"])'
        )
        with self.assertRaises(ElementSymbolInvalid, msg=err):
            AlloySchema().load(alloy)

    def test_alloy_schema_compositions_valid(self):
        """Ensure the schema validates the correct Periodic symbol."""
        alloy = {
            'name':
            'Alloy-1001',
            'compositions': [
                {
                    "symbol": "C",
                    "weight": 0.044
                }, {
                    "symbol": "Mn",
                    "weight": 1.73
                }, {
                    "symbol": "Si",
                    "weight": 0.22
                }, {
                    "symbol": "Ni",
                    "weight": 0.0
                }, {
                    "symbol": "Cr",
                    "weight": 0.0
                }, {
                    "symbol": "Mo",
                    "weight": 0.26
                }, {
                    "symbol": "Co",
                    "weight": 0.0
                }, {
                    "symbol": "Al",
                    "weight": 0.0
                }, {
                    "symbol": "Cu",
                    "weight": 0.0
                }, {
                    "symbol": "As",
                    "weight": 0.0
                }, {
                    "symbol": "Ti",
                    "weight": 0.0
                }, {
                    "symbol": "V",
                    "weight": 0.0
                }, {
                    "symbol": "W",
                    "weight": 0.0
                }, {
                    "symbol": "S",
                    "weight": 0.0
                }, {
                    "symbol": "N",
                    "weight": 0.0
                }, {
                    "symbol": "Nb",
                    "weight": 0.0
                }, {
                    "symbol": "B",
                    "weight": 0.0
                }, {
                    "symbol": "P",
                    "weight": 0.0
                }, {
                    "symbol": "Fe",
                    "weight": 0.0
                }
            ]
        }

        res = AlloySchema().load(alloy)
        self.assertEqual(res['compositions'][0]['symbol'], 'C')
        self.assertEqual(res['compositions'][0]['weight'], 0.044)


if __name__ == '__main__':
    unittest.main()

#
