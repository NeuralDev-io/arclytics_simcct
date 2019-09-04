# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_documentation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------

import unittest
import arc_app


class TestScriptDocumentation(unittest.TestCase):
    def test_models_script(self):
        self.assertIn('Andrew Che <@codeninja55>', arc_app.models.__author__)
        self.assertEqual('2019.07.03', arc_app.models.__date__)

    def test_mongodb_script(self):
        self.assertIn('Andrew Che <@codeninja55>', arc_app.mongodb.__author__)
        self.assertIn('TBA', arc_app.mongodb.__license__)
        self.assertIn('1.0.0', arc_app.mongodb.__version__)
        self.assertIn('2019.07.04', arc_app.mongodb.__date__)


if __name__ == '__main__':
    unittest.main()
