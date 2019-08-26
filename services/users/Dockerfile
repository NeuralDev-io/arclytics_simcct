# base image
FROM python:3.7.3-alpine

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

# install dependencies
RUN apk update && \
    apk add --virtual build-deps gcc && \
    apk add --no-cache build-base python3-dev && \
    apk add --no-cache libffi-dev py-pip && \
    apk add --no-cache netcat-openbsd

# Pillow dependencies
# RUN apk --no-cache add python-dev  jpeg-dev \
#                       zlib-dev \
#                       freetype-dev \
#                       lcms2-dev \
#                       openjpeg-dev \
#                       tiff-dev \
#                       tk-dev \
#                       tcl-dev \
#                       harfbuzz-dev \
#                       fribidi-dev

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --quiet --upgrade pip
RUN pip install --quiet --no-cache-dir -r requirements.txt

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
#CMD ["gunicorn", "-b", "0.0.0.0:8000", "users_app.app:app"]
#CMD ["python", "manage.py", "run", "-h", "0.0.0.0", "-p", "8000"]
