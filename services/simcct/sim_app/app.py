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
import sys

from dotenv import load_dotenv
from flask import Flask

from sim_app.extensions import cors, api, sess
from sim_app.utilities import JSONEncoder
from sim_app.resources.session import session_blueprint
from sim_app.resources.sim_configurations import configs_blueprint
from sim_app.resources.alloys import alloys_blueprint
from sim_app.resources.simulation import sim_blueprint
from sim_app.resources.sim_alloys import sim_alloys_blueprint


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
    app_settings = os.environ.get('APP_SETTINGS', None)
    app.config.from_object(app_settings)

    # Register blueprints
    app.register_blueprint(session_blueprint)
    app.register_blueprint(configs_blueprint)
    app.register_blueprint(alloys_blueprint)
    app.register_blueprint(sim_blueprint)
    app.register_blueprint(sim_alloys_blueprint)

    # ========== # INIT FLASK EXTENSIONS # ========== #
    extensions(app)

    # Use the modified JSON encoder to handle serializing ObjectId, sets, and
    # datetime objects
    app.json_encoder = JSONEncoder

    # Shell context for Flask CLI
    @app.shell_context_processor
    def ctx():
        return {'app': app}

    return app


def extensions(app) -> None:
    """Registers 0 or more extensions for Flask and then mutates the app
    instance passed in.

    Args:
        app: A Flask app instance.

    Returns:
        None.
    """
    api.init_app(app)
    cors.init_app(app)
    sess.init_app(app)

    return None
