#!/bin/sh

##### Constants
TITLE="Arclytics Sim Users Service Flask Server Information for $HOSTNAME"
RIGHT_NOW=$(date +"%x %r %Z")
TIME_STAMP="Started on $RIGHT_NOW by $USER"

##### Check if DB is up and running
echo "Waiting for Mongo..."

while ! nc -z mongodb 27017; do
    sleep 0.1
done

echo "Mongo started."

##### Check for positional arguments
usage() {
    echo "Usage: start_server.sh [-S WSGI server] [-H host] [-P port]"
}

# defaults
HOST=0.0.0.0
PORT=8000
WSGI=""

while [ "$1" != "" ]; do
    case $1 in
        -H | --host )
            shift
            HOST=$1
            ;;
        -P | --port )
            shift
            PORT=$1
            ;;
        -S | --server )
            shift
            WSGI=$1
            ;;
        -h | --help )
            usage
            exit
            ;;
        * )
            usage
            exit 1
    esac
    shift
done

echo "$TITLE"
echo "$TIME_STAMP"
echo "ENVIRONMENT VARIABLES:"
echo "FLASK_APP: Arclytics Sim Users Service"
echo "FLASK_ENV: $FLASK_ENV"
echo "APP_SETTINGS: $APP_SETTINGS"
echo "Starting Flask server..."
echo ""

# if [ $WSGI == ""]; then
#     exit
if [ "$WSGI" == "gunicorn" ]; then
    gunicorn -b $HOST:$PORT api.__init__:app
else
    python manage.py run -h $HOST -p $PORT
fi
