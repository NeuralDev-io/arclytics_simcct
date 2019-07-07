# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# auth.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.05'
"""auth.py: 

{Description}
"""

from bson import ObjectId
from flask import Blueprint, jsonify, request
from mongoengine.errors import ValidationError, NotUniqueError

from api.models import User
from api import bcrypt

from logger.arc_logger import AppLogger
from api.auth_decorators import authenticate

logger = AppLogger(__name__)

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route(rule='/auth/register', methods=['POST'])
def register_user():
    """Blueprint route for registration of users."""

    # Get the post data
    post_data = request.get_json()

    # Validating empty payload
    response = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response), 400

    # Extract the request body data
    email = post_data.get('email', '')
    username = post_data.get('username', '')
    password = post_data.get('password', '')

    if not email:
        response['message'] = 'A user account must have an email.'
        return jsonify(response), 400

    if not password:
        response['message'] = 'A user account must have a password.'
        return jsonify(response), 400

    if len(str(password)) < 6 or len(str(password)) > 254:
        response['message'] = 'The password is invalid.'
        return jsonify(response), 400

    # Validation checks

    # Create a Mongo User object if one doesn't exists
    if not User.objects(email=email):
        new_user = User(
            email=email,
            username=username,
        )
        new_user.set_password(
            raw_password=password)  # ensure we set an encrypted password.
    else:
        response['message'] = 'This user already exists.'
        return jsonify(response), 400

    try:
        new_user.save()

        # generate auth token
        auth_token = new_user.encode_auth_token(new_user.id)
        response['status'] = 'success'
        response['message'] = 'User has been registered.'
        response['auth_token'] = auth_token.decode()
        return jsonify(response), 201

    except ValidationError as e:
        # logger.error('Validation Error: {}'.format(e))
        response['message'] = 'The user cannot be validated.'
        return jsonify(response), 400
    except NotUniqueError as e:
        # logger.error('Not Unique Error: {}'.format(e))
        response['message'] = 'The users details already exists.'
        return jsonify(response), 400


@auth_blueprint.route(rule='/auth/login', methods=['POST'])
def login():
    """Blueprint route for registration of users with a returned JWT if successful."""

    # Get the post data
    post_data = request.get_json()

    # Validating empty payload
    response = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response), 400

    # Extract the request data required for login
    email = post_data.get('email', '')
    password = post_data.get('password', '')

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
            response['status'] = 'success'
            response['message'] = 'Successfully logged in.'
            response['auth_token'] = auth_token.decode()
            return jsonify(response), 200

    response['message'] = 'Email or password combination incorrect.'
    return jsonify(response), 404


@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
def logout(resp):
    """Log the user out and invalidate the auth token."""
    response = {'status': 'success', 'message': 'Successfully logged out.'}

    return jsonify(response), 200


@auth_blueprint.route('/auth/status', methods=['GET'])
@authenticate
def get_user_status(resp):
    """Get the current session status of the user."""
    user = User.objects.get(id=resp)
    response = {
        'status': 'success',
        'message': 'User status good.',
        'data': user.to_dict()
    }
    return jsonify(response), 200
