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

from celery.states import PENDING

from tests.test_api_base import BaseTestCase


class TestCeleryRequest(BaseTestCase):
    def test_celery_tasks(self):
        """Ensure we can send a task to Celery worker and get the result."""
        from celery_runner import celery
        task = celery.send_task(
            'tasks.log', args=['Hello from the other side!'], kwargs={}
        )
        self.assertTrue(task.id)
        task_state = celery.AsyncResult(task.id).state
        while task_state == PENDING:
            task_state = celery.AsyncResult(task.id).state
        res = celery.AsyncResult(task.id)
        self.assertEqual(res.result, 'Hello from the other side!')


if __name__ == '__main__':
    unittest.main()
