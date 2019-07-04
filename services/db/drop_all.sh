#!/bin/bash

docker-compose exec users-db mongo arc --eval "db.dropDatabase()"

docker-compose exec users-db mongo arc_test --eval "db.dropDatabase()"

docker-compose exec users-db mongo arclytics --eval "db.dropDatabase()"
