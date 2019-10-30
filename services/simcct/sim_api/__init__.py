# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# __init__.py
#
# Attributions:
# [1]
# https://testdriven.io/courses/microservices-with-docker-flask-and-react/
# part-one-microservices/
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '1.1.0'

__status__ = 'production'
__date__ = '2019.06.04'
"""__init__.py:

This is the entrypoint to our Arclytics Flask API server.
"""

import logging
from os import environ as env
from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from mongoengine.connection import (
    MongoEngineConnectionError, disconnect_all, get_connection, get_db
)
from redis import Redis

from sim_api.extensions import JSONEncoder
from sim_api.extensions import MongoSingleton
from sim_api.extensions import (api, bcrypt, redis_session, apm)

# Environment Variable Flask Configurations object path to use or by default
# use production configurations because it is the most secure and restrictive.
app_settings = env.get('APP_SETTINGS', 'configs.flask_conf.ProductionConfig')
# Instantiate the Mongo object to store a connection
_mongo_client = None


def init_db(
    app=None, db_name=None, host=None, port=None, alias='default'
) -> MongoSingleton:
    """Make a connection to the MongoDB container and returns a singleton
    wrapper on a pymongo.MongoClient."""
    disconnect_all()

    testing = False

    if app is not None:
        db_name = app.config['MONGO_DBNAME']
        host = app.config['MONGO_HOST']
        port = int(app.config['MONGO_PORT'])
        testing = app.config['TESTING']

    if env.get('FLASK_ENV') == 'production':
        _db_name = str(env.get('MONGO_APP_DB'))
        _host = env.get('MONGO_HOST')
        _port = env.get('MONGO_PORT')
        _username = env.get('MONGO_APP_USER')
        _password = str(env.get('MONGO_APP_USER_PASSWORD'))
        mongo_uri = (
            f'mongodb://{_username}:{_password}@{_host}:{_port}'
            f'/?authSource=admin'
        )
        mongo_client = connect(
            _db_name,
            host=mongo_uri,
            alias=alias,
            authentication_mechanism='SCRAM-SHA-1'
        )
    else:
        if testing:
            db_name = 'arc_test'
        mongo_client = connect(db_name, host=host, port=int(port), alias=alias)

    try:
        # This is necessary to connect at least once
        get_db(alias)
    except MongoEngineConnectionError as e:
        print('MongoDB Failed to Get Database.\n Error: {}'.format(e))

    # Test to make sure the connection has been created.
    try:
        get_connection(alias)
    except MongoEngineConnectionError as e:
        print('MongoDB Failed to Connect.\n Error: {}'.format(e))

    return MongoSingleton(mongo_client)


def set_flask_mongo(mongo_singleton: MongoSingleton) -> None:
    """Simply sets the module-level global database singleton object."""
    global _mongo_client
    _mongo_client = mongo_singleton


def get_flask_mongo() -> any:
    """Simply get the module-level global database singleton object."""
    return _mongo_client


def extensions(app) -> None:
    """Registers 0 or more extensions for Flask and then mutates the app
    instance passed in.

    Args:
        app: A Flask app instance.

    Returns:
        None.
    """
    log_level = logging.ERROR if app.env == 'production' else True
    apm.init_app(app, logging=log_level)
    api.init_app(app)
    bcrypt.init_app(app)
    redis_session.init_app(app)
    # talisman.init_app(app, force_https_permanent=False, force_https=False)

    return None


def create_app(configs_path=app_settings) -> Flask:
    """Create a Flask application using the app factory pattern.

    Args:
        configs_path: the path to the Configs file to build Flask from.

    Returns:
        A Flask app instance.
    """

    # instantiate the application
    app = Flask(__name__)

    # ========== # CONFIGURATIONS # ========== #
    # Setup the configuration for Flask
    app.config.from_object(configs_path)
    app.secret_key = env.get('SECRET_KEY')
    prod_environment = app.env == 'production'

    # ========== # CONNECT TO DATABASES # ========== #
    if not prod_environment:
        redis = Redis(
            host=env.get('REDIS_HOST'),
            port=int(env.get('REDIS_PORT')),
            db=0,
        )
    else:
        redis = Redis(
            host=env.get('REDIS_HOST'),
            port=int(env.get('REDIS_PORT')),
            password=env.get('REDIS_PASSWORD'),
            db=0,
        )

    # Mongo Client interface with MongoEngine as Object Document Mapper (ODM)
    app.config.update(
        dict(
            MONGO_HOST=env.get('MONGO_HOST', ''),
            MONGO_PORT=env.get('MONGO_PORT', 27017),
            SESSION_REDIS=redis
        )
    )

    # Connect to the Mongo Client
    db = init_db(app)
    set_flask_mongo(db)

    # Set up the Flask App Context
    with app.app_context():
        from sim_api.resources import (
            users_blueprint, auth_blueprint, user_alloys_blueprint,
            admin_blueprint, share_blueprint, last_sim_blueprint,
            save_sim_blueprint, ratings_blueprint, configs_blueprint,
            alloys_blueprint, sim_blueprint, sim_alloys_blueprint,
            root_blueprint, data_personal_blueprint
        )
        # ========== # FLASK BLUEPRINTS # ========== #
        app.register_blueprint(root_blueprint)
        app.register_blueprint(users_blueprint)
        app.register_blueprint(auth_blueprint)
        app.register_blueprint(user_alloys_blueprint)
        app.register_blueprint(admin_blueprint)
        app.register_blueprint(share_blueprint)
        app.register_blueprint(last_sim_blueprint)
        app.register_blueprint(save_sim_blueprint)
        app.register_blueprint(ratings_blueprint)
        app.register_blueprint(configs_blueprint)
        app.register_blueprint(alloys_blueprint)
        app.register_blueprint(sim_blueprint)
        app.register_blueprint(sim_alloys_blueprint)
        app.register_blueprint(data_personal_blueprint)

    # ========== # INIT FLASK EXTENSIONS # ========== #
    # Notes:
    #  - `headers` will inject the Content-Type in all responses.
    #  - `expose_headers`: The header or list which are safe to expose to
    #  the
    #     API of a CORS API specification.
    #  - `support_credentials`: Allows users to make authenticated requests.
    #     If true, injects the Access-Control-Allow-Credentials header in
    #     responses. This allows cookies and credentials to be submitted
    #     across
    #     domains.
    #     Note:	This option cannot be used in conjunction with a ‘*’ origin
    CORS(
        app=app,
        headers=['Content-Type'],
        expose_headers=[
            'Access-Control-Allow-Origin', 'Access-Control-Allow-Credentials',
            'Content-Type'
        ],
        supports_credentials=True
    )
    # Uncomment this for debugging logs
    # logging.getLogger('flask_cors').level = logging.DEBUG

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
