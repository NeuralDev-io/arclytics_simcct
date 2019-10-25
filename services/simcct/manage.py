#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# manage.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '2.0.0'
__status__ = 'production'
__date__ = '2019.06.04'
"""manage.py: 

This script is to our CLI script tool to manage the application and the 
entrypoint to create a Flask application.
"""

import json
import os
import sys
import unittest
from pathlib import Path

import coverage
import redis
from flask.cli import FlaskGroup
from mongoengine.connection import connect, disconnect_all, get_db
from prettytable import PrettyTable
from pymongo import MongoClient

from sim_api import create_app
from sim_api.models import AdminProfile, User, UserProfile

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

DATETIME_FMT = '%Y-%m-%dT%H:%M:%S%z'
DATE_FMT = '%Y-%m-%d'

COV = coverage.coverage(
    branch=True,
    include=[
        'sim_api/schemas.py', 'sim_api/resources/*', 'sim_api/alloys/*',
        'sim_api/alloys_service.py', 'sim_api/middleware.py',
        'sim_api/sim_session_service.py', 'sim_api/models.py',
        'sim_api/resources/users.py', 'sim_api/resources/auth.py',
        'sim_api/middleware.py', 'sim_api/mongodb.py', 'sim_api/token.py',
        'sim_api/resources/share.py', 'sim_api/resources/admin_auth.py',
        'sim_api/resources/ratings.py', 'sim_api/resources/last_simulation.py',
        'sim_api/resources/save_simulation.py',
        'sim_api/resources/simulation.py', 'sim_api/resources/sim_alloys.py',
        'sim_api/resources/sim_configurations.py',
        'sim_api/resources/global_alloys.py'
    ],
    omit=[
        'arc_api/__init__.py'
        'configs/flask_conf.py', 'configs/gunicorn_conf.py', 'tests/*',
        'configs/*', 'data/*', 'logger/*', 'logs/*',
        'sim_api/extensions/Session/*', 'sim_api/extensions/SimSession/*',
        'flask-fluentd-logger/*'
    ]
)
COV.start()

# Create an instance of the global Flask app for the SimCCT Server.
app = create_app()
# Add the Flask Instance to the Flask CLI tool to use as a factory to create
# more Flask instances when you run a CLI command.
cli = FlaskGroup(create_app=create_app)


@cli.command('flush')
def flush():
    """Drop all collections in the database."""
    if os.environ.get('FLASK_ENV', 'development') == 'production':
        print('You should not flush the database in production.')
        return

    client = MongoClient(
        host=os.environ.get('MONGO_HOST'),
        port=int(os.environ.get('MONGO_PORT'))
    )
    redis_client = redis.Redis(
        host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT')
    )

    # List of collections to drop
    collections = [
        'users', 'feedback', 'saved_simulations', 'shared_simulations',
        'alloys'
    ]

    # Start dropping those collections for each of our dev environments.
    print(
        'Dropping collections in <{}> database:'.format('arc_dev'),
        file=sys.stderr
    )

    for c in collections:
        client['arc_dev'].drop_collection(c)

    print(
        'Dropping collections in <{}> database:'.format('arc_test'),
        file=sys.stderr
    )

    for c in collections:
        client['arc_dev'].drop_collection(c)

    dbs_created = redis_client.config_get('databases')
    print('Flushing Redis: {}'.format(dbs_created), file=sys.stderr)
    redis_client.flushall()


@cli.command('flush_all')
def flush():
    """Flush all databases and data stores."""
    if os.environ.get('FLASK_ENV', 'development') == 'production':
        print('You should not flush the database in production.')
        return

    client = MongoClient(
        host=os.environ.get('MONGO_HOST'),
        port=int(os.environ.get('MONGO_PORT'))
    )
    redis_client = redis.Redis(
        host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT')
    )
    print('Dropping <{}> database:'.format('arc_dev'), file=sys.stderr)
    client.drop_database('arc_dev')
    print('Dropping <{}> database:'.format('arc_test'), file=sys.stderr)
    client.drop_database('arc_test')

    dbs_created = redis_client.config_get('databases')
    print('Flushing Redis: {}'.format(dbs_created), file=sys.stderr)
    redis_client.flushall()


