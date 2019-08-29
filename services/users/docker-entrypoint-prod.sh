#!/bin/sh

##### Check if DB is up and running
echo "Waiting for Mongo..."

while ! nc -z mongodb 27017; do
    sleep 0.1
done

echo "Mongo started."

gunicorn -b 0.0.0.0:8000 manage:app
