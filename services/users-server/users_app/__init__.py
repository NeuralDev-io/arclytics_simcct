# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# app.py
#
# Attributions:
# [1]
# https://testdriven.io/courses/microservices-with-docker-flask-and-react/
# part-one-microservices/
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.04'
"""__init__.py:

This is the entrypoint to our Users Flask API server.
"""

import datetime
import decimal
import os
import json
from bson import ObjectId

from flask import Flask
from mongoengine import connect
from mongoengine.connection import (
    disconnect_all, get_connection, get_db, MongoEngineConnectionError
)
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow

from users_app.mongodb import MongoSingleton
from configs.settings import DEFAULT_LOGGER


class JSONEncoder(json.JSONEncoder):
    """Extends the json-encoder to properly convert dates and bson.ObjectId"""

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime.datetime):
            return str(o.isoformat())
        if isinstance(o, decimal.Decimal):
            return str(o)
        return json.JSONEncoder.default(self, o)


# Instantiate the Mongo object to store a connection
_mongo_client = None
# Some other extensions to Flask
cors = CORS()
bcrypt = Bcrypt()
ma = Marshmallow()


def init_db(app=None, db_name=None, host=None, port=None) -> MongoSingleton:
    """Make a connection to the MongoDB container and returns a singleton
    wrapper on a pymongo.MongoClient."""
    disconnect_all()

    if app is not None:
        db_name = app.config['MONGO_DBNAME']
        host = app.config['MONGO_HOST']
        port = int(app.config['MONGO_PORT'])

    mongo_client = connect(
        db_name,
        host=host,
        port=int(port),
        alias='default'
        # FIXME(andrew@neuraldev.io): Do not leave this commented for
        #  Production Environment
        # username=app.config['MONGO_USER'],
        # password=app.config['MONGO_PASSWORD'],
    )

    # Test to make sure the connection has been created.
    try:
        conn = get_connection('default')
        # DEFAULT_LOGGER.debug('MongoDB Connected: {}'.format(conn))
    except MongoEngineConnectionError as e:
        DEFAULT_LOGGER.error(
            'MongoDB Failed to Connect.\n Error: {}'.format(e)
        )

    try:
        db_curr = get_db('default')
        # DEFAULT_LOGGER.debug('MongoDB Database in use: {}'.format(db_curr))
    except MongoEngineConnectionError as e:
        DEFAULT_LOGGER.error(
            'MongoDB Failed to Get Database.\n Error: {}'.format(e)
        )

    return MongoSingleton(mongo_client)


def set_flask_mongo(mongo_singleton: MongoSingleton) -> None:
    """Simply sets the module-level global database singleton object."""
    global _mongo_client
    _mongo_client = mongo_singleton


def get_flask_mongo() -> any:
    """Simply get the module-level global database singleton object."""
    return _mongo_client


def create_app(script_info=None) -> Flask:
    """

    Args:
        script_info:

    Returns:

    """

    # instantiate the application
    app = Flask(__name__)

    # Setup the configuration for Flask
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # ========== # CONNECT TO DATABASE # ========== #
    # Mongo Client interface with MongoEngine as Object Document Mapper (ODM)
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', '')
    app.config['MONGO_HOST'] = os.environ.get('MONGO_HOST', '')
    app.config['MONGO_PORT'] = os.environ.get('MONGO_PORT', 27017)
    # app.config['MONGO_USER'] = os.environ.get('MONGODB_USER', '')
    # stored in .env
    # app.config['MONGO_PASSWORD'] = os.environ.get('MONGODB_PASSWORD', None)
    # stored in .env

    # Connect to the Mongo Client
    db = init_db(app)
    set_flask_mongo(db)

    # ========== # INIT FLASK EXTENSIONS # ========== #
    # Set up Flask extensions
    cors.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)

    # Register blueprints
    from users_app.resources.users import users_blueprint
    app.register_blueprint(users_blueprint)
    from users_app.resources.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Use the modified JSON encoder to handle serializing ObjectId, sets, and
    # datetime objects
    app.json_encoder = JSONEncoder

    # Shell context for Flask CLI
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'mongo': db}

    return app
