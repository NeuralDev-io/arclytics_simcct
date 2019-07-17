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
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.18'

import unittest
from pathlib import Path

from bson import ObjectId
from flask import json
from marshmallow import ValidationError

from sim_app.app import BASE_DIR
from tests.test_api_base import BaseTestCase
from sim_app.schemas import (
    AlloySchema,
    ConfigurationsSchema,
    NonLimitConfigsSchema
)

_TEST_CONFIGS_PATH = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'


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
            'alloy_type': 'parent'
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
                    e.messages,
                    {'grain_size': ['Not a valid number.']}
                )
                raise ValidationError(e.messages)

    def test_config_dump(self):
        configs, _ = self.import_test_configs()
        configs['grain_size'] = "8.0"
        self.assertIsInstance(json.dumps(configs), str)
        self.assertIsInstance(configs['grain_size'], str)
        valid_configs = ConfigurationsSchema().dump(configs)
        self.assertIsInstance(valid_configs, dict)


if __name__ == '__main__':
    unittest.main()

# 
