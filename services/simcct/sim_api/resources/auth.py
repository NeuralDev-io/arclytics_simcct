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

import json
import os
from datetime import datetime
from typing import Tuple

import geoip2
import geoip2.database
from email_validator import EmailNotValidError, validate_email
from flask import (
    Blueprint, jsonify, redirect, render_template, request, session
)
from geoip2.errors import AddressNotFoundError
from mongoengine.errors import NotUniqueError, ValidationError

from logger import AppLogger
from sim_api.extensions import bcrypt
from sim_api.extensions.SimSession.sim_session_service import SimSessionService
from sim_api.extensions.utilities import URLTokenError, URLTokenExpired
from sim_api.middleware import (authenticate_user_and_cookie_flask)
from sim_api.models import LoginData, User
from sim_api.token import (
    confirm_token, generate_confirmation_token, generate_url
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

    protocol = os.environ.get('CLIENT_PROTOCOL')
    client_host = os.environ.get('CLIENT_HOST')
    client_port = os.environ.get('CLIENT_PORT')
    redirect_url = f"{protocol}://{client_host}:{client_port}"

    # We must confirm the token by decoding it
    try:
        email = confirm_token(token)
    except URLTokenError as e:
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)
    except URLTokenExpired as e:
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)
    except Exception as e:
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)

    # We ensure there is a user for this email
    user = User.objects.get(email=email)
    # And do the real work confirming their status
    user.verified = True
    user.save()

    response['status'] = 'success'
    response.pop('message')
    return redirect(f'{redirect_url}/signin', code=302)


@auth_blueprint.route('/confirm/resend', methods=['GET'])
@authenticate_user_and_cookie_flask
def confirm_email_resend(user):

    response = {'status': 'fail', 'message': 'Bad request'}

    if user.verified:
        response['message'] = 'User is already verified.'
        return jsonify(response), 400

    # generate the confirmation token for verifying email
    confirmation_token = generate_confirmation_token(user.email)
    confirm_url = generate_url('auth.confirm_email', confirmation_token)

    from sim_api.email_service import send_email
    send_email(
        to=[user.email],
        subject_suffix='Please Confirm Your Email',
        html_template=render_template(
            'activate.html',
            confirm_url=confirm_url,
            user_name=f'{user.first_name} {user.last_name}'
        ),
        text_template=render_template(
            'activate.txt',
            confirm_url=confirm_url,
            user_name=f'{user.first_name} {user.last_name}'
        )
    )

    response['status'] = 'success'
    response['message'] = 'Another confirmation email has been sent.'
    return jsonify(response), 200


@auth_blueprint.route('/confirmadmin/<token>', methods=['GET'])
def confirm_email_admin(token):
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    protocol = os.environ.get('CLIENT_PROTOCOL')
    client_host = os.environ.get('CLIENT_HOST')
    client_port = os.environ.get('CLIENT_PORT')
    redirect_url = f"{protocol}://{client_host}:{client_port}"

    try:
        email = confirm_token(token)
    except URLTokenError as e:
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)
    except URLTokenExpired as e:
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)
    except Exception as e:
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)

    user = User.objects.get(email=email)
    user.admin_profile.verified = True
    user.save()

    response['status'] = 'success'
    response.pop('message')
    return redirect(f'{redirect_url}/signin', code=302)


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

        from sim_api.email_service import send_email
        send_email(
            to=[email],
            subject_suffix='Please Confirm Your Email',
            html_template=render_template(
                'activate.html',
                confirm_url=confirm_url,
                user_name=f'{new_user.first_name} {new_user.last_name}'
            ),
            text_template=render_template(
                'activate.txt',
                confirm_url=confirm_url,
                user_name=f'{new_user.first_name} {new_user.last_name}'
            )
        )

        # Generic response regardless of email task working
        response['status'] = 'success'
        response['token'] = auth_token.decode()
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

    try:
        if not User.objects(email=email):
            response['message'] = 'User does not exist.'
            return jsonify(response), 404
    except Exception as e:
        logger.error(str(e))
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

            user.save()

            # Get location data
            reader = geoip2.database.Reader(
                '/usr/src/app/sim_api/resources/GeoLite2-City/'
                'GeoLite2-City.mmdb'
            )
            try:
                location_data = reader.city(str(request.remote_addr))
                # location_data = reader.city('203.10.91.88')
                country = location_data.country.names['en']
                state = location_data.subdivisions[0].names['en']
                ip_address = location_data.traits.ip_address

                user.login_data.append(
                    LoginData(
                        country=country, state=state, ip_address=ip_address
                    )
                )
                user.save()
            except AddressNotFoundError:
                user.reload()
                ip_address = request.remote_addr
                user.login_data.append(LoginData(ip_address=ip_address))
                user.save()
            reader.close()

            session['jwt'] = auth_token.decode()
            session['ip_address'] = request.remote_addr
            session['signed_in'] = True

            # Inject the Simulation Session data
            SimSessionService().new_session(user=user)

            response['status'] = 'success'
            response['message'] = 'Successfully logged in.'
            return jsonify(response), 200

    response['message'] = 'Email or password combination incorrect.'
    return jsonify(response), 404


