# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# views.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.09'

"""views.py: 

The controller and routes for the Arclytics Sim API.
"""

from flask import request, jsonify
from flask_restful import Resource
from api.app import app, api, mongo, flask_bcrypt, jwt
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity
)
from api.schemas import validate_user

# TODO: Add a logger

# TODO: Testing index entry
@app.route('/')
def index():
    return jsonify({'message': 'Hello World!'}), 200


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({
        'ok': False,
        'message': 'No Authorisation Header.'
    }), 401


@app.route('/auth', methods=['POST'])
def auth_user():
    """Authorisation login endpoint."""
    data = validate_user(request.get_json())
    if data['ok']:
        data = data['data']
        user = mongo.db.users.find_one({'email': data['email']})
        if user and flask_bcrypt.check_password_hash(user['password'], data['password']):
            del user['password']
            access_token = create_access_token(identity=data)
            refresh_token = create_refresh_token(identity=data)
            user['token'] = access_token
            user['refresh'] = refresh_token
            return jsonify({'ok': True, 'data': user}), 200
        else:
            return jsonify({'ok': False, 'message': 'Invalid username or password.'}), 401
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


@app.route('/register', methods=['POST'])
def register():
    """Register user endpoint."""
    data = validate_user(request.get_json())

    # TODO: validate if existing user
    if data['ok']:
        data = data['data']
        data['password'] = flask_bcrypt.generate_password_hash(data['password'])
        mongo.db.users.insert_one(data)
        return jsonify({'ok': True, 'message': 'User created successfully!'}), 200
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """Refresh token endpoint."""
    current_user = get_jwt_identity()
    res = {
        'token': create_refresh_token(identity=current_user)
    }
    return jsonify({'ok': True, 'data': res})


@app.route('/users', methods=['GET', 'DELETE', 'PATCH'])
@jwt_required
def user():
    """User endpoints."""
    if request.method == 'GET':
        query = request.args
        data = mongo.db.users.find_one(query, {"_id": 0})
        print(data)
        return jsonify({'ok': True, 'data': data}), 200

    data = request.json()
    if request.method == 'DELETE':
        pass

    if request.method == 'PATCH':
        pass


# TODO: Testing using flask_restful api resources
class PingTest(Resource):
    def get(self):
        return {
            'status': 'success',
            'message': 'pong'
        }


api.add_resource(PingTest, '/arc/ping')
