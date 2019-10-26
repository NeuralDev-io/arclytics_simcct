#!/usr/bin/env bash
# REFERENCES:
# [1] https://docs.mongodb.com/manual/reference/program/mongodump/#bin.mongodump
# [2] https://docs.mongodb.com/manual/tutorial/backup-and-restore-tools/
# [3] https://docs.mongodb.com/manual/reference/program/mongorestore/

# Connect to mongodb container
# kubectl exec -it mongo-0 bash

kubectl cp ./services/db/production_data/dump_data \
    mongo-0:/data/backups/dump_data

kubectl exec mongo-0 -c mongo-container -- \
    mongorestore --host localhost \
        --port 27017 \
        -u "${MONGO_ROOT_USER}" \
        -p "${MONGO_ROOT_PASSWORD}" \
        --authenticationDatabase admin \
        /data/backups/dump_data

#mongo --host localhost \
#    --port 27017 \
#    -u "${MONGO_ROOT_USER}" \
#    -p "${MONGO_ROOT_PASSWORD}" \
#    --authenticationDatabase admin
