# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_documentation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------

import unittest
import users_app


class TestScriptDocumentation(unittest.TestCase):
    def test_models_script(self):
        self.assertIn('Andrew Che <@codeninja55>', users_app.models.__author__)
        self.assertEqual('2019.07.03', users_app.models.__date__)

    def test_mongodb_script(self):
        self.assertIn(
            'Andrew Che <@codeninja55>', users_app.mongodb.__author__
        )
        self.assertIn('TBA', users_app.mongodb.__license__)
        self.assertIn('1.0.0', users_app.mongodb.__version__)
        self.assertIn('2019.07.04', users_app.mongodb.__date__)


if __name__ == '__main__':
    unittest.main()
