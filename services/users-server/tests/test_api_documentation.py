# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_documentation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------

import unittest
import users_api


class TestScriptDocumentation(unittest.TestCase):
    def test_models_script(self):
        self.assertIn(
            'Andrew Che <@codeninja55>', users_api.models.models.__author__
        )
        self.assertEqual('2019.07.03', users_api.models.models.__date__)

    def test_mongodb_script(self):
        self.assertIn(
            'Andrew Che <@codeninja55>', users_api.mongodb.__author__
        )
        self.assertIn('TBA', users_api.mongodb.__license__)
        self.assertIn('1.0.0', users_api.mongodb.__version__)
        self.assertIn('2019.07.04', users_api.mongodb.__date__)


if __name__ == '__main__':
    unittest.main()
