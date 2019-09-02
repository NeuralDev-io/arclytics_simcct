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
from rq import Connection, Worker

import settings
from arc_app.app import create_app, get_flask_mongo
from arc_app.models import User, AdminProfile, UserProfile

COV = coverage.coverage(
    branch=True,
    include=[
        'arc_app/models.py', 'arc_app/resources/users.py',
        'arc_app/resources/auth.py', 'arc_app/middleware.py',
        'arc_app/mongodb.py', 'arc_app/token.py', 'arc_app/resources/share.py',
        'arc_app/resources/admin_auth.py', 'arc_app/resources/ratings.py'
    ],
    omit=[
        'arc_app/app.py'
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


@cli.command()
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_api_*.py')
    result = unittest.TextTestRunner(verbosity=3).run(tests)
    if result.wasSuccessful():
        return 0
    sys.exit(result)


@cli.command('flush')
def flush():
    """Drop all collections in the database."""
    from mongoengine.connection import get_db
    conn = get_flask_mongo()
    db = get_db('default')
    print('Dropping <{}> database:'.format(db.name), file=sys.stderr)
    conn.instance.client.drop_database(db.name)


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
