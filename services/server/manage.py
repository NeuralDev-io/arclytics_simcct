#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# manage.py
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

from api import create_app, get_app_db
from api.models import User

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
    conn = get_app_db()
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

    tbl = PrettyTable(['No.', 'Username', 'Email'])
    print('Seeding users to <{}> database:'.format(db.name))
    for i, u in enumerate(data):
        User.objects.create(**u)
        tbl.add_row((str(i+1), u['username'], u['email']))
    tbl.align['Username'] = 'l'
    tbl.align['Email'] = 'l'
    print(tbl)


if __name__ == '__main__':
    cli()
