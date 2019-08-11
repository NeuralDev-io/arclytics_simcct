# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# users.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'David Matthews <@tree1004>']

__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.11'
"""users.py: 

TODO
"""

import os
from datetime import datetime

from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, jsonify, request, render_template
from flask import current_app as app
from flask_restful import Resource

from logger.arc_logger import AppLogger
from users_app.models import (User, AdminProfile)
from users_app.middleware import authenticate, authenticate_admin
from users_app.extensions import api
from users_app.token import (
    generate_confirmation_token, generate_url, confirm_token, URLTokenError,
    generate_promotion_confirmation_token
)

logger = AppLogger(__name__)

admin_blueprint = Blueprint('admin', __name__)


class AdminCreate(Resource):
    """Route for Admins to Create Admin."""

    method_decorators = {'post': [authenticate_admin]}

    def post(self, resp):
        """Make a user an administrator"""
        post_data = request.get_json()

        # Validating empty payload
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not post_data:
            return response, 400

        # Extract the request body data
        email = post_data.get('email', '')
        position = post_data.get('position', '')

        # Ensure email and position data was given
        if not email:
            response['message'] = 'No email provided.'
            return response, 400
        if not position:
            response['message'] = 'No position provided.'
            return response, 400

        # Verify it is actually a valid email
        try:
            # validate and get info
            v = validate_email(email)
            # replace with normalized form
            valid_email = v['email']
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            response['error'] = str(e)
            response['message'] = 'Invalid email.'
            return response, 400

        # Make sure the user exists in the database.
        if not User.objects(email=valid_email):
            response['message'] = 'User does not exist.'
            return response, 404

        # Get the user object and verify that it is verified and an admin
        user = User.objects.get(email=valid_email)
        if not user.verified:
            response['message'] = 'The user must verify their email.'
            return response, 401
        if user.is_admin:
            response['message'] = 'User is already an Administrator.'
            return response, 400

        # Get the admin object so we can email them a confirmation email.
        admin = User.objects.get(id=resp)

        # Start promotion
        user.admin_profile = AdminProfile(
            position=position,
            mobile_number=None,
            verified=False,
            promoted_by=admin.id
        )
        user.last_updated = datetime.utcnow()
        user.save()

        # Create a cancellation link for the promoter
        promotion_cancellation_token = generate_promotion_confirmation_token(
            admin.email, user.email
        )
        promotion_cancellation_url = generate_url(
            'admin.cancel_promotion', promotion_cancellation_token
        )

        from celery_runner import celery
        celery.send_task(
            'tasks.send_email',
            kwargs={
                'to': [admin.email],
                'subject_suffix':
                'You Promoted a User!',
                'html_template':
                render_template(
                    'cancel_promotion.html',
                    promotion_cancellation_url=promotion_cancellation_url,
                    email=admin.email,
                    position=position,
                    admin_name=f'{admin.first_name} {admin.last_name}',
                    user_name=f'{user.first_name} {user.last_name}'
                ),
                'text_template':
                render_template(
                    'cancel_promotion.txt',
                    promotion_cancellation_url=promotion_cancellation_url,
                    email=admin.email,
                    position=position,
                    admin_name=f'{admin.first_name} {admin.last_name}',
                    user_name=f'{user.first_name} {user.last_name}'
                )
            }
        )

        # Create a verification link for the user being promoted
        promotion_verification_token = generate_confirmation_token(user.email)
        promotion_verification_url = generate_url(
            'admin.verify_promotion', promotion_verification_token
        )

        celery.send_task(
            'tasks.send_email',
            kwargs={
                'to': [user.email],
                'subject_suffix':
                'Acknowledge Promotion',
                'html_template':
                render_template(
                    'acknowledge_promotion.html',
                    promotion_verification_url=promotion_verification_url,
                    email=user.email,
                    position=position,
                    user_name=(f'{user.first_name} {user.last_name}')
                ),
                'text_template':
                render_template(
                    'acknowledge_promotion.html',
                    promotion_verification_url=promotion_verification_url,
                    email=user.email,
                    position=position,
                    user_name=(f'{user.first_name} {user.last_name}')
                )
            }
        )

        response['status'] = 'success'
        response.pop('message')
        return response, 202


