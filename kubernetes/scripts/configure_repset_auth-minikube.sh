#!/bin/bash
##
# Script to connect to the first Mongod instance running in a container of the
# Kubernetes StatefulSet, via the Mongo Shell, to initalise a MongoDB Replica
# Set and create a MongoDB admin user.
#
# IMPORTANT: Only run this once 3 StatefulSet mongod pods are show with status
# running (to see pod status run: $ kubectl get all)
##

# Check for password argument
#if [[ $# -eq 0 ]] ; then
#    echo 'You must provide one argument for the password of the "main_admin" user to be created'
#    echo '  Usage:  configure_repset_auth.sh MyPa55wd123'
#    echo
#    exit 1
#fi

# Initiate replica set configuration
echo "Configuring the MongoDB Replica Set"
#kubectl exec mongod-0 -c mongod-container -- mongo --eval 'rs.initiate({_id: "MainRepSet", version: 1, members: [ {_id: 0, host: "mongod-0.mongodb-service.default.svc.cluster.local:27017"}, {_id: 1, host: "mongod-1.mongodb-service.default.svc.cluster.local:27017"}, {_id: 2, host: "mongod-2.mongodb-service.default.svc.cluster.local:27017"} ]});'

# Wait a bit until the replica set should have a primary ready
echo "Waiting for the Replica Set to initialise..."
#sleep 30
#kubectl exec mongod-0 -c mongod-container -- mongo --eval 'rs.status();'

# Create the admin user (this will automatically disable the localhost exception)
echo "Creating user: 'YW5zdG9fYXJjbHl0aWNz'"
TEMPFILE=$(mktemp)

# shellcheck disable=SC2086
kubectl get secret credentials -o jsonpath="{.data.mongo_root_password}" | base64 -d > ${TEMPFILE}
ROOT_PW=$(<$TEMPFILE)
echo "${ROOT_PW}"
#kubectl exec mongod-0 -c mongod-container -- mongo --eval 'db.getSiblingDB("admin").createUser({user:"YW5zdG9fYXJjbHl0aWNz",pwd:"'"${1}"'",roles:[{role:"root",db:"admin"}]});'
# TODO(andrew@neuraldev.io): Add the application user.
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
echo

