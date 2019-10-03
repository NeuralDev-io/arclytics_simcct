#!/bin/sh

##### Constants
TITLE="Arclytics Sim Service Flask Server Information for $HOSTNAME"
RIGHT_NOW=$(date +"%x %r %Z")
TIME_STAMP="Started on $RIGHT_NOW by $USER"

# defaults
HOST=0.0.0.0
PORT=8001

echo "$TITLE"
echo "$TIME_STAMP"
echo "ENVIRONMENT VARIABLES:"
echo "FLASK_APP: ${FLASK_APP}"
echo "FLASK_ENV: $FLASK_ENV"
echo "APP_SETTINGS: $APP_SETTINGS"
echo "Starting Flask server..."
echo ""

# Uncomment to print ENV variables to Docker logs
echo "ENVIRONMENT VARIABLES"
printenv
echo ""

#rq worker default low --url "redis://${REDIS_HOST}:${REDIS_PORT}/14" &
python manage.py run -h ${HOST} -p ${PORT}
