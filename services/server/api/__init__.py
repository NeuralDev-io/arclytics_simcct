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
import datetime

from flask import Flask, jsonify
from flask_restful import Resource, Api
from mongoengine import connect, Document, StringField, EmailField, ObjectIdField, BooleanField, DateTimeField

from configs.settings import DEFAULT_LOGGER, APP_CONFIGS

# instantiate the application
app = Flask(__name__)

# API interface
api = Api(app=app)

# Setup the configuration for Flask
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Mongo Client interface with MongoEngine as Object Document Mapper (ODM)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME', 'arclytics')
app.config['MONGO_HOST'] = os.environ.get('MONGO_HOST', 'localhost')
app.config['MONGO_PORT'] = os.environ.get('MONGO_PORT', 27017)
# app.config['MONGO_USER'] = os.environ.get('MONGODB_USER', '')               # stored in .env
# app.config['MONGO_PASSWORD'] = os.environ.get('MONGODB_PASSWORD', None)     # stored in .env

# Connect to the Mongo Client
mongo = connect(
    app.config['MONGO_DBNAME'],
    host=app.config['MONGO_HOST'],
    port=int(app.config['MONGO_PORT']),
    # username=app.config['MONGO_USER'],  # FIXME: Do not leave this commented for Production Environment
    # password=app.config['MONGO_PASSWORD'],
)

# User type choices
USERS = (('1', 'ADMIN'), ('2', 'USER'))


# ========== # MODEL # ========== #
class User(Document):
    _user_id = ObjectIdField(name='_user_id', primary_key=True)
    email = EmailField(required=True, unique=True)
    password = StringField()
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    username = StringField(required=True)
    user_type = StringField(required=True, max_length=1, choices=USERS)
    active = BooleanField(default=True)
    is_admin = BooleanField(default=False)
    created = DateTimeField(default=datetime.datetime.utcnow())
    last_updated = DateTimeField(default=None)
    last_login = DateTimeField(default=None)
    # Define the collection and indexing for this document
    meta = {
        'collection': 'users',
        'indexes': [
            'last_login',
            # {'fields': ['created'], 'expireAfterSeconds': 3600},  # Time To Live index - expires from collection
            'email'
        ]
    }

    # MongoEngine allows you to create custom cleaning rules for your documents when calling save().
    # By providing a custom clean() method you can do any pre validation / data cleaning.
    # This might be useful if you want to ensure a default value based on other document values.
    # def clean(self):
    #     pass


# ========== # ROUTES # ========== #
class PingTest(Resource):
    def get(self):
        return {
            'status': 'success',
            'message': 'pong'
        }


api.add_resource(PingTest, '/users/ping')
