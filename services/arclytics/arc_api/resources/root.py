# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# root.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------

__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.10.03'

"""root.py: 

{Description}
"""


import os

from flask import Blueprint, Response, request, make_response, jsonify
from arc_api.auth_service import AuthService

from arc_logging import AppLogger

logger = AppLogger(__name__)
root_blueprint = Blueprint('root', __name__)

API_TOKEN_NAME = 'JWT_TOKEN'


@root_blueprint.route('/', methods=['GET'])
def index():
    resp_string = f'Container: {os.uname()[1]}'
    response = Response(resp_string)
    response.headers['Connection'] = 'Close'
    response.headers['Keep-Alive'] = 'timeout=0'
    response.status_code = 200
    return response


@root_blueprint.route('/healthy', methods=['GET'])
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


@root_blueprint.route('/test_auth', methods=['GET'])
def test():
    cookies = request.cookies.get(API_TOKEN_NAME)
    user_id, role = AuthService().decode_auth_token(cookies)
    response = {'cookies': cookies, 'user': user_id, 'role': role}
    return jsonify(response), 200
