# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# users.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004']

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
    ElementSymbolInvalid, ElementInvalid, MissingElementError
)

logger = AppLogger(__name__)

share_blueprint = Blueprint('share', __name__)


class ShareSimulationLink(Resource):
    """
    Allow a user to generate a link that can be used to share configurations.
    """

    method_decorators = {'post': [authenticate]}

    def post(self, resp) -> Tuple[dict, int]:
        # Get post data
        data = request.get_json()

        #json .dumps and then make mongo obj using from json

        # Ensure payload is not empty
        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not data:
            return response, 400

        # Extract the data
        owner = User.objects.get(id=resp)
        shared_date = datetime.utcnow()
        configuration = data.get('configuration', None)
        alloy_store = data.get('alloy_store', None)

        # Validate the request simulate data using the database model and
        # validate method
        try:
            # Create a Configuration object and an Alloy Store object from the
            # values in the request
            config_object = Configuration(**configuration)
            alloy_store_object = AlloyStore(**alloy_store)
            shared_simulation_object = SharedSimulation(
                owner_email=owner.email,
                created_date=shared_date,
                configuration=config_object,
                alloy_store=alloy_store_object
            )
            shared_simulation_object.save()
        except KeyError as e:
            response['errors'] = str(e)
            response['message'] = 'Key error.'
            return response, 400
        except ValidationError as e:
            response['errors'] = str(e)
            response['message'] = 'Validation error.'
            return response, 400
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
    and send that link out to a list of email addresses.
    """

    method_decorators = {'post': [authenticate]}

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

        # Get the email address (string) or list of email addresses (list) from
        # the response and validate them.
        email_list = data.get('email_list', None)
        if not email_list:
            response['message'] = 'No email addresses provided.'
            return response, 400
        valid_email_list = []
        if isinstance(email_list, list):
            for email in email_list:
                try:
                    # validate and get info
                    v = validate_email(email)
                    # replace with normalized form
                    valid_email_list.append(v['email'])
                except EmailNotValidError as e:
                    # email is not valid, exception message is human-readable
                    response['error'] = str(e)
                    response['message'] = 'Invalid email.'
                    return response, 400
        elif isinstance(email_list, str):
            try:
                # validate and get info
                v = validate_email(email_list)
                # replace with normalized form
                valid_email_list.append(v['email'])
            except EmailNotValidError as e:
                # email is not valid, exception message is human-readable
                response['error'] = str(e)
                response['message'] = 'Invalid email.'
                return response, 400
        else:
            response['message'] = 'Invalid email address type.'
            return response, 400

        configuration = data.get('configuration', None)
        alloy_store = data.get('alloy_store', None)

        # Validate the request simulate data using the database model and
        # validate method
        try:
            # Create a Configuration object and an Alloy Store object from the
            # values in the request
            config_object = Configuration(**configuration)
            alloy_store_object = AlloyStore(**alloy_store)
            shared_simulation_object = SharedSimulation(
                owner_email=owner.email,
                created_date=shared_date,
                configuration=config_object,
                alloy_store=alloy_store_object
            )
            shared_simulation_object.save()
        except KeyError as e:
            response['errors'] = str(e)
            response['message'] = 'Key error.'
            return response, 400
        except ValidationError as e:
            response['errors'] = str(e)
            response['message'] = 'Validation error.'
            return response, 400
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

        simulation_token = generate_shared_simulation_token(
            str(shared_simulation_object.id)
        )
        simulation_url = generate_url(
            'share.request_shared_simulation', simulation_token
        )

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
                    owner_name=(f'{owner.first_name} {owner.last_name}'),
                    config_url=simulation_url
                ),
                'text_template':
                render_template(
                    'share_configuration.txt',
                    email=valid_email_list,
                    owner_name=(f'{owner.first_name} {owner.last_name}'),
                    config_url=simulation_url
                ),
            }
        )
        # else:
        #     for email in valid_email_list:
        #         celery.send_task(
        #             'tasks.send_email',
        #             kwargs={
        #                 'to': [email],
        #                 'subject_suffix':
        #                 f'{owner.first_name} {owner.last_name} '
        #                 'has shared a configuration with you!',
        #                 'html_template':
        #                 render_template(
        #                     'share_configuration.html',
        #                     email=valid_email_list,
        #                     owner_name=(
        #                         f'{owner.first_name} {owner.last_name}'
        #                     ),
        #                     config_url=simulation_url
        #                 ),
        #                 'text_template':
        #                 render_template(
        #                     'share_configuration.txt',
        #                     email=valid_email_list,
        #                     owner_name=(
        #                         f'{owner.first_name} {owner.last_name}'
        #                     ),
        #                     config_url=simulation_url
        #                 ),
        #             }
        #         )

        response['status'] = 'success'
        response['message'] = 'Email(s) sent.'
        return response, 201


@share_blueprint.route(
    '/users/share/simulation/request/<token>', methods=['GET']
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


@share_blueprint.route('/users/share/simulation/view/<token>', methods=['GET'])
def view_shared_simulation(token):
    """
    After we have established a client to communicate with, we can send the
    shared data to the client
    """

    # Ensure payload is not empty
    response = {'status': 'fail', 'message': 'Invalid payload.'}
    # if not data:
    #     return jsonify(response), 400

    # Extract the data
    if not token:
        response['message'] = 'Signature not provided.'
        return jsonify(response), 400

    try:
        sim_id = confirm_simulation_token(token)
    except URLTokenError as e:
        response['error'] = str(e)
        response['message'] = 'Invalid token.'
        return jsonify(response), 400

    if not SharedSimulation.objects(id=sim_id):
        response['message'] = 'Simulation does not exist.'
        return jsonify(response), 404

    shared_simulation = SharedSimulation.objects.get(id=sim_id)
    data = shared_simulation.to_dict()

    response['status'] = 'success'
    response.pop('message')
    response['data'] = data
    return jsonify(response), 200


api.add_resource(ShareSimulationLink, '/user/share/simulation/link')
api.add_resource(ShareSimulationEmail, '/user/share/simulation/email')
