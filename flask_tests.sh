#!/bin/sh

docker-compose exec -T users-server python manage.py test
