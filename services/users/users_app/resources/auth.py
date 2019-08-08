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
from socket import gaierror
from datetime import datetime
from typing import Tuple, Optional
from threading import Thread

from celery.states import PENDING
from email_validator import validate_email, EmailNotValidError
from flask import current_app as app
from flask import (
    Blueprint, jsonify, request, render_template, redirect, Response
)
from mongoengine.errors import ValidationError, NotUniqueError

from users_app.models import User
from users_app.extensions import bcrypt
from logger.arc_logger import AppLogger
from users_app.middleware import authenticate_flask, logout_authenticate
from users_app.token import (
    generate_confirmation_token, generate_url, confirm_token, URLTokenError
)

logger = AppLogger(__name__)

auth_blueprint = Blueprint('auth', __name__)


class SessionValidationError(Exception):
    """
    A custom exception to be raised by a threaded async call to register if
    the response is not what we are expecting.
    """

    def __init__(self, msg: str):
        super(SessionValidationError, self).__init__(msg)


class SimCCTBadServerLogout(Exception):
    """
    A custom exception to be raised by a synchronous call to logout on the
    SimCCT server if the response is not what we are expecting.
    """

    def __init__(self, msg: str):
        super(SimCCTBadServerLogout, self).__init__(msg)


@auth_blueprint.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    """This endpoint simply just takes in the token that a user would send
    from going to a link in their confirmation email and attaching the token
    as part of the request parameter.

    Args:
        token: The valid URL Timed token.

    Returns:

    """
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    # We must confirm the token by decoding it
    try:
        email = confirm_token(token)
    except URLTokenError as e:
        response['error'] = e
        return jsonify(response), 400
    except Exception as e:
        response['error'] = str(e)
        return jsonify(response), 400

    # We ensure there is a user for this email
    user = User.objects.get(email=email)
    # And do the real work confirming their status
    user.verified = True

    response['status'] = 'success'
    response.pop('message')
    # TODO(andrew@neuraldev.io): Need to check how to change this during
    #  during production and using Ingress/Load balancing for Kubernetes
    client_host = os.environ.get('CLIENT_HOST')
    return redirect('http://localhost:3000/signin', code=302)