@admin_blueprint.route('/admin/create/cancel/<token>', methods=['GET'])
def cancel_promotion(token):
    """
    Allow an admin to cancel their promotion of another user
    """

    response = {'status': 'fail', 'message': 'Invalid token.'}

    # Decode the token from the email to confirm it was the right one
    try:
        # The token was encoded with the admin and user email as a list so
        # we want a list back of emails.
        email_list = confirm_token(token)
    except URLTokenError as e:
        response['error'] = str(e)
        return jsonify(response), 400
    except Exception as e:
        response['error'] = str(e)
        return jsonify(response), 400

    # If a list is not returned, we should get out of here.
    if not isinstance(email_list, list):
        response['message'] = 'Invalid Token.'
        return jsonify(response), 400

    # Ensure both admin and user email is present in list
    if not len(email_list) == 2:
        response['message'] = 'Invalid data in Token.'
        return jsonify(response), 400

    # Let's just be sure that we don't go out of index range
    try:
        admin_email = email_list[0]
        user_email = email_list[1]
    except IndexError as e:
        response['message'] = 'Invalid list from token.'
        response['error'] = str(e)
        return jsonify(response), 400

    if not admin_email or not user_email:
        response['message'] = 'Missing information in Token.'
        return jsonify(response), 400

    # Ensure both users exist in the database
    if not User.objects(email=admin_email):
        response['message'] = 'Administrator does not exist.'
        return jsonify(response), 400
    if not User.objects(email=user_email):
        response['message'] = 'Target User does not exist.'
        return jsonify(response), 400

    # Get Admin user object
    admin_user = User.objects.get(email=admin_email)

    # Ensure the admin user is allowed to promote other users.
    if not admin_user.is_admin or not admin_user.admin_profile.verified:
        response['message'] = 'User is not authorised to promote other users.'
        return jsonify(response), 401

    # Get target user object
    target_user = User.objects.get(email=user_email)

    target_user.disabled_admin = True
    target_user.admin_profile = None
    target_user.save()

    # TODO(davidmatthews1004@gmail.com): Ensure the link can be dynamic.
    client_host = os.environ.get('CLIENT_HOST')
    # We can make our own redirect response by doing the following
    custom_redir_response = app.response_class(
        status=302, mimetype='application/json'
    )
    # TODO(davidmatthews1004@gmail.com): Redirect the Admin somewhere else,
    #  maybe the home screen or a confirmation page.
    redirect_url = 'http://localhost:3000/signin'
    custom_redir_response.headers['Location'] = redirect_url
    return custom_redir_response


@admin_blueprint.route('/admin/create/verify/<token>', methods=['GET'])
def verify_promotion(token):
    """
    Allow a user to acknowledge their promotion and in doing so verify their
    status as an admin
    """

    response = {'status': 'fail', 'message': 'Invalid token.'}

    # Decode the token from the email to confirm it was the right one
    try:
        email = confirm_token(token)
    except URLTokenError as e:
        response['error'] = str(e)
        return jsonify(response), 400
    except Exception as e:
        response['error'] = str(e)
        return jsonify(response), 400

    # Ensure the user exists in the database
    if not User.objects(email=email):
        response['message'] = 'User does not exist.'
        return jsonify(response), 400

    # Get the user object
    user = User.objects.get(email=email)

    # Ensure the user is verified, an admin and that they have a valid admin
    # profile
    if not user.verified:
        response['message'] = 'User is not verified.'
        return jsonify(response), 400
    if not user.is_admin:
        response['message'] = 'User is not an Admin.'
        return jsonify(response), 400
    if user.disable_admin:
        response['message'] = 'User is not an Admin.'
        return jsonify(response), 400

    # Verify user's admin status
    user.admin_profile.verified = True
    user.save()

    # Get promoter information so that they can be sent an email letting them
    # know that the user they promoted has been verified.
    promoter_id = user.admin_profile.promoted_by
    promoter = User.objects.get(id=promoter_id)

    from celery_runner import celery
    celery.send_task(
        'tasks.send_email',
        kwargs={
            'to': [promoter.email],
            'subject_suffix':
            'Promotion Verified',
            'html_template':
            render_template(
                'promotion_verified.html',
                email=promoter.email,
                promoter_name=(f'{promoter.first_name} {promoter.last_name}'),
                user_name=(f'{user.first_name} {user.last_name}')
            ),
            'text_template':
            render_template(
                'promotion_verified.txt',
                email=promoter.email,
                promoter_name=(f'{promoter.first_name} {promoter.last_name}'),
                user_name=(f'{user.first_name} {user.last_name}')
            )
        }
    )

    # TODO(davidmatthews1004@gmail.com): Ensure the link can be dynamic.
    client_host = os.environ.get('CLIENT_HOST')
    # We can make our own redirect response by doing the following
    custom_redir_response = app.response_class(
        status=302, mimetype='application/json'
    )
    redirect_url = f'http://localhost:3000/signin'
    custom_redir_response.headers['Location'] = redirect_url
    # Additionally, if we need to, we can attach the JWT token in the header
    # custom_redir_response.headers['Authorization'] = f'Bearer {jwt_token}'
    return custom_redir_response


class DisableAccount(Resource):
    """Route for Admins to disable user accounts"""

    method_decorators = {'put': [authenticate_admin]}

    def put(self, resp):
        post_data = request.get_json()

        # Validating empty payload
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not post_data:
            return response, 400

        # Extract the request body data
        email = post_data.get('email', None)

        if not email:
            response['message'] = 'No email provided.'
            return response, 400

        # Verify it is actually a valid email
        try:
            # validate and get info
            v = validate_email(email)
            # replace with normalized form
            valid_email = v['email']
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            response['error'] = str(e)
            response['message'] = 'Invalid email.'
            return response, 400

        # Validation checks
        if not User.objects(email=valid_email):
            response['message'] = 'User does not exist.'
            return response, 404

        user = User.objects.get(email=valid_email)
        user.active = False
        user.last_updated = datetime.utcnow()
        user.save()

        response['status'] = 'success'
        response['message'] = (
            f'The account for User {user.email} has been '
            f'disabled.'
        )
        return response, 200


api.add_resource(AdminCreate, '/admin/create')
api.add_resource(DisableAccount, '/user/disable')
