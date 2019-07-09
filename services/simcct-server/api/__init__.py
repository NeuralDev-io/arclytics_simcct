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
from datetime import datetime

from bson import ObjectId
from flask import Flask
from flask_restful import Api
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from flask_cors import CORS

import configs


class JSONEncoder(json.JSONEncoder):
    """Extends the json-encoder to properly convert dates and bson.ObjectId"""

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime):
            return str(o.isoformat())
        return json.JSONEncoder.default(self, o)


# Some Flask extensions
cors = CORS()


def create_app(script_info=None) -> Flask:
    """Default Flask method to start the Flask server through the script."""

    # instantiate the application
    app = Flask(__name__)

    # Setup the configuration for Flask
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # Mongo Client interface with MongoEngine as Object Document Mapper (ODM)
    app.config['MONGO_HOST'] = os.environ.get('MONGO_HOST', '')
    app.config['MONGO_PORT'] = os.environ.get('MONGO_PORT', 27017)
    # app.config['MONGO_USER'] = os.environ.get('MONGODB_USER', '')
    # stored in .env
    # app.config['MONGO_PASSWORD'] = os.environ.get('MONGODB_PASSWORD', None)
    # stored in .env

    # Connect to the Mongo Client
    mongo_client = MongoClient(host=app.config['MONGO_HOST'],
                               port=int(app.config['MONGO_PORT']))
    try:
        mongo_client.admin.command('ismaster')
        print('[INFO] Connected to MongoDB')
        print(mongo_client)
    except ConnectionFailure as e:
        print('[DEBUG] Unable to Connect to MongoDB')

    # Set up Flask extensions
    cors.init_app(app)

    # Log the App Configs
    # if app is None:
    #     DEFAULT_LOGGER.pprint(app.config)

    # Register blueprints
    from api.views import test_blueprint
    app.register_blueprint(test_blueprint)

    # Use the modified JSON encoder to handle serializing ObjectId, sets, and
    # datetime objects
    app.json_encoder = JSONEncoder

    # Shell context for Flask CLI
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'mongo': mongo_client}

    return app