@auth_blueprint.route('/confirmadmin/<token>', methods=['GET'])
def confirm_email_admin(token):
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    try:
        email = confirm_token(token)
    except URLTokenError as e:
        response['error'] = e
        return jsonify(response), 400
    except Exception as e:
        return jsonify(response), 400

    user = User.objects.get(email=email)
    user.admin_profile.verified = True

    response['status'] = 'success'
    response.pop('message')
    # TODO(davidmatthews1004@gmail.com): Need to check how to change this during
    #  during production and using Ingress/Load balancing for Kubernetes
    client_host = os.environ.get('CLIENT_HOST')
    return redirect('http://localhost:3000/signin', code=302)


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

    # Create a Mongo User object if one doesn't exists
    if not User.objects(email=email):
        new_user = User(
            email=email, first_name=first_name, last_name=last_name
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
        # generate the confirmation token for verifying email
        confirmation_token = generate_confirmation_token(email)
        confirm_url = generate_url('auth.confirm_email', confirmation_token)

        from celery_runner import celery
        task = celery.send_task(
            'tasks.send_email',
            kwargs={
                'to':
                email,
                'subject_suffix':
                'Please Confirm Your Email',
                'html_template':
                render_template(
                    'activate.html',
                    confirm_url=confirm_url,
                    user_name=f'{new_user.first_name} {new_user.last_name}'
                ),
                'text_template':
                render_template(
                    'activate.txt',
                    confirm_url=confirm_url,
                    user_name=f'{new_user.first_name} {new_user.last_name}'
                )
            }
        )
        # FIXME(andrew@neuraldev.io): Need to find a way to validate that it has
        #  sent without waiting for the result.
        task_status = celery.AsyncResult(task.id).state

        while task_status == PENDING:
            task_status = celery.AsyncResult(task.id).state
        # The email tasks responds with a Tuple[bool, str]
        res = celery.AsyncResult(task.id)

        # Generic response regardless of email task working
        response['status'] = 'success'
        response['token'] = auth_token.decode()

        if isinstance(res.result, gaierror):
            response['error'] = 'Socket error.'
            response['message'] = (
                'User registered but registration '
                'email failed.'
            )
            return jsonify(response), 201

        if not res.result[0]:
            response['error'] = res.result[1]
            response['message'] = (
                'User registered but registration '
                'email failed.'
            )
            return jsonify(response), 201

        response['message'] = 'User has been registered.'
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
        user: the `users_app.models.User` to create a session for.
        auth_token: a stringified type of the User's JWT token.

    Returns:
        The response from the simcct server.
    """

    # We now need to send a request to the simcct server to initiate
    # a session as a server-side store to save the last compositions/configs
    simcct_host = os.environ.get('SIMCCT_HOST', None)
    # Using the `json` param tells requests to serialize the dict to
    # JSON and write the correct MIME type ('application/json') in
    # header.

    last_configs = None
    last_alloy = None
    user_id = ''  # Just for printing SessionValidationError

    if isinstance(user, User):
        user_id = user.id

        # We get the configurations if None, otherwise simcct server is
        # expecting an empty dict.

        if user.last_configuration is not None:
            last_configs = user.last_configuration.to_dict()

        if user.last_alloy_store is not None:
            last_alloy = user.last_alloy_store.to_dict()

    resp = requests.post(
        url=f'http://{simcct_host}/session/login',
        json={
            '_id': str(user_id),
            'is_admin': user.is_admin,
            'last_configurations': last_configs,
            'last_alloy_store': last_alloy
        },
        headers={
            'Authorization': f'Bearer {auth_token}',
            'Content-type': 'application/json'
        }
    )
    # Because this method is in an async state, we want to know if our request
    # to the other side has failed by raising an exception.
    if resp.json().get('status') == 'fail':
        _id = None if user_id == '' else user.id
        raise SessionValidationError(
            f'[DEBUG] A session cannot be initiated for the user_id: {_id}'
        )
    # q.put(resp)
    return resp.json()


def register_session(user: User = None, auth_token: str = None):
    # We now need to send a request to the simcct server to initiate
    # a session as a server-side store to save the last compositions/configs
    simcct_host = os.environ.get('SIMCCT_HOST', None)
    # Using the `json` param tells requests to serialize the dict to
    # JSON and write the correct MIME type ('application/json') in
    # header.

    last_configs = None
    last_alloy = None

    if isinstance(user, User):
        if user.last_configuration is not None:
            last_configs = user.last_configuration.to_dict()

        if user.last_alloy_store is not None:
            last_alloy = user.last_alloy_store.to_dict()

    resp = requests.post(
        url=f'http://{simcct_host}/session/login',
        json={
            '_id': str(user.id),
            'is_admin': user.is_admin,
            'last_configurations': last_configs,
            'last_alloy_store': last_alloy
        },
        headers={
            'Authorization': f'Bearer {auth_token}',
            'Content-type': 'application/json'
        }
    )
    data = resp.json()
    # Because this method is in an async state, we want to know if our request
    # to the other side has failed by raising an exception.
    if not data or data.get('status') == 'fail':
        _id = user.id
        raise SessionValidationError(
            f'[DEBUG] A session cannot be initiated for the user_id: {_id}'
        )
    return data.get('session_key')


@auth_blueprint.route(rule='/auth/login', methods=['POST'])
def login() -> any:
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
            if not user.active:
                response['message'] = 'Your Account has been disabled.'
                return jsonify(response), 401

            # Let's save some stats for later
            user.last_login = datetime.utcnow()

            # TODO(andrew@neuraldev.io): Save the users' login location

            user.save()

            # We will register the session for the user to the simcct server
            # in the background so as not to slow the login process down.
            # thr = Thread(
            #     target=async_register_session,
            #     args=[user, str(auth_token.decode())]
            # )
            # thr.start()
            # Leave this here -- create a queue for responses
            # thr.join()
            # print(q.get().json())
            try:
                session_key = register_session(user, auth_token.decode())
            except SessionValidationError as e:
                response['message'] = 'Session validation error.'
                response['error'] = str(e)
                return jsonify(response), 400

            response['status'] = 'success'
            response['message'] = 'Successfully logged in.'
            response['token'] = auth_token.decode()
            response['session'] = session_key
            return jsonify(response), 200

    response['message'] = 'Email or password combination incorrect.'
    return jsonify(response), 404


@auth_blueprint.route('/auth/password/reset', methods=['PUT'])
def reset_password():
    response = {'status': 'fail', 'message': 'Provide a valid JWT auth token.'}

    # get the auth token
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        return jsonify(response), 400

    token = auth_header.split(' ')[1]

    # Decode either returns bson.ObjectId if successful or a string from an
    # exception
    resp_or_id = User.decode_password_reset_token(auth_token=token)

    # Either returns an ObjectId User ID or a string response.
    if isinstance(resp_or_id, str):
        response['message'] = resp_or_id
        return jsonify(response), 401

    request_data = request.get_json()
    if not request_data:
        response['message'] = 'Invalid payload.'
        return jsonify(response), 400

    # validate the passwords
    password = request_data.get('password', None)
    confirm_password = request_data.get('confirm_password', None)

    if not password or not confirm_password:
        response['message'] = 'Must provide a password and confirm password.'
        return jsonify(response), 400

    if len(str(password)) < 6 or len(str(password)) > 120:
        response['message'] = 'The password is invalid.'
        return jsonify(response), 400

    if not password == confirm_password:
        response['message'] = 'Passwords do not match.'
        return jsonify(response), 400

    # Validate the user is active
    user = User.objects.get(id=resp_or_id)
    if not user or not user.active:
        response['message'] = 'User does not exist.'
        return jsonify(response), 401

    # TODO(andrew@neuraldev.io): Send a confirmation email again to the user
    #  that their password has been reset.

    # Well, they have passed every test
    user.set_password(password)
    user.save()

    response['status'] = 'success'
    response.pop('message')
    return jsonify(response), 202


@auth_blueprint.route('/reset/password/confirm/<token>', methods=['GET'])
def confirm_reset_password(token):
    response = {'status': 'fail', 'message': 'Invalid token.'}

    # Decode the token from the email to the confirm it was the right one
    try:
        email = confirm_token(token)
    except URLTokenError as e:
        response['error'] = str(e)
        return jsonify(response), 400
    except Exception as e:
        response['error'] = str(e)
        return jsonify(response), 400

    # Confirm and validate that the user exists
    user = User.objects.get(email=email)

    # We create a JWT token to send to the client-side so they can attach
    # it as part of the next request
    jwt_token = user.encode_password_reset_token(user_id=user.id).decode()

    # TODO(andrew@neuraldev.io): Ensure the link can be dynamic.
    client_host = os.environ.get('CLIENT_HOST')
    # We can make our own redirect response by doing the following
    custom_redir_response = app.response_class(
        status=302, mimetype='application/json'
    )
    redirect_url = f'http://localhost:3000/password/reset={jwt_token}'
    custom_redir_response.headers['Location'] = redirect_url
    # Additionally, if we need to, we can attach the JWT token in the header
    # custom_redir_response.headers['Authorization'] = f'Bearer {jwt_token}'
    return custom_redir_response


@auth_blueprint.route('/reset/password', methods=['POST'])
def reset_password_email() -> Tuple[dict, int]:
    """This endpoint is to be used by the client-side browser to send the email
    to the API server for validation with the user's details. It will only send
    an email if the email has a registered user in the users collection and
    will only send to the email of that user stored in their document. If all
    validation is successful, a URL timed token will be generated and sent to
    the user's email to click the link which will then validate the token
    with another endpoint at `/auth/resetpassword/confirm/<token>`.

    Returns:
        A dict of of response messages converted to 'application/json' and a
        HTML status code.
    """
    post_data = request.get_json()

    # Validating empty payload
    response = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response), 400

    # Get the email from the client-side request body
    post_email = post_data.get('email')

    if not post_email:
        return jsonify(response), 400

    # Verify it is actually a valid email
    try:
        # validate and get info
        v = validate_email(post_email)
        # replace with normalized form
        valid_email = v['email']
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        response['error'] = str(e)
        response['message'] = 'Invalid email.'
        return jsonify(response), 400

    # Verify the email matches a user in the database
    if not User.objects(email=valid_email):
        response['message'] = 'User does not exist.'
        return jsonify(response), 404

    # If there is a user with this email address, we must send to that email
    user = User.objects.get(email=valid_email)

    # Verify the user's account has been verified/confirmed
    if not user.verified:
        response['message'] = 'The user must verify their email.'
        return jsonify(response), 401

    # Generate the JWT token with the user id embedded
    # Generate the password reset url to use another endpoint
    reset_token = generate_confirmation_token(user.email)
    reset_url = generate_url('auth.confirm_reset_password', reset_token)

    # Send with the url to an email stored in the document of that user
    from celery_runner import celery
    celery.send_task(
        'tasks.send_email',
        kwargs={
            'to':
            user.email,
            'subject_suffix':
            'Reset your Arclytics Sim password',
            'html_template':
            render_template(
                'reset_password.html',
                reset_url=reset_url,
                email=valid_email,
                user_name=f'{user.first_name} {user.last_name}'
            ),
            'text_template':
            render_template(
                'reset_password.txt',
                reset_url=reset_url,
                email=valid_email,
                user_name=f'{user.first_name} {user.last_name}'
            )
        }
    )

    response['status'] = 'success'
    response.pop('message')
    return jsonify(response), 202


@auth_blueprint.route('/auth/logout', methods=['GET'])
@logout_authenticate
def logout(user_id, token, session_key) -> Tuple[dict, int]:
    """Log the user out and invalidate the auth token."""
    # FIXME(andrew@neuraldev.io): There seems to be a huge issue with this
    #  as in testing, or possibly even live, there seems to be no cross-server
    #  session storage of the user.

    response = {'status': 'success', 'message': 'Successfully logged out.'}

    simcct_host = os.environ.get('SIMCCT_HOST', None)
    simcct_resp = requests.get(
        url=f'http://{simcct_host}/session/logout',
        headers={
            'Authorization': 'Bearer {token}'.format(token=token),
            'Session': f'{session_key}',
            'Content-type': 'application/json'
        }
    )

    # print(simcct_resp)
    if simcct_resp.json().get('status', 'fail') == 'fail':
        raise SimCCTBadServerLogout(
            f'Unable to logout the user_id: {user_id} from the SimCCT server'
        )

    return jsonify(response), 202


@auth_blueprint.route('/auth/status', methods=['GET'])
@authenticate_flask
def get_user_status(user_id) -> Tuple[dict, int]:
    """Get the current session status of the user."""
    user = User.objects.get(id=user_id)
    response = {'status': 'success', 'data': user.to_dict()}
    return jsonify(response), 200
