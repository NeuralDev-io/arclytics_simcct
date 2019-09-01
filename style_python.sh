#!/usr/bin/env bash


BASEDIR=$PWD
CONFIG="${BASEDIR}/.yapf.cfg"
ARC_DIR="${BASEDIR}/services/arclytics"
EXCLUDE_DIR="${BASEDIR}/services/client"
echo "Running yapf formatter"
echo "Current Directory: ${BASEDIR}"
echo "Configuration used: ${CONFIG}"
echo "Exclude directory: ${EXCLUDE_DIR}"
yapf -ri --verbose --style=${CONFIG} --exclude=${EXCLUDE_DIR} ${ARC_DIR}
