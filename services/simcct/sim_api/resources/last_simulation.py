# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# last_simulation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.08.11'
"""last_simulation.py: 

This module defines the Resource for saving and retrieving a user's last 
simulation they ran with all the configurations, alloy, and results if it was
successfully simulated.
"""

from flask import request, Blueprint, json
from flask_restful import Resource
from mongoengine import ValidationError, FieldDoesNotExist

from sim_api.extensions import api
from sim_api.middleware import authenticate
from sim_api.models import Configuration, AlloyStore, User
from sim_api.extensions.utilities import (
    ElementInvalid, ElementSymbolInvalid, MissingElementError,
    DuplicateElementError
)

last_sim_blueprint = Blueprint('user_last_simulation', __name__)


class LastSimulation(Resource):

    method_decorators = {'post': [authenticate], 'get': [authenticate]}

    # noinspection PyMethodMayBeStatic
    def post(self, user_id):
        """Exposes the POST method to save the last configurations and alloy
        storage to the `sim_api.models.User` document in the fields
        `last_configurations` and `last_alloy_store`.

        Args:
            user_id: a valid user_id verified and passed by the
                     `sim_api.middleware.authenticate` method.

        Returns:
            A HTTP Flask Restful Response.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()

        # First we validate the request data
        if not post_data:
            return response, 400

        post_configs = post_data.get('configurations', None)
        post_alloy_store = post_data.get('alloy_store', None)

        if not post_configs:
            response['message'] = 'Missing Configurations in payload.'
            return response, 400

        if not post_alloy_store:
            response['message'] = 'Missing Alloy Store in payload.'
            return response, 400

        # TODO(andrew@neuraldev.io): Add the graphs also\
        # The following `mongoengine.EmbeddedDocument` models have in-built
        # custom validation that will be passed down.
        try:
            valid_configs = Configuration.from_json(json.dumps(post_configs))
            valid_configs.validate(clean=True)
            valid_store = AlloyStore.from_json(json.dumps(post_alloy_store))
            valid_store.validate(clean=True)
        except FieldDoesNotExist as e:
            # In case the request has fields we do not expect.
            response['error'] = str(e)
            response['message'] = 'Field does not exist error.'
            return response, 400
        except ElementSymbolInvalid as e:
            # Where the symbol used for the element is not valid meaning it
            # does not exist in a Periodic Table.
            response['error'] = str(e)
            response['message'] = 'Invalid element symbol error.'
            return response, 400
        except ElementInvalid as e:
            # If no "symbol" or "weight" passed as an Element object.
            response['error'] = str(e)
            response['message'] = 'Invalid element error.'
            return response, 400
        except MissingElementError as e:
            # Where the alloy is missing elements we expect to always be
            # available as they are required downstream in the algorithm.
            response['error'] = str(e)
            response['message'] = 'Missing element error.'
            return response, 400
        except DuplicateElementError as e:
            # One of the alloys contains two or more elements with the same
            # chemical symbol.
            response['error'] = str(e)
            response['message'] = 'Alloy contains a duplicate element.'
            return response, 400
        except ValidationError as e:
            # All other validation errors
            response['error'] = str(e)
            response['message'] = 'Model schema validation error.'
            return response, 400

        # Passing all the validations built into the models so we can save
        user = User.objects.get(id=user_id)
        user.last_configuration = valid_configs
        user.last_alloy_store = valid_store
        # TODO(andrew@neuraldev.io): Add the last_results
        user.save()

        response['status'] = 'success'
        response['message'] = 'Saved Alloy Store, Configurations and Results.'
        response['data'] = {
            'last_configuration': user.last_configuration.to_dict(),
            'last_alloy_store': user.last_alloy_store.to_dict()
        }
        return response, 201

    # noinspection PyMethodMayBeStatic
    def get(self, user_id):
        """Exposes the GET method to get the last configurations and alloy
        storage from the `sim_api.models.User` document.

        Args:
            user_id: a valid user_id verified and passed by the
                     `sim_api.middleware.authenticate` method.

        Returns:
            A HTTP Flask Restful Response.
        """
        response = {'status': 'fail'}

        user = User.objects.get(id=user_id)

        # We need to check there's something to return first.
        if not user.last_configuration:
            response['message'] = 'User does not have a last configurations.'
            return response, 404

        if not user.last_alloy_store:
            response['message'] = 'User does not have a last alloy stored.'
            return response, 404

        # TODO(andrew@neuraldev.io): Add the last_results also

        response['status'] = 'success'
        response['data'] = {
            'last_configurations': user.last_configuration.to_dict(),
            'last_alloy_store': user.last_alloy_store.to_dict(),
        }
        return response, 200


api.add_resource(LastSimulation, '/api/v1/sim/user/last/simulation')
