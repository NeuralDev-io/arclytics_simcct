#!/bin/bash

docker-compose exec arclytics mongo arc --eval "db.dropDatabase()"

docker-compose exec arclytics mongo arc_test --eval "db.dropDatabase()"

docker-compose exec arclytics mongo arclytics --eval "db.dropDatabase()"