@cli.command('test_conn')
def test_data_conn():
    """
    A simple CLI command to test the Mongo and Redis connections when in a
    production environment.
    """
    if os.environ.get('FLASK_ENV', 'development') == 'production':
        disconnect_all()

        _db_name = str(os.environ.get('MONGO_APP_DB'))
        _host = os.environ.get('MONGO_HOST')
        _port = os.environ.get('MONGO_PORT')
        _username = os.environ.get('MONGO_APP_USER')
        _password = str(os.environ.get('MONGO_APP_USER_PASSWORD'))
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
        db = get_db('default')

        redis_client = redis.Redis(
            host=os.environ.get('REDIS_HOST'),
            port=os.environ.get('REDIS_PORT'),
            password=os.environ.get('REDIS_PASSWORD')
        )
        print(f'MongoDB Client: \n{client}\n', file=sys.stderr)
        print(f'MongoDB Database: \n{db}\n', file=sys.stderr)
        print(f'Redis Datastore Client: \n{redis_client}\n', file=sys.stderr)
    else:
        print(
            f'This CLI command is only used for Production\nCurrent Flask ENV: '
            f'{os.environ.get("FLASK_ENV")}',
            file=sys.stderr
        )


@cli.command('seed_db')
def seed_user_db():
    """Seed the database with some basic users."""
    db = get_db('default')
    print('Seeding users to <{}> database:'.format(db.name), file=sys.stderr)

    user_data_path = Path(BASE_DIR) / 'seed_user_data.json'
    alloy_data_path = Path(BASE_DIR) / 'seed_alloy_data.json'
    if os.path.isfile(user_data_path):
        with open(user_data_path) as f:
            user_data = json.load(f)
    if os.path.isfile(alloy_data_path):
        with open(alloy_data_path) as f:
            alloy_data = json.load(f)

    tbl = PrettyTable(['No.', 'Email', 'Name', 'Admin', 'Alloys'])
    for i, u in enumerate(user_data):
        new_user = User(
            email=u['email'],
            first_name=u['first_name'],
            last_name=u['last_name']
        )
        new_user.set_password(u['password'])

        if u['first_name'] == 'Tony' or u['first_name'] == 'Natasha':
            for alloy in alloy_data['alloys']:
                new_user.saved_alloys.create(**alloy)

        if u.get("profile", None):
            profile = UserProfile(
                **{
                    'aim': u['profile']['aim'],
                    'highest_education': u['profile']['highest_education'],
                    'sci_tech_exp': u['profile']['sci_tech_exp'],
                    'phase_transform_exp': u['profile']['phase_transform_exp'],
                }
            )
            new_user.profile = profile

        if u.get('is_admin', False):
            profile = AdminProfile(
                position=u['admin_profile']['position'],
                mobile_number=u['admin_profile']['mobile_number']
            )
            profile.verified = True
            new_user.disable_admin = not u.get('is_admin', False)
            new_user.admin_profile = profile

        new_user.verified = True
        new_user.save()
        tbl.add_row(
            (
                str(i + 1), u['email'],
                '{} {}'.format(u['first_name'],
                               u['last_name']), new_user.is_admin,
                new_user.saved_alloys.count()
            )
        )
    tbl.align['Name'] = 'l'
    tbl.align['Email'] = 'l'
    print(tbl)


@cli.command('seed_alloys_db')
def seed_alloy_db():
    """Seed the global alloys database."""
    if os.environ.get('FLASK_ENV', 'development') == 'production':
        client = MongoClient(
            host=str(os.environ.get('MONGO_HOST')),
            port=int(os.environ.get('MONGO_PORT')),
            username=str(os.environ.get('MONGO_APP_USER')),
            password=str(os.environ.get('MONGO_APP_USER_PASSWORD')),
            authSource='admin',
        )
    else:
        client = MongoClient(
            host=os.environ.get('MONGO_HOST'),
            port=int(os.environ.get('MONGO_PORT'))
        )
    db = client[os.environ.get('MONGO_APP_DB', 'arc_dev')]
    path = Path(BASE_DIR) / 'seed_global_alloys_data.json'
    if os.path.isfile(path):
        with open(path) as f:
            json_data = json.load(f)

    with app.app_context():
        from sim_api.schemas import AlloySchema
        data = AlloySchema(many=True).load(json_data['alloys'])

        print(
            'Seeding global alloys to <{}> database:'.format(db.name),
            file=sys.stderr
        )
        # Check the correct database -- arc_dev
        db.alloys.insert_many(data)

    tbl = PrettyTable(['Symbol', 'Weight'])

    for alloy in db.alloys.find():
        print(f"Alloy name: {alloy['name']}")
        for el in alloy['compositions']:
            tbl.add_row((el['symbol'], el['weight']))
        print(tbl)
        tbl.clear_rows()


@cli.command()
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_api_*.py')
    result = unittest.TextTestRunner(verbosity=3).run(tests)
    if result.wasSuccessful():
        return 0
    sys.exit(result)


@cli.command('test_coverage')
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_api_*.py')
    result = unittest.TextTestRunner(verbosity=4).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report(show_missing=False)
        COV.html_report()
        COV.erase()
        return 0
    sys.exit(result)


if __name__ == '__main__':
    cli()
