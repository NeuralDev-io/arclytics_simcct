# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# __init__.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.09'
"""__init__.py:

This is the module to create the Flask app instance as a factory pattern. 
It is also the entrypoint and set up module for the Arclytics API which is 
a microservice to retrieve logs, metrics, and data from data stores such as 
MongoDB, Redis, and Elasticsearch for analytics purposes.
"""

from os import environ as env

from flask import Flask
from flask_cors import CORS

from arc_api.extensions import api, apm

DATETIME_FMT = '%Y-%m-%dT%H:%M:%S%z'
DATE_FMT = '%Y-%m-%d'

# Environment Variable Flask Configurations object path to use or by default
# use production configurations because it is the most secure and restrictive.
app_settings = env.get('APP_SETTINGS', 'configs.flask_conf.ProductionConfig')


def create_app(configs_path=app_settings) -> Flask:
    """Create a Flask application using the app factory pattern.

    Args:
        configs_path: the path to the Configs file to build Flask from.

    Returns:
        A Flask app object.
    """

    # Instantiate the application
    app = Flask('arclytics_flask_server')

    # ========== # CONFIGURATIONS # ========== #
    # Setup the configuration for Flask
    app.config.from_object(configs_path)
    app.secret_key = env.get('SECRET_KEY')
    prod_environment = app.env == 'production'

    # ========== # INIT FLASK EXTENSIONS # ========== #
    # Set up the Flask App Context
    with app.app_context():
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
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Credentials',
                'Content-Type'
            ],
            supports_credentials=True
        )

        # Set up Flask extensions plugins
        extensions(app)

        # ========== # IMPORT FLASK BLUEPRINTS # ========== #

        # ========== # REGISTER FLASK BLUEPRINTS # ========== #

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
    apm.init_app(app)
    api.init_app(app)
    return None
