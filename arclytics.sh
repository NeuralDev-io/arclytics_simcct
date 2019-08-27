#!/bin/bash
# shellcheck disable=SC2086

# Set the Project Name for docker-compose  note: cannot be done any other way
# other than setting it as part of the docker-compose COMMAND -p flag.
export COMPOSE_PROJECT_NAME='arc'

# ======================================================= #
# ==================== # Variables # ==================== #
# ======================================================= #
VERSION=1.1.1
WORKDIR="$(dirname "$(readlink -f "$0")")"
DOCKER_COMPOSE_PATH="${WORKDIR}/docker-compose.yml"
COMMAND=""
ARGS=""
CONTAINER_ARGS="users simcct client redis mongodb dask-scheduler dask-worker celery-worker"
CONTAINER_LOG=""
BUILD_CONTAINER_ARGS=""
BUILD_FLAG=0
DETACH_FLAG=0
SEED_DB_FLAG=0
SCALE_FLAG=0
SCALE_CONTAINERS_ARGS=""
DOCKER_DOWN_FLAG=0
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
        docker-compose -f ${DOCKER_COMPOSE_PATH} exec -T users python manage.py "${test_type}"
    else
        generalMessage "docker-compose exec users python manage.py ${test_type}"
        docker-compose -f ${DOCKER_COMPOSE_PATH} exec users python manage.py "${test_type}"
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
        docker-compose -f ${DOCKER_COMPOSE_PATH} exec -T simcct python manage.py "${test_type}"
    else
        generalMessage "docker-compose exec simcct python manage.py ${test_type}"
        docker-compose -f ${DOCKER_COMPOSE_PATH} exec simcct python manage.py "${test_type}"
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
    docker-compose -f ${DOCKER_COMPOSE_PATH} exec users python manage.py flush
    generalMessage "Flushing simcct microservice database (Redis and MongoDB)"
    generalMessage "docker-compose exec simcct python manage.py flush"
    docker-compose -f ${DOCKER_COMPOSE_PATH} exec simcct python manage.py flush
}

# Flush and seed database
flushAndSeedDb() {
    headerMessage "SEED AND FLUSH BACK-END MICROSERVICES"
    generalMessage "Flushing users microservice database (MongoDB)"
    generalMessage "docker-compose exec users python manage.py flush"
    docker-compose -f ${DOCKER_COMPOSE_PATH} exec users python manage.py flush
    generalMessage "Flushing simcct microservice database (Redis and MongoDB)"
    generalMessage "docker-compose exec simcct python manage.py flush"
    docker-compose -f ${DOCKER_COMPOSE_PATH} exec simcct python manage.py flush
    echoSpace
    generalMessage "Seeding users microservice database with users"
    generalMessage "docker-compose exec users python manage.py SEED_DB_FLAG"
    docker-compose -f ${DOCKER_COMPOSE_PATH} exec users python manage.py SEED_DB_FLAG
    echoSpace
    generalMessage "Seeding simcct microservice database with global alloys"
    generalMessage "docker-compose exec simcct python manage.py SEED_DB_FLAG"
    docker-compose -f ${DOCKER_COMPOSE_PATH} exec simcct python manage.py SEED_DB_FLAG
    echoSpace
}

