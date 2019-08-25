#!/bin/bash

export COMPOSE_PROJECT_NAME='arc'

docker-compose up -d --build

##### Check for positional arguments
usage() {
   # shellcheck disable=SC1078
   echo """Usage: arclytics.sh [OPTIONS] COMMAND

A CLI script for running unit tests on the Arclytics Sim Docker Orchestration.

Options:
  -b, --build      Build the Docker containers before running.
  -t, --tty        Attach a pseudo-TTY to the tests.
  -c, --coverage   Run the unit tests with coverage.

Commands:
  all         Run all unit tests for Arclytics Sim
  server      Run the server-side unit tests.
  client      Run the client-side unit tests.
  users       Run only the users tests.
  simcct      Run only the simcct tests.
"""
}

if [[ $1 == "" ]]; then
  usage
  exit 1
fi

while [[ "$1" != "" ]] ; do
    case $1 in
        -b | --build )
            build=1
            ;;
        -t | --tty )
            tty=1
            ;;
        -c | --coverage )
            coverage=1
            test_type="test_coverage"
            test_type_title="Flask-Testing Unittests with Coverage"
            ;;
        -h | --help )
            usage
            exit 0
            ;;
        * )
            type=$1
            run
            exit 1
    esac
    shift
done
