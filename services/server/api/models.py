# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# models.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, NeuralDev'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.03'
"""models.py: 

{Description}
"""

import datetime

from mongoengine import Document, StringField, EmailField, ObjectIdField, BooleanField, DateTimeField


# User type choices
USERS = (('1', 'ADMIN'), ('2', 'USER'))


# ========== # MODELS SCHEMA # ========== #
class User(Document):
    _user_id = ObjectIdField(name='_user_id', primary_key=True)
    email = EmailField(required=True, unique=True)
    # password = StringField()
    # first_name = StringField(required=True)
    # last_name = StringField(required=True)
    username = StringField(required=True)
    # user_type = StringField(required=True, max_length=1, choices=USERS)
    active = BooleanField(default=True)
    # is_admin = BooleanField(default=False)
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
