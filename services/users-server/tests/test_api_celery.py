# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# test_api_celery.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.25'
"""test_api_celery.py: 

{Description}
"""

import unittest

from flask import json
from flask import current_app as app

from tests.test_api_base import BaseTestCase


class MyTestCase(BaseTestCase):
    def test_celery_request(self):
        """Ensure we get the expected results from our test."""
        with app.test_client() as client:
            res = client.get(
                '/test/celery',
                content_type='application/json'
            )
            self.assert200(res)
            data = json.loads(res.data.decode())
            self.assertEqual(data['data'], 30)


if __name__ == '__main__':
    unittest.main()

# 
