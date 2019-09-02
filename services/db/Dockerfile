FROM mongo:4.0.11

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

# make a directory to store scripts
RUN mkdir -p /data/db/scripts
COPY ./scripts /data/db/scripts
COPY seed_alloy.json /data/seed_alloy.json
COPY ./entrypoint.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/entrypoint.sh
