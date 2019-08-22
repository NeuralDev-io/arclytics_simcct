#!/bin/bash

docker-compose exec users python manage.py flush
docker-compose exec simcct python manage.py flush
echo "Flush Complete."
echo ""
docker-compose exec users python manage.py seed_db
echo ""
docker-compose exec simcct python manage.py seed_db
echo "Seed Complete."
echo ""
