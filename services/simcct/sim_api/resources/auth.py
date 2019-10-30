# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# auth.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.7.0'
__status__ = 'production'
__date__ = '2019.07.05'
"""auth.py:

This module describes the Users authentication endpoints for registration,
login, logout, and any additional endpoints that require authentication and 
authorisation purposes..
"""

import os
from datetime import datetime
from typing import Tuple
from pathlib import Path
from copy import deepcopy

import geoip2
import geoip2.database
from bson import ObjectId
from email_validator import EmailNotValidError
from flask import (
    Blueprint, jsonify, redirect, render_template, request, session
)
from geoip2.errors import AddressNotFoundError
from maxminddb.errors import InvalidDatabaseError
from mongoengine.errors import NotUniqueError, ValidationError
from redis import ReadOnlyError

from arc_logging import AppLogger
from sim_api.routes import Routes
from sim_api.extensions import bcrypt, apm, redis_session
from sim_api.extensions.utilities import (
    URLTokenError, URLTokenExpired, arc_validate_email
)
from sim_api.middleware import (authenticate_user_and_cookie_flask)
from sim_api.models import LoginData, User, SharedSimulation
from sim_api.token import (
    confirm_token, generate_confirmation_token, generate_url
)
from sim_api.auth_service import AuthService

logger = AppLogger(__name__)

auth_blueprint = Blueprint('auth', __name__)


# noinspection PyBroadException
@auth_blueprint.route(Routes.confirm_email.value, methods=['GET'])
def confirm_email(token) -> Tuple[dict, int]:
    """This endpoint simply just takes in the token that a user would send
    from going to a link in their confirmation email and attaching the token
    as part of the request parameter.

    Args:
        token: The valid URL Timed token.

    Returns:

    """
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    protocol = os.environ.get('CLIENT_SCHEME')
    client_host = os.environ.get('CLIENT_HOST')
    client_port = os.environ.get('CLIENT_PORT')
    redirect_url = f'{protocol}://{client_host}:{client_port}'

    # We must confirm the token by decoding it
    try:
        email = confirm_token(token)
    except URLTokenError:
        # We send a redirect to the frontend with a query in the params to
        # say that the token has expired and they will handle it appropriately
        # for the user.
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)
    except URLTokenExpired:
        # We send a redirect to the frontend with a query in the params to
        # say that the token has expired and they will handle it appropriately
        # for the user.
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)
    except Exception as e:
        message = 'An Exception Occurred.'
        log_message = {'message': message, "error": str(e)}
        logger.error(log_message)
        apm.capture_exception()
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)

    # We ensure there is a user for this email
    if not User.objects(email=email):
        log_message = {'message': 'User does not exist.'}
        logger.error(log_message)
        apm.capture_message(log_message)
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)

    # And do the real work confirming their status
    user = User.objects.get(email=email)
    user.verified = True
    user.save()

    response['status'] = 'success'
    response.pop('message')
    return redirect(f'{redirect_url}/signin', code=302)


@auth_blueprint.route(Routes.confirm_email_resend.value, methods=['GET'])
@authenticate_user_and_cookie_flask
def confirm_email_resend(user) -> Tuple[dict, int]:
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


@auth_blueprint.route(
    Routes.confirm_email_resend_after_registration.value, methods=['PUT']
)
def confirm_email_resend_after_registration() -> Tuple[dict, int]:
    response = {'status': 'success'}

    data = request.get_json()

    email = data.get('email', None)

    if not User.objects(email=email):
        log_message = 'User does not exist'
        logger.warning(log_message)
        return jsonify(response), 200

    user = User.objects.get(email=email)

    if user.verified:
        log_message = 'User is already verified.'
        logger.warning(log_message)
        # response['message'] = 'User is already verified.'
        return jsonify(response), 200

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
    # response['message'] = 'Another confirmation email has been sent.'
    return jsonify(response), 200


