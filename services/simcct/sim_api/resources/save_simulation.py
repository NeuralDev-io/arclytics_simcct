# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# save_simulation.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.08.11'
"""save_simulation.py: 

This module defines the Resource for saving and retrieving a user's saved 
simulation to the their personal Document.
"""

from bson import ObjectId
from flask import Blueprint, json, request
from flask_restful import Resource
from mongoengine import DoesNotExist, FieldDoesNotExist, ValidationError

from arc_logging import AppLogger
from sim_api.extensions import api, apm
from sim_api.extensions.utilities import (
    DuplicateElementError, ElementInvalid, ElementSymbolInvalid,
    MissingElementError
)
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.models import (
    AlloyStore, Configuration, SavedSimulation, SimulationResults
)
from sim_api.routes import Routes

save_sim_blueprint = Blueprint('user_save_simulation', __name__)
logger = AppLogger(__name__)

# Note: An is_valid = False Configuration instance means it has not been run.


class SaveSimulationList(Resource):

    method_decorators = {
        'get': [authenticate_user_cookie_restful],
        'post': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def post(self, user):
        """The endpoint that exposes a POST HTTP method to created a saved
        simulation in the saved_simulation collection with reference to the
        `user_id` which is decoded from Authorization JWT by the middleware.

        Args:
            user: a valid `sim_api.models.User` passed from the middleware.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()

        if not post_data:
            return response, 400

        post_configs = post_data.get('configurations')
        post_alloy_store = post_data.get('alloy_store')
        post_results = post_data.get('simulation_results')

        # Valid the request body
        if not post_configs:
            response['message'] = 'Missing Configurations in payload.'
            return response, 400

        if not post_alloy_store:
            response['message'] = 'Missing Alloy Store in payload.'
            return response, 400

        saved_sim_inst = SavedSimulation(
            user=user,
            configurations=Configuration.from_json(json.dumps(post_configs)),
            alloy_store=AlloyStore.from_json(json.dumps(post_alloy_store)),
            simulation_results=SimulationResults.from_json(
                json.dumps(post_results)
            )
        )

        # The following `mongoengine.EmbeddedDocument` models have in-built
        # custom validation that will be passed down.
        try:
            saved_sim_inst.save()
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
            log_message = {'message': response['message'], 'error': str(e)}
            logger.exception(log_message)
            apm.capture_exception()
            return response, 400
        except OverflowError as e:
            response['error'] = str(e)
            response['message'] = 'Overflow error.'
            log_message = {'message': response['message'], 'error': str(e)}
            logger.exception(log_message)
            apm.capture_exception()
            return response, 500

        response.pop('message')
        response['status'] = 'success'
        response['data'] = saved_sim_inst.to_dict()
        return response, 201

    # noinspection PyMethodMayBeStatic
    def get(self, user):
        """The endpoint that exposes a GET HTTP method to retrieve a list of
        saved simulations with reference to the `user_id` passed in the params
        from the saved_simulation collection.

        Args:
            user: a valid `sim_api.models.User` object passed from middleware.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """

        # First we get the queryset via the in-built filter and exclude the
        # user reference which would return a user id.
        qs = SavedSimulation.objects(user=user.id).exclude('user')

        if qs.count() == 0:
            response = {
                'status': 'fail',
                'message': 'No saved simulations found.'
            }
            return response, 404

        # We convert it to a list because the custom to_dict() method in the
        # Document implementation provides a better date representation and to
        # also maintain consistency with other endpoints that return _id.
        saved_sim_list = [inst.to_dict() for inst in qs]
        return {'status': 'success', 'data': saved_sim_list}, 200


class SaveSimulationDetail(Resource):

    method_decorators = {
        'get': [authenticate_user_cookie_restful],
        'delete': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def get(self, _, sim_id):
        """The endpoint that exposes a GET HTTP method to retrieve a saved
        simulation detail from the saved_simulation collection.

        Args:
            _: a user ObjectId passed from the middleware not used.
            sim_id: a valid SavedSimulation ObjectId of the document.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """

        if not ObjectId.is_valid(sim_id):
            return {'status': 'fail', 'message': 'Invalid ObjectId.'}, 400

        try:
            qs = SavedSimulation.objects.get(id=sim_id)
        except DoesNotExist:
            return {'status': 'fail', 'message': 'Does not exist.'}, 404
        return {'status': 'success', 'data': qs.to_dict()}, 200

    # noinspection PyMethodMayBeStatic
    def delete(self, _, sim_id):
        """The endpoint that exposes a DELETE HTTP method to delete a saved
        simulation from the saved_simulation collection.

        Args:
            _: a user ObjectId passed from the middleware not used.
            sim_id: a valid SavedSimulation ObjectId of the document.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """
        if not ObjectId.is_valid(sim_id):
            return {'status': 'fail', 'message': 'Invalid ObjectId.'}, 400

        try:
            qs = SavedSimulation.objects.get(id=sim_id)
        except DoesNotExist:
            return {'status': 'fail', 'message': 'Does not exist.'}, 404

        qs.delete()
        return {'status': 'success'}, 202


api.add_resource(SaveSimulationList, Routes.save_simulation_list.value)
api.add_resource(SaveSimulationDetail, Routes.save_simulation_detail.value)
