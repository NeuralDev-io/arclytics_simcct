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
__date__ = '2019.09.16'

"""root.py: 

Just a basic module to define some testing endpoints. 
"""

import os
from flask import Blueprint, jsonify, Response

root_blueprint = Blueprint('root', __name__)


@root_blueprint.route('/', methods=['GET'])
def index():
    resp_string = f'Container: {os.uname()[1]}'
    response = Response(resp_string)
    response.headers['Connection'] = 'close'
    response.status_code = 200
    return response


@root_blueprint.route('/ping', methods=['GET'])
def ping():
    """Just a sanity check."""
    response = {
        'status': 'success',
        'message': 'pong',
        'container_id': os.uname()[1]
    }
    return jsonify(response), 200


@root_blueprint.route('/healthy', methods=['GET'])
def readiness_probe():
    """Readiness probe for GCP Ingress."""
    response = Response("")
    # Remove Connection: keep-alive as a work-around to readinessProbe issue
    # confirmed by Google Kubernetes Engine team.
    # [1] https://medium.com/google-cloud/ingress-load-balancing-issues-on-
    # googles-gke-f54c7e194dd5
    response.headers['Connection'] = 'close'
    response.status_code = 200
    return response
