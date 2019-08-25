# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# users.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>']

__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'David Matthews'
__email__ = 'davidmatthews1004@gmail.com'
__status__ = 'development'
__date__ = '2019.08.11'
"""share.py: 

This file defines all the API resource routes and controller definitions for 
Sharing endpoints using the Flask Resource inheritance model.
"""

import os
from datetime import datetime

from typing import Tuple

from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, jsonify, request, render_template
from flask import current_app as app
from flask_restful import Resource
from mongoengine.errors import ValidationError

from logger.arc_logger import AppLogger
from users_app.models import (
    User, Configuration, SharedSimulation, AlloyStore
)
from users_app.middleware import authenticate
from users_app.extensions import api
from users_app.token import (
    URLTokenError, generate_shared_simulation_token, generate_url,
    confirm_simulation_token
)
from users_app.utilities import (
    ElementSymbolInvalid, ElementInvalid, MissingElementError,
    DuplicateElementError
)

logger = AppLogger(__name__)

share_blueprint = Blueprint('share', __name__)


class ShareSimulationLink(Resource):
    """
    Allow a user to generate a link that can be used to share configurations.
    """

    method_decorators = {'post': [authenticate]}

    # noinspection PyMethodMayBeStatic
    def post(self, resp) -> Tuple[dict, int]:
        # Get post data
        data = request.get_json()

        # Ensure payload is not empty
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not data:
            return response, 400

        # Extract the data
        owner = User.objects.get(id=resp)
        shared_date = datetime.utcnow()
        configuration = data.get('configurations', None)
        alloy_store = data.get('alloy_store', None)

        if not configuration or not alloy_store:
            response['message'] = 'Configurations or Alloy Store not sent.'
            return response, 400

        # Validate the request simulation data. Validation is done by the
        # clean() methods for each object/document in users_app/models.py.
        try:
            config_object = Configuration(**configuration)
            config_object.validate(clean=True)
            alloy_store_object = AlloyStore(**alloy_store)
            alloy_store_object.validate(clean=True)
            shared_simulation_object = SharedSimulation(
                owner_email=owner.email,
                created_date=shared_date,
                configuration=config_object,
                alloy_store=alloy_store_object
            )
            shared_simulation_object.save()
        except ElementSymbolInvalid as e:
            response['errors'] = str(e)
            response['message'] = 'Element Symbol Invalid.'
            return response, 400
        except ElementInvalid as e:
            response['errors'] = str(e)
            response['message'] = 'Element Invalid.'
            return response, 400
        except MissingElementError as e:
            response['errors'] = str(e)
            response['message'] = 'Alloy is missing essential elements.'
            return response, 400
        except DuplicateElementError as e:
            response['errors'] = str(e)
            response['message'] = 'Alloy contains duplicate elements.'
            return response, 400
        except ValidationError as e:
            response['errors'] = str(e)
            response['message'] = 'Validation error.'
            return response, 400

        # Create a token that contains the ObjectId for the shared simulation
        # and put it in a link/url that can be sent back to the frontend.
        simulation_token = generate_shared_simulation_token(
            str(shared_simulation_object.id)
        )
        simulation_url = generate_url(
            'share.request_shared_simulation', simulation_token
        )

        response['status'] = 'success'
        response.pop('message')
        response['link'] = simulation_url
        return response, 201


