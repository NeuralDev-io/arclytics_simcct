# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# celery_runner.py
#
# Attributions:
# [1]
# J. Stouffer and D. Gaspar. Mastering Flask Web Development - Second Edition.
# Birmingham: Packt Publishing, 2018.
# [2] https://github.com/nickjj/build-a-saas-app-with-flask
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'MIT'
__version__ = '1.0.0'

__status__ = 'development'
__date__ = '2019.07.25'
"""celery_runner.py: 

This module defines a factory pattern of creating a Celery instance which
can be used to make a worker by running 
`docker-compose exec -T arclytics celery worker -l info -A celery_runner` 
"""

from celery import Celery
from flask import Flask

from sim_api import create_app


def make_celery(app: Flask = None) -> Celery:
    """This method is necessary for Celery to work within the right app context
    because we are using a Factory pattern for creating Flask applications.

    Args:
        app: the current Flask application

    Returns:
        A Celery object.
    """
    if app is None:
        app = create_app()

    # We make a new Celery subsystem instance with the configs using Redis
    # as the Message Queue broker and also to store results.
    celery_beat: Celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery_beat.conf.update(app.config)

    # We need to ensure that the tasks are called within the App context
    TaskBase = celery_beat.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery_beat.Task = ContextTask

    return celery_beat


flask_app = create_app()
celery = make_celery(flask_app)
