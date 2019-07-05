# base image
FROM python:3.7.3-alpine

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

# install dependencies
RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
    apk add --no-cache libffi-dev build-base py2-pip python2-dev && \
    apk add netcat-openbsd

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# add docker-entrypoint.sh
COPY ./docker-entrypoint.sh /usr/src/app/docker-entrypoint.sh
RUN chmod +x /usr/src/app/docker-entrypoint.sh
RUN ln -s /usr/src/app/docker-entrypoint.sh /docker-entrypoint.sh

# add app
COPY . /usr/src/app

# Start the container with entrypoint or comment to use manual below
ENTRYPOINT ["/docker-entrypoint.sh"]
# Comment above and uncomment below to run gunicorn server
#ENTRYPOINT ["/docker-entrypoint.sh", "-S", "gunicorn"]

# uncomment to run server manually
#CMD ["gunicorn", "-b", "0.0.0.0:8000", "api.app:app"]
#CMD ["python", "manage.py", "run", "-h", "0.0.0.0", "-p", "8000"]