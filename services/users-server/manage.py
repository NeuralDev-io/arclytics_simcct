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
__copyright__ = 'Copyright (C) 2019, NeuralDev'
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

from flask.cli import FlaskGroup
from prettytable import PrettyTable
import coverage

from users_api import create_app, get_flask_mongo
from users_api.models.models import User

COV = coverage.coverage(
    branch=True,
    include=[
        'users_api/models.py',
        'users_api/users.py',
        'users_api/auth.py',
        'users_api/auth_decorators.py',
        'users_api/mongodb.py',
    ],
    omit=[
        'users_api/__init__.py'
        'config.py',
        'tests/*',
        'simulation/*',
        'configs/*',
        'data/*',
        'logger/*',
        'logs/*',
    ]
)
COV.start()

app = create_app()
cli = FlaskGroup(create_app=create_app)


# TODO: Command to recreate database
@cli.command('recreate_db')
def recreate_db():
    pass


@cli.command()
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_api_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    sys.exit(result)


@cli.command('flush')
def flush():
    """Drop all collections in the database."""
    from mongoengine.connection import get_db
    conn = get_flask_mongo()
    db = get_db('default')
    conn.instance.client.drop_database(db.name)


@cli.command('seed_db')
def seed_user_db():
    """Seed the database with some basic users."""
    from configs.settings import BASE_DIR
    from mongoengine.connection import get_db
    db = get_db('default')

    path = Path(BASE_DIR) / 'data' / 'seed_user_data.json'
    if os.path.isfile(path):
        with open(path) as f:
            data = json.load(f)

    tbl = PrettyTable(['No.', 'Email', 'Name'])
    print('Seeding users to <{}> database:'.format(db.name))
    for i, u in enumerate(data):
        new_user = User(
            email=u['email'],
            first_name=u['first_name'],
            last_name=u['last_name']
        )
        new_user.set_password(u['password'])
        new_user.save()
        tbl.add_row(
            (
                str(i + 1),
                u['email'],
                '{} {}'.format(u['first_name'], u['last_name'])
            )
        )
    tbl.align['Name'] = 'l'
    tbl.align['Email'] = 'l'
    print(tbl)


@cli.command('test_coverage')
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_api_*.py')
    result = unittest.TextTestRunner(verbosity=3).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report(show_missing=True)
        COV.html_report()
        COV.erase()
        return 0
    sys.exit(result)


if __name__ == '__main__':
    cli()
