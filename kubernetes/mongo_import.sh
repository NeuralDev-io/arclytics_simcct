# REFERENCES:
# [1] https://docs.mongodb.com/manual/reference/program/mongoexport/

# Connect to mongodb container
# -- kubectl exec -it mongo-0 bash

# -- kubectl cp ./services/db/production_data/* mongo-0:/data/backups/
# -- export $(egrep -v '^#' .env | xargs)

# Create the admin user (this will automatically disable the localhost exception)
TEMPFILE_USER=$(mktemp)
TEMPFILE_PW=$(mktemp)

# Get the decoded values from the credentials secrets store.
kubectl get secret credentials -o jsonpath="{.data.mongo_root_user}" --namespace=arclytics | base64 -d > "${TEMPFILE_USER}"
kubectl get secret credentials -o jsonpath="{.data.mongo_root_password}" --namespace=arclytics | base64 -d > "${TEMPFILE_PW}"

# Get the decoded password back from the temp files.
MONGO_ROOT_USER=$(<"${TEMPFILE_USER}")
MONGO_ROOT_PASSWORD=$(<"${TEMPFILE_PW}")

TEMPFILE_DB=$(mktemp)
kubectl get secret credentials -o jsonpath="{.data.mongo_app_db}" --namespace=arclytics | base64 -d > ${TEMPFILE_DB}
MONGO_APP_DB=$(<"${TEMPFILE_DB}")

kubectl exec mongo-0 -c mongo-container --namespace=arclytics -- \
    mongoimport --host localhost \
        --port 27017 \
        -u "${MONGO_ROOT_USER}" \
        -p "${MONGO_ROOT_PASSWORD}" \
        --db "${MONGO_APP_DB}" \
        --authenticationDatabase admin \
        --collection users \
        --drop \
        --file /data/backups/production_user_data.json

kubectl exec mongo-0 -c mongo-container --namespace=arclytics -- \
    mongoimport --host localhost \
        --port 27017 \
        -u "${MONGO_ROOT_USER}" \
        -p "${MONGO_ROOT_PASSWORD}" \
        --db "${MONGO_APP_DB}" \
        --authenticationDatabase admin \
        --collection alloys \
        --drop \
        --file /data/backups/production_global_alloys.json
