#!/bin/sh
echo "Waiting for Mongo..."
while ! socat - TCP4:mongodb:27017; do
    sleep 0.1
done

gunicorn -b 0.0.0.0:8001 manage:app
