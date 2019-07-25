# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# tasks.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.25'
"""tasks.py: 

{Description}
"""

from celery_runner import celery


@celery.task()
def add_together(a, b):
    return a + b
