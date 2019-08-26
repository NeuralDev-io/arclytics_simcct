#!/bin/bash

# Set the Project Name for docker-compose  note: cannot be done any other way
# other than setting it as part of the docker-compose command -p flag.
export COMPOSE_PROJECT_NAME='arc'

# ======================================================= #
# ==================== # Variables # ==================== #
# ======================================================= #
VERSION=1.0.0
command=""
args=""
containers="users simcct client redis mongodb dask-scheduler dask-worker celery-worker"
container_log=""
build=0
detach=0
seed_db=0
build_containers=""
scale=0
scale_num=2
docker_down=0
swagger=0
jupyter=0

test_server=""
test_type="test"
test_type_title="Flask-Testing Unittests (without coverage)"
tty=0

printWidth=0
terminalColWidth=$(tput cols)

# ========================================================= #
# ==================== # ANSI colors # ==================== #
# ========================================================= #
##### -- use these variables to make output in differen colors
esc="\033";  # if this doesn't work, enter an ESC directly

# Foreground colours
blackf="${esc}[30m"; redf="${esc}[31m"; greenf="${esc}[32m"; yellowf="${esc}[33m"
bluef="${esc}[34m"; purplef="${esc}[35m"; cyanf="${esc}[36m"; whitef="${esc}[37m"
# Background colors
blackb="${esc}[40m"; redb="${esc}[41m"; greenb="${esc}[42m"; yellowb="${esc}[43m"
blueb="${esc}[44m"; purpleb="${esc}[45m"; cyanb="${esc}[46m"; whiteb="${esc}[47m"
# Bold, italic, underline, and inverse style toggles
boldon="${esc}[1m"; boldoff="${esc}[22m"; italicson="${esc}[3m";
italicsoff="${esc}[23m"; ulon="${esc}[4m"; uloff="${esc}[24m";
invon="${esc}[7m"; invoff="${esc}[27m";
reset="${esc}[0m"

# ====================================================== #
# ==================== # Messages # ==================== #
# ====================================================== #
function headerMessage() { echo -e "${greenf}${boldon}[ARCLYTICS]  |  $1${boldoff}${reset}"; }
function actionMessage() { echo -e "${whiteb}${redf}${boldon}[ARCLYTICS]  |  $1...${boldoff}${reset}"; echo ""; }
function generalMessage() { echo -e "${yellowf}[ARCLYTICS]  |  $1${reset}"; }
function echoSpace() { echo ""; }
function completeMessage() { echo -e "${greenf}${boldon}[ARCLYTICS]  |  Complete${boldoff}${reset}"; }

function echoLine() {
    width=$terminalColWidth-4;
    printWidth=0
    echo -ne "${greenf}${boldon}# "
    while [[ ${printWidth} -lt ${width} ]]; do
        echo -n -e "=";
        printWidth=$printWidth+1;
    done
    echo -n -e "${greenf}${boldon} #${boldoff}${reset}"
}

# =============================================================== #
# ==================== # Utility Functions # ==================== #
# =============================================================== #
# Run only the users tests
users() {
    headerMessage "RUNNING USERS SERVER TESTS"
    generalMessage "Beginning ${test_type_title} for Users Server"
    echoSpace
    if [[ ${tty} == 1 ]]; then
        generalMessage "docker-compose exec -T users python manage.py ${test_type}"
        docker-compose exec -T users python manage.py "${test_type}"
    else
        generalMessage "docker-compose exec users python manage.py ${test_type}"
        docker-compose exec users python manage.py "${test_type}"
    fi
    generalMessage "Finishing ${test_type_title} for Users Server"
}

