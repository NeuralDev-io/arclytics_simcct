#!/bin/bash

type=""
build=0
tty=0
test_type="test"
test_type_title="Flask-Testing Unittests (without coverage)"

# Run only the users tests
users() {
    echo ""
    echo "# ==================== # RUNNING USERS SERVER TESTS # ===================== #"
    echo "# Beginning ${test_type_title} for Users Server"
    echo ""
    if [[ ${tty} == 1 ]]; then
        docker-compose exec -T users python manage.py "${test_type}"
    else
        docker-compose exec users python manage.py "${test_type}"
    fi
    echo ""
    echo "# Finishing ${test_type_title} for Users Server"
    echo "# ======================================================================== #"
}

# Run only the simcct server tests
simcct() {
    echo ""
    echo "# ==================== # RUNNING SIMCCT SERVER TESTS # ==================== #"
    echo "# Beginning ${test_type_title} for SimCCT Server"
    echo ""
    docker-compose exec users python manage.py flush
    if [[ ${tty} == 1 ]]; then
        docker-compose exec -T simcct python manage.py "${test_type}"
    else
        docker-compose exec simcct python manage.py "${test_type}"
    fi
    echo ""
    echo "# Finishing ${test_type_title} for SimCCT Server"
    echo "# ======================================================================== #"
}

# Run server-side tests
server() {
  users
  simcct
}

client() {
  pass
}

# run all tests
all() {
  users
  simcct
  # client
  # e2e
}

##### Check for positional arguments
usage() {
   # shellcheck disable=SC1078
   echo """Usage: run_tests.sh [OPTIONS] COMMAND

A CLI script for running unit tests on the Arclytics Sim Docker Orchestration.

Options:
  -b, --build      Build the Docker containers before running tests.
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

run() {
    ## run appropriate tests
    if [[ "${type}" == "server" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users simcct mongodb redis
            server
            docker-compose down
        else
            server
        fi
    elif [[ "${type}" == "users" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users simcct mongodb redis
            users
            docker-compose down
        else
            users
        fi
    elif [[ "${type}" == "simcct" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users simcct mongodb redis
            simcct
            docker-compose down
        else
            simcct
        fi
    elif [[ "${type}" == "client" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users simcct mongodb redis client
            client
            docker-compose down
        fi
    elif [[ "${type}" == "e2e" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users simcct mongodb redis client
        fi
    elif [[ "${type}" == "all" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users simcct mongodb redis client
            all
            docker-compose down
        else
            all
        fi
    else
        usage
        exit 1
    fi
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
