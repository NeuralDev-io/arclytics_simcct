# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# auth.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.05'
"""auth.py: 

This script describes the Users authentication endpoints for registration,
login, and logout.
"""

import os
import requests
from datetime import datetime
from typing import Tuple, Optional
from threading import Thread

from flask import Blueprint, jsonify, request
from mongoengine.errors import ValidationError, NotUniqueError

from users_api.models.models import User
from users_api import bcrypt
from logger.arc_logger import AppLogger
from users_api.middleware import authenticate
from users_api.models.models import SimpleUTC

logger = AppLogger(__name__)

auth_blueprint = Blueprint('auth', __name__)


class SessionValidationError(Exception):
    """
    A custom exception to be raised by a threaded async call to register if
    the response is not what we are expecting.
    """
    def __init__(self, msg: str):
        super(SessionValidationError, self).__init__(msg)


@auth_blueprint.route(rule='/auth/register', methods=['POST'])
def register_user() -> Tuple[dict, int]:
    """Blueprint route for registration of users."""

    # Get the post data
    post_data = request.get_json()

    # Validating empty payload
    response = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response), 400

    # Extract the request body data
    email = post_data.get('email', '')
    password = post_data.get('password', '')
    first_name = post_data.get('first_name', '')
    last_name = post_data.get('last_name', '')

    if not email:
        response['message'] = 'A user account must have an email.'
        return jsonify(response), 400

    if not password:
        response['message'] = 'A user account must have a password.'
        return jsonify(response), 400

    if len(str(password)) < 6 or len(str(password)) > 120:
        response['message'] = 'The password is invalid.'
        return jsonify(response), 400

    # Validation checks

    # Create a Mongo User object if one doesn't exists
    if not User.objects(email=email):
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        # ensure we set an encrypted password.
        new_user.set_password(raw_password=password)
    else:
        response['message'] = 'This user already exists.'
        return jsonify(response), 400

    try:
        new_user.save()

        # generate auth token
        auth_token = new_user.encode_auth_token(new_user.id)
        response['status'] = 'success'
        response['message'] = 'User has been registered.'
        response['token'] = auth_token.decode()
        return jsonify(response), 201

    except ValidationError as e:
        # logger.error('Validation Error: {}'.format(e))
        response['message'] = 'The user cannot be validated.'
        return jsonify(response), 400
    except NotUniqueError as e:
        # logger.error('Not Unique Error: {}'.format(e))
        response['message'] = 'The users details already exists.'
        return jsonify(response), 400


def async_register_session(user: User = None,
                           auth_token: str = None) -> Optional[dict]:
    """We make an async method to allow registering the user to a session
    during login. Doing this in a separate thread doesn't slow the process
    down. Although you may need to be careful about tracking down bugs.

    Args:
        user: the `users_api.models.User` to create a session for.
        auth_token: a stringified type of the User's JWT token.

    Returns:
        The response from the simcct-server.
    """

    # We now need to send a request to the simcct-server to initiate
    # a session as a server-side store to save the last compositions
    # TODO(andrew@neuraldev.io): need to also set last configurations.
    simcct_host = os.environ.get('SIMCCT_HOST', None)
    # Using the `json` param tells requests to serialize the dict to
    # JSON and write the correct MIME type ('application/json') in
    # header.

    last_configs = {}
    last_compositions = {'comp': []}
    user_id = ''

    if isinstance(user, User):
        user_id = user.id

        # We get the configurations if None, otherwise simcct-server is
        # expecting an empty dict.

        if user.last_configuration is not None:
            last_configs = user.last_configuration.to_dict()

        if user.last_compositions is not None:
            last_compositions['comp'] = user.last_compositions

    resp = requests.post(
        url=f'http://{simcct_host}/session',
        json={
            '_id': str(user_id),
            'token': auth_token,
            'last_configurations': last_configs,
            'last_compositions': last_compositions
        })
    # Because this method is in an async state, we want to know if our request
    # to the other side has failed by raising an exception.
    if resp.json().get('status') == 'fail':
        _id = None if user_id == '' else user.id
        raise SessionValidationError(
            f'[DEBUG] A session cannot be initiated for the user_id: {_id}'
        )
    # q.put(resp)
    return resp.json()


@auth_blueprint.route(rule='/auth/login', methods=['POST'])
def login() -> Tuple[dict, int]:
    """
    Blueprint route for registration of users with a returned JWT if successful.
    """

    # Get the post data
    post_data = request.get_json()

    # Validating empty payload
    response = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response), 400

    # Extract the request data required for login
    email = post_data.get('email', '')
    password = post_data.get('password', '')

    # Validate some of these
    if not email:
        response['message'] = 'You must provide an email.'
        return jsonify(response), 400

    if not password:
        response['message'] = 'You must provide a password.'
        return jsonify(response), 400

    if len(str(password)) < 6 or len(str(password)) > 254:
        response['message'] = 'Email or password combination incorrect.'
        return jsonify(response), 400

    if not User.objects(email=email):
        response['message'] = 'User does not exist.'
        return jsonify(response), 404

    user = User.objects.get(email=email)

    if bcrypt.check_password_hash(user.password, password):
        auth_token = user.encode_auth_token(user.id)
        if auth_token:
            # Let's save some stats for later
            user.last_login = datetime.utcnow()
            user.save()

            # We will register the session for the user to the simcct-server
            # in the background so as not to slow the login process down.
            thr = Thread(target=async_register_session,
                         args=[user, str(auth_token)])
            thr.start()
            # Leave this here -- create a queue for responses
            # thr.join()
            # print(q.get().json())

            response['status'] = 'success'
            response['message'] = 'Successfully logged in.'
            response['token'] = auth_token.decode()
            return jsonify(response), 200

    response['message'] = 'Email or password combination incorrect.'
    return jsonify(response), 404


@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
def logout(resp) -> Tuple[dict, int]:
    """Log the user out and invalidate the auth token."""
    response = {'status': 'success', 'message': 'Successfully logged out.'}

    return jsonify(response), 200


@auth_blueprint.route('/auth/status', methods=['GET'])
@authenticate
def get_user_status(resp) -> Tuple[dict, int]:
    """Get the current session status of the user."""
    user = User.objects.get(id=resp)
    response = {
        'status': 'success',
        'data': user.to_dict()
    }
    return jsonify(response), 200
