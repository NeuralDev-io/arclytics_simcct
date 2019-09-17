#!/usr/bin/env bash

echo 'Creating Development application database development test data data'

# mongoimport -- GOES HERE
mongoimport --db arc_dev \
    --collection alloys \
    --drop --file /data/test/global_alloys.json \
    --port 27017

mongoimport --db arc_dev \
    --collection users \
    --drop \
    --file /data/test/users.json \
    --port 27017
