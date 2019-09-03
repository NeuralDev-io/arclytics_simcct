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
kubectl exec mongod-0 -c mongod-container -- mongo --eval 'rs.initiate({_id: "MainRepSet", version: 1, members: [ {_id: 0, host: "mongod-0.mongodb-service.default.svc.cluster.local:27017"}, {_id: 1, host: "mongod-1.mongodb-service.default.svc.cluster.local:27017"}, {_id: 2, host: "mongod-2.mongodb-service.default.svc.cluster.local:27017"} ]});'

# Wait a bit until the replica set should have a primary ready
echo "Waiting for the Replica Set to initialise..."
sleep 30
kubectl exec mongod-0 -c mongod-container -- mongo --eval 'rs.status();'

# Create the admin user (this will automatically disable the localhost exception)
echo "Creating user: 'YW5zdG9fYXJjbHl0aWNz'"
TEMPFILE_PW=$(mktemp)
TEMPFILE_USER=$(mktemp)

# Get the decoded values from the credentials secrets store.
kubectl get secret credentials -o jsonpath="{.data.mongo_root_user}" | base64 -d > ${TEMPFILE_USER}
kubectl get secret credentials -o jsonpath="{.data.mongo_root_password}" | base64 -d > ${TEMPFILE_PW}

ROOT_USER=$(<"${TEMPFILE_USER}")
ROOT_PW=$(<"${TEMPFILE_PW}")

kubectl exec mongod-0 -c mongod-container -- mongo --eval 'db.getSiblingDB("admin").createUser({user:"'"${ROOT_USER}"'",pwd:"'"${ROOT_PW}"'",roles:[{role:"root",db:"admin"}]});'
# TODO(andrew@neuraldev.io): Add the application user.

TEMPFILE_DB=$(mktemp)
kubectl get secret credentials -o jsonpath="{.data.mongo_app_db}" | base64 -d > ${TEMPFILE_DB}
MONGO_APP_DB=$(<"${TEMPFILE_DB}")

TEMPFILE_APP_USER=$(mktemp)
TEMPFILE_APP_USER_PW=$(mktemp)

kubectl get secret credentials -o jsonpath="{.data.mongo_app_user}" | base64 -d > ${TEMPFILE_APP_USER}
kubectl get secret credentials -o jsonpath="{.data.mongo_app_user_password}" | base64 -d > ${TEMPFILE_APP_USER_PW}
APP_USER=$(<"${TEMPFILE_APP_USER}")
APP_USER_PW=$(<"${TEMPFILE_APP_USER_PW}")

kubectl exec mongod-0 -c mongod-container -- mongo "${MONGO_APP_DB}" -u "${ROOT_USER}" -p "${ROOT_PW}" --authenticationDatabase admin \
        --eval "db.getSiblingDB('admin').createUser({user: \"${APP_USER}\", pwd: \"${APP_USER_PW}\", roles:[{role: \"dbOwner\",
        db: \"${MONGO_APP_DB}\"}, {role: \"dbOwner\", db: \"arc_dev\"}]});"

rm ${TEMPFILE_USER}
rm ${TEMPFILE_PW}
rm ${TEMPFILE_DB}
rm ${TEMPFILE_APP_USER}
rm ${TEMPFILE_APP_USER_PW}

echo

