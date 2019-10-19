# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# global_alloys.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
from sim_api.extensions.utilities import ElementWeightInvalid

__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.14'
"""global_alloys.py: 

This defines the resources and endpoints for Global Alloys CRUD operations.
"""

from bson import ObjectId
from flask import Blueprint, request
from flask_restful import Resource
from marshmallow import ValidationError

from arc_logging import AppLogger
from sim_api.extensions import api
from sim_api.extensions.utilities import (
    MissingElementError, ElementWeightInvalid, ElementInvalid,
    ElementSymbolInvalid, DuplicateElementError
)
from sim_api.middleware import (
    authenticate_user_cookie_restful, authorize_admin_cookie_restful
)
from sim_api.routes import Routes
from sim_api.schemas import AlloySchema

alloys_blueprint = Blueprint('alloys', __name__)
logger = AppLogger(__name__)


class AlloysList(Resource):
    """The resource of endpoints for retrieving an alloy list and creating in
    the global alloy database.
    """

    method_decorators = {
        'post': [authorize_admin_cookie_restful],
        'get': [authenticate_user_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def post(self, _):
        """Exposes the POST method for `/alloys` to allow creating an alloy.
        The request must also include a request body of data that will need to
        comply to the schema.

        Returns:
            A Response object as a dict and a status code as an int.
        """
        response = {'status': 'fail', 'message': 'Invalid payload.'}

        post_data = request.get_json()
        if not post_data:
            return response, 400

        post_comps = post_data.get('compositions', None)
        post_name = post_data.get('name', None)

        if not post_comps or not isinstance(post_comps, list):
            response['message'] = (
                'Compositions must be provided as a list of valid elements e.g.'
                ' {"symbol": "C", "weight": 1.0}'
            )
            return response, 400

        if not post_name:
            response['message'] = 'No alloy name was provided.'
            return response, 400

        # We validate it to make sure it's valid before we do any
        # conversions below with the compositions
        try:
            valid_data = AlloySchema().load(post_data)
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
            response['error'] = e.messages
            response['message'] = 'Request data failed schema validation.'
            return response, 400

        from sim_api.alloys_service import AlloysService
        id_or_error = AlloysService().create_alloy(valid_data)

        # create_alloy() will return a string on DuplicateKeyError meaning it
        # wasn't created.
        if isinstance(id_or_error, str):
            response['message'] = id_or_error
            return response, 412

        alloy = AlloysService().find_alloy(id_or_error)

        response['status'] = 'success'
        response['data'] = alloy
        response.pop('message')
        return response, 201

    # noinspection PyMethodMayBeStatic
    def get(self, _):
        """Exposes the GET method for `/alloys` to retrieve a list of alloys in
        the database.

        Args:
            _: unused User object returned from middleware.

        Returns:
            A Response object with a response dict and status code as int.
        """
        response = {'status': 'fail', 'message': 'Empty.'}

        from sim_api.alloys_service import AlloysService
        alloys = AlloysService().find_all_alloys()

        # No point returning data if there is none to return.
        if len(alloys) == 0:
            return response, 404

        response['data'] = alloys
        response['status'] = 'success'
        response.pop('message')
        return response, 200


class Alloys(Resource):
    """The resource of endpoints for retrieving an alloy detail, partial
    updating and deleting an alloy in the global database.
    """

    method_decorators = {
        'get': [authenticate_user_cookie_restful],
        'put': [authorize_admin_cookie_restful],
        'delete': [authorize_admin_cookie_restful]
    }

    # noinspection PyMethodMayBeStatic
    def get(self, _, alloy_id):
        """Allows the GET method with `/alloys/{id}` as an endpoint to get
        a single alloy from the database.

        Args:
            _: unused User object returned from middleware.
            alloy_id: A valid ObjectId string that will be checked.

        Returns:
            A Response object consisting of a dict and status code as an int.
        """
        response = {'status': 'fail', 'message': 'Invalid ObjectId.'}

        # Verify the request params is a valid ObjectId to use
        if not ObjectId.is_valid(alloy_id):
            return response, 400

        from sim_api.alloys_service import AlloysService
        alloy = AlloysService().find_alloy(ObjectId(alloy_id))

        # The service will return True or False based on successfully finding
        # an alloy.
        if not alloy:
            response['message'] = 'Alloy not found.'
            return response, 404

        response['status'] = 'success'
        response['data'] = alloy
        response.pop('message')
        return response, 200

    # noinspection PyMethodMayBeStatic
    def put(self, _, alloy_id):
        put_data = request.get_json()

        response = {'status': 'fail', 'message': 'Invalid payload.'}
        if not put_data:
            return response, 400

        # Verify the request params is a valid ObjectId to use
        if not ObjectId.is_valid(alloy_id):
            response['message'] = 'Invalid ObjectId.'
            return response, 400

        put_name = put_data.get('name', None)
        put_comp = put_data.get('compositions', None)

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

        # Just validate the input schema first before we do anything else which
        # will also validate the Elements symbol
        try:
            new_alloy = AlloySchema().load(put_data)
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
            response['error'] = e.messages
            response['message'] = 'Request data failed schema validation.'
            return response, 400

        from sim_api.alloys_service import AlloysService
        good = AlloysService().update_alloy(ObjectId(alloy_id), new_alloy)

        # The service will return True or False based on successfully updating
        # an alloy.
        if not good:
            response['message'] = 'Alloy not found.'
            return response, 404

        updated_alloy = AlloysService().find_alloy(ObjectId(alloy_id))

        response['status'] = 'success'
        response['data'] = updated_alloy
        response.pop('message')
        return response, 200

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def patch(self, alloy_id):
        """Exposes the PATCH method for `/alloys` to update an existing alloy by
        an admin to update the existing data.

        Args:
            alloy_id: A valid ObjectId string that will be checked that is
            not used.

        Returns:
            A Response object consisting of a dict and status code as an int.
        """
        msg = (
            'Method Not Allowed. These are not the endpoints you are '
            'looking for.'
        )
        return {'message': msg}, 405

        # patch_data = request.get_json()
        #
        # response = {'status': 'fail', 'message': 'Invalid payload.'}
        # if not patch_data:
        #     return response, 400
        #
        # # Verify the request params is a valid ObjectId to use
        # if not ObjectId.is_valid(alloy_id):
        #     response['message'] = 'Invalid ObjectId.'
        #     return response, 400
        #
        # patch_name = patch_data.get('name', None)
        # patch_comp = patch_data.get('compositions', None)
        #
        # if not patch_name and not patch_comp:
        #     response['message'] = (
        #         'No valid keys was provided for alloy '
        #         '(i.e. must be "name" or "compositions")'
        #     )
        #     return response, 400
        #
        # if patch_comp and not isinstance(patch_comp, list):
        #     response['message'] = (
        #         'Compositions must be provided as a list of valid elements '
        #         'e.g. {"symbol": "C", "weight": 1.0}'
        #     )
        #     return response, 400
        #
        # # Just validate the input schema first before we do anything else
        # # which will also validate the Elements symbol
        # try:
        #     AlloySchema().load(patch_data)
        # except ValidationError as e:
        #     response['message'] = 'Request data failed schema validation.'
        #     response['error'] = e.messages
        #     return response, 400
        #
        # # First we update the compositions of the existing alloy if any.
        # existing_alloy = AlloysService().find_alloy(ObjectId(alloy_id))
        #
        # if not existing_alloy:
        #     response['message'] = 'Alloy not found.'
        #     return response, 404
        #
        # if patch_comp:
        #     existing_comp = existing_alloy.get('compositions')
        #
        #     # Update the elements by search
        #     for el in patch_data.get('compositions'):
        #         exists = False
        #         for i, ex_el in enumerate(existing_comp):
        #             if ex_el['symbol'] == el['symbol']:
        #                 exists = True
        #                 existing_comp[i] = el
        #                 break
        #         if not exists:
        #             existing_comp.append(el)
        #
        # # update the name if a new one is provided
        # if patch_name and not patch_name == existing_alloy['name']:
        #     existing_alloy['name'] = patch_name
        #
        # # Ensure the newly saved alloy is valid
        # try:
        #     # Must remove ObjectId in data to pass
        #     valid_data = AlloySchema(exclude=['_id']).load(existing_alloy)
        # except ValidationError as e:
        #     response['error'] = e.messages
        #     return response, 400
        #
        # good = AlloysService().update_alloy(ObjectId(alloy_id), valid_data)
        #
        # # The service will return True or False based on successfully updating
        # # an alloy.
        # if not good:
        #     response['message'] = 'Alloy not found.'
        #     return response, 404
        #
        # updated_alloy = AlloysService().find_alloy(ObjectId(alloy_id))
        #
        # response['status'] = 'success'
        # response['data'] = updated_alloy
        # response.pop('message')
        # return response, 200

    # noinspection PyMethodMayBeStatic
    def delete(self, _, alloy_id):
        """Exposes the DELETE method on `/alloys/{id}` to delete an existing
        alloy in the database.

        Args:
            _: A valid User object that is not used.
            alloy_id: A valid ObjectId string that will be checked.

        Returns:
            A Response object consisting of a dict and status code as an int.
        """
        response = {'status': 'fail', 'message': 'Invalid ObjectId.'}

        # Verify the request params is a valid ObjectId to use
        if not ObjectId.is_valid(alloy_id):
            return response, 400

        from sim_api.alloys_service import AlloysService
        good = AlloysService().delete_alloy(ObjectId(alloy_id))

        if not good:
            response['message'] = 'Alloy not found.'
            return response, 404

        response['status'] = 'success'
        response.pop('message')
        return response, 202


api.add_resource(Alloys, Routes.Alloys.value)
api.add_resource(AlloysList, Routes.AlloysList.value)
