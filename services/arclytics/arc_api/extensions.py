# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# extensions.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>',
    'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '1.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.09.22'
"""extensions.py: 

This module just defines extensions for Flask that can be used across the
context of the app.
"""

from flask_restful import Api
from elasticapm.contrib.flask import ElasticAPM

apm = ElasticAPM()
api = Api()