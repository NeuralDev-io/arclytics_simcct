# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# celery_runner.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = '{license}'
__version__ = '{mayor}.{minor}.{rel}'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.25'
"""celery_runner.py: 

{Description}
"""

from celery import Celery

from users_app.app import create_app


CELERY_TASK_LIST = [
    'users_app.tasks',
]


def make_celery(app=None) -> Celery:
    """This method is necessary for Celery to work within the right app context
    because we are using a Factory pattern for creating Flask applications.

    Args:
        app: the current Flask application

    Returns:
        A Celery object.
    """
    if app is None:
        app = create_app()

    # We make a new Celery subsystem instance with the configs.
    _celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND'],
        include=CELERY_TASK_LIST
    )
    _celery.conf.update(app.config)

    # We need to ensure that the tasks are called within the App context
    TaskBase = _celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    _celery.Task = ContextTask

    return _celery


flask_app = create_app()
celery = make_celery(flask_app)
