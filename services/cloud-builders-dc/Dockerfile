# From cloud-builders-community
# https://github.com/GoogleCloudPlatform/cloud-builders-community/tree/master/docker-compose
# RUN before cloudbuild.yaml can be applied:
# docker build --build-arg version=1.24.1 -t asia.gcr.io/arc-sim-testing/docker:latest .
FROM ubuntu:bionic

ARG version=1.24.1

# https://docs.docker.com/compose/install/
RUN \
   apt -y update && \
   apt -y install ca-certificates curl docker.io && \
   curl -L "https://github.com/docker/compose/releases/download/$version/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose && \
        chmod +x /usr/local/bin/docker-compose

ENTRYPOINT ["/usr/local/bin/docker-compose"]
