# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# root.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '0.1.0'
__status__ = 'development'
__date__ = '2019.10.03'

"""root.py: 

This is the root resource with mostly Flask style API View methods including 
the one necessary to do Kubernetes Readiness Probes.
"""

import os

from flask import Blueprint, Response

from arc_api.routes import Routes
from arc_logging import AppLogger

logger = AppLogger(__name__)
root_blueprint = Blueprint('root', __name__)


@root_blueprint.route(Routes.index.value, methods=['GET'])
def index():
    resp_string = f'Container: {os.uname()[1]}'
    response = Response(resp_string)
    response.headers['Connection'] = 'Close'
    response.headers['Keep-Alive'] = 'timeout=0'
    response.status_code = 200
    return response


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


# This is used to only test the application in development.
# Do not leave this here otherwise.
# from flask import jsonify, request
# from arc_api.middleware import authorize_admin_cookie_flask
# @root_blueprint.route('/test_auth', methods=['GET'])
# @authorize_admin_cookie_flask
# def test(user_id):
#     response = {'user': user_id}
#     return jsonify(response), 200
