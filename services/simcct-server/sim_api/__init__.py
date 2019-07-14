# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# __init__.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.09'
"""__init__.py:

This is the entrypoint to our SimCCT Flask API server.
"""

import os
import json
import sys
from datetime import datetime

import redis
import numpy as np
from dotenv import load_dotenv
from bson import ObjectId
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_session import Session as FlaskSession
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from sim_api.resources.session import Session, UsersPing


class JSONEncoder(json.JSONEncoder):
    """Extends the json-encoder to properly convert dates and bson.ObjectId"""

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime):
            return str(o.isoformat())
        if isinstance(o, np.float):
            return str(o)
        if isinstance(o, np.float32):
            return str(o)
        if isinstance(o, np.float64):
            return str(o)
        return json.JSONEncoder.default(self, o)


# Setup the environment
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
sys.path.append(BASE_DIR)

# Load environment variables
env_path = os.path.join(BASE_DIR, '.env')
if os.path.isfile(env_path):
    load_dotenv(env_path)

DATETIME_FMT = '%Y-%m-%dT%H:%M:%S%z'
DATE_FMT = '%Y-%m-%d'

# Some Flask extensions
cors = CORS()
sess = FlaskSession()


def create_app(script_info=None) -> Flask:
    """Default Flask method to start the Flask server through the script."""

    # instantiate the application
    app = Flask(__name__)

    # ========== # CONFIGURATIONS # ========== #
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # ========== # CONNECT TO DATABASE # ========== #
    # Mongo Client interface with PyMongo
    app.config['MONGO_HOST'] = os.environ.get('MONGO_HOST', '')
    app.config['MONGO_PORT'] = os.environ.get('MONGO_PORT', 27017)
    # app.config['MONGO_USER'] = os.environ.get('MONGODB_USER', '')
    # stored in .env
    # app.config['MONGO_PASSWORD'] = os.environ.get('MONGODB_PASSWORD', None)
    # stored in .env

    # Connect to the Mongo Client
    # TODO(andrew@neuraldev.io): Need to set the password in production
    mongo_client = MongoClient(
        host=app.config['MONGO_HOST'], port=int(app.config['MONGO_PORT'])
    )
    try:
        mongo_client.admin.command('ismaster')
    except ConnectionFailure as e:
        print('[DEBUG] Unable to Connect to MongoDB')

    # Redis Client
    # TODO(andrew@neuraldev.io): Need to set the password in production
    redis_client = redis.Redis(
        host=os.environ.get('REDIS_HOST'),
        port=int(os.environ.get('REDIS_PORT')),
        db=int(app.config['REDIS_DB'])
    )

    # ========== # INIT FLASK EXTENSIONS # ========== #
    cors.init_app(app)

    # Flask-Session and Redis
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis_client
    app.config['SESSION_USER_SIGNER'] = True
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_KEY_PREFIX'] = 'session:'
    sess.init_app(app)

    from sim_api.resources.session import session_blueprint
    api = Api(session_blueprint)

    # Register blueprints
    app.register_blueprint(session_blueprint)
    from sim_api.resources.sim_configurations import configs_blueprint
    app.register_blueprint(configs_blueprint)

    # ========== # API ROUTES # ========== #
    api.add_resource(Session, '/session')
    api.add_resource(UsersPing, '/users/ping')

    # Use the modified JSON encoder to handle serializing ObjectId, sets, and
    # datetime objects
    app.json_encoder = JSONEncoder

    # Shell context for Flask CLI
    @app.shell_context_processor
    def ctx():
        return {'app': app}

    return app
