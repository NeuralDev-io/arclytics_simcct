# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_jwt_auth.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'David Matthews <@tree1004>']
__status__ = 'development'
__date__ = '2019.07.05'

import unittest

from flask import json
import requests

from tests.test_base import BaseTestCase, app


class TestRootResources(BaseTestCase):
    """This module tests the cross server authentication and middleware."""

    def test_healthy(self):
        with app.test_client() as client:
            res = client.get('/healthy')
            self.assert200(res)

    def test_user_registration(self):
        with app.test_client() as client:
            pass


if __name__ == '__main__':
    unittest.main()
