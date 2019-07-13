#!/usr/bin/env bash


BASEDIR=$PWD
CONFIG="${BASEDIR}/.yapf.cfg"
USERS_DIR="${BASEDIR}/services/users-server"
SIM_DIR="${BASEDIR}/services/simcct-server"
EXCLUDE_DIR="${BASEDIR}/services/client"
echo "Running yapf formatter"
echo "Current Directory: ${BASEDIR}"
echo "Configuration used: ${CONFIG}"
echo "Exclude directory: ${EXCLUDE_DIR}"
yapf -ri --verbose --style=${CONFIG} --exclude=${EXCLUDE_DIR} ${USERS_DIR} ${SIM_DIR}