@auth_blueprint.route(rule='/auth/password/check', methods=['POST'])
@authenticate_user_and_cookie_flask
def check_password(user) -> Tuple[dict, int]:
    """
    Route for verifying a user's password.
    """

    # Get request data
    data = request.get_json()

    response = {'status': 'fail', 'message': 'Invalid payload.'}
    if not data:
        return jsonify(response), 400

    password = data.get('password', '')

    if not password:
        response['message'] = 'You must provide a password.'
        return jsonify(response), 400

    if len(str(password)) < 6 or len(str(password)) > 254:
        response['message'] = 'Password incorrect.'
        return jsonify(response), 400

    if bcrypt.check_password_hash(user.password, password):
        response.pop('message')
        response['status'] = 'success'
        return jsonify(response), 200

    response['message'] = 'Password incorrect.'
    return jsonify(response), 400


@auth_blueprint.route('/auth/password/reset', methods=['PUT'])
def reset_password() -> Tuple[dict, int]:
    """The endpoint that resets the password using a password reset token rather
    than the JWT token we usually give for a user. This is only to be used
    for resetting the password of a user who has forgotten their password.

    Returns:
        A valid HTTP Response and a statue code as a tuple.
    """
    # Not using Middleware because w need to use a different token decoding
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
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    protocol = os.environ.get('CLIENT_PROTOCOL')
    client_host = os.environ.get('CLIENT_HOST')
    client_port = os.environ.get('CLIENT_PORT')
    redirect_url = f"{protocol}://{client_host}:{client_port}"

    # Decode the token from the email to the confirm it was the right one
    try:
        email = confirm_token(token)
    except URLTokenError as e:
        return redirect(
            f'{redirect_url}/password/reset?tokenexpired=true', code=302
        )
    except Exception as e:
        return redirect(
            f'{redirect_url}/password/reset?tokenexpired=true', code=302
        )

    # Confirm and validate that the user exists
    user = User.objects.get(email=email)

    # We create a JWT token to send to the client-side so they can attach
    # it as part of the next request
    jwt_token = user.encode_password_reset_token(user_id=user.id).decode()

    response['status'] = 'success'
    response.pop('message')
    return redirect(f'{redirect_url}/password/reset={jwt_token}', code=302)


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
    from sim_api.email_service import send_email
    send_email(
        to=[user.email],
        subject_suffix='Reset your Arclytics Sim password',
        html_template=render_template(
            'reset_password.html',
            reset_url=reset_url,
            email=valid_email,
            user_name=f'{user.first_name} {user.last_name}'
        ),
        text_template=render_template(
            'reset_password.txt',
            reset_url=reset_url,
            email=valid_email,
            user_name=f'{user.first_name} {user.last_name}'
        )
    )

    response['status'] = 'success'
    response.pop('message')
    return jsonify(response), 202


