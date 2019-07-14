#!/opt/conda/bin/python
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
__date__ = '2019.07.09'
"""manage.py: 

This script is to our CLI script tool to manage the application.
"""

import os
import json
import sys
import unittest
from pathlib import Path

import coverage
from flask.cli import FlaskGroup
from pymongo import MongoClient

from sim_api import create_app

COV = coverage.coverage(
    branch=True,
    include=[
        'sim_api/resources/*',
        'sim_api/alloys/*',
        'sim_api/alloys_service.py',
        'sim_api/schemas.py',
        'sim_api/middleware.py',
    ],
    omit=[
        'sim_api/__init__.py'
        'tests/*',
        'configs/*',
        'logs/*',
    ]
)
COV.start()

BASE_DIR = os.path.dirname(os.path.relpath(__file__))

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command('seed_db')
def seed_alloy_db():
    client = MongoClient(host=os.environ.get('MONGO_HOST'),
                         port=int(os.environ.get('MONGO_PORT')))
    db = client['alloys-dev']
    path = Path(BASE_DIR) / 'simulation' / 'sim_configs.json'
    if os.path.isfile(path):
        with open(path) as f:
            data = json.load(f)

    comp = data['compositions']

    from sim_api.schemas import AlloySchema
    data = AlloySchema().load({'name': 'Alloy-1', 'compositions': comp})
    db.alloys.insert_one(data)
    import pprint
    for alloy in db.alloys.find():
        pprint.pprint(alloy)


@cli.command('flush')
def flush():
    client = MongoClient(host=os.environ.get('MONGO_HOST'),
                         port=int(os.environ.get('MONGO_PORT')))
    client['arc'].drop_collection('alloys')
    client['arc-dev'].drop_collection('alloys')
    client['arc-test'].drop_collection('alloys')
    client.drop_database('arc')
    client.drop_database('arc-dev')
    client.drop_database('arc-test')


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
        print('\nCoverage Summary:')
        COV.report(show_missing=False)
        COV.html_report()
        COV.erase()
        return 0
    sys.exit(result)


if __name__ == '__main__':
    cli()
