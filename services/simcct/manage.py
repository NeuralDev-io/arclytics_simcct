#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# manage.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']

__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.04'
"""manage.py: 

This script is to our CLI script tool to manage the application.
"""

import os
import json
import sys
import unittest
from pathlib import Path

import coverage
import redis
from flask.cli import FlaskGroup
from prettytable import PrettyTable
from pymongo import MongoClient
from rq import Connection, Worker

import settings
from sim_api.app import create_app
from sim_api.models import User, AdminProfile, UserProfile

COV = coverage.coverage(
    branch=True,
    include=[
        'sim_api/schemas.py', 'sim_api/resources/*', 'sim_api/alloys/*',
        'sim_api/alloys_service.py', 'sim_api/middleware.py',
        'sim_api/sim_session.py', 'sim_api/models.py',
        'sim_api/resources/users.py', 'sim_api/resources/auth.py',
        'sim_api/middleware.py', 'sim_api/mongodb.py', 'sim_api/token.py',
        'sim_api/resources/share.py', 'sim_api/resources/admin_auth.py',
        'sim_api/resources/ratings.py'
    ],
    omit=[
        'arc_api/app.py'
        'configs/flask_conf.py',
        'tests/*',
        'configs/*',
        'data/*',
        'logger/*',
        'logs/*',
    ]
)
COV.start()

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command('run_worker')
def run_worker():
    redis_url = app.config['REDIS_URL']
    with Connection(redis.from_url(redis_url)):
        worker = Worker(app.config['QUEUES'])
        worker.work()


@cli.command('flush')
def flush():
    """Drop all collections in the database."""
    from mongoengine.connection import get_db
    db = get_db('default')
    print('Dropping <{}.{}> database:'.format(db.name, 'users'),file=sys.stderr)
    db.users.drop()


@cli.command('flush_all')
def flush():
    if os.environ.get('FLASK_ENV', 'development') == 'production':
        client = MongoClient(
            host=str(os.environ.get('MONGO_HOST')),
            port=int(os.environ.get('MONGO_PORT')),
            username=str(os.environ.get('MONGO_APP_USER')),
            password=str(os.environ.get('MONGO_APP_USER_PASSWORD')),
            authSource='admin',
            replicaSet='MainRepSet',
        )
        redis_client = redis.Redis(
            host=os.environ.get('REDIS_HOST'),
            port=os.environ.get('REDIS_PORT'),
            password=os.environ.get('REDIS_PASSWORD')
        )
        db = os.environ.get('MONGO_APP_DB')
        print('Dropping <{}> database:'.format(db), file=sys.stderr)
        client.drop_database(db)
    else:
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


@cli.command('seed_db')
def seed_user_db():
    """Seed the database with some basic users."""
    from mongoengine.connection import get_db
    db = get_db('default')

    user_data_path = Path(settings.BASE_DIR) / 'seed_user_data.json'
    alloy_data_path = Path(settings.BASE_DIR) / 'seed_alloy_data.json'
    if os.path.isfile(user_data_path):
        with open(user_data_path) as f:
            user_data = json.load(f)
    if os.path.isfile(alloy_data_path):
        with open(alloy_data_path) as f:
            alloy_data = json.load(f)

    tbl = PrettyTable(['No.', 'Email', 'Name', 'Admin', 'Alloys'])
    print('Seeding users to <{}> database:'.format(db.name), file=sys.stderr)
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
    if os.environ.get('FLASK_ENV', 'development') == 'production':
        client = MongoClient(
            host=str(os.environ.get('MONGO_HOST')),
            port=int(os.environ.get('MONGO_PORT')),
            username=str(os.environ.get('MONGO_APP_USER')),
            password=str(os.environ.get('MONGO_APP_USER_PASSWORD')),
            authSource='admin',
            replicaSet='MainRepSet',
        )
    else:
        client = MongoClient(
            host=os.environ.get('MONGO_HOST'),
            port=int(os.environ.get('MONGO_PORT'))
        )
    db = client[os.environ.get('MONGO_APP_DB', 'arc_dev')]
    path = Path(settings.BASE_DIR) / 'seed_global_alloys_data.json'
    if os.path.isfile(path):
        with open(path) as f:
            json_data = json.load(f)

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
    tests = unittest.TestLoader().discover('tests', pattern='test_api_users.py')
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
