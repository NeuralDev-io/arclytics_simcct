# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# gunicorn_conf.py
# 
# Attributions: 
# [1]
# https://medium.com/google-cloud/a-guide-to-deploy-flask-app-on-google-
# kubernetes-engine-bfbbee5c6fb
# ----------------------------------------------------------------------------------------------------------------------

__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'MIT'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.09.10'

"""gunicorn_conf.py: 

Configuration file for Gunicorn to be used in Production Environment.
"""

import multiprocessing
from os import environ as env

PORT = 8000
DEBUG_MODE = 1 if env.get('FLASK_ENV') == 'development' else 0

# Gunicorn Configs
bind = f'0.0.0.0:{PORT}'
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2 * multiprocessing.cpu_count()
