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
"""app.py:

This is the entrypoint to our Users Flask API server.
"""

import os

from flask import Flask
from mongoengine import connect
from mongoengine.connection import (
    disconnect_all, get_connection, get_db, MongoEngineConnectionError
)

from configs.settings import DEFAULT_LOGGER
from users_app.utilities import JSONEncoder
from users_app.extensions import cors, bcrypt, ma, api
from users_app.mongodb import MongoSingleton
from users_app.resources.users import users_blueprint
from users_app.resources.auth import auth_blueprint
from users_app.resources.user_alloys import user_alloys_blueprint

# Instantiate the Mongo object to store a connection
app_settings = os.getenv('APP_SETTINGS')
_mongo_client = None


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


def create_app(script_info=None, configs_path=app_settings) -> Flask:
    """Create a Flask application using the app factory pattern.

    Args:
        configs_path: the path to the Configs file to build Flask from.
        script_info: any additional information from the script running.

    Returns:
        A Flask app instance.
    """

    # instantiate the application
    app = Flask(__name__)

    # Setup the configuration for Flask
    app.config.from_object(configs_path)

    # ========== # CONNECT TO DATABASE # ========== #
    # Mongo Client interface with MongoEngine as Object Document Mapper (ODM)
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', '')
    app.config['MONGO_HOST'] = os.environ.get('MONGO_HOST', '')
    app.config['MONGO_PORT'] = os.environ.get('MONGO_PORT', 27017)
    # app.config['MONGO_USER'] = os.environ.get('MONGODB_USER', '')
    # stored in .env
    # app.config['MONGO_PASSWORD'] = os.environ.get('MONGODB_PASSWORD', None)
    # stored in .env

    # ========== # FLASK BLUEPRINTS # ========== #
    app.register_blueprint(users_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_alloys_blueprint)

    # Connect to the Mongo Client
    db = init_db(app)
    set_flask_mongo(db)

    # ========== # INIT FLASK EXTENSIONS # ========== #
    # Set up Flask extensions
    extensions(app)

    # Use the modified JSON encoder to handle serializing ObjectId, sets, and
    # datetime objects
    app.json_encoder = JSONEncoder

    # Shell context for Flask CLI
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'mongo': db}

    return app


def extensions(app) -> None:
    """Registers 0 or more extensions for Flask and then mutates the app
    instance passed in.

    Args:
        app: A Flask app instance.

    Returns:
        None.
    """
    cors.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    api.init_app(app)

    return None
