#!/usr/bin/env bash

echo 'Creating application user and db'

mongo "${MONGO_APP_DB}" \
        --host localhost \
        --port 27017 \
        -u "${MONGO_ROOT_USER}" \
        -p "${MONGO_ROOT_PASSWORD}" \
        --authenticationDatabase admin \
        --eval "db.createUser({user: \"${MONGO_APP_USER}\", pwd: \"${MONGO_APP_USER_PASSWORD}\", roles:
        [{role: \"dbOwner\", db: \"${MONGO_APP_DB}\"},
        {role: \"dbOwner\", db: \"arc_dev\"},
        {role: \"dbOwner\", db: \"arc_test\"}]});"

echo 'Importing application database development test data'
mongoimport "${MONGO_APP_DB}" \
    --host localhost \
    --port 27017 \
    -u "${MONGO_ROOT_USER}" \
    -p "${MONGO_ROOT_PASSWORD}" \
    --authenticationDatabase admin \
    --db "${MONGO_APP_DB}" \
    --collection alloys \
    --drop \
    --file /data/backups/production_global_alloys.json \

mongoimport "${MONGO_APP_DB}" \
    --host localhost \
    --port 27017 \
    -u "${MONGO_ROOT_USER}" \
    -p "${MONGO_ROOT_PASSWORD}" \
    --db "${MONGO_APP_DB}" \
    --collection users \
    --drop \
    --file /data/backups/production_user_data.json \