class ShareSimulationEmail(Resource):
    """
    Allow a user to generate a link that can be used to share configurations
    and send that link out to a list of email addresses provided.
    """

    method_decorators = {'post': [authenticate]}

    # noinspection PyMethodMayBeStatic
    def post(self, resp) -> Tuple[dict, int]:
        # Get post data
        data = request.get_json()

        # Ensure payload is not empty
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not data:
            return response, 400

        # Extract the data
        owner = User.objects.get(id=resp)
        shared_date = datetime.utcnow()

        # Get the email address/addresses from the response and validate them.
        email_list = data.get('emails', None)
        if not email_list:
            response['message'] = 'No email addresses provided.'
            return response, 400
        if not isinstance(email_list, list):
            response['message'] = 'Invalid email address type.'
            return response, 400
        if not all(isinstance(email, str) for email in email_list):
            response['message'] = 'An email address is invalid in the list.'
            return response, 400

        valid_email_list = []
        if len(email_list) == 1:
            try:
                v = validate_email(email_list[0])
                valid_email_list.append(v['email'])
            except EmailNotValidError as e:
                response['error'] = str(e)
                response['message'] = 'Invalid email.'
                return response, 400
        else:
            for email in email_list:
                try:
                    v = validate_email(email)
                    valid_email_list.append(v['email'])
                except EmailNotValidError as e:
                    response['error'] = str(e)
                    response['message'] = 'Invalid email.'
                    return response, 400

        # Get the configuration and alloy_store information from the request so
        # we can attempt to make a SharedSimulation object out of it.
        configuration = data.get('configurations', None)
        alloy_store = data.get('alloy_store', None)

        if not configuration or not alloy_store:
            response['message'] = 'Configurations or Alloy Store not sent.'
            return response, 400

        # We also provide the user an opportunity to send an optional message
        optional_msg = data.get('message', None)
        if not optional_msg:
            optional_msg = ''

        # Validate the request simulation data. Validation is done by the
        # clean() methods for each object/document in users_app/models.py.
        try:
            config_object = Configuration(**configuration)
            config_object.validate(clean=True)
            alloy_store_object = AlloyStore(**alloy_store)
            alloy_store_object.validate(clean=True)
            shared_simulation_object = SharedSimulation(
                **{
                    'owner_email': owner.email,
                    'created_date': shared_date,
                    'configuration': config_object,
                    'alloy_store': alloy_store_object
                }
            )
            shared_simulation_object.save()
        except ElementSymbolInvalid as e:
            response['errors'] = str(e)
            response['message'] = 'Element Symbol Invalid.'
            return response, 400
        except ElementInvalid as e:
            response['errors'] = str(e)
            response['message'] = 'Element Invalid.'
            return response, 400
        except MissingElementError as e:
            response['errors'] = str(e)
            response['message'] = 'Alloy is missing essential elements.'
            return response, 400
        except DuplicateElementError as e:
            response['errors'] = str(e)
            response['message'] = 'Alloy contains duplicate elements.'
            return response, 400
        except ValidationError as e:
            response['errors'] = str(e)
            response['message'] = 'Validation error.'
            return response, 400

        # Create a token that contains the ObjectId for the shared simulation
        # and put it in a link/url that can be sent back to the frontend.
        simulation_token = generate_shared_simulation_token(
            str(shared_simulation_object.id)
        )
        simulation_url = generate_url(
            'share.request_shared_simulation', simulation_token
        )

        # Send email/emails to the email address/addresses provided in the
        # request with the link to the shared simulation.
        from celery_runner import celery
        # if isinstance(valid_email_list, str):
        celery.send_task(
            'tasks.send_email',
            kwargs={
                'to':
                valid_email_list,
                'subject_suffix':
                f'{owner.first_name} {owner.last_name} '
                'has shared a configuration with you!',
                'html_template':
                render_template(
                    'share_configuration.html',
                    email=valid_email_list,
                    owner_name=f'{owner.first_name} {owner.last_name}',
                    optional_message=optional_msg,
                    config_url=simulation_url
                ),
                'text_template':
                render_template(
                    'share_configuration.txt',
                    email=valid_email_list,
                    owner_name=f'{owner.first_name} {owner.last_name}',
                    optional_message=optional_msg,
                    config_url=simulation_url
                ),
            }
        )

        response['status'] = 'success'
        response['message'] = 'Email(s) sent.'
        response['link'] = simulation_url
        return response, 201


@share_blueprint.route(
    '/user/share/simulation/request/<token>', methods=['GET']
)
def request_shared_simulation(token):
    """
    When the user clicks on a link to view a shared configuration, we need to
    establish a client on their end so that we can send the configuration data
    to the user. The point of this endpoint is to redirect them to a blank page
    on the front end which will request the configuration data from the backend.
    """

    # TODO(davidmatthews1004@gmail.com): Ensure the link can be dynamic.
    client_host = os.environ.get('CLIENT_HOST')
    # We can make our own redirect response by doing the following
    custom_redir_response = app.response_class(
        status=302, mimetype='application/json'
    )
    # TODO(davidmatthews1004@gmail.com): Correct this endpoint and make sure I
    #  am correctly sending the signature.
    redirect_url = \
        f'http://{client_host}/share/simulation/request/token={token}'
    custom_redir_response.headers['Location'] = redirect_url
    return custom_redir_response


@share_blueprint.route('/user/share/simulation/view/<token>', methods=['GET'])
def view_shared_simulation(token):
    """
    Requests to this endpoint should be sent by the blank page described in
    request_shared_simulation() (above).
    After we have established a client to communicate with, we can send the
    shared data to the client.
    """

    response = {'status': 'fail', 'message': 'Invalid payload.'}

    # Extract the data
    # Comment to Andrew -- I'm not sure if this is even possible. I haven't been
    # able to get a test to trigger this condition. I have left it in just to be
    # safe.
    if not token:
        response['message'] = 'Token not provided.'
        return jsonify(response), 400

    # Try to decode the token and get the simulation id from it.
    try:
        sim_id = confirm_simulation_token(token)
    except URLTokenError as e:
        response['error'] = str(e)
        response['message'] = 'Invalid token.'
        return jsonify(response), 400

    # If the id decoded from the simulation does not exist, we must inform the
    # client. This could occur if a SharedSimulation document in the database
    # has been deleted since a link has been generated for it.
    if not SharedSimulation.objects(id=sim_id):
        response['message'] = 'Simulation does not exist.'
        return jsonify(response), 404

    # Using the do_dict() method for the SharedSimulation document in
    # users_app/models.py to put the sim data into the response body.
    shared_simulation = SharedSimulation.objects.get(id=sim_id)
    data = shared_simulation.to_dict()

    response['status'] = 'success'
    response.pop('message')
    response['data'] = data
    return jsonify(response), 200


api.add_resource(ShareSimulationLink, '/user/share/simulation/link')
api.add_resource(ShareSimulationEmail, '/user/share/simulation/email')