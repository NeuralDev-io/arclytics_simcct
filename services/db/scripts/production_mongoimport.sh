# REFERENCES:
# [1] https://docs.mongodb.com/manual/reference/program/mongoexport/

# Connect to mongodb container
# kubectl exec -it mongo-0 bash

# kubectl cp ./services/db/production_data/* mongo-0:/data/backups/

mongoimport --host localhost \
    --port 27017 \
    -u "${MONGO_ROOT_USER}" \
    -p "${MONGO_ROOT_PASSWORD}" \
    --db "${MONGO_APP_DB}" \
    --authenticationDatabase admin \
    --collection users \
    --drop \
    --file /data/backups/production_user_data.json

mongoimport --host localhost \
    --port 27017 \
    -u "${MONGO_ROOT_USER}" \
    -p "${MONGO_ROOT_PASSWORD}" \
    --db "${MONGO_APP_DB}" \
    --authenticationDatabase admin \
    --collection alloys \
    --drop \
    --file /data/backups/production_global_alloys.json
