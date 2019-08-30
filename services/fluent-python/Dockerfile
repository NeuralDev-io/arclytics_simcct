FROM python:3.7.3-alpine

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

RUN apk update && \
    apk add --no-cache py-pip

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add and install requirements
#COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --quiet --upgrade pip
RUN pip install --quiet --no-cache-dir \
                flask==1.0.2 \
                fluent-logger==0.9.3 \
                Flask-Cors==3.0.7 \
                gunicorn==19.9.0

COPY ./app.py /usr/src/app

CMD ["gunicorn",  "-b 0.0.0.0:5000", "app:app"]