@auth_blueprint.route('/auth/password/change', methods=['PUT'])
@authenticate_user_and_cookie_flask
def change_password(user):
    """The endpoint that allows a user to change password after they have been
    authorized by the authentication middleware.

    Args:
        user_id: the middleware will pass a user_id if successful

    Returns:
        A valid HTTP Response and a statue code as a tuple.
    """
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    request_data = request.get_json()
    if not request_data:
        return jsonify(response), 400

    # validate the old password first because we want to ensure we have the
    # right user.
    old_password = request_data.get('password', None)
    new_password = request_data.get('new_password', None)
    confirm_password = request_data.get('confirm_password', None)

    if not old_password:
        response['message'] = 'Must provide the current password.'
        return jsonify(response), 401

    if not new_password or not confirm_password:
        response['message'] = 'Must provide a password and confirm password.'
        return jsonify(response), 400

    if len(str(new_password)) < 6 or len(str(new_password)) > 120:
        response['message'] = 'The password is invalid.'
        return jsonify(response), 400

    if not new_password == confirm_password:
        response['message'] = 'Passwords do not match.'
        return jsonify(response), 400

    # Validate the user is active
    if not user.verified:
        response['message'] = 'User needs to verify account.'
        return jsonify(response), 401

    if bcrypt.check_password_hash(user.password, old_password):
        user.set_password(new_password)
        user.save()

        # The email to notify users.
        from sim_api.email_service import send_email
        send_email(
            to=[user.email],
            subject_suffix='Your Arclytics Sim password has been changed',
            html_template=render_template(
                'change_password.html',
                change_datetime=datetime.utcnow().isoformat(),
                email=user.email,
                user_name=f'{user.first_name} {user.last_name}'
            ),
            text_template=render_template(
                'change_password.txt',
                change_datetime=datetime.utcnow().isoformat(),
                email=user.email,
                user_name=f'{user.first_name} {user.last_name}'
            )
        )

        response['status'] = 'success'
        response['message'] = 'Successfully changed password.'
        return jsonify(response), 200

    response['message'] = 'Password is not correct.'
    return jsonify(response), 401


@auth_blueprint.route('/auth/email/change', methods=['PUT'])
@authenticate_user_and_cookie_flask
def change_email(user) -> Tuple[dict, int]:
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    request_data = request.get_json()
    if not request_data:
        return jsonify(response), 400

    new_email = request_data.get('new_email', None)

    if not new_email:
        response['message'] = 'No new email given.'
        return jsonify(response), 400

    # Validate new email address.
    try:
        v = validate_email(new_email)
        valid_new_email = v['email']
    except EmailNotValidError as e:
        response['error'] = str(e)
        response['message'] = 'Invalid email.'
        return jsonify(response), 400

    user.email = valid_new_email
    user.verified = False
    user.save()

    confirm_token = generate_confirmation_token(valid_new_email)
    confirm_url = generate_url('auth.confirm_email', confirm_token)

    from sim_api.email_service import send_email
    send_email(
        to=[valid_new_email],
        subject_suffix='Your have changed your Arclytics Sim account email.',
        html_template=render_template(
            'change_email.html',
            user_name=f'{user.first_name} {user.last_name}',
            confirm_url=confirm_url
        ),
        text_template=render_template(
            'change_email.txt',
            user_name=f'{user.first_name} {user.last_name}',
            confirm_url=confirm_url
        )
    )

    response['status'] = 'success'
    response['message'] = 'Email changed.'
    response['new_email'] = valid_new_email
    return jsonify(response), 200


@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate_user_and_cookie_flask
def logout(_) -> Tuple[dict, int]:
    """Log the user out and invalidate the auth token."""

    # Remove the data from the user's current session.
    session.clear()
    response = {'status': 'success', 'message': 'Successfully logged out.'}
    return jsonify(response), 202


@auth_blueprint.route('/auth/status', methods=['GET'])
@authenticate_user_and_cookie_flask
def get_user_status(user) -> Tuple[dict, int]:
    """Get the current session status of the user."""
    is_profile = True
    if not user.profile:
        is_profile = False

    sim_session = json.loads(session['simulation'])

    response = {
        "status": 'success',
        "isProfile": is_profile,
        "verified": user.verified,
        "active": user.active,
        "signedIn": session['signed_in'],
        "simulationValid": sim_session['configurations']['is_valid'],
        "admin": user.is_admin,
    }
    return jsonify(response), 200
