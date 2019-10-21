# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# celery_worker.py
#
# Attributions:
# [1] https://github.com/mattkohl/docker-flask-celery-redis
# [2] https://github.com/kubernetes-for-developers/kfd-celery
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.25'
"""celery_worker.py: 

This module defines a one off instantiation of a Flask App instance and a Celery
instance that connects to the Redis datastore for polling of tasks to run and 
storage of the results.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import datetime
from logging import ERROR
from os import environ as env

from celery import Celery
from celery.schedules import crontab
from elasticapm.contrib.flask import ElasticAPM
from flask import Flask
from flask_mail import Mail
from redis import Redis

from mongo_service import MongoService

# Define the modules that contain Celery tasks
CELERY_TASK_LIST = ['tasks']

# instantiate the application
app = Flask(__name__)

# Setup the configuration for Flask
app_settings = env.get('APP_SETTINGS')
app.config.from_object(app_settings)

# ========== # INIT FLASK EXTENSIONS # ========== #
mail = Mail(app)
apm = ElasticAPM(app, logging=ERROR)

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


# noinspection PyPropertyAccess
celery.Task = ContextTask

# ========== # CELERY BEAT # ========== #
# Setup the Redis client to a different database
redis_host = env.get('REDIS_HOST', None)
redis_port = env.get('REDIS_PORT', None)
if app.env == 'production':
    redis_password = env.get('REDIS_PASSWORD', None)
    redis_uri = f'redis://user:{redis_password}@{redis_host}:{redis_port}/0'
else:
    redis_uri = f'redis://{redis_host}:{redis_port}/0'
redis_client = Redis.from_url(redis_uri)


# noinspection PyUnusedLocal
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Testing hello every 10 seconds
    sender.add_periodic_task(
        crontab(),  # By default this occurs on the minute
        get_logged_users_total.s(),
        name='Get logged in users every 30 secs'
    )


# PERIODIC TASKS
@celery.task()
def get_logged_users_total():
    """Simply get the number of logged in users by Session in Redis."""

    # Get the number of keys using the pattern that we defined
    # in `services.simcct.sim_api.extensions.Session.redis_session`
    # as being `session:{session id}`. We just get all the keys
    # matching this pattern which means they have logged in.
    keys = redis_client.keys(pattern=u'session*')

    # Documents will be stored on size bucketing with day as the key so
    # we need to get the date using the ISO Date format.
    # Using an ISO Date creates an optimal index.
    date = datetime.datetime.utcnow().strftime('%Y-%m-%d')

    # We need to store the timestamp for when this entry was created
    now = datetime.datetime.utcnow()
    # timestamp = datetime.datetime.timestamp(now)

    # Every sample in the document will be a value for how many users are
    # logged in the application at the current timestamp.
    sample = {'datetime': now, 'value': len(keys)}
    # We use the query to find the document or make a new one if it does not
    # exist when we pass in `upsert=True`
    # As new data samples are added it is simply appended to the document
    # until the number of samples hit 1000
    q = {'date': date, 'n_samples': {'$lt': 2000}}
    # Make some updates on the document based by doing:
    #  - Insert the new sample into the `logged_in` key which is an array.
    #  - Increment the `n_samples` key by `.
    u = {
        '$push': {
            'logged_in': sample
        },
        '$inc': {
            'n_samples': 1
        },
    }

    MongoService().update_one(query=q, update=u, upsert=True)
