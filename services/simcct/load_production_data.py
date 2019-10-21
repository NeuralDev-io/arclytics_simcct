# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# arclytics_sim
# load_production_data.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>', 'Dinol Shrestha<@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.09.15'
"""load_production_data.py: 
​
Script to load Production data into MongoDB container.
"""

import json
import os
import random
import sys
from datetime import datetime, timedelta
from os import environ as env
from pathlib import Path
from sys import stderr
import numpy as np
from tqdm import tqdm

import geoip2
from geoip2.errors import AddressNotFoundError
from maxminddb.errors import InvalidDatabaseError
from mongoengine import connect, disconnect_all, get_connection, get_db
from pymongo import MongoClient
from sim_api import create_app, init_db
from sim_api.extensions.utilities import get_mongo_uri
from sim_api.models import (
    AdminProfile, Feedback, LoginData, SavedSimulation, User, UserProfile,
    SharedSimulation
)

DEBUG = True
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

app = create_app()
# LOAD FROM JSON FILE BY NAME
user_data_path = (
    Path(BASE_DIR) / 'production_data' / 'production_user_data.json'
)
alloy_data_path = Path(
    BASE_DIR
) / 'production_data' / 'production_alloy_data.json'
global_alloy_data_path = Path(
    BASE_DIR
) / 'production_data' / 'production_global_alloys_data.json'
simulation_data_path = Path(
    BASE_DIR
) / 'production_data' / 'production_saved_sim_data.json'
feedback_data_path = Path(
    BASE_DIR
) / 'production_data' / 'production_feedback_data.json'
shared_sim_data_path = Path(
    BASE_DIR
) / 'production_data' / 'production_shared_sim_data.json'

if os.path.isfile(user_data_path):
    with open(user_data_path) as f:
        user_data = json.load(f)
if os.path.isfile(alloy_data_path):
    with open(alloy_data_path) as f:
        alloy_data = json.load(f)
if os.path.isfile(global_alloy_data_path):
    with open(global_alloy_data_path) as f:
        global_alloy_data = json.load(f)
if os.path.isfile(simulation_data_path):
    with open(simulation_data_path) as f:
        simulation_data = json.load(f)
if os.path.isfile(feedback_data_path):
    with open(feedback_data_path) as f:
        feedback_data = json.load(f)
if os.path.isfile(shared_sim_data_path):
    with open(shared_sim_data_path) as f:
        shared_sim_data = json.load(f)

# test data for rating and login
varied_date = [
    datetime.utcnow(),
    datetime.utcnow() - timedelta(days=1),
    datetime.utcnow() - timedelta(days=2),
    datetime.utcnow() - timedelta(days=3),
    datetime.utcnow() - timedelta(days=4),
    datetime.utcnow() - timedelta(days=5),
    datetime.utcnow() - timedelta(days=6),
    datetime.utcnow() - timedelta(days=7)
]
random_ip = [2, 3, 4, 5, 6]

type_of_user = [1, 2, 3]

vic_ip = [
    "103.224.88.150L", "1.152.105.58", "101.181.99.103", "103.1.205.85",
    "27.253.2.2", "27.253.2.5", "58.108.194.247", "13.77.50.96"
]
qld_ip = [
    "61.69.158.62", "120.22.10.205", "61.87.176.0", "220.240.228.236",
    "203.220.77.101", "110.174.244.180", "1.132.96.140", "1.132.96.120",
    "1.132.96.2"
]
ip_set1 = [
    "110.174.244.180", "185.220.102.7", "185.220.102.8", "185.225.16.14",
    "185.225.69.52", "185.225.69.60", "1.37.0.0", "188.213.49.176"
]
ip_set2 = [
    "27.34.0.0", "192.42.116.15", "192.82.198", "192.32.216", "14.224.0.0",
    "14.224.0.1", "2.32.0.0", "192.12.111"
]
ip_set3 = [
    "61.69.158.62", "3.128.0.0", "61.87.176.0", "220.240.228.236",
    "203.220.77.101", "24.232.0.0", "1.132.96.140", "1.132.96.120",
    "1.132.96.2"
]
# initialising pymongo connection
mongo_client = MongoClient(get_mongo_uri())
db = mongo_client['arc_dev']

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

