# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# user_alloys.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.08.02'
"""user_alloys.py: 

This module defines the CRUD methods to save an Embedded Document List of an
Alloy on the User's Document. 
"""

from typing import Tuple

from bson import ObjectId
from flask import Blueprint, request
from flask_restful import Resource
from mongoengine import ValidationError
from mongoengine.errors import (
    DoesNotExist, FieldDoesNotExist, MultipleObjectsReturned
)

from arc_logging import AppLogger
from sim_api.extensions import api, apm
from sim_api.extensions.utilities import (
    DuplicateElementError, ElementInvalid, ElementSymbolInvalid,
    MissingElementError
)
from sim_api.middleware import authenticate_user_cookie_restful
from sim_api.models import Alloy, User
from sim_api.routes import Routes

user_alloys_blueprint = Blueprint('user_alloys', __name__)
logger = AppLogger(__name__)


class UserAlloysList(Resource):
    """The resource for endpoints to get an Alloy list and create an alloy
    to the User's database.
    """

    method_decorators = {
        'get': [authenticate_user_cookie_restful],
        'post': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def post(self, user) -> Tuple[dict, int]:
        """The endpoint that exposes a POST HTTP method to create an alloy in
        the User's document.

        Args:
            user: a valid `sim_api.models.User` passed from the middleware.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """

        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()

        if not post_data:
            return response, 400

        # We need to pass the `mongoengine` library a kwargs so we need to
        # validate the data request has been successfully converted to a dict
        if not isinstance(post_data, dict):
            return response, 400

        alloy_name = post_data.get('name', None)
        alloy_comp = post_data.get('compositions', None)

        if not alloy_name:
            response['message'] = 'Name must be provided.'
            return response, 400

        if not alloy_comp or not isinstance(alloy_comp, list):
            response['message'] = (
                'Compositions must be provided as a list of valid elements e.g.'
                ' {"symbol": "C", "weight": 1.0}'
            )
            return response, 400

        try:
            Alloy(name=alloy_name, compositions=alloy_comp).validate()
        except FieldDoesNotExist as e:
            response['error'] = str(e)
            response['message'] = 'Field does not exist error.'
            log_message = {'message': response['message'], 'error': str(e)}
            logger.exception(log_message)
            apm.capture_exception()
            return response, 400
        except ElementSymbolInvalid as e:
            # This validation is a custom one used to validate the symbol used
            # in the element is one that is valid with the Periodic Table.
            response['error'] = str(e)
            response['message'] = 'Invalid element symbol error.'
            log_message = {'message': response['message'], 'error': str(e)}
            logger.exception(log_message)
            apm.capture_exception()
            return response, 400
        except ElementInvalid as e:
            # This validation is a custom one used to validate the Element used
            response['error'] = str(e)
            response['message'] = 'Invalid element error.'
            log_message = {'message': response['message'], 'error': str(e)}
            logger.exception(log_message)
            apm.capture_exception()
            return response, 400
        except MissingElementError as e:
            # This validation is a custom one used to validate missing Elements
            response['error'] = str(e)
            response['message'] = 'Missing element error.'
            log_message = {'message': response['message'], 'error': str(e)}
            logger.exception(log_message)
            apm.capture_exception()
            return response, 400
        except DuplicateElementError as e:
            # One of the alloys contains two or more elements with the same
            # chemical symbol.
            response['error'] = str(e)
            response['message'] = 'Alloy contains a duplicate element.'
            log_message = {'message': response['message'], 'error': str(e)}
            logger.exception(log_message)
            apm.capture_exception()
            return response, 400
        except ValidationError as e:
            response['error'] = str(e.message)
            response['message'] = 'Alloy validation error.'
            log_message = {'message': response['message'], 'error': str(e)}
            logger.exception(log_message)
            apm.capture_exception()
            return response, 400

        valid_data = {
            'name': post_data.pop('name'),
            'compositions': post_data.pop('compositions')
        }

        alloy = user.saved_alloys.create(**valid_data)
        user.save()

        response['status'] = 'success'
        response['data'] = alloy.to_dict()
        response.pop('message')
        return response, 201

    # noinspection PyMethodMayBeStatic
    def get(self, user) -> Tuple[dict, int]:
        """The endpoint that exposes a GET HTTP method to retrieve a list of
        alloys on the User's document.

        Args:
            user: a valid `sim_api.models.User` passed from the middleware.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """
        # To avoid running a list comprehension loop, if there's nothing
        # to return we get out of here and notify the client.
        if user.saved_alloys.count() == 0:
            return {'status': 'fail', 'message': 'No alloys found.'}, 404

        # Mongo by default returns a Cursor which we must convert to dict
        alloy_list = [obj.to_dict() for obj in user.saved_alloys]
        return {'status': 'success', 'data': alloy_list}, 200


class UserAlloy(Resource):
    method_decorators = {
        'get': [authenticate_user_cookie_restful],
        'put': [authenticate_user_cookie_restful],
        'delete': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def get(self, user, alloy_id):
        """The endpoint that exposes a GET HTTP method to retrieve an alloy
        detail from the User's document.

        Args:
            user: a valid `sim_api.models.User` passed from the middleware.
            alloy_id: a valid Alloy ObjectId of the embedded document.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """
        response = {'status': 'fail', 'message': 'Invalid ObjectId.'}

        # Verify the request params is a valid ObjectId to use
        if not ObjectId.is_valid(alloy_id):
            return response, 400

        if user.saved_alloys.count() == 1:
            # If there is only one alloy to return.
            alloy = user.saved_alloys.first()
        else:
            try:
                alloy = user.saved_alloys.get(**{'oid': ObjectId(alloy_id)})
            except DoesNotExist as e:
                response['error'] = str(e)
                response['message'] = 'Alloy does not exist.'
                return response, 404
            except MultipleObjectsReturned as e:
                response['error'] = str(e)
                response['message'] = 'Multiple objects returned.'
                log_message = {'message': response['message'], 'error': str(e)}
                logger.exception(log_message)
                apm.capture_exception()
                return response, 418

        response = {'status': 'success', 'data': alloy.to_dict()}
        return response, 200

    # noinspection PyMethodMayBeStatic
    def put(self, user, alloy_id):
        """The endpoint that exposes a PUT HTTP method to update an alloy
        from the User's document.

        Args:
            user: a valid `sim_api.models.User` passed from the middleware.
            alloy_id: a valid Alloy ObjectId of the embedded document.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        put_data = request.get_json()

        if not put_data:
            return response, 400

        # Verify the request params is a valid ObjectId to use
        if not ObjectId.is_valid(alloy_id):
            response['message'] = 'Invalid ObjectId.'
            return response, 400

        put_name = put_data.get('name', None)
        put_comp = put_data.get('compositions', None)

        # If there are no keys in the request body that match what we want.
        if not put_name:
            response['message'] = 'Alloy name must be provided.'
            return response, 400

        if not put_comp:
            response['message'] = 'Alloy compositions list must be provided.'
            return response, 400

        if not isinstance(put_comp, list):
            response['message'] = (
                'Compositions must be provided as a list of valid elements e.g.'
                ' {"symbol": "C", "weight": 1.0}'
            )
            return response, 400

        try:
            new_alloy = Alloy(name=put_name, compositions=put_comp)
            new_alloy.validate(clean=True)
        except FieldDoesNotExist as e:
            response['error'] = str(e)
            response['message'] = 'Field does not exist error.'
            log_message = {'message': response['message'], 'error': str(e)}
            logger.exception(log_message)
            apm.capture_exception()
            return response, 400
        except ElementSymbolInvalid as e:
            # This validation is a custom one used to validate the symbol
            # in the element is one that is valid with the Periodic Table.
            response['error'] = str(e)
            response['message'] = 'Invalid element symbol error.'
            return response, 400
        except ElementInvalid as e:
            # This validation is a custom one used to validate the
            # Element used
            response['error'] = str(e)
            response['message'] = 'Invalid element error.'
            return response, 400
        except MissingElementError as e:
            # This validation is a custom one used to validate missing Elements
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
            response['error'] = str(e.message)
            response['message'] = 'Alloy validation error.'
            return response, 400

        if user.saved_alloys.count() == 0:
            response['message'] = 'No alloys found.'
            return response, 404

        # Now we do the real updating work
        updated = User.objects.filter(
            saved_alloys__oid=ObjectId(alloy_id)
        ).update_one(set__saved_alloys__S__name=put_name, upsert=False)

        if updated == 0:
            response['message'] = 'Alloy does not exist.'
            return response, 404

        updated = User.objects.filter(
            saved_alloys__oid=ObjectId(alloy_id)
        ).update_one(
            set__saved_alloys__S__compositions=put_comp, upsert=False
        )

        if updated == 0:
            response['message'] = 'Failed to update alloy.'
            logger.error(response['message'])
            apm.capture_message(response['message'])
            return response, 500

        try:
            user.save()
        except ValidationError as e:
            # We do this to ensure there isn't some error that occurs on saving
            # and if there is, then we return an internal server error.
            response['error'] = str(e.message)
            response['message'] = 'Validation error on saving.'
            apm.capture_exception()
            return response, 500

        user.reload()
        alloy = user.saved_alloys.get(**{'oid': ObjectId(alloy_id)})

        response['data'] = alloy.to_dict()
        response['status'] = 'success'
        response.pop('message')
        return response, 200

    # noinspection PyMethodMayBeStatic
    def patch(self, alloy_id):
        """The endpoint that exposes a PATCH HTTP method to partially update
        an alloy in the User's document.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """
        msg = (
            'Method Not Allowed. These are not the endpoints you are '
            'looking for.'
        )
        return {'message': msg}, 405

    # noinspection PyMethodMayBeStatic
    def delete(self, user, alloy_id):
        """The endpoint that exposes a DELETE HTTP method to delete an alloy
        from the User's document.

        Args:
            user: a valid `sim_api.models.User` passed from the middleware.
            alloy_id: a valid Alloy ObjectId of the embedded document.

        Returns:
            A valid HTTP Response with a dict and a HTTP status code.
        """
        response = {'status': 'fail', 'message': 'Invalid ObjectId.'}

        # Verify the request params is a valid ObjectId to use
        if not ObjectId.is_valid(alloy_id):
            return response, 400

        if user.saved_alloys.count() == 0:
            # If there is no alloy to delete.
            response['message'] = 'No alloy found.'
            logger.info(response['message'])
            apm.capture_message(response['message'])
            return response, 404

        # To ensure we delete the correct one, we must first find it. If
        # we can't find the correct alloy, we get out of here to avoid deleting
        # the wrong alloy.
        try:
            user.saved_alloys.get(**{'oid': ObjectId(alloy_id)})
        except DoesNotExist as e:
            response['error'] = str(e)
            response['message'] = 'Alloy does not exist.'
            return response, 404
        except MultipleObjectsReturned as e:
            response['error'] = str(e)
            response['message'] = 'Multiple objects returned.'
            log_message = {'message': response['message'], 'error': str(e)}
            logger.exception(log_message)
            apm.capture_exception()
            return response, 418

        # If we find the alloy above, we overwrite it by doing a $pull
        deleted = user.update(pull__saved_alloys__oid=ObjectId(alloy_id))
        user.save(force=True)

        # Just another validation check that it's been acted upon.
        if not deleted == 1:
            response['message'] = 'Failed to delete alloy.'
            return response, 400

        response.pop('message')
        response['status'] = 'success'
        return response, 202


api.add_resource(UserAlloysList, Routes.UserAlloysList.value)
api.add_resource(UserAlloy, Routes.UserAlloy.value)
