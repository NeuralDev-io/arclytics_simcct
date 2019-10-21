#!/bin/bash
# shellcheck disable=SC2086
# ============================================================================ #
# Script to connect to the first Mongod instance running in a container of the
# Kubernetes StatefulSet, via the Mongo Shell, to initalise a MongoDB Replica
# Set and create a MongoDB root user with root privileges on the admin doc.
#
# IMPORTANT: Only run this once 3 StatefulSet mongod pods are show with status
# running (to see pod status run: $ kubectl get all)
# ============================================================================ #

# Initiate replica set configuration
echo "Configuring the MongoDB Replica Set"
kubectl exec mongo-0 -c mongo-container --namespace=arclytics -- mongo --eval 'rs.initiate({_id: "MainRepSet", version: 1,
    members: [
        {_id: 0, host: "mongo-0.mongo-service.arclytics.svc.cluster.local:27017"},
        {_id: 1, host: "mongo-1.mongo-service.arclytics.svc.cluster.local:27017"},
        {_id: 2, host: "mongo-2.mongo-service.arclytics.svc.cluster.local:27017"}
    ]});'

# Wait for the MongoDB Replica Set to have a primary ready
echo "Waiting for the MongoDB Replica Set to initialise..."
kubectl exec mongo-0 -c mongo-container --namespace=arclytics -- mongo --eval 'while (rs.status().hasOwnProperty("myState") && rs.status().myState != 1) { print("."); sleep(1000); };'
#sleep 2 # Just a little more sleep to ensure everything is ready!
sleep 30 # More sleep to ensure everything is ready! (3.6.0 workaround for https://jira.mongodb.org/browse/SERVER-31916 )
echo "...initialisation of MongoDB Replica Set completed"
echo

# Create the admin user (this will automatically disable the localhost exception)
echo "Creating user: 'YW5zdG9fYXJjbHl0aWNz'"
TEMPFILE_USER=$(mktemp)
TEMPFILE_PW=$(mktemp)

# Get the decoded values from the credentials secrets store.
kubectl get secret credentials -o jsonpath="{.data.mongo_root_user}" --namespace=arclytics | base64 -d > ${TEMPFILE_USER}
kubectl get secret credentials -o jsonpath="{.data.mongo_root_password}" --namespace=arclytics | base64 -d > ${TEMPFILE_PW}

# Get the decoded password back from the temp files.
ROOT_USER=$(<"${TEMPFILE_USER}")
ROOT_PW=$(<"${TEMPFILE_PW}")

# Run an evaluation command on Mongo to create the Root user.
kubectl exec mongo-0 -c mongo-container --namespace=arclytics -- mongo --eval "db.getSiblingDB(\"admin\").createUser({user:\"${ROOT_USER}\",pwd:\"${ROOT_PW}\",roles:[{role:\"root\",db:\"admin\"}]});"

TEMPFILE_DB=$(mktemp)
kubectl get secret credentials -o jsonpath="{.data.mongo_app_db}" --namespace=arclytics | base64 -d > ${TEMPFILE_DB}
MONGO_APP_DB=$(<"${TEMPFILE_DB}")

TEMPFILE_APP_USER=$(mktemp)
TEMPFILE_APP_USER_PW=$(mktemp)

kubectl get secret credentials -o jsonpath="{.data.mongo_app_user}" --namespace=arclytics | base64 -d > ${TEMPFILE_APP_USER}
kubectl get secret credentials -o jsonpath="{.data.mongo_app_user_password}" --namespace=arclytics | base64 -d > ${TEMPFILE_APP_USER_PW}
APP_USER=$(<"${TEMPFILE_APP_USER}")
APP_USER_PW=$(<"${TEMPFILE_APP_USER_PW}")

# Create an application user on the main Production Database
kubectl exec mongo-0 -c mongo-container --namespace=arclytics -- mongo -u "${ROOT_USER}" -p "${ROOT_PW}" --authenticationDatabase admin \
        --eval "db.getSiblingDB(\"admin\").createUser({user: \"${APP_USER}\", pwd: \"${APP_USER_PW}\", roles:[{role: \"dbOwner\", db: \"${MONGO_APP_DB}\"}]});"

# Create a TTL index on the date field for the celery_beat collection for collecting logged in user data
kubectl exec mongo-0 -c mongo-container -- mongo -u "${ROOT_USER}" -p "${ROOT_PW}" --authenticationDatabase admin \
        --eval "db.celery_beat.createIndex({ \"date\": 1 }, { expireAfterSeconds: 1209600 });"

rm ${TEMPFILE_USER}
rm ${TEMPFILE_PW}
rm ${TEMPFILE_DB}
rm ${TEMPFILE_APP_USER}
rm ${TEMPFILE_APP_USER_PW}

echo

