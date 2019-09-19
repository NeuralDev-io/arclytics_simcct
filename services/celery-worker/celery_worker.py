# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# celery_worker.py
#
# Attributions:
# [1] https://github.com/mattkohl/docker-flask-celery-redis
# [2] https://github.com/kubernetes-for-developers/kfd-celery
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.25'
"""celery_worker.py: 

This module defines a one off instantiation of a Flask App instance and a Celery
instance that connects to the Redis datastore for polling of tasks to run and 
storage of the results.
"""

import os
import sys

from celery import Celery
from flask import Flask
from flask_mail import Mail

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Define the modules that contain Celery tasks
CELERY_TASK_LIST = [
    'tasks',
]

# instantiate the application
app = Flask('Celery Worker')

# Setup the configuration for Flask
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)

# ========== # INIT FLASK EXTENSIONS # ========== #
mail = Mail(app)

# We make a new Celery subsystem instance with the configs using Redis
# as the Message Queue broker and also to store results.
celery: Celery = Celery(
    app.import_name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'],
    include=CELERY_TASK_LIST
)
celery.conf.update(app.config)

# We need to ensure that the tasks are called within the App context
TaskBase = celery.Task


class ContextTask(TaskBase):
    abstract = True

    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)


celery.Task = ContextTask
