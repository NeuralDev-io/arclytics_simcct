FROM python:3.7.3-alpine

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# add app
COPY . /usr/src/app

#ENTRYPOINT celery flower -A celery_runner -l info --address=0.0.0.0 --port=5555
ENTRYPOINT celery worker -A celery_worker.celery -l info
