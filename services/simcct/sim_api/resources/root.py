# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# root.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.09.16'
"""root.py: 

Just a basic module to define some testing endpoints. 
"""

import os

from flask import Blueprint, Response, jsonify

from sim_api.routes import Routes
from arc_logging import AppLogger

root_blueprint = Blueprint('root', __name__)
logger = AppLogger(__name__)


@root_blueprint.route(Routes.index.value, methods=['GET'])
def index():
    resp_string = f'Container: {os.uname()[1]}'
    response = Response(resp_string)
    response.headers['Connection'] = 'Close'
    response.headers['Keep-Alive'] = 'timeout=0'
    response.status_code = 200
    return response


@root_blueprint.route(Routes.ping.value, methods=['GET'])
def ping():
    """Just a sanity check."""
    response = {
        'status': 'success',
        'message': 'pong',
        'container_id': os.uname()[1]
    }
    return jsonify(response), 200


# @root_blueprint.route('Routes.log.value', methods=['GET'])
# def log():
#     """Just a log sanity check."""
#     response = {
#         'status': 'success',
#         'message': 'fluentd logging',
#         'container_id': os.uname()[1]
#     }
#     # Use the APM logger
#     # apm.capture_message('APM logging')
#     # Use the new Flask-Fluentd-Logger as a global variable.
#     logger.info(response)
#     return jsonify(response), 200


@root_blueprint.route(Routes.readiness_probe.value, methods=['GET'])
def readiness_probe():
    """Readiness probe for GCP Ingress."""
    response = Response('')
    # Remove Connection: keep-alive as a work-around to readinessProbe issue
    # confirmed by Google Kubernetes Engine team.
    # [1] https://medium.com/google-cloud/ingress-load-balancing-issues-on-
    # googles-gke-f54c7e194dd5
    response.headers['Connection'] = 'Close'
    response.headers['Keep-Alive'] = 'timeout=0'
    response.status_code = 200
    return response
