# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# middleware.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.10.03'

"""middleware.py: 

This is the request middleware that ensures every single request is checked 
for cookies and authentication or authorisation based on the endpoint View 
methods used.
"""


from functools import wraps

from flask import jsonify, request

from arc_api.auth_service import AuthService
from arc_api.extensions import API_TOKEN_NAME
from arc_api.extensions import apm


# ========================== # FLASK VERSIONS # ============================= #
def authorize_admin_cookie_flask(f):
    """A wrapper decorator as a middleware to authenticate if the user has a
    cookie in their request. Before any request to this server, we verify that
    they have a JWT Authentication token.

    Args:
        f: the endpoint View method to run that is being wrapped.

    Returns:
        A HTTP JSON Response and status code indicating the status if the user
        is neither Authenticated nor Authorised or a valid User ObjectId.
    """

    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {'status': 'fail', 'message': 'Not authenticated.'}
        auth_token = request.cookies.get(API_TOKEN_NAME)

        if not auth_token:
            return jsonify(response), 401

        # if we have a JWT token, we decode it and verify their role.
        user_obj_id, role = AuthService().decode_auth_token(auth_token)

        # If their role is None, which is what is returned in the Tuple element
        # position 1 from the AuthService, then we know the Token is invalid.
        if role is None or not role == 'admin':
            response.update({'message': 'Not authorised.'})
            apm.capture_message('Not authorised attempt on Arclytics.')
            return jsonify(response), 403

        return f(user_obj_id, *args, **kwargs)

    return decorated_func


# ======================== # RESTFUL VERSIONS # ============================= #
def authorize_admin_cookie_restful(f):
    """A wrapper decorator as a middleware to authenticate if the user has a
    cookie in their request. Before any request to this server, we verify that
    they have a JWT Authentication token.

    Args:
        f: the endpoint View method to run that is being wrapped.

    Returns:
        A HTTP JSON Response and status code indicating the status if the user
        is neither Authenticated nor Authorised or a valid User ObjectId.
    """

    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = {'status': 'fail', 'message': 'Not authenticated.'}
        auth_token = request.cookies.get(API_TOKEN_NAME)

        if not auth_token:
            return response, 401

        # if we have a JWT token, we decode it and verify their role.
        user_obj_id, role = AuthService().decode_auth_token(auth_token)

        # If their role is None, which is what is returned in the Tuple element
        # position 1 from the AuthService, then we know the Token is invalid.
        if role is None or not role == 'admin':
            response.update({'message': 'Not authorised.'})
            apm.capture_message('Not authorised attempt on Arclytics.')
            return response, 403

        return f(user_obj_id, *args, **kwargs)

    return decorated_func
