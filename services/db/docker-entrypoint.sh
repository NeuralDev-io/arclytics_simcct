#!/usr/bin/env bash

echo 'Creating Development application database data'

#mongo "${MONGO_APP_DB}" \
#        --host localhost \
#        --port 27017 \
#        -u "${MONGO_ROOT_USER}" \
#        -p "${MONGO_ROOT_PASSWORD}" \
#        --authenticationDatabase admin \
#        --eval "db.createUser({user: \"${MONGO_APP_USER}\", pwd: \"${MONGO_APP_USER_PASSWORD}\", roles:
#        [{role: \"dbOwner\", db: \"${MONGO_APP_DB}\"},
#        {role: \"dbOwner\", db: \"arc_dev\"},
#        {role: \"dbOwner\", db: \"arc_test\"}]});"

# mongoimport -- GOES HERE
