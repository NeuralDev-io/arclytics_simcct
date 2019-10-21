# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# last_simulation.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.2.0'
__status__ = 'production'
__date__ = '2019.08.11'
"""last_simulation.py: 

This module defines the Resource for saving and retrieving a user's last 
simulation they ran with all the configurations, alloy, and results if it was
successfully simulated or an invalid set of data if it not.
"""

from flask import Blueprint, request
from flask_restful import Resource
from marshmallow import ValidationError
from mongoengine import ValidationError as MEValidationError

from arc_logging import AppLogger
from sim_api.extensions import api, apm
from sim_api.extensions.utilities import (
    DuplicateElementError, ElementInvalid, ElementSymbolInvalid,
    MissingElementError, ElementWeightInvalid
)
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.routes import Routes
from sim_api.schemas import (
    ConfigurationsSchema, AlloyStoreSchema, SimulationResultsSchema
)

last_sim_blueprint = Blueprint('user_last_simulation', __name__)
logger = AppLogger(__name__)


class LastSimulation(Resource):
    """
    This Resource defines methods to POST and GET the long-term saved last
    set of Configurations, Alloys, and Results (if any) used by the User.
    This allows the client front-end to load this data on login or set it
    on logout.

    Note that an invalid set of configurations and alloys returned must first
    be validated by the front-end before we can run simulation on it.
    """
    method_decorators = {
        'post': [authenticate_user_cookie_restful],
        'get': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def post(self, user):
        """Exposes the POST method to save the last configurations and alloy
        storage to the `sim_api.models.User` document in the appropriate fields
        for each of these.

        Args:
            user: a valid `models.User` object verified and passed by the
            `sim_api.middleware.authenticate` method.

        Returns:
            A HTTP Flask Restful Response.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()
        # First we validate the request data
        if not post_data:
            return response, 400

        is_valid = post_data.get('is_valid', None)
        post_invalid_fields = post_data.get('invalid_fields', None)
        post_configs = post_data.get('configurations', None)
        post_alloy_store = post_data.get('alloy_store', None)
        post_results = post_data.get('simulation_results', None)

        # We enforce the client tells us this last set of configurations and
        # alloys are either valid or not so that we can save appropriately.
        if is_valid is None:
            response['message'] = 'Validity must be defined.'
            return response, 400

        if (
            not post_configs and not post_alloy_store and not post_results
            and not post_invalid_fields
        ):
            return response, 400

        # ===== # Saving of Invalid Configurations/Alloy # ===== #
        # If the client says that the data is not valid, we simply save
        # it as a dictionary whatever it is.
        if not is_valid:
            # Save everything that we're given which has no validation since
            # `models.User` is using `mongoengine.DictField` for all these.
            if post_configs:
                user.last_configuration = post_configs
                user.last_configuration['is_valid'] = is_valid
            else:
                user.last_configuration = {}
            user.last_alloy_store = post_alloy_store if post_alloy_store else {}
            user.last_simulation_results = post_results if post_results else {}
            user.last_simulation_invalid_fields = (
                post_invalid_fields if post_invalid_fields else {}
            )

            try:
                user.save()
            except MEValidationError as e:
                # This is just to check that our schema validation matches
                # everything expected with Mongoengine, however, this is
                # strictly to fail gracefully as the mongoengine model uses
                # `mongoengine.DictField` which has no requirement for
                # validation.
                response['message'] = 'Mongoengine Validation error.'
                logger.exception(
                    {
                        'error': e.message,
                        'message': response['message']
                    }
                )
                apm.capture_exception()
                return response, 500

            # Update the final response dict with everything for a
            # successful POST method.
            response.update(
                {
                    'message': 'Saved Invalid Last Simulation Data.',
                    'data': {
                        'last_configuration': post_configs,
                        'last_alloy_store': post_alloy_store
                    },
                    'status': 'success'
                }
            )
            return response, 201

        # ===== # Validation of Valid Configurations/Alloy # ===== #
        valid_configs = None
        valid_store = None
        valid_results = None

        # At this point, we have been told by the client that the data is
        # valid so we do our own internal validity check and deserialize
        # everything to a Python Dict
        try:
            if post_configs:
                valid_configs = ConfigurationsSchema().load(post_configs)

                if valid_results or is_valid:
                    # If we're told that the configurations are valid or they
                    # have a set of results, we set that in our storage of the
                    # data.
                    # Note: a set of results means the data is valid for a
                    # simulation # run so therefore it is valid in that sense.
                    valid_configs['is_valid'] = is_valid
            if post_alloy_store:
                valid_store = AlloyStoreSchema().load(post_alloy_store)
            if post_results:
                valid_results = SimulationResultsSchema().load(post_results)
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
        except ElementWeightInvalid as e:
            # If no "symbol" or "weight" passed as an Element object.
            response['error'] = str(e)
            response['message'] = 'Invalid element weight error.'
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
            response['error'] = str(e.messages)
            response['message'] = 'Model schema validation error.'
            apm.capture_exception()
            return response, 400

        # Response data to send back.
        data = {}
        # Passing all the validations built into the models so we can save
        if post_configs and valid_configs:
            user.last_configuration = valid_configs
            data.update({'last_configuration': valid_configs})
        else:
            user.last_configuration = {}

        if post_alloy_store and valid_store:
            user.last_alloy_store = valid_store
            data.update({'last_alloy_store': valid_configs})
        else:
            user.last_alloy_store = {}

        if post_results and valid_results:
            user.last_simulation_results = valid_results
            data.update({'last_simulation_results': valid_results})
        else:
            user.last_simulation_results = {}

        if post_invalid_fields:
            user.last_simulation_invalid_fields = post_invalid_fields
            data.update(
                {'last_simulation_invalid_fields': post_invalid_fields}
            )
        else:
            user.last_simulation_invalid_fields = {}

        try:
            user.save()
        except MEValidationError as e:
            # This is just to check that our schema validation matches
            # everything expected with Mongoengine, however, this is strictly
            # to fail gracefully as the mongoengine model uses
            # `mongoengine.DictField` which has no requirement for validation.
            response['message'] = 'Mongoengine Validation error.'
            logger.exception(
                {
                    'error': e.message,
                    'message': response['message']
                }
            )
            apm.capture_exception()
            return response, 500

        # Update the final response dict with everything for a successful
        # POST method.
        response.update(
            {
                'message': 'Saved Last Simulation Data.',
                'data': data,
                'status': 'success'
            }
        )
        return response, 201

    # noinspection PyMethodMayBeStatic
    def get(self, user):
        """Exposes the GET method to get the last configurations and alloy
        storage from the `sim_api.models.User` document.

        Args:
            user: a valid `models.User` object verified and passed by the
            `sim_api.middleware.authenticate` method.

        Returns:
            A HTTP Flask Restful Response.
        """
        response = {'status': 'fail'}

        # Note:
        # If the user has no last configurations, we ensure that we use
        # the default one rather than set it to None.
        # This is an agreement with frontend and they will update each
        # individual configuration as the user fixes it.
        # In this case, we can just return and let the frontend know that
        # nothing in the session state has changed for the user.
        if not user.last_configuration and not user.last_alloy_store:
            response['message'] = (
                'User does not have a last configurations or alloy store.'
            )
            return response, 404

        # At this point, we know the user has at least some last configuration
        # or alloy store saved and we need to update the session state with
        # those values. Because on login, the default values are already set,
        # to ensure that we stay in sync, we only set the session store with
        # the dictionary where the user has something stored from the past.

        # Build up our response data as we go.
        data = {}

        if user.last_configuration:
            is_valid = user.last_configuration['is_valid']
            data.update(
                {
                    'last_configuration': user.last_configuration,
                    'is_valid': is_valid
                }
            )

        if user.last_alloy_store:
            data.update({'last_alloy_store': user.last_alloy_store})

        if user.last_simulation_results:
            data.update(
                {'last_simulation_results': user.last_simulation_results}
            )

        if user.last_simulation_invalid_fields:
            data.update(
                {
                    'last_simulation_invalid_fields':
                    user.last_simulation_invalid_fields
                }
            )

        response.update({'status': 'success', 'data': data})
        return response, 200


api.add_resource(LastSimulation, Routes.LastSimulation.value)
