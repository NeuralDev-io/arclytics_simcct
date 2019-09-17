FROM mongo:4.0.11

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

# make a directory to store scripts
RUN mkdir -p /data/backups
RUN mkdir -p /data/db/scripts
RUN mkdir -p /data/test
WORKDIR /data/test

COPY ./test_data /data/test

COPY ./docker-entrypoint.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/docker-entrypoint.sh
