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

This is the entrypoint to our Arclytics Flask API server.
"""

import os

from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from mongoengine.connection import (
    disconnect_all, get_connection, get_db, MongoEngineConnectionError
)
from redis import Redis

from sim_api.extensions import bcrypt, api, mail, redis_session
from sim_api.extensions import MongoSingleton
from sim_api.extensions import JSONEncoder

# Instantiate the Mongo object to store a connection
app_settings = os.getenv('APP_SETTINGS', 'configs.flask_conf.ProductionConfig')
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

    if os.environ.get('FLASK_ENV') == 'production':
        mongo_client = connect(
            str(os.environ.get('MONGO_APP_DB')),
            host=os.environ.get('MONGO_HOST'),
            port=int(os.environ.get('MONGO_PORT')),
            alias=alias,
            username=os.environ.get('MONGO_APP_USER'),
            password=os.environ.get('MONGO_APP_USER_PASSWORD'),
            authentication_source='admin',
            replicaset='MainRepSet'
        )
    else:
        if testing:
            db_name = 'arc_test'
        mongo_client = connect(db_name, host=host, port=int(port), alias=alias)

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
    app.secret_key = os.environ.get('SECRET_KEY')

    # ========== # CONNECT TO DATABASES # ========== #
    if os.environ.get('FLASK_ENV', 'development') == 'production':
        redis = Redis(
            host=os.environ.get('REDIS_HOST'),
            port=int(os.environ.get('REDIS_PORT')),
            password=os.environ.get('REDIS_PASSWORD'),
            db=1,
        )
    else:
        redis = Redis(
            host=os.environ.get('REDIS_HOST'),
            port=int(os.environ.get('REDIS_PORT')),
            db=1,
        )

    # Mongo Client interface with MongoEngine as Object Document Mapper (ODM)
    app.config.update(
        dict(
            MONGO_HOST=os.environ.get('MONGO_HOST', ''),
            MONGO_PORT=os.environ.get('MONGO_PORT', 27017),
            SESSION_REDIS=redis
        )
    )

    # Connect to the Mongo Client
    db = init_db(app)
    set_flask_mongo(db)

    # ========== # INIT FLASK EXTENSIONS # ========== #
    # Notes:
    #  - `headers` will inject the Content-Type in all responses.
    #  - `expose_headers`: The header or list which are safe to expose to the
    #     API of a CORS API specification.
    #  - `support_credentials`: Allows users to make authenticated requests.
    #     If true, injects the Access-Control-Allow-Credentials header in
    #     responses. This allows cookies and credentials to be submitted across
    #     domains.
    #     Note:	This option cannot be used in conjunction with a ‘*’ origin
    CORS(
        app=app,
        headers=['Content-Type'],
        expose_headers=[
            'Access-Control-Allow-Origin', 'Access-Control-Allow-Credentials'
        ],
        supports_credentials=True
    )
    # Uncomment this for debugging logs
    # logging.getLogger('flask_cors').level = logging.DEBUG

    # Set up Flask extensions
    extensions(app)

    # Set up the Flask App Context
    with app.app_context():
        from sim_api.resources import (
            users_blueprint, auth_blueprint, user_alloys_blueprint,
            admin_blueprint, share_blueprint, last_sim_blueprint,
            save_sim_blueprint, ratings_blueprint, configs_blueprint,
            alloys_blueprint, sim_blueprint, sim_alloys_blueprint
        )
        # ========== # FLASK BLUEPRINTS # ========== #
        app.register_blueprint(users_blueprint, url_prefix='/api/v1/sim')
        app.register_blueprint(auth_blueprint, url_prefix='/api/v1/sim')
        app.register_blueprint(user_alloys_blueprint, url_prefix='/api/v1/sim')
        app.register_blueprint(admin_blueprint, url_prefix='/api/v1/sim')
        app.register_blueprint(share_blueprint, url_prefix='/api/v1/sim')
        app.register_blueprint(last_sim_blueprint, url_prefix='/api/v1/sim')
        app.register_blueprint(save_sim_blueprint, url_prefix='/api/v1/sim')
        app.register_blueprint(ratings_blueprint, url_prefix='/api/v1/sim')
        app.register_blueprint(configs_blueprint, url_prefix='/api/v1/sim')
        app.register_blueprint(alloys_blueprint, url_prefix='/api/v1/sim')
        app.register_blueprint(sim_blueprint, url_prefix='/api/v1/sim')
        app.register_blueprint(sim_alloys_blueprint, url_prefix='/api/v1/sim')

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
    bcrypt.init_app(app)
    api.init_app(app)
    mail.init_app(app)
    redis_session.init_app(app)

    return None