random.seed(100000)
np.random.seed(3000)

# loading global alloy's
print(
    'Seeding global alloys to <{}> database:'.format(db.name), file=sys.stderr
)
with app.app_context():
    json_data = global_alloy_data
    from sim_api.schemas import AlloySchema

    data = AlloySchema(many=True).load(json_data['alloys'])
    # Check the correct database -- arc_dev
    db.alloys.insert_many(data)

# STAY INSIDE THE FLASK APPLICATION CONTEXT
print('Seeding users to <{}> database:'.format(db.name), file=sys.stderr)
with app.app_context():
    for user in tqdm(user_data):
        # ==================== # NEW USER BASE DETAILS # =================== #
        new_user = User(
            **{
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
            }
        )
        new_user.set_password(user['password'])
        # print(new_user.to_dict())

        # Get from a list of [1, 2, 3] what type of user this user is.
        user_type = random.sample(type_of_user, 1)

        if user_type[0] == 1:
            n_user_alloys = random.randint(0, 5)
        if user_type[0] == 2:
            n_user_alloys = random.randint(5, 15)
        if user_type[0] == 3:
            n_user_alloys = random.randint(15, 31)

        # ==================== # USER SAVED ALLOYS # =================== #
        alloy = random.sample(alloy_data['alloys'], n_user_alloys)
        # adding alloys
        for alloy_to_add in alloy:
            new_user.saved_alloys.create(**alloy_to_add)

        # ==================== # LOGIN AND RATINGS DATA # =================== #
        IP_check = random.sample(random_ip, 1)

        if IP_check[0] == 2:
            IP = random.sample(vic_ip, 8)
        if IP_check[0] == 3:
            IP = random.sample(qld_ip, 8)
        if IP_check[0] == 4:
            IP = random.sample(ip_set1, 8)
        if IP_check[0] == 5:
            IP = random.sample(ip_set2, 8)
        if IP_check[0] == 6:
            IP = random.sample(ip_set3, 8)

        # Our ratings options from 1-5
        ratings_options = np.arange(2, 6, 1)
        # Make each of the last elements 15x more likely
        prob = [1.0] * (len(ratings_options) - 1) + [15.0] * 1
        # Normalising to 1.0
        prob /= np.sum(prob)

        # adding login and rating
        for index, var_date in enumerate(varied_date):
            # Use the skewed probability to skew it more than 3.
            ratings_val = np.random.choice(ratings_options, 1, p=prob)
            ratings_info = {
                'rating': ratings_val,
                'created_date': varied_date[index]
            }
            new_user.ratings.create(**ratings_info)

            db_path = (
                Path(BASE_DIR) / 'sim_api' / 'resources' / 'GeoLite2-City' /
                'GeoLite2-City.mmdb'
            )

            # If we can't record this data, we will store it as a Null
            country, state, continent = None, None, None
            geopoint, timezone = None, None
            accuracy_radius = 0

            try:
                if not db_path.exists():
                    raise FileNotFoundError(
                        f'MaxMind DB file not found in {db_path.as_posix()}.'
                    )
                # Read from a MaxMind DB  that we have stored as so the
                # `geoip2` library cna look for the IP address location.
                # noinspection PyUnresolvedReferences
                reader = geoip2.database.Reader(db_path.as_posix())

                location_data = reader.city(str(IP[index]))

                if location_data.country:
                    country = location_data.country.names['en']

                if location_data.subdivisions:
                    state = location_data.subdivisions[0].names['en']

                if location_data.continent:
                    continent = location_data.continent.names['en']

                if location_data.location:
                    accuracy_radius = location_data.location.accuracy_radius
                    geopoint = {
                        'type':
                        'Point',
                        'coordinates': [
                            location_data.location.latitude,
                            location_data.location.longitude
                        ]
                    }
                    timezone = location_data.location.time_zone

                reader.close()
            except (FileNotFoundError, ValueError):
                pass
            except (InvalidDatabaseError, AddressNotFoundError):
                # If our library cannot find a location based on the IP address
                # usually because we're in a localhost testing environment or
                # if the address is somehow bad, then we need to handle this
                # error and allow the response.
                pass
            finally:
                login_data = LoginData(
                    **{
                        'created_datetime': varied_date[index],
                        'continent': continent,
                        'country': country,
                        'state': state,
                        'accuracy_radius': accuracy_radius,
                        'geo_point': geopoint,
                        'timezone': timezone,
                        'ip_address': IP[index]
                    }
                )
                new_user.login_data.append(login_data)

        if user.get("profile", None):
            profile = UserProfile(
                **{
                    'aim': user['profile']['aim'],
                    'highest_education': user['profile']['highest_education'],
                    'sci_tech_exp': user['profile']['sci_tech_exp'],
                    'phase_transform_exp': user['profile']
                    ['phase_transform_exp'],
                }
            )
            new_user.profile = profile

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

        # SAVE
        if DEBUG:
            new_user.save()

        # ==================== # SHARED SIMULATIONS # =================== #
        # Reload the data for the user so we have an ObjectId
        new_user.reload()
        # adding saved simulation to test data
        # 0-3 number of shared sim per user.
        n_shared_sim = random.randint(0, 4)
        if n_shared_sim != 0:
            # Make a random sample based on the number of shared simulations.
            sim_data = random.sample(shared_sim_data, n_shared_sim)

            for s in sim_data:
                user_shared = SharedSimulation(
                    **{
                        'owner_email': new_user.email,
                        'configuration': s['configuration'],
                        'alloy_store': s['alloy_store'],
                        'simulation_results': s['simulation_results']
                    }
                )
                user_shared.save()

        # ==================== # SAVED SIMULATIONS # =================== #
        # Just count the number of simulations
        sim_count = 0

        # Based on the user type, we generate the appropriate number of saved
        # simulations for them.
        if user_type[0] == 1:
            n_saved_sim = random.randint(0, 3)
        elif user_type[0] == 2:
            n_saved_sim = random.randint(4, 7)
        else:
            n_saved_sim = random.randint(8, 10)

        saved_sim_list = random.sample(simulation_data, n_saved_sim)
        # adding
        for s in saved_sim_list:
            saved_sim = SavedSimulation(
                **{
                    'user': new_user.id,
                    'configurations': s['configurations'],
                    'alloy_store': s['alloy_store'],
                    'simulation_results': s['simulation_results']
                }
            )
            saved_sim.save()
        # Just randomly multiple their number of simulation count.
        # Based on the user type, we multiple their saved simulations by the
        # number we think they would run simulations.
        if user_type[0] == 1:
            sim_multiply_factor = random.randint(1, 3)
        elif user_type[0] == 2:
            sim_multiply_factor = random.randint(4, 6)
        else:
            sim_multiply_factor = random.randint(7, 9)
        new_user.simulations_count = n_saved_sim * sim_multiply_factor
        new_user.save()

# adding feedback to test data
print('Seeding feedback to <{}> database:'.format(db.name), file=sys.stderr)
with app.app_context():
    cursor = db.users.find({}, {"_id"})
    for x in tqdm(list(cursor)):
        # to use later(to randomise rating)
        no_of_feedback = random.randint(0, 15)
        feedback = random.sample(feedback_data, no_of_feedback)

        for feedback_to_add in feedback:
            new_user3 = Feedback(
                **{
                    'user': x['_id'],
                    'category': feedback_to_add['category'],
                    'rating': feedback_to_add['rating'],
                    'comment': feedback_to_add['comment']
                }
            )
            new_user3.save()