# Run only the simcct server tests
simcct() {
    headerMessage "RUNNING SIMCCT SERVER TESTS"
    generalMessage "Beginning ${test_type_title} for SimCCT Server"
    echoSpace
    docker-compose exec users python manage.py flush
    if [[ ${tty} == 1 ]]; then
        generalMessage "docker-compose exec -T simcct python manage.py ${test_type}"
        docker-compose exec -T simcct python manage.py "${test_type}"
    else
        generalMessage "docker-compose exec simcct python manage.py ${test_type}"
        docker-compose exec simcct python manage.py "${test_type}"
    fi
    generalMessage "Finishing ${test_type_title} for SimCCT Server"
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

flushDb() {
    headerMessage "FLUSH BACK-END MICROSERVICES"
    generalMessage "Flushing users microservice database (MongoDB)"
    generalMessage "docker-compose exec users python manage.py flush"
    docker-compose exec users python manage.py flush
    generalMessage "Flushing simcct microservice database (Redis and MongoDB)"
    generalMessage "docker-compose exec simcct python manage.py flush"
    docker-compose exec simcct python manage.py flush
}

# Flush and seed database
flushAndSeedDb() {
    headerMessage "SEED AND FLUSH BACK-END MICROSERVICES"
    generalMessage "Flushing users microservice database (MongoDB)"
    generalMessage "docker-compose exec users python manage.py flush"
    docker-compose exec users python manage.py flush
    generalMessage "Flushing simcct microservice database (Redis and MongoDB)"
    generalMessage "docker-compose exec simcct python manage.py flush"
    docker-compose exec simcct python manage.py flush
    echoSpace
    generalMessage "Seeding users microservice database with users"
    generalMessage "docker-compose exec users python manage.py seed_db"
    docker-compose exec users python manage.py seed_db
    echoSpace
    generalMessage "Seeding simcct microservice database with global alloys"
    generalMessage "docker-compose exec simcct python manage.py seed_db"
    docker-compose exec simcct python manage.py seed_db
    echoSpace
}

# shellcheck disable=SC1079,SC1078,SC2006
upUsage() {
    echo -e """
${greenf}ARCLYTICS CLI SCRIPT

Usage: arclytics.sh up [options] [SERVICE ARGS...]

The Arclytics CLI command to run the containers.

Options:
  -b, --build           Build the Docker containers before running.
  -d, --detach          Run Docker Engine logs in a detached shell mode.
  -s, --seed_db         Seed the MongoDB database with test data.
  --scale SERVICE=NUM   Scale SERVICE to NUM instances. Overrides the
                        'scale' setting in the Compose file if present
  -h, --help            Get the Usage information for this command.

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
${reset}
"""
}

# shellcheck disable=SC1079
testUsage() {
    # shellcheck disable=SC1078
    echo -e """
${greenf}ARCLYTICS CLI SCRIPT

Usage: arclytics.sh up [OPTIONS] [TEST TYPE]

The Arclytics CLI command to run Unit Tests.

Options:
  -b, --build      Build the Docker containers before running tests.
  -t, --tty        Attach a pseudo-TTY to the tests.
  -c, --coverage   Run the unit tests with coverage.
  -h, --help       Get the Usage information for this command.

Test Types (one only):
  all         Run all unit tests for Arclytics Sim
  server      Run the server-side unit tests.
  client      Run the client-side unit tests.
  users       Run only the users tests.
  simcct      Run only the simcct tests.
${reset}
"""
}

# shellcheck disable=SC1079
usage() {
   # shellcheck disable=SC1078
   echo -e """
${greenf}ARCLYTICS CLI SCRIPT

The Arclytics CLI script for running docker and docker-compose commands on the
Arclytics Sim Docker orchestration.

Usage:
arclytics.sh build [SERVICE ARGS...]
arclytics.sh up [options] [SERVICE ARGS...]
arclytics.sh logs [SERVICE]
arclytics.sh test [options] [TEST TYPE]
arclytics.sh down [options]
arclytics.sh [COMMAND]

Options:
  -b, --build      Build the Docker containers before running.
  -d, --detach     Run Docker Engine logs in a detached shell mode.
  -s, --seed_db    Seed the MongoDB database with test data.
  -h, --help       Get the Usage information for this script.

  Test Options:
  -b, --build      Build the Docker containers before running tests.
  -t, --tty        Attach a pseudo-TTY to the tests.
  -c, --coverage   Run the unit tests with coverage.

  Down Options:
  -D, --docker     Stop the containers using the Docker PS stat.

Commands:
  build       Build the Docker images from docker-compose.yml only (passing services
              to build specific ones or leave empty to build all).
  up          Run the main containers in docker-compose.yml or provide a list of
              arguments to run only those provided.
  logs        Get the logs of the container.
  ps          List the running containers
  stats       Display a live stream of container(s) resource usage statistics
  flush       Flush both Redis datastore and MongoDB database only.
  seed        Seed the microservices with test data and flush both Redis
              datastore and MongoDB database.
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

Test Types (one only):
  all         Run all unit tests for Arclytics Sim
  server      Run the server-side unit tests.
  client      Run the client-side unit tests.
  users       Run only the users tests.
  simcct      Run only the simcct tests.
${reset}
"""
}

# ==================================================================== #
# ==================== # Main Command Functions # ==================== #
# ==================================================================== #
run_tests() {
    ## run appropriate tests
    if [[ "${test_server}" == "server" ]]; then
        if [[ ${build} == 1 ]]; then
            generalMessage "docker-compose up -d --build ${containers}"
            docker-compose up -d --build "${containers}"
            server
            generalMessage "docker-compose down"
            docker-compose down
        else
            server
        fi
    elif [[ "${test_server}" == "users" ]]; then
        if [[ ${build} == 1 ]]; then
            generalMessage "docker-compose up -d --build ${containers}"
            docker-compose up -d --build "${containers}"
            users
            generalMessage "docker-compose down"
            docker-compose down
        else
            users
        fi
    elif [[ "${test_server}" == "simcct" ]]; then
        if [[ ${build} == 1 ]]; then
            generalMessage "docker-compose up -d --build ${containers}"
            docker-compose up -d --build "${containers}"
            simcct
            generalMessage "docker-compose down"
            docker-compose down
        else
            simcct
        fi
    elif [[ "${test_server}" == "client" ]]; then
        if [[ ${build} == 1 ]]; then
            generalMessage "docker-compose up -d --build ${containers}"
            docker-compose up -d --build "${containers}"
            client
            generalMessage "docker-compose down"
            docker-compose down
        fi
    elif [[ "${test_server}" == "e2e" ]]; then
        if [[ ${build} == 1 ]]; then
            generalMessage "docker-compose up -d --build ${containers}"
            docker-compose up -d --build "${containers}"
        fi
    elif [[ "${test_server}" == "all" ]]; then
        if [[ ${build} == 1 ]]; then
            generalMessage "docker-compose up -d --build ${containers}"
            docker-compose up -d --build "${containers}"
            all
            generalMessage "docker-compose down"
            docker-compose down
        else
            all
        fi
    else
        testUsage
        exit 1
    fi
    completeMessage
}

# shellcheck disable=SC2086
run() {
    ## run appropriate tests
    if [[ "${command}" == "build" ]]; then
        headerMessage "BUILDING ARCLYTICS SIM CONTAINERS ONLY"
        generalMessage "docker-compose build ${build_containers}"
        docker-compose build ${build_containers}
    elif [[ "${command}" == "up" ]]; then
        headerMessage "RUN ARCLYTICS SIM CONTAINERS"

        if [[ ${scale} == 1 ]]; then
            containers="--scale ${scale_service} ${containers}"
        fi

        if [[ ${swagger} == 1 ]]; then
            containers="${containers} swagger"
        fi

        if [[ ${jupyter} == 1 ]]; then
            containers="${containers} jupyter"
        fi

        if [[ ${build} == 1 ]]; then
            if [[ ${detach} == 1 ]]; then
                generalMessage "docker-compose up -d --build ${containers}"
                docker-compose up -d --build ${containers}
            else
                generalMessage "docker-compose up --build ${containers}"
                docker-compose up --build ${containers}
            fi
        else
            if [[ ${detach} == 1 ]]; then
                generalMessage "docker-compose up -d ${containers}"
                docker-compose up -d ${containers}
            else
                generalMessage "docker-compose up ${containers}"
                docker-compose up ${containers}
            fi
        fi

        if [[ ${seed_db} == 1 ]]; then
            echoSpace
            flushAndSeedDb
        fi
    elif [[ "${command}" == "ps" ]]; then
        headerMessage "ARCLYTICS SIM RUNNING CONTAINERS"
        generalMessage "docker ps --size ${args}"
        docker ps --size ${args}
    elif [[ "${command}" == "logs" ]]; then
        headerMessage "ARCLYTICS SIM CONTAINER LOGS"
        generalMessage "docker-compose logs ${container_log}"
        docker-compose logs ${container_log}
    elif [[ "${command}" == "down" ]]; then
        headerMessage "STOPPING ARCLYTICS SIM CONTAINERS"
        if [[ "${docker_down}" == 1 ]]; then
            running=$(docker ps -aq)
            if [[ ${running} == "" ]]; then
                generalMessage "No containers running"
                docker ps
            else
                generalMessage "docker stop \$(docker ps -aq)"
                # shellcheck disable=SC2046
                docker stop ${running}
            fi
        else
            generalMessage "docker-compose down ${args}"
            docker-compose down ${args}
        fi
    elif [[ "${command}" == "stats" ]]; then
        headerMessage "ARCLYTICS SIM CONTAINER STATS"
        generalMessage "docker stats ${args}"
        docker stats ${args}
    elif [[ "${command}" == "prune" ]]; then
        headerMessage "PRUNE ARCLYTICS SIM DOCKER ORCHESTRATION"
        generalMessage "docker stop $(docker ps -aq)"
        # shellcheck disable=SC2046
        docker stop $(docker ps -aq)
        generalMessage "docker system prune -af"
        docker system prune -af
    else
        usage
        exit 1
    fi
    completeMessage
}

# =========================================================== #
# ==================== # CLI Arguments # ==================== #
# =========================================================== #
if [[ $1 == "" ]]; then
  usage
  exit 1
fi

while [[ "$1" != "" ]] ; do
    case $1 in
        ps )
            command="ps"
            args=$2
            while [[ "$3" != "" ]] ; do
                args="${args} $3"
                shift
            done
            run
            ;;
        stats )
            command="stats"
            args=$2
            while [[ "$3" != "" ]] ; do
                args="${args} $3"
                shift
            done
            run
            ;;
        down )
            command="down"
            while [[ "$2" != "" ]] ; do
                case $2 in
                    -D | --docker )
                        docker_down=1
                        ;;
                    * )
                        args=$2
                        while [[ "$3" != "" ]] ; do
                            args="${args} $3"
                            shift
                        done
                esac
                shift
            done
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
            build_containers=$2
            while [[ "$3" != "" ]] ; do
                build_containers="${build_containers} $3"
                shift
            done
            run
            exit 0
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
                    --scale )
                        scale=1
                        # Shift to the arg after --scale
                        shift
                        # Get the first argument after --scale flag
                        # TODO(andrew@neuraldev.io): Currently only taking one
                        scale_service=$2
                        # scale_num="$(cut -d'=' -f2 <<< "${scale_service}" )"
                        shift
                        ;;
                    -h | --help )
                        upUsage
                        exit 0
                        ;;
                    * )
                        containers=$2
                        while [[ "$3" != "" ]] ; do
                            containers="${containers} $3"
                            shift
                        done
                        ;;
                esac
                shift
            done
            run
            exit 0
            ;;
        logs )
            command="logs"
            container_log=$2
            run
            exit 0
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
                        testUsage
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
            exit 0
            ;;
        flush )
            flushDb
            exit 0
            ;;
        seed )
            flushAndSeedDb
            exit 0
            ;;
        -h | --help )
            usage
            exit 0
            ;;
    esac
    shift
done
