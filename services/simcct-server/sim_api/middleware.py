# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# middleware.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2019.07.14'
"""middleware.py: 

This module is just a simple middleware with decorator methods to ensure we can
get a JWT token in the headers of endpoints that require them.
"""

from functools import wraps

from flask import request, jsonify


def token_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        # Get the auth header
        auth_header = request.headers.get('Authorization', None)

        if not auth_header:
            response['message'] = 'No valid Authorization in header.'
            return jsonify(response), 401

        token = auth_header.split(' ')[1]

        if token == '':
            response['message'] = 'Invalid JWT token in header.'
            return jsonify(response), 401

        # TODO(andrew@neuraldev.io -- Sprint 6): Find a way to validate this is
        #  is a valid token for a user.

        return f(token, *args, **kwargs)

    return decorated_func


def token_required_restful(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        # Get the auth header
        auth_header = request.headers.get('Authorization', None)

        if not auth_header:
            response['message'] = 'No valid Authorization in header.'
            return response, 401

        token = auth_header.split(' ')[1]

        if token == '':
            response['message'] = 'Invalid JWT token in header.'
            return response, 401

        # TODO(andrew@neuraldev.io -- Sprint 6): Find a way to validate this is
        #  is a valid token for a user.

        return f(token, *args, **kwargs)

    return decorated_func
