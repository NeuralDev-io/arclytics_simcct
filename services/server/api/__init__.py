# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# app.py
#
# Attributions:
# [1] https://testdriven.io/courses/microservices-with-docker-flask-and-react/part-one-microservices/
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.04'
__name__ = 'Arclytics_API'
"""__init__.py:

This is the entrypoint to our Python Flask API server.
"""

import os
from typing import Tuple

from flask import Flask
from mongoengine import connect
from mongoengine.connection import disconnect_all, get_connection, get_db, MongoEngineConnectionError

from configs.settings import DEFAULT_LOGGER, APP_CONFIGS
from api.mongodb import MongoSingleton

# Instantiate the Mongo object to store a connection
_db = None


def init_db(app) -> MongoSingleton:
    """Make a connection to the MongoDB container and returns a singleton wrapper on a pymongo.MongoClient."""
    disconnect_all()

    mongo_client = connect(
        app.config['MONGO_DBNAME'],
        host=app.config['MONGO_HOST'],
        port=int(app.config['MONGO_PORT']),
        alias='default'
        # username=app.config['MONGO_USER'],  # FIXME: Do not leave this commented for Production Environment
        # password=app.config['MONGO_PASSWORD'],
    )

    # Test to make sure the connection has been created.
    try:
        conn = get_connection('default')
        # DEFAULT_LOGGER.debug('MongoDB Connected: {}'.format(conn))
    except MongoEngineConnectionError as e:
        DEFAULT_LOGGER.error('MongoDB Failed to Connect.\n Error: {}'.format(e))

    try:
        db_curr = get_db('default')
        # DEFAULT_LOGGER.debug('MongoDB Database in use: {}'.format(db_curr))
    except MongoEngineConnectionError as e:
        DEFAULT_LOGGER.error('MongoDB Failed to Get Database.\n Error: {}'.format(e))

    return MongoSingleton(mongo_client)


def set_app_db(db: MongoSingleton) -> None:
    """Simply sets the module-level global database singleton object."""
    global _db
    _db = db


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
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '')

    # Mongo Client interface with MongoEngine as Object Document Mapper (ODM)
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', '')
    app.config['MONGO_HOST'] = os.environ.get('MONGO_HOST', '')
    app.config['MONGO_PORT'] = os.environ.get('MONGO_PORT', 27017)
    # app.config['MONGO_USER'] = os.environ.get('MONGODB_USER', '')               # stored in .env
    # app.config['MONGO_PASSWORD'] = os.environ.get('MONGODB_PASSWORD', None)     # stored in .env

    # Connect to the Mongo Client
    db = init_db(app)
    set_app_db(db)

    # Log the App Configs
    # if app is None:
    #     DEFAULT_LOGGER.pprint(app.config)

    # Register blueprints
    from api.users import users_blueprint
    app.register_blueprint(users_blueprint)

    # Shell context for Flask CLI
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'mongo': db}

    return app
