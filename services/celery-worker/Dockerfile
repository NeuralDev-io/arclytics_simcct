FROM python:3.7.3-alpine

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --quiet --no-cache-dir --upgrade pip
RUN pip install --quiet --no-cache-dir -r requirements.txt

# add app
COPY . /usr/src/app

ENTRYPOINT celery worker -A celery_worker.celery -l info