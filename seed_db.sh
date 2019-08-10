#!/bin/bash

docker-compose exec users python manage.py flush
docker-compose exec simcct python manage.py flush
echo "Flush Complete."
docker-compose exec users python manage.py seed_db
docker-compose exec simcct python manage.py seed_db
echo "Seed Complete."
