#!/bin/bash

# Set the Project Name for docker-compose  note: cannot be done any other way
# other than setting it as part of the docker-compose command.
export COMPOSE_PROJECT_NAME='arc'

command=""
containers="users simcct client redis mongodb dask-scheduler dask-worker celery-worker"
container_log=""
build=0
detach=0
seed_db=0
build_containers=""
swagger=0
jupyter=0

test_server=""
test_type="test"
test_type_title="Flask-Testing Unittests (without coverage)"
tty=0

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

# shellcheck disable=SC1079
usage() {
   # shellcheck disable=SC1078
   echo """Usage:
arclytics.sh [OPTIONS] COMMAND [OPTIONAL CONTAINERS]

arclytics.sh build [OPTIONAL SERVICES]
arclytics.sh [OPTIONS] up [OPTIONAL CONTAINERS]
arclytics.sh logs [SERVICE]
arclytics.sh test [TEST OPTIONS] [TEST TYPE]

A CLI script for running docker-compose on the Arclytics Sim Docker Orchestration.

Options:
  -b, --build      Build the Docker containers before running.
  -d, --detach     Run Docker Engine logs in a detached shell mode.
  -s, --seed_db    Seed the MongoDB database with test data.
  -h, --help       Get the Usage information for this script.

  Test Options:
  -b, --build      Build the Docker containers before running tests.
  -t, --tty        Attach a pseudo-TTY to the tests.
  -c, --coverage   Run the unit tests with coverage.

Commands:
  build       Build the Docker images from docker-compose.yml only (passing services
              to build specific ones or leave empty to build all).
  up          Run the main containers in docker-compose.yml (users, simcct,
              client redis mongodb celery-worker dask-scheduler dask-worker).
  logs        Get the logs of the container.
  test        Run unit tests on the microservices.
  down        Stop all containers.
  prune       Prune all stopped images, containers, and networks.

Optional Containers:
  -S, --swagger    Run the Swagger container with the cluster.
  -J, --jupyter    Run the Jupyter container with the cluster.

Service (only one for logs):
  users
  celery-worker
  simcct
  dask-scheduler
  dask-worker
  redis
  mongodb
  jupyter
  swagger

Test Services:
  all         Run all unit tests for Arclytics Sim
  server      Run the server-side unit tests.
  client      Run the client-side unit tests.
  users       Run only the users tests.
  simcct      Run only the simcct tests.

"""
}

run_tests() {
    ## run appropriate tests
    if [[ "${test_server}" == "server" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build "${containers}"
            server
            docker-compose down
        else
            server
        fi
    elif [[ "${test_server}" == "users" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build "${containers}"
            users
            docker-compose down
        else
            users
        fi
    elif [[ "${test_server}" == "simcct" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build "${containers}"
            simcct
            docker-compose down
        else
            simcct
        fi
    elif [[ "${test_server}" == "client" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build "${containers}"
            client
            docker-compose down
        fi
    elif [[ "${test_server}" == "e2e" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build "${containers}"
        fi
    elif [[ "${test_server}" == "all" ]]; then
        if [[ ${build} == 1 ]]; then
            docker-compose up -d --build "${containers}"
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

# shellcheck disable=SC2086
run() {
    ## run appropriate tests
    if [[ "${command}" == "build" ]]; then
        docker-compose build ${build_containers}
    elif [[ "${command}" == "up" ]]; then
        if [[ ${swagger} == 1 ]]; then
            containers="${containers} swagger"
        fi

        if [[ ${jupyter} == 1 ]]; then
            containers="${containers} jupyter"
        fi

        if [[ ${build} == 1 ]]; then
            if [[ ${detach} == 1 ]]; then
                docker-compose up -d --build ${containers}
            else
                docker-compose up --build ${containers}
            fi
        else
            if [[ ${detach} == 1 ]]; then
                docker-compose up -d ${containers}
            else
                docker-compose up ${containers}
            fi
        fi

        if [[ ${seed_db} == 1 ]]; then
            echo ""
            docker-compose exec users python manage.py flush
            docker-compose exec simcct python manage.py flush
            docker-compose exec users python manage.py seed_db
            docker-compose exec simcct python manage.py seed_db
        fi
    elif [[ "${command}" == "logs" ]]; then
        docker-compose logs ${container_log}
    elif [[ "${command}" == "down" ]]; then
        docker-compose down
    elif [[ "${command}" == "prune" ]]; then
        docker-compose down
        docker system prune -af
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
        down )
            command="down"
            run
            ;;
        prune )
            command="prune"
            run
            ;;
        -d | --detach )
            detach=1
            ;;
        -b | --build )
            build=1
            ;;
        build )
            command="build"
            while [[ "$2" != "" ]] ; do
                case $2 in
                    * )
                        build_containers="${build_containers} $2"
                        ;;
                esac
                shift
            done
            run
            ;;
        up )
            command="up"

            while [[ "$2" != "" ]] ; do
                case $2 in
                    -b | --build )
                        build=1
                        ;;
                    -d | --detach )
                        detach=1
                        ;;
                    -s | --seed_db )
                        seed_db=1
                        ;;
                    -S | --swagger )
                        swagger=1
                        ;;
                    -J | --jupyter )
                        jupyter=1
                        ;;
                esac
                shift
            done
            run
            ;;
        logs )
            command="logs"
            container_log=$2
            run
            ;;
        test )
            while [[ "$2" != "" ]] ; do
                case $2 in
                    -b | --build )
                        build=1
                        ;;
                    -t | --tty )
                        tty=1
                        ;;
                    -c | --coverage )
                        test_type="test_coverage"
                        test_type_title="Flask-Testing Unittests with Coverage"
                        ;;
                    -h | --help )
                        usage
                        exit 0
                        ;;
                    * )
                        test_server=$2
                        run_tests
                        exit 0
                esac
                shift
            done
            run_tests
            ;;
        -h | --help )
            usage
            exit 0
            ;;
    esac
    shift
done