# shellcheck disable=SC1079,SC1078,SC2006
upUsage() {
    echo -e """
${greenf}ARCLYTICS CLI SCRIPT

Usage: arclytics.sh up [options] [SERVICE ARGS...]

The Arclytics CLI COMMAND to run the containers.

Options:
  -b, --build           Build the Docker CONTAINER_ARGS before running.
  -d, --detach          Run Docker Engine logs in a detached shell mode.
  -s, --seed_db         Seed the MongoDB database with test data.
  --scale SERVICE=NUM   Scale SERVICE to NUM instances. Overrides the
                        \`--scale\` setting in the Compose file if present
  -h, --help            Get the Usage information for this COMMAND.

Optional Containers:
  -S, --swagger         Run the Swagger container with the cluster.
  -J, --jupyter         Run the Jupyter container with the cluster.

Service (only one for \`logs\`; * default for \`up\`):
  users *
  celery-worker *
  simcct *
  dask-scheduler *
  dask-worker *
  redis *
  mongodb *
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

The Arclytics CLI COMMAND to run Unit Tests.

Options:
  -b, --build      Build the Docker CONTAINER_ARGS before running tests.
  -t, --tty        Attach a pseudo-TTY to the tests.
  -c, --coverage   Run the unit tests with coverage.
  -h, --help       Get the Usage information for this COMMAND.

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
arclytics.sh up --scale [SERVICE=NUM]
arclytics.sh logs [SERVICE]
arclytics.sh test [options] [TEST TYPE]
arclytics.sh down [options]
arclytics.sh scale [SERVICE=NUM...]
arclytics.sh [COMMAND]

Options:
  -b, --build           Build the Docker CONTAINER_ARGS before running.
  -d, --detach          Run Docker Engine logs in a detached shell mode.
  -s, --seed_db         Seed the MongoDB database with test data.
  -h, --help            Get the Usage information for this script.

  Up Options:
  --scale SERVICE=NUM   Scale the a single container when running the cluster.
  -S, --swagger         Run the Swagger container with the cluster.
  -J, --jupyter         Run the Jupyter container with the cluster.

  Test Options:
  -b, --build           Build the Docker CONTAINER_ARGS before running tests.
  -t, --tty             Attach a pseudo-TTY to the tests.
  -c, --coverage        Run the unit tests with coverage.

  Down Options:
  -D, --docker          Stop the CONTAINER_ARGS using the Docker PS stat.

Commands:
  build       Build the Docker images from docker-compose.yml only (passing services
              to build specific ones or leave empty to build all).
  up          Run the main CONTAINER_ARGS in docker-compose.yml or provide a list of
              arguments to run only those provided.
  logs        Get the logs of the container.
  ps          List the running containers.
  stats       Display a live stream of container(s) resource usage statistics.
  flush       Flush both Redis datastore and MongoDB database only.
  seed        Seed the microservices with test data and flush both Redis
              datastore and MongoDB database.
  test        Run unit tests on the microservices.
  down        Stop all containers.
  prune       Prune all stopped images, CONTAINER_ARGS, and networks.
  pwd         Get the full path directory of the Arclytics CLI script.
  scale       Set number of CONTAINER_ARGS to run for a service. Numbers are specified
              in the form \`service=num\` as arguments.

Service (only one for \`logs\`; * default for \`up\`):
  users *
  celery-worker *
  simcct *
  dask-scheduler *
  dask-worker *
  redis *
  mongodb *
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
dockerPs() {
    headerMessage "ARCLYTICS SIM RUNNING CONTAINER_ARGS"
    generalMessage "docker ps --size ${ARGS}"
    docker ps --size ${ARGS}
    completeMessage
}

dockerLogs() {
    headerMessage "ARCLYTICS SIM CONTAINER LOGS"
    generalMessage "docker-compose logs ${CONTAINER_LOG}"
    docker-compose -f ${DOCKER_COMPOSE_PATH} logs ${CONTAINER_LOG}
    completeMessage
}

dockerStats() {
    headerMessage "ARCLYTICS SIM CONTAINER STATS"
    generalMessage "docker stats ${ARGS}"
    docker stats ${ARGS}
}

dockerSystemPrune() {
    headerMessage "PRUNE ARCLYTICS SIM DOCKER ORCHESTRATION"
    running_container_ids=$(docker ps -aq)
    generalMessage "docker stop ${running_container_ids}"
    docker stop ${running_container_ids}
    generalMessage "docker system prune -af"
    docker system prune -af
    completeMessage
}

containerDown() {
    headerMessage "STOPPING ARCLYTICS SIM CONTAINER_ARGS"
    if [[ "${DOCKER_DOWN_FLAG}" == 1 ]]; then
        running=$(docker ps -aq)
        if [[ ${running} == "" ]]; then
            generalMessage "No CONTAINER_ARGS running"
            docker ps
        else
            generalMessage "docker stop \$(docker ps -aq)"
            # shellcheck disable=SC2046
            docker stop ${running}
        fi
    else
        generalMessage "docker-compose down ${ARGS}"
        docker-compose -f ${DOCKER_COMPOSE_PATH} down ${ARGS}
    fi
    completeMessage
}

scaleContainers() {
  headerMessage "SCALING ARCLYTICS SIM CONTAINER_ARGS"
  docker-compose -f ${DOCKER_COMPOSE_PATH} SCALE_FLAG ${SCALE_CONTAINERS_ARGS}
  completeMessage
}

# shellcheck disable=SC2086
run_tests() {
    ## run appropriate tests
    if [[ "${test_server}" == "server" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            generalMessage "docker-compose up -d --BUILD_FLAG ${CONTAINER_ARGS}"
            docker-compose -f ${DOCKER_COMPOSE_PATH} up -d --BUILD_FLAG "${CONTAINER_ARGS}"
            server
            generalMessage "docker-compose down"
            docker-compose -f ${DOCKER_COMPOSE_PATH} down
        else
            server
        fi
    elif [[ "${test_server}" == "users" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            generalMessage "docker-compose up -d --BUILD_FLAG ${CONTAINER_ARGS}"
            docker-compose -f ${DOCKER_COMPOSE_PATH} up -d --BUILD_FLAG "${CONTAINER_ARGS}"
            users
            generalMessage "docker-compose down"
            docker-compose -f ${DOCKER_COMPOSE_PATH} down
        else
            users
        fi
    elif [[ "${test_server}" == "simcct" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            generalMessage "docker-compose up -d --BUILD_FLAG ${CONTAINER_ARGS}"
            docker-compose -f ${DOCKER_COMPOSE_PATH} up -d --BUILD_FLAG "${CONTAINER_ARGS}"
            simcct
            generalMessage "docker-compose down"
            docker-compose -f ${DOCKER_COMPOSE_PATH} down
        else
            simcct
        fi
    elif [[ "${test_server}" == "client" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            generalMessage "docker-compose up -d --BUILD_FLAG ${CONTAINER_ARGS}"
            docker-compose -f ${DOCKER_COMPOSE_PATH} up -d --BUILD_FLAG "${CONTAINER_ARGS}"
            client
            generalMessage "docker-compose down"
            docker-compose -f ${DOCKER_COMPOSE_PATH} down
        fi
    elif [[ "${test_server}" == "e2e" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            generalMessage "docker-compose up -d --BUILD_FLAG ${CONTAINER_ARGS}"
            docker-compose -f ${DOCKER_COMPOSE_PATH} up -d --BUILD_FLAG "${CONTAINER_ARGS}"
        fi
    elif [[ "${test_server}" == "all" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            generalMessage "docker-compose up -d --BUILD_FLAG ${CONTAINER_ARGS}"
            docker-compose -f ${DOCKER_COMPOSE_PATH} up -d --BUILD_FLAG "${CONTAINER_ARGS}"
            all
            generalMessage "docker-compose down"
            docker-compose -f ${DOCKER_COMPOSE_PATH} down
        else
            all
        fi
    else
        testUsage
        exit 1
    fi
    completeMessage
}

run() {
    ## run appropriate tests
    if [[ "${COMMAND}" == "build" ]]; then
        headerMessage "BUILDING ARCLYTICS SIM CONTAINERS ONLY"
        generalMessage "docker-compose build ${BUILD_CONTAINER_ARGS}"
        docker-compose -f ${DOCKER_COMPOSE_PATH} build ${BUILD_CONTAINER_ARGS}
    elif [[ "${COMMAND}" == "up" ]]; then
        headerMessage "RUN ARCLYTICS SIM CONTAINER_ARGS"

        if [[ ${SCALE_FLAG} == 1 ]]; then
            CONTAINER_ARGS="--scale ${scale_service} ${CONTAINER_ARGS}"
        fi

        if [[ ${swagger} == 1 ]]; then
            CONTAINER_ARGS="${CONTAINER_ARGS} swagger"
        fi

        if [[ ${jupyter} == 1 ]]; then
            CONTAINER_ARGS="${CONTAINER_ARGS} jupyter"
        fi

        if [[ ${BUILD_FLAG} == 1 ]]; then
            if [[ ${DETACH_FLAG} == 1 ]]; then
                generalMessage "docker-compose up -d --build ${CONTAINER_ARGS}"
                docker-compose -f ${DOCKER_COMPOSE_PATH} up -d --build ${CONTAINER_ARGS}
            else
                generalMessage "docker-compose up --build ${CONTAINER_ARGS}"
                docker-compose -f ${DOCKER_COMPOSE_PATH} up --build ${CONTAINER_ARGS}
            fi
        else
            if [[ ${DETACH_FLAG} == 1 ]]; then
                generalMessage "docker-compose up -d ${CONTAINER_ARGS}"
                docker-compose -f ${DOCKER_COMPOSE_PATH} up -d ${CONTAINER_ARGS}
            else
                generalMessage "docker-compose up ${CONTAINER_ARGS}"
                docker-compose -f ${DOCKER_COMPOSE_PATH} up ${CONTAINER_ARGS}
            fi
        fi

        if [[ ${SEED_DB_FLAG} == 1 ]]; then
            echoSpace
            flushAndSeedDb
        fi
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
        -V | --version )
            generalMessage "Arclytis CLI"
            echo v${VERSION}
            ;;
        -h | --help )
            usage
            exit 0
            ;;
        -d | --detach )
            DETACH_FLAG=1
            ;;
        -b | --build )
            BUILD_FLAG=1
            ;;
        -s | --seed_db )
            SEED_DB_FLAG=1
            ;;
        -S | --swagger )
            swagger=1
            ;;
        -J | --jupyter )
            jupyter=1
            ;;
        --group )
            # TODO(andrew@neuraldev.io): Add grouping for container services.
            ;;
        ps )
            ARGS=$2
            while [[ "$3" != "" ]] ; do
                ARGS="${ARGS} $3"
                shift
            done
            dockerPs
            ;;
        stats )
            ARGS=$2
            while [[ "$3" != "" ]] ; do
                ARGS="${ARGS} $3"
                shift
            done
            dockerStats
            ;;
        prune )
            dockerSystemPrune
            ;;
        down )
            while [[ "$2" != "" ]] ; do
                case $2 in
                    -D | --docker )
                        DOCKER_DOWN_FLAG=1
                        ;;
                    * )
                        ARGS=$2
                        while [[ "$3" != "" ]] ; do
                            ARGS="${ARGS} $3"
                            shift
                        done
                esac
                shift
            done
            containerDown
            ;;
        scale )
            SCALE_CONTAINERS_ARGS=$2
            while [[ $3 != "" ]] ; do
                SCALE_CONTAINERS_ARGS="${SCALE_CONTAINERS_ARGS} $3"
                shift
            done
            scaleContainers
            ;;
        build )
            COMMAND="build"
            BUILD_CONTAINER_ARGS=$2
            while [[ "$3" != "" ]] ; do
                BUILD_CONTAINER_ARGS="${BUILD_CONTAINER_ARGS} $3"
                shift
            done
            run
            ;;
        up )
            COMMAND="up"

            while [[ "$2" != "" ]] ; do
                case $2 in
                    -b | --build )
                        BUILD_FLAG=1
                        ;;
                    -d | --detach )
                        DETACH_FLAG=1
                        ;;
                    -s | --seed_db )
                        SEED_DB_FLAG=1
                        ;;
                    -S | --swagger )
                        swagger=1
                        ;;
                    -J | --jupyter )
                        jupyter=1
                        ;;
                    --scale )
                        SCALE_FLAG=1
                        # Shift to the arg after --SCALE_FLAG
                        shift
                        # Get the first argument after --SCALE_FLAG flag
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
                        CONTAINER_ARGS=$2
                        while [[ "$3" != "" ]] ; do
                            CONTAINER_ARGS="${CONTAINER_ARGS} $3"
                            shift
                        done
                        ;;
                esac
                shift
            done
            run
            ;;
        logs )
            CONTAINER_LOG=$2
            dockerLogs
            ;;
        test )
            while [[ "$2" != "" ]] ; do
                case $2 in
                    -b | --build )
                        BUILD_FLAG=1
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
                esac
                shift
            done
            run_tests
            ;;
        flush )
            flushDb
            ;;
        seed )
            flushAndSeedDb
            ;;
        dir )
            echo ${WORKDIR}
            ;;
        pwd )
            generalMessage "Arclytics Sim Project Root Directory"
            echo "${WORKDIR}"
            ;;
    esac
    shift
done
