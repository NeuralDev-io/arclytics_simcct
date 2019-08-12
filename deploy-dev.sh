#!/bin/bash

TITLE="Arclytics Sim Container Deployment for Development Environment on $HOSTNAME"
RIGHT_NOW=$(date +"%x %r %Z")
TIME_STAMP="Started on $RIGHT_NOW by $USER"

echo "$TITLE"
echo "$TIME_STAMP"
echo ""

echo "Building and deploying docker-compose.yml"
docker-compose up -d --build

echo ""
echo "Executing flush and seed_db on users and simcct containers"
docker-compose exec users python manage.py flush
docker-compose exec simcct python manage.py flush
echo "Flush Complete."
echo ""
docker-compose exec users python manage.py seed_db
echo ""
docker-compose exec simcct python manage.py seed_db
echo "Seed Complete."
echo ""
