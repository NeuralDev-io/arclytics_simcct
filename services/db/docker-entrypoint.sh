#!/usr/bin/env bash

echo 'Creating Development application database development test data data'

# mongoimport -- GOES HERE
mongoimport --db arc_dev --collection alloys --drop --file /data/test/seed_alloy.json --jsonArray --port 27017
# User Password not encoded properly. Must use the Python manage.py CLI
#mongoimport --db arc_dev --collection users --drop --file /data/test/seed_user.json --jsonArray --port 27017
