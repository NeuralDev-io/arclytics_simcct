FROM python:3.7.3-alpine

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

# Even though celery developers recommend not to run as root, there is
# no issues as we are using an Alpine image.
# We force it to run regardless.
USER root

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --quiet --no-cache-dir --upgrade pip
RUN pip install --quiet --no-cache-dir -r requirements.txt

# add app
COPY . /usr/src/app

# install our arc_logging library
WORKDIR /usr/src/app/arc_logging
RUN python setup.py install

WORKDIR /usr/src/app

ENTRYPOINT celery worker -A celery_worker.celery -l debug --uid 0 --gid 0 -B
