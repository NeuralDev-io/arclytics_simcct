#!/usr/bin/env bash

kubectl exec -it mongo-0 -c mongo-container --namespace arclytics -- \
  mongo --host localhost --port 27017 -u "${MONGO_ROOT_USER}" -p "${MONGO_ROOT_PASSWORD}" --authenticationDatabase admin
