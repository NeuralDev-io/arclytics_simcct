# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# app.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.5.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.09'
"""app.py:

This is the entrypoint to our SimCCT Flask API server.
"""

import os
import json
import sys
from datetime import datetime

import numpy as np
from dotenv import load_dotenv
from bson import ObjectId
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_session import Session as FlaskSession

from sim_app.resources.session import Session, UsersPing


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
    """Default Flask method to create a Flask app and its context. It sets
    the configurations first and then initialises the extensions to other
    required libraries to be used in the application.

    Args:
        script_info: None

    Returns:
        A Flask app object.
    """

    # Instantiate the application
    app = Flask(__name__)

    # ========== # CONFIGURATIONS # ========== #
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # ========== # INIT FLASK EXTENSIONS # ========== #
    cors.init_app(app)
    # Flask-Session and Redis
    sess.init_app(app)

    from sim_app.resources.session import session_blueprint
    api = Api(session_blueprint)

    # Register blueprints
    app.register_blueprint(session_blueprint)
    from sim_app.resources.sim_configurations import configs_blueprint
    app.register_blueprint(configs_blueprint)
    # from sim_app.resources.alloys import alloys_blueprint
    # app.register_blueprint(alloys_blueprint)

    # ========== # API ROUTES # ========== #
    # Importing within Flask app context scope because trying to init the
    # the MongoAlloys adapter and the database before mongo.init_app(app)
    # will raise all sorts of import issues.
    from sim_app.resources.alloys import AlloysList, Alloys

    api.add_resource(Session, '/session')
    api.add_resource(UsersPing, '/users/ping')
    api.add_resource(Alloys, '/alloys/<alloy_id>')
    api.add_resource(AlloysList, '/alloys')

    # Use the modified JSON encoder to handle serializing ObjectId, sets, and
    # datetime objects
    app.json_encoder = JSONEncoder

    # Shell context for Flask CLI
    @app.shell_context_processor
    def ctx():
        return {'app': app}

    return app
