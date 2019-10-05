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
from datetime import datetime,   timedelta
from os import environ as env
from pathlib import Path
from sys import stderr
from pprint import pprint

import geoip2
from geoip2.errors import AddressNotFoundError
from maxminddb.errors import InvalidDatabaseError
from mongoengine import connect, disconnect_all, get_connection, get_db
from pymongo import MongoClient
from prettytable import PrettyTable
from sim_api import create_app, init_db
from sim_api.extensions.utilities import get_mongo_uri
from sim_api.models import AdminProfile, Feedback, LoginData, SavedSimulation, \
    User, UserProfile

DEBUG = True
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

app = create_app()
# LOAD FROM JSON FILE BY NAME
user_data_path = (
        Path(BASE_DIR) / 'production_data' / 'production_user_data.json'
)
alloy_data_path = Path(BASE_DIR) / 'production_data' / 'production_alloy_data.json'
global_alloy_data_path = Path(BASE_DIR) / 'production_data' / 'production_global_alloys_data.json'
simulation_data_path = Path(BASE_DIR) / 'production_data' / 'production_simulation_data.json'
feedback_data_path = Path(BASE_DIR) / 'production_data' / 'production_feedback_data.json'

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

# test data for rating and login
varied_date = [
    datetime.utcnow() - timedelta(days=10),
    datetime.utcnow(),
    datetime.utcnow() - timedelta(days=603),
    datetime.utcnow() - timedelta(days=365),
    datetime.utcnow() - timedelta(days=900)]
random_ip = [1, 2, 3]

type_of_user = [1, 2, 3]

nsw_ip = ["54.153.174.145", "110.21.5.11", "175.184.220.9", "115.186.226.162",
          "1.42.126.9", "13.54.208.142", "203.219.219.71", "203.24.7.5"]
vic_ip = ["103.224.88.150L", "1.152.105.58", "101.181.99.103", "103.1.205.85",
          "27.253.2.2", "27.253.2.5", "58.108.194.247", "13.77.50.96"]
qld_ip = [
    "61.69.158.62", "120.22.10.205", "61.87.176.0", "220.240.228.236",
    "203.220.77.101", "110.174.244.180", "1.132.96.140", "1.132.96.120",
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

# loading global alloy's
with app.app_context():
    json_data = global_alloy_data
    from sim_api.schemas import AlloySchema

    data = AlloySchema(many=True).load(json_data['alloys'])

    print(
        'Seeding global alloys to <{}> database:'.format(db.name),
        file=sys.stderr
    )
    # Check the correct database -- arc_dev
    db.alloys.insert_many(data)

# tbl = PrettyTable(['Symbol', 'Weight'])

# for alloy in db.alloys.find():
#     print(f"Alloy name: {alloy['name']}")
#     for el in alloy['compositions']:
#         tbl.add_row((el['symbol'], el['weight']))
#     print(tbl)
#     tbl.clear_rows()

# STAY INSIDE THE FLASK APPLICATION CONTEXT
with app.app_context():
    for user in user_data:
        # BASE USER DETAILS
        new_user = User(
            **{
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
            }
        )
        new_user.set_password(user['password'])
        # print(new_user.to_dict())

        # generate random permutation of alloy for each user
        user_type = random.sample(type_of_user, 1)

        if user_type[0] == 1:
            no_of_alloy = random.randint(0, 5)
        if user_type[0] == 2:
            no_of_alloy = random.randint(5, 15)
        if user_type[0] == 3:
            no_of_alloy = random.randint(15, 30)

        alloy = random.sample(alloy_data['alloys'], no_of_alloy)
        # adding alloys
        for alloy_to_add in alloy:
            new_user.saved_alloys.create(**alloy_to_add)

        IP_check = random.sample(random_ip, 1)

        if IP_check[0] == 1:
            IP = random.sample(nsw_ip, 5)
        if IP_check[0] == 2:
            IP = random.sample(vic_ip, 5)
        if IP_check[0] == 3:
            IP = random.sample(qld_ip, 5)
        # adding login and rating
        for index, var_date in enumerate(varied_date):
            ratings_int = random.randint(1, 5)
            ratings_info = {
                'rating': ratings_int,
                'created_date': varied_date[index]
            }
            new_user.ratings.create(**ratings_info)

            db_path = (
                    Path(BASE_DIR) / 'sim_api' / 'resources' / 'GeoLite2-City'
                    / 'GeoLite2-City.mmdb'
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
                        'type': 'Point',
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
                    'phase_transform_exp': user['profile']['phase_transform_exp'],
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

# adding saved simulation to test data
with app.app_context():
    for x in db.users.find({}, {"_id"}):

        for val in simulation_data:
            new_user2 = SavedSimulation(
                **{
                    'user': x['_id'],
                    'configurations': val['configurations'],
                    'alloy_store': val['alloy_store'],
                    'simulation_results': val['simulation_results']
                }
            )
            new_user2.save()

# adding feedback to test data
with app.app_context():
    for x in db.users.find({}, {"_id"}):
        # to use later(to randomise rating)
        no_of_feedback = random.randint(0, 2)
        feedback = random.sample(feedback_data, no_of_feedback)

        for feedback_to_add in feedback:
            new_user3 = Feedback(
                **{
                    'user': feedback_to_add['user'],
                    'category': feedback_to_add['category'],
                    'rating': feedback_to_add['rating'],
                    'comment': feedback_to_add['comment']
                }
            )
            new_user3.save()
