#!/bin/bash

type=""
build=0
tty=0
fails=""

#inspect() {
#  if [ "$1" -ne 0 ]; then
#    fails="${fails} $2"
#  fi
#}

# Run only the users-server tests
users-server() {
  echo "# ==================== # USERS-SERVER TESTS # ===================== #"
  echo "Beginning Test Coverage for Users-Server"
  if [[ ${tty} == 1 ]]; then
      docker-compose exec -T users-server python manage.py test
  else
      docker-compose exec users-server python manage.py test
  fi
  inspect $? users-server
  echo "Finishing Test Coverage for Users-Server"
  echo "# =========================================================== #"
}

# Run only the simcct-server tests
simcct-server() {
  echo "# ==================== # SIMCCT-SERVER TESTS # ==================== #"
  echo "Beginning Test Coverage for SimCCT-Server"
  if [[ ${tty} == 1 ]]; then
    docker-compose exec -T simcct-server python manage.py test
  else
    docker-compose exec simcct-server python manage.py test
  fi
  inspect $? simcct-server
  echo "Finishing Test Coverage for SimCCT-Server"
  echo "# =========================================================== #"
}

# Run server-side tests
server() {
  users-server
  simcct-server
}

client() {
  pass
}

# run all tests
all() {
  users-server
  simcct-server
  # client
  # e2e
}

##### Check for positional arguments
usage() {
   echo """Usage: run_tests.sh [OPTIONS] COMMAND

A CLI script for running unit tests on the Arclytics Sim Docker Orchestration.

Options:
    -b, --build    Build the Docker containers before running tests.
    -t, --tty      Attach a pseudo-TTY to the tests.

Commands:
    all              Run all unit tests for Arclytics Sim
    server           Run the server-side unit tests.
    client           Run the client-side unit tests.
    users-server     Run only the users-server tests.
    simcct-server    Run only the simcct-serve tests.
   """
}

run() {
    ## run appropriate tests
    if [[ "${type}" == "server" ]]; then
        echo "# ========== # Running server-side tests! # ========== #"
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users-server simcct-server mongodb redis
        fi

        server
        docker-compose down
    elif [[ "${type}" == "users-server" ]]; then
        echo "# ========== # Running users-server tests! # ==========#"
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users-server simcct-server mongodb redis
        fi
        users-server
        docker-compose down
    elif [[ "${type}" == "simcct-server" ]]; then
        echo ""
        echo "# ========== # Running simcct-server tests! # ==========#"
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users-server simcct-server mongodb redis
        fi
        simcct-server
        docker-compose down
    elif [[ "${type}" == "client" ]]; then
        echo ""
        echo "# ========== # Running client-side tests! # ========== #"
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users-server simcct-server mongodb redis client
        fi
        client
    elif [[ "${type}" == "e2e" ]]; then
        echo ""
        echo "# ========== # Running e2e tests! # ========== #"
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users-server simcct-server mongodb redis client
        fi
    elif [[ "${type}" == "all" ]]; then
        echo ""
        echo "# ========== # Running all tests! # ========== #"
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build users-server simcct-server mongodb redis client
        fi
        all
        docker-compose down
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
        -b | --build )    build=1
                          ;;
        -t | --tty )      tty=1
                          ;;
        -h | --help )     usage
                          exit
                          ;;
        * )               type=$1
                          run
                          exit 1
    esac
    shift
done

# return proper code
if [ -n "${fails}" ]; then
    echo ""
    echo "TESTS FAILED: ${fails}"
    exit 1
else
    echo ""
    echo "ALL TESTS PASSED!"
    exit 0
fi