@auth_blueprint.route(Routes.confirm_email_admin.value, methods=['GET'])
def confirm_email_admin(token) -> Tuple[dict, int]:
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    protocol = os.environ.get('CLIENT_SCHEME')
    client_host = os.environ.get('CLIENT_HOST')
    client_port = os.environ.get('CLIENT_PORT')
    redirect_url = f"{protocol}://{client_host}:{client_port}"

    try:
        email = confirm_token(token)
    except URLTokenError:
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)
    except URLTokenExpired:
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)
    except Exception as e:
        message = 'An Exception Occured.'
        log_message = {'message': message, "error": str(e)}
        logger.error(log_message)
        apm.capture_exception()
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)

    if not User.objects(email=email):
        log_message = {'message': 'User does not exist.'}
        logger.error(log_message)
        apm.capture_message(log_message)
        return redirect(f'{redirect_url}/signin?tokenexpired=true', code=302)

    user = User.objects.get(email=email)
    user.admin_profile.verified = True
    user.save()

    response['status'] = 'success'
    response.pop('message')
    return redirect(f'{redirect_url}/signin', code=302)


@auth_blueprint.route(Routes.register_user.value, methods=['POST'])
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

    # Verify email is valid
    try:
        v = arc_validate_email(email)
        valid_email = v['email']
    except EmailNotValidError as e:
        response['error'] = str(e)
        response['message'] = 'Invalid email.'
        return response, 400

    # Create a Mongo User object if one doesn't exists
    if not User.objects(email=valid_email):
        new_user = User(
            email=valid_email, first_name=first_name, last_name=last_name
        )
        # ensure we set an encrypted password.
        new_user.set_password(raw_password=password)
    else:
        response['message'] = 'This user already exists.'
        return jsonify(response), 400

    try:
        new_user.save()

        # generate auth token and pass the role of the user, which at the
        # beginning is always the default.
        auth_token = AuthService().encode_auth_token(new_user.id, role='user')
        # generate the confirmation token for verifying email
        confirmation_token = generate_confirmation_token(valid_email)
        confirm_url = generate_url('auth.confirm_email', confirmation_token)

        from sim_api.email_service import send_email
        send_email(
            to=[valid_email],
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

    except ValidationError:
        response['message'] = 'The user cannot be validated.'
        return jsonify(response), 400
    except NotUniqueError:
        response['message'] = 'The users details already exists.'
        return jsonify(response), 400


@auth_blueprint.route(Routes.check_password.value, methods=['POST'])
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


@auth_blueprint.route(Routes.reset_password.value, methods=['PUT'])
def reset_password() -> Tuple[dict, int]:
    """The endpoint that resets the password using a password reset token rather
    than the JWT token we usually give for a user. This is only to be used
    for resetting the password of a user who has forgotten their password.

    Returns:
        A valid HTTP Response and a statue code as a tuple.
    """
    # Not using Middleware because we need to use a different token decoding
    response = {'status': 'fail', 'message': 'Provide a valid JWT auth token.'}

    # get the auth token
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        return jsonify(response), 400

    token = auth_header.split(' ')[1]

    # Decode either returns bson.ObjectId if successful or a string from an
    # exception
    resp_or_id = AuthService().decode_password_reset_token(auth_token=token)
    if isinstance(resp_or_id, str):
        response['message'] = resp_or_id
        logger.info(response['message'])
        apm.capture_message(response['message'])
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
        # For security reasons we send back successful even if the user exists.
        # response['message'] = 'User does not exist.'
        # return jsonify(response), 401
        response['status'] = 'success'
        response.pop('message')
        return jsonify(response), 202

    # The email to notify the user that their password has been changed.
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

    # Well, they have passed every test
    user.set_password(password)
    user.save()

    response['status'] = 'success'
    response.pop('message')
    return jsonify(response), 202


@auth_blueprint.route(Routes.confirm_reset_password.value, methods=['GET'])
def confirm_reset_password(token) -> Tuple[dict, int]:
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    protocol = os.environ.get('CLIENT_SCHEME')
    client_host = os.environ.get('CLIENT_HOST')
    client_port = os.environ.get('CLIENT_PORT')
    redirect_url = f"{protocol}://{client_host}:{client_port}"

    # Decode the token from the email to the confirm it was the right one
    try:
        email = confirm_token(token)
    except URLTokenError:
        logger.exception('Bad URL token.')
        apm.capture_exception()
        return redirect(
            f'{redirect_url}/password/reset?tokenexpired=true', code=302
        )
    except Exception as e:
        logger.exception(
            {
                'msg': 'URL token confirmation error. ',
                'error': str(e)
            }
        )
        apm.capture_exception()
        return redirect(
            f'{redirect_url}/password/reset?tokenexpired=true', code=302
        )

    # Ensure the user exists
    if not User.objects(email=email):
        logger.error('User does not exist.')
        apm.capture_message('User does not exist.')
        return redirect(
            f'{redirect_url}/password/reset?tokenexpired=true', code=302
        )

    # Confirm and validate that the user exists
    user = User.objects.get(email=email)

    # We create a JWT token to send to the client-side so they can attach
    # it as part of the next request
    jwt_token = AuthService().encode_password_reset_token(user_id=user.id
                                                          ).decode()

    response['status'] = 'success'
    response.pop('message')
    return redirect(f'{redirect_url}/password/reset={jwt_token}', code=302)


@auth_blueprint.route(Routes.reset_password_email.value, methods=['POST'])
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
        v = arc_validate_email(post_email)
        # replace with normalized form
        valid_email = v['email']
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        response['error'] = str(e)
        response['message'] = 'Invalid email.'
        return jsonify(response), 400

    # Verify the email matches a user in the database
    if not User.objects(email=valid_email):
        # For security reasons we send back 'success'
        response['status'] = 'success'
        response.pop('message')
        return jsonify(response), 202
        # response['message'] = 'User does not exist.'
        # return jsonify(response), 404

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


@auth_blueprint.route(Routes.change_password.value, methods=['PUT'])
@authenticate_user_and_cookie_flask
def change_password(user) -> Tuple[dict, int]:
    """The endpoint that allows a user to change password after they have been
    authorized by the authentication middleware.

    Args:
        user: the middleware will pass a `models.User` object if successful

    Returns:
        A valid HTTP Response and a statue code as a tuple.
    """
    response = {'status': 'fail', 'message': 'Invalid payload.'}

    request_data = request.get_json()
    if not request_data:
        return jsonify(response), 400

    # validate the old password first because we want to ensure we have the
    # right user.
    new_password = request_data.get('new_password', None)
    confirm_password = request_data.get('confirm_password', None)

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


@auth_blueprint.route(Routes.change_email.value, methods=['PUT'])
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
        v = arc_validate_email(new_email)
        valid_new_email = v['email']
    except EmailNotValidError as e:
        response['error'] = str(e)
        response['message'] = 'Invalid email.'
        return jsonify(response), 400

    user.email = valid_new_email
    user.verified = False
    user.save()

    _confirm_token = generate_confirmation_token(valid_new_email)
    confirm_url = generate_url('auth.confirm_email', _confirm_token)

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


# noinspection PyBroadException
@auth_blueprint.route(Routes.login.value, methods=['POST'])
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
            # response['message'] = 'User does not exist.'
            # return jsonify(response), 404
            # For security reasons we do not responsed with 'user does not
            # exist'
            response['message'] = 'Email or password combination incorrect.'
            return jsonify(response), 400
    except Exception:
        # response['message'] = 'User does not exist'
        # return jsonify(response), 404
        # For security reasons we do not responsed with 'user does not
        # exist'
        response['message'] = 'Email or password combination incorrect.'
        return jsonify(response), 400

    # Let's save some stats for later
    login_datetime = datetime.utcnow()

    user = User.objects.get(email=str(email).lower())

    # Now let's really check if the User can access our application
    if bcrypt.check_password_hash(user.password, password):
        user_role = 'admin' if user.is_admin else 'user'
        auth_token = AuthService().encode_auth_token(user.id, role=user_role)

        if auth_token:
            if not user.active:
                response['message'] = 'This user account has been disabled.'
                logger.info(
                    {
                        'message': response['message'],
                        'user': user.email
                    }
                )
                apm.capture_message('Unauthorised access.')
                return jsonify(response), 403

            # First we check if there is a proxy or other network service
            # that forwards the IP address. If it is not the case,
            # we can check for the HTTP_X_REAL_IP which is part of
            # the header and is often used in a proxy.
            if not request.headers.get('X-Forwarded-For', None):
                # If HTTP_X_REAL_IP not found, we can then fall back
                # to use the `request.remote_addr` even though it is
                # unlikely to be a real address.
                request_ip = request.environ.get(
                    'HTTP_X_REAL_IP', request.remote_addr
                )
            else:
                # If we have a forwarded IP, it usually can be split
                # We want the first one because the syntax is as follows:
                # X-Forwarded-For: <client>, <proxy1>, <proxy2>
                # Refer to:
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/
                # Headers/X-Forwarded-For
                # "The X-Forwarded-For (XFF) header is a de-facto standard
                # header for identifying the originating IP address of a
                # client connecting to a web server through an HTTP proxy
                # or a load balancer."
                forwarded_ip = request.headers.get('X-Forwarded-For')
                request_ip = str(forwarded_ip).split(',')[0]

            # Get the relative path of the database from the current path
            # Applying dirname to a directory yields the parent directory
            par_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = Path(par_dir) / 'GeoLite2-City' / 'GeoLite2-City.mmdb'

            # If we can't record this data, we will store it as a Null
            country, state, continent, timezone = None, None, None, None
            geopoint = None
            accuracy_radius = 0

            try:
                if not db_path.exists():
                    raise FileNotFoundError(
                        f'MaxMind DB file not found in {db_path.as_posix()}.'
                    )
                # Read from a MaxMind DB  that we have stored as so the
                # `geoip2` library cna look for the IP address location.
                reader = geoip2.database.Reader(db_path.as_posix())

                location_data = reader.city(str(request_ip))

                if location_data.country:
                    country = location_data.country.names['en']

                if location_data.subdivisions:
                    state = location_data.subdivisions[0].names['en']

                if location_data.continent:
                    continent = location_data.continent.names['en']

                if location_data.location:
                    accuracy_radius = location_data.location.accuracy_radius
                    geopoint = {
                        'type':
                        'Point',
                        'coordinates': [
                            location_data.location.latitude,
                            location_data.location.longitude
                        ]
                    }
                    timezone = location_data.location.time_zone

                reader.close()
            except FileNotFoundError as e:
                apm.capture_exception()
                logger.critical(
                    {
                        'message': 'File not found error.',
                        'error': str(e)
                    }
                )
            except ValueError as e:
                apm.capture_exception()
                logger.exception(
                    {
                        'message': 'geoip2 Read error.',
                        'error': str(e)
                    }
                )
            except InvalidDatabaseError as e:
                apm.capture_exception()
                logger.exception(
                    {
                        'message': 'Invalid MaxMind DB error.',
                        'error': str(e)
                    }
                )
            except AddressNotFoundError:
                # If our library cannot find a location based on the IP address
                # usually because we're in a localhost testing environment or
                # if the address is somehow bad, then we need to handle this
                # error and allow the response.
                apm.capture_exception()
            finally:
                # logger.info(
                #     {
                #         'message': 'User logged in.',
                #         'user': user.email,
                #         'country': country,
                #         'state': state,
                #         'ip_address': request_ip
                #     }
                # )
                login_data = LoginData(
                    **{
                        'ip_address': request_ip,
                        'created_datetime': login_datetime,
                        'continent': continent,
                        'country': country,
                        'state': state,
                        'accuracy_radius': accuracy_radius,
                        'geo_point': geopoint,
                        'timezone': timezone,
                    }
                )
                user.last_login = login_datetime
                user.login_data.append(login_data)
                user.save()

            # Store additional information in their session as it will be
            # required by the server-side session interface to check and
            # generate other tokens and keys.
            session['jwt'] = auth_token.decode()
            session['ip_address'] = request_ip
            session['is_admin'] = user.is_admin
            session['user_id'] = str(user.id)
            session['location'] = login_data.to_dict()

            response.update(
                {
                    'status': 'success',
                    'message': 'Successfully logged in.'
                }
            )
            return jsonify(response), 200

    response['message'] = 'Email or password combination incorrect.'
    logger.info(response['message'])
    apm.capture_message(response['message'])
    return jsonify(response), 400


@auth_blueprint.route(Routes.logout.value, methods=['GET'])
@authenticate_user_and_cookie_flask
def logout(_) -> Tuple[dict, int]:
    """Log the user out and invalidate the auth token."""
    # Save the session ID for later
    sid = deepcopy(session.sid)

    # Ensure we remove the JWT from the session dict.
    session.pop('jwt')

    # Remove the data from the user's current session.
    session.clear()

    # Remove the session stored in Redis so that the next time the user
    # tries to use an endpoint with a deleted cookie, there will be no
    # Redis value returned and they will need to have a new session created.

    # Grab the exposed RedisSessionInterface instance exposed.
    r_sess_interface = redis_session.interface
    # Get the Redis connection stored in the instance
    redis = r_sess_interface.redis
    # We need to include the prefix that we use to store the Session in Redis
    redis_session_key = r_sess_interface.redis_key(sid)
    # Delete the Redis storage to ensure the cookie is not valid anymore
    try:
        redis.delete(redis_session_key)
    except ReadOnlyError:
        logger.exception('Redis read error in logout.')
        apm.capture_exception()
        redis.connection_pool.reset()

    # logger.debug({'msg': redis.get(redis_session_key)})
    # logger.debug({'session': session})
    response = {'status': 'success', 'message': 'Successfully logged out.'}
    return jsonify(response), 202


@auth_blueprint.route(Routes.get_user_status.value, methods=['GET'])
@authenticate_user_and_cookie_flask
def get_user_status(user) -> Tuple[dict, int]:
    """Get the current session status of the user."""
    is_profile = True
    if not user.profile:
        is_profile = False

    response = {
        "status": 'success',
        "isProfile": is_profile,
        "verified": user.verified,
        "active": user.active,
        "admin": user.is_admin,
    }
    return jsonify(response), 200


@auth_blueprint.route(Routes.delete_user, methods=['DELETE'])
@authenticate_user_and_cookie_flask
def delete_user(user) -> Tuple[dict, int]:
    """This method deletes a User's document and all documents that are
    referenced to the user. It further deletes all other documents that are
    created by the user.

    Args:
        user: a `sim_api.models.User` instance passed from the middleware.

    Returns:
        A valid HTTP response and status code.
    """

    # Store these so we can delete documents related to this user.
    # oid = ObjectId(deepcopy(user.id))
    email = deepcopy(user.email)

    # Due to the ReferenceField used in the `sim_api.model.Feedback`
    # and `sim_api.models.SavedSimulation` being set with
    # `on_delete_rule=mongoengine.CASCADE`, doing this will also delete those
    # documents in those collections.
    user.delete()

    # Delete Shared Simulations
    SharedSimulation.objects(owner_email=email).delete()

    # Delete the cookie from the response
    sid = deepcopy(session.sid)
    # Ensure we remove the JWT from the session dict.
    session.pop('jwt')
    # Remove the data from the user's current session.
    session.clear()
    # Remove the session stored in Redis so that the next time the user
    # tries to use an endpoint with a deleted cookie, there will be no
    # Redis value returned and they will need to have a new session created.

    # Grab the exposed RedisSessionInterface instance exposed.
    r_sess_interface = redis_session.interface
    # Get the Redis connection stored in the instance
    redis = r_sess_interface.redis
    # We need to include the prefix that we use to store the Session in Redis
    redis_session_key = r_sess_interface.redis_key(sid)
    # Delete the Redis storage to ensure the cookie is not valid anymore
    try:
        redis.delete(redis_session_key)
    except ReadOnlyError:
        logger.exception('Redis read error in logout.')
        apm.capture_exception()
        redis.connection_pool.reset()

    return {}, 204
