# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# load_production_data.py
# 
# Attributions: 
# [1] 
# ----------------------------------------------------------------------------------------------------------------------

__author__ = ['Andrew Che <@codeninja55>']
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'TBA'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'production'
__date__ = '2019.09.15'

"""load_production_data.py: 

Script to load Production data into MongoDB container.
"""

import os
import json
import sys
from pathlib import Path
from os import environ as env
from sys import stderr
from mongoengine import get_db, connect, disconnect_all, get_connection
from sim_api import init_db, create_app
from sim_api.models import User, UserProfile, AdminProfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

app = create_app()

# LOAD FROM JSON FILE BY NAME
# user_data_path = Path(BASE_DIR) / 'production_user_data.json'
# alloy_data_path = Path(BASE_DIR) / 'production_user_alloys_data.json'
user_data_path = Path(BASE_DIR) / 'production_data' / 'seed_user_data.json'
alloy_data_path = Path(BASE_DIR) / 'production_data' / 'seed_alloy_data.json'
if os.path.isfile(user_data_path):
    with open(user_data_path) as f:
        user_data = json.load(f)
if os.path.isfile(alloy_data_path):
    with open(alloy_data_path) as f:
        alloy_data = json.load(f)

# If we are in a production environment, we need these security values
if env.get('FLASK_ENV', 'development') == 'production':
    disconnect_all()

    _db_name = str(env.get('MONGO_APP_DB'))
    _host = env.get('MONGO_HOST')
    _port = env.get('MONGO_PORT')
    _username = env.get('MONGO_APP_USER')
    _password = str(env.get('MONGO_APP_USER_PASSWORD'))
    mongo_uri = (
        f'mongodb://{_username}:{_password}@{_host}:{_port}'
        f'/?authSource=admin'
    )
    client = connect(
        db=_db_name,
        host=mongo_uri,
        alias='default',
        authentication_mechanism='SCRAM-SHA-1'
    )
else:
    init_db(app)
    client = get_connection('default')

# This will get the correct database.
db = get_db('default')
print(f'MongoDB Client: \n{client}\n', file=stderr)
print(f'MongoDB Database: \n{db}\n', file=stderr)

# STAY INSIDE THE FLASK APPLICATION CONTEXT
with app.app_context():
    for i, user in enumerate(user_data):
        # BASE USER DETAILS
        new_user = User(
            **{
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
            }
        )
        new_user.set_password(user['password'])
        print(new_user.to_dict())

        # PROFILE

        # ADMIN
        if user['is_admin']:
            admin_profile = AdminProfile(
                **{
                    'position': user['admin_profile']['position'],
                    'mobile_number': user['admin_profile']['mobile_number']
                }
            )
            # THIS IS IMPORTANT TO MAKE THEM AN ADMIN
            admin_profile.verified = True
            new_user.disable_admin = False

            new_user.admin_profile = admin_profile

        if user.get('saved_alloys', False):
            for alloy_name in user['saved_alloys']:
                # LOAD THE ALLOY FROM ANOTHER DICTIONARY OR ARRAY BASHED ON NAME
                pass


        # SAVE
        new_user.save()


# ALLOYS NEED REQUIRED ELEMENTS
# Carbon
# Manganese
# Nickel
# Chromium
# Molybdenum
# Silicon
# Cobalt
# Tungsten
# Arsenic
# Iron
