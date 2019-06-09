# base image
FROM python:3.7.3-alpine

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# add app
COPY . /usr/src/app

# entrypoint - only if using unix env
#COPY docker-entrypoint.sh /usr/local/bin/
#RUN ln -s /usr/local/bin/docker-entrypoint.sh /
#ENTRYPOINT ['docker-entrypoint.sh']
# Uncomment to run gunicorn server
#CMD ['-S', 'gunicorn']

# uncomment to run server manually
#CMD ["gunicorn", "-b", "0.0.0.0:8000", "api.app:app"]
CMD ["python", "manage.py", "run", "-h", "0.0.0.0", "-p", "8000"]