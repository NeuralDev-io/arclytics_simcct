#!/bin/bash
# shellcheck disable=SC2086

# Set the Project Name for docker-compose  note: cannot be done any other way
# other than setting it as part of the docker-compose COMMAND -p flag.
export COMPOSE_PROJECT_NAME='arc'

# ======================================================= #
# ==================== # Variables # ==================== #
# ======================================================= #
VERSION=1.1.2
WORKDIR=$(dirname "$(readlink -f "$0")")
DOCKER_COMPOSE_PATH="${WORKDIR}/docker-compose.yml"
ARGS=""
CONTAINER_GROUP=""
CONTAINER_ARGS="simcct client redis mongodb nginx celery-worker"
CONTAINER_LOG=""
LOGS_WATCH=0
FLUSH_ALL=0
BUILD_CONTAINER_ARGS=""
BUILD_FLAG=0
DETACH_FLAG=0
SEED_DB_FLAG=0
SCALE_FLAG=0
SCALE_CONTAINERS_ARGS=""
DOCKER_DOWN_FLAG=0
SWAGGER_FLAG=0
JUPYTER_FLAG=0

MONGO_USERNAME=""
MONGO_PASSWORD=""
MONGO_APP_DB=""

TEST_SERVER_ARGS=""
TEST_TYPE="test"
TEST_TITLE="Flask-Testing Unittests (without coverage)"
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
function headerMessage() { echo -e "${greenf}${boldon}# [ARCLYTICS CLI]  |  $1${boldoff}${reset}"; }
function actionMessage() { echo -e "${whiteb}${redf}${boldon}# [ARCLYTICS CLI]  |  $1...${boldoff}${reset}"; echo ""; }
function generalMessage() { echo -e "${yellowf}# [ARCLYTICS CLI]  |  $1${reset}"; }
function echoSpace() { echo ""; }
function completeMessage() { echo -e "${greenf}${boldon}# [ARCLYTICS CLI]  |  Complete${boldoff}${reset}"; }

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

# Read the .env file and get the password
getMongoUserAndPassword() {
    input="${WORKDIR}/.env"
    user_key=""
    pass_key=""

    if [[ $1 == 'root' ]]; then
        user_key='MONGO_ROOT_USER'
        pass_key='MONGO_ROOT_PASSWORD'
    elif [[ $1 == 'user' ]]; then
        user_key="MONGO_APP_USER"
        pass_key="MONGO_APP_USER_PASSWORD"
    fi

    if [[ ${user_key} != "" ]]; then
        while IFS= read -r line
        do
            KEY="$(cut -d'=' -f1 <<< "${line}" )"

            if [[ ${KEY} == "${user_key}" ]]; then
                MONGO_USERNAME="$(cut -d'=' -f2 <<< "${line}" )"
            fi

            if [[ ${KEY} == "${pass_key}" ]]; then
                MONGO_PASSWORD="$(cut -d'=' -f2 <<< "${line}" )"
            fi

            if [[ ${KEY} == "MONGO_APP_DB" ]]; then
                MONGO_APP_DB="$(cut -d'=' -f2 <<< "${line}" )"
            fi
        done < "$input"
    fi
}

# Run only the arclytics tests
arcTest() {
    headerMessage "RUNNING USERS SERVER TESTS"
    generalMessage "Beginning ${TEST_TITLE} for Users Server"
    echoSpace
    if [[ ${tty} == 1 ]]; then
        generalMessage "docker-compose exec -T arclytics python manage.py ${TEST_TYPE}"
        docker-compose -f "${DOCKER_COMPOSE_PATH}" exec -T arclytics python manage.py "${TEST_TYPE}"
    else
        generalMessage "docker-compose exec arclytics python manage.py ${TEST_TYPE}"
        docker-compose -f "${DOCKER_COMPOSE_PATH}" exec arclytics python manage.py "${TEST_TYPE}"
    fi
    generalMessage "Finishing ${TEST_TITLE} for Users Server"
}

# Run only the simcct server tests
simcct() {
    headerMessage "RUNNING SIMCCT SERVER TESTS"
    generalMessage "Beginning ${TEST_TITLE} for SimCCT Server"
    echoSpace
    if [[ ${tty} == 1 ]]; then
        generalMessage "docker-compose exec -T simcct python manage.py ${TEST_TYPE}"
        docker-compose -f "${DOCKER_COMPOSE_PATH}" exec -T simcct python manage.py "${TEST_TYPE}"
    else
        generalMessage "docker-compose exec simcct python manage.py ${TEST_TYPE}"
        docker-compose -f "${DOCKER_COMPOSE_PATH}" exec simcct python manage.py "${TEST_TYPE}"
    fi
    generalMessage "Finishing ${TEST_TITLE} for SimCCT Server"
}

# Run server-side tests
server() {
    simcct
}

client() {
    pass
}

# run all tests
all() {
    # arcTest
    simcct
    # client
    # e2e
}

groupUsage() {
    echo -e """
${greenf}ARCLYTICS CLI SCRIPT

Usage:
arc_cli.sh [options...] up --group [SERVICE GROUP]
arc_cli.sh --group [SERVICE GROUP] up [options...]

The Arclytics CLI group flag command to run a group of docker-compose services
based on the available service groups.

Options:
  -b, --build           Build the Docker containers before running.
  -d, --detach          Run Docker Engine logs in a detached shell mode.
  -s, --seed_db         Seed the MongoDB database with test data.

Service Group:
  all               Run all available services which includes the following:
                    arclytics, simcct, redis, mongodb, dask-scheduler,
                    dask-worker, jupyter, swagger, fluentd, elasticsearch,
                    kibana, client.
  e2e               Run the services to with the front-end client and back-end
                    microservices to test an end-to-end example of any feature.
                    This includes: client, simcct, mongodb, redis.
  server            Run all services related to the back-end microservices and
                    database which includes the following: simcct, mongodb, redis.
  server-dask       Run all services related to the back-end and include the
                    \`dask\` containers. This includes: simcct, mongodb, redis,
                    dask-scheduler, dask-worker.
  client            Run only the client microservice.
  dask              Run only the services to test the \`dask\` containers which
                    includes: dask-scheduler, dask-worker, jupyter.
  fluentd           Run only the microservices with the \`fluentd\` logging
                    container and associated containers for storage. This
                    includes: fluentd, elasticsearch, kibana.
  fluentd-test      Run only the microservices for \`fluentd\` testing with a
                    basic Flask API server and a production build React app.
                    This includes: fluent-python, fluent-react, fluentd, kibana,
                    elasticsearch.
  swagger-test      Run the microservices to test the back-end API from swagger.
                    This includes: swagger, simcct, redis, mongodb.
${reset}
"""
}

# shellcheck disable=SC1079,SC1078,SC2006
upUsage() {
    echo -e """
${greenf}ARCLYTICS CLI SCRIPT

Usage: arc_cli.sh up [options] [SERVICE ARGS...]

The Arclytics CLI command to run the containers.

Options:
  -b, --build           Build the Docker containers before running.
  -d, --detach          Run Docker Engine logs in a detached shell mode.
  -s, --seed_db         Seed the MongoDB database with test data.
  --scale SERVICE=NUM   Scale SERVICE to NUM instances. Overrides the
                        \`--scale\` setting in the Compose file if present
  -G, --group GROUP     Specify a GROUP of services to use to run. You can use
                        \`help\` to get more information about groups available.
  -h, --help            Get the Usage information for this COMMAND.

Optional Containers:
  -S, --swagger         Run the Swagger container with the cluster.
  -J, --jupyter         Run the Jupyter container with the cluster.

Service (only one for \`logs\`; * default for \`up\`):
  client *
  nginx *
  simcct *
  arclytics *
  celery-worker *
  redis *
  mongodb *
  dask-scheduler
  dask-worker
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

Usage: arc_cli.sh test [OPTIONS] [TEST TYPE]

The Arclytics CLI command to run Unit Tests.

Options:
  -b, --build      Build the Docker containers before running tests.
  -t, --tty        Attach a pseudo-TTY to the tests.
  -c, --coverage   Run the unit tests with coverage.
  -f, --file       Set the path of the docker-compose YAML file to use.
  -h, --help       Get the Usage information for this command.

Test Types (one only):
  all         Run all unit tests for Arclytics Sim
  server      Run the server-side unit tests.
  client      Run the client-side unit tests.
  arclytics   Run only the arclytics tests.
  simcct      Run only the simcct tests.
${reset}
"""
}

# shellcheck disable=SC1079
usage() {
   # shellcheck disable=SC1078
   echo -e """
${greenf}ARCLYTICS CLI SCRIPT

The Arclytics CLI script for running \`docker\` and \`docker-compose\` commands on the
Arclytics Sim Docker orchestration.

Usage:
arc_cli.sh build [SERVICE ARGS...]
arc_cli.sh up [options] [SERVICE ARGS...]
arc_cli.sh up --scale [SERVICE=NUM]
arc_cli.sh logs [SERVICE]
arc_cli.sh test [options] [TEST TYPE]
arc_cli.sh down [options]
arc_cli.sh scale [SERVICE=NUM...]
arc_cli.sh [COMMAND] [ARGS...]

Options:
  -b, --build           Build the Docker containers before running.
  -d, --detach          Run Docker Engine logs in a detached shell mode.
  -s, --seed_db         Seed the MongoDB database with test data.
  -f, --file            Set the path of the docker-compose YAML file to use.
  -h, --help            Get the Usage information for this script.

  Up Options:
  --scale SERVICE=NUM   Scale the a single container when running the cluster.
  -S, --swagger         Run the Swagger container with the cluster.
  -J, --jupyter         Run the Jupyter container with the cluster.

  Test Options:
  -b, --build           Build the Docker containers before running tests.
  -t, --tty             Attach a pseudo-TTY to the tests.
  -c, --coverage        Run the unit tests with coverage.

  Down Options:
  -D, --docker          Stop the containers using the Docker PS stat.

  System Options:
  usage, df             Show docker disk usage.
  events                Get real time events from the server.
  info                  Display the system-wide information.


Management Commands:
  container   Manage containers. Run \`help | --help\` to get usage options.
  image       Manage image. Run \`help | --help\` to get usage options.
  system      Manage Docker system. Additional options available.

Commands:
  build       Build the Docker images from docker-compose.yml only (passing services
              to build specific ones or leave empty to build all).
  down        Stop all containers.
  flush       Flush both Redis datastore and MongoDB database only.
  images      List images build.
  logs        Get the logs of the container.
  ls          List all containers, volumes, and images with formatting.
  mongo       Connect to the \`mongo\` CLI running in the container.
  ps          List the running containers.
  pull        Pull an image or a repository from a registry
  push        Push an image or a repository to a registry
  prune       Prune all stopped images, containers, networks, and volumes based
              on the \`labels\` used for this project.
  pwd         Get the full path directory of the Arclytics CLI script.
  seed        Seed the microservices with test data and flush both Redis
              datastore and MongoDB database.
  scale       Set number of containers to run for a service. Numbers are specified
              in the form \`service=num\` as arguments.
  minikube    Use as a wrapper for the minikube service.
  stats       Display a live stream of container(s) resource usage statistics.
  test        Run unit tests on the microservices.
  up          Run the main containers in docker-compose.yml or provide a list of
              arguments to run only those provided.
  help        Get the Usage information for this script and exit.

Service (only one for \`logs\`; * default for \`up\`):
  client *
  nginx *
  simcct *
  arclytics *
  celery-worker *
  redis *
  mongodb *
  dask-scheduler
  dask-worker
  jupyter
  swagger

Test Types (one only):
  all         Run all unit tests for Arclytics Sim
  server      Run the server-side unit tests.
  client      Run the client-side unit tests.
  arclytics   Run only the arclytics tests.
  simcct      Run only the simcct tests.
${reset}
"""
}

# ==================================================================== #
# ==================== # Main Command Functions # ==================== #
# ==================================================================== #

dockerLsFormatted() {
  echo
  headerMessage "ARCLYTICS SIM DOCKER CONTAINERS, VOLUMES, AND IMAGES"
  echoLine
  generalMessage "Containers"
  echoLine
  docker container ls -a --format \
      "table {{.ID}}\t{{.Image}}\t{{.RunningFor}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}" \
      --filter "label=arclytics.io"
  echoLine
  generalMessage "Volumes"
  echoLine
  docker volume ls --format \
      "table {{.Name}}\t{{.Labels}}\t{{.Driver}}\t{{.Mountpoint}}" \
#      --filter "label=arclytics.io"
  echoLine
  generalMessage "Images"
  echoLine
  docker image ls --format \
      "table {{.ID}}\t{{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" \
      --filter "label=arclytics.io"
  echoLine
  completeMessage
  echo
}

dockerPs() {
    headerMessage "ARCLYTICS SIM RUNNING CONTAINERS"
    generalMessage "docker ps --size ${ARGS}"
    docker ps --size ${ARGS}
    completeMessage
}

dockerLogs() {
    if [[ $LOGS_WATCH == 1 ]] ; then
        echo "watch docker-compose -f ${DOCKER_COMPOSE_PATH} logs ${CONTAINER_LOG}"
        watch docker-compose -f "${DOCKER_COMPOSE_PATH}" logs ${CONTAINER_LOG}
    else
        headerMessage "ARCLYTICS SIM CONTAINER LOGS"
        generalMessage "docker-compose logs ${CONTAINER_LOG}"
        docker-compose -f "${DOCKER_COMPOSE_PATH}" logs ${CONTAINER_LOG}
    fi
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
    generalMessage "docker system prune -af --volumes --filter 'label=arclytics.io'"
    docker volume prune -f
    docker system prune -af --volumes --filter 'label=arclytics.io'
    completeMessage
}

containerDown() {
    headerMessage "STOPPING ARCLYTICS SIM CONTAINERS"
    if [[ "${DOCKER_DOWN_FLAG}" == 1 ]]; then
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
        generalMessage "docker-compose down ${ARGS}"
        docker-compose -f "${DOCKER_COMPOSE_PATH}" down ${ARGS}
    fi
    completeMessage
}

buildContainers() {
    headerMessage "BUILDING ARCLYTICS SIM CONTAINERS ONLY"
    generalMessage "docker-compose build ${BUILD_CONTAINER_ARGS}"
    docker-compose -f "${DOCKER_COMPOSE_PATH}" build ${BUILD_CONTAINER_ARGS}
}

scaleContainers() {
  headerMessage "SCALING ARCLYTICS SIM CONTAINERS"
  docker-compose -f "${DOCKER_COMPOSE_PATH}" scale ${SCALE_CONTAINERS_ARGS}
  completeMessage
}

flushDb() {
    headerMessage "FLUSH BACK-END MICROSERVICES"
    generalMessage "Flushing simcct microservice database (Redis and MongoDB)"
    if [[ $FLUSH_ALL == 1 ]] ; then
      generalMessage "docker-compose exec simcct python manage.py flush_all"
      docker-compose -f "${DOCKER_COMPOSE_PATH}" exec simcct python manage.py flush_all
    else
      generalMessage "docker-compose exec simcct python manage.py flush"
      docker-compose -f "${DOCKER_COMPOSE_PATH}" exec simcct python manage.py flush
    fi
}

# Flush and seed database
flushAndSeedDb() {
    headerMessage "SEED AND FLUSH BACK-END MICROSERVICES"
    generalMessage "Flushing simcct microservice database (Redis and MongoDB)"
    generalMessage "docker-compose exec simcct python manage.py flush_all"
    docker-compose -f "${DOCKER_COMPOSE_PATH}" exec simcct python manage.py flush_all
    echoSpace
    generalMessage "Seeding simcct microservice database with global alloys"
    generalMessage "docker-compose exec simcct python manage.py seed_db"
    docker-compose -f "${DOCKER_COMPOSE_PATH}" exec simcct python manage.py seed_db
    docker-compose -f "${DOCKER_COMPOSE_PATH}" exec simcct python manage.py seed_alloys_db
    echoSpace
}

# shellcheck disable=SC2086
runTests() {
    # Make sure the correct container groups are run for each test.
    # By default, we ensure the server back-end ones are running
    CONTAINER_GROUP="server"
    changeContainerGroup

    ## run appropriate tests
    if [[ "${TEST_SERVER_ARGS}" == "server" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            generalMessage "docker-compose up -d --build ${CONTAINER_ARGS}"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" up -d --build "${CONTAINER_ARGS}"
            server
            generalMessage "docker-compose down"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" down
        else
            server
        fi
    elif [[ "${TEST_SERVER_ARGS}" == "arclytics" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            generalMessage "docker-compose up -d --build ${CONTAINER_ARGS}"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" up -d --build "${CONTAINER_ARGS}"
            arcTest
            generalMessage "docker-compose down"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" down
        else
            arcTest
        fi
    elif [[ "${TEST_SERVER_ARGS}" == "simcct" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            generalMessage "docker-compose up -d --build ${CONTAINER_ARGS}"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" up -d --build "${CONTAINER_ARGS}"
            simcct
            generalMessage "docker-compose down"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" down
        else
            simcct
        fi
    elif [[ "${TEST_SERVER_ARGS}" == "client" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            CONTAINER_GROUP="client"
            changeContainerGroup

            generalMessage "docker-compose up -d --build ${CONTAINER_ARGS}"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" up -d --build "${CONTAINER_ARGS}"
            client
            generalMessage "docker-compose down"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" down
        fi
    elif [[ "${TEST_SERVER_ARGS}" == "e2e" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            CONTAINER_GROUP="e2e"
            changeContainerGroup
            generalMessage "docker-compose up -d --build ${CONTAINER_ARGS}"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" up -d --build "${CONTAINER_ARGS}"
        fi
    elif [[ "${TEST_SERVER_ARGS}" == "all" ]]; then
        if [[ ${BUILD_FLAG} == 1 ]]; then
            CONTAINER_GROUP="e2e"
            changeContainerGroup

            generalMessage "docker-compose up -d --build ${CONTAINER_ARGS}"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" up -d --build "${CONTAINER_ARGS}"
            all
            generalMessage "docker-compose down"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" down
        else
            all
        fi
    else
        testUsage
        exit 1
    fi
    completeMessage
}

changeContainerGroup() {
    if [[ "${CONTAINER_GROUP}" == "all" ]]; then
        # Leaving this empty will build everything in the docker-compose.yml
        CONTAINER_ARGS=""
        # Make sure these are not added to the CONTAINERS_ARGS
        SWAGGER_FLAG=0
        JUPYTER_FLAG=0
    elif [[ "${CONTAINER_GROUP}" == "server" ]]; then
        CONTAINER_ARGS="simcct celery-worker redis mongodb"
    elif [[ "${CONTAINER_GROUP}" == "server-dask" ]]; then
        CONTAINER_ARGS="simcct celery-worker redis mongodb dask-scheduler dask-worker"
    elif [[ "${CONTAINER_GROUP}" == "client-dask" ]]; then
        CONTAINER_ARGS="client simcct celery-worker redis mongodb dask-scheduler dask-worker"
    elif [[ "${CONTAINER_GROUP}" == "client" ]]; then
        CONTAINER_ARGS="client nginx"
    elif [[ "${CONTAINER_GROUP}" == "fluentd" ]]; then
        CONTAINER_ARGS="fluentd elasticsearch kibana"
    elif [[ "${CONTAINER_GROUP}" == "fluentd-test" ]]; then
        CONTAINER_ARGS="fluentd fluent-python fluent-react elasticsearch kibana"
    elif [[ "${CONTAINER_GROUP}" == "swagger-test" ]]; then
        CONTAINER_ARGS="simcct redis celery-worker mongodb swagger"
    elif [[ "${CONTAINER_GROUP}" == "dask" ]]; then
        CONTAINER_ARGS="dask-scheduler dask-worker jupyter"
    elif [[ "${CONTAINER_GROUP}" == "e2e" ]]; then
            CONTAINER_ARGS="client simcct nginx celery-worker redis mongodb"
    fi
}

run() {
    headerMessage "RUN ARCLYTICS SIM CONTAINERS"

    if [[ ${SCALE_FLAG} == 1 ]]; then
        CONTAINER_ARGS="--scale ${scale_service} ${CONTAINER_ARGS}"
    fi

    if [[ ${SWAGGER_FLAG} == 1 ]]; then
        # Check if we haven't been told to build all
        if [[ "${CONTAINER_GROUP}" != "all" ]]; then
            CONTAINER_ARGS="${CONTAINER_ARGS} swagger"
        fi
    fi

    if [[ ${JUPYTER_FLAG} == 1 ]]; then
        if [[ "${CONTAINER_GROUP}" != "all" ]]; then
            CONTAINER_ARGS="${CONTAINER_ARGS} jupyter"
        fi
    fi

    if [[ ${BUILD_FLAG} == 1 ]]; then
        if [[ ${DETACH_FLAG} == 1 ]]; then
            generalMessage "docker-compose up -d --build ${CONTAINER_ARGS}"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" up -d --build ${CONTAINER_ARGS}
        else
            generalMessage "docker-compose up --build ${CONTAINER_ARGS}"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" up --build ${CONTAINER_ARGS}
        fi
    else
        if [[ ${DETACH_FLAG} == 1 ]]; then
            generalMessage "docker-compose up -d ${CONTAINER_ARGS}"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" up -d ${CONTAINER_ARGS}
        else
            generalMessage "docker-compose up ${CONTAINER_ARGS}"
            docker-compose -f "${DOCKER_COMPOSE_PATH}" up ${CONTAINER_ARGS}
        fi
    fi

    if [[ ${SEED_DB_FLAG} == 1 ]]; then
        echoSpace
        flushAndSeedDb
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
        -f | --file )
            DOCKER_COMPOSE_PATH=$2
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
            SWAGGER_FLAG=1
            ;;
        -J | --jupyter )
            JUPYTER_FLAG=1
            ;;
        -G | --group )
            # Simply change the CONTAINER_ARGS based on the CONTAINER_GROUP
            CONTAINER_GROUP=$2

            if [[ "${CONTAINER_GROUP}" == 'help' ]]; then
                groupUsage
                exit 0
            fi

            changeContainerGroup
            # Let the while condition continue and shift $3 --> $2 below
            ;;
        ps )
            ARGS=$2
            while [[ "$3" != "" ]] ; do
                ARGS="${ARGS} $3"
                shift
            done
            dockerPs
            ;;
        ls | list | show )
            dockerLsFormatted
            exit 0
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
            BUILD_CONTAINER_ARGS=$2
            while [[ "$3" != "" ]] ; do
                BUILD_CONTAINER_ARGS="${BUILD_CONTAINER_ARGS} $3"
                shift
            done
            buildContainers
            ;;
        up )
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
                        SWAGGER_FLAG=1
                        ;;
                    -J | --jupyter )
                        JUPYTER_FLAG=1
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
                    -G | --group )
                        shift
                        CONTAINER_GROUP=$2
                        changeContainerGroup

                        while [[ "$3" != "" ]]; do
                          case $3 in
                            -b | --build )
                              BUILD_FLAG=1
                              ;;
                            -d | --detach )
                              DETACH_FLAG=1
                              ;;
                            -s | --seed_db )
                              SEED_DB_FLAG=1
                              ;;
                            --scale )
                              SCALE_FLAG=1
                              # Shift to the arg after --scale
                              shift
                              # Get the first argument after --SCALE_FLAG flag
                              # TODO(andrew@neuraldev.io): Currently only taking one
                              scale_service=$3
                              # scale_num="$(cut -d'=' -f2 <<< "${scale_service}" )"
                              shift
                              ;;
                            help )
                              groupUsage
                              exit 0
                              ;;
                            esac
                            shift
                          done
                      # We run from here and as will only accept the flags above
                      run
                      exit 0
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
            shift

            if [[ $2 == "--watch" ]] ; then
                LOGS_WATCH=1
            fi

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
                        TEST_TYPE="test_coverage"
                        TEST_TITLE="Flask-Testing Unittests with Coverage"
                        ;;
                    -h | --help )
                        testUsage
                        exit 0
                        ;;
                    * )
                        TEST_SERVER_ARGS=$2
                esac
                shift
            done
            runTests
            ;;
        images )
            docker images --format \
                "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"
            ;;
        image )
            ARGS=$2
            while [[ "$3" != "" ]] ; do
                ARGS="${ARGS} $3"
                shift
            done
            docker image "${ARGS}"
            ;;
        pull )
            ARGS=$2
            while [[ "$3" != "" ]] ; do
                ARGS="${ARGS} $3"
                shift
            done
            docker pull "${ARGS}"
            ;;
        push )
            ARGS=$2
            while [[ "$3" != "" ]] ; do
                ARGS="${ARGS} $3"
                shift
            done
            docker push "${ARGS}"
            ;;
        container )
            ARGS=$2
            while [[ "$3" != "" ]] ; do
                ARGS="${ARGS} $3"
                shift
            done
            docker container "${ARGS}"
            ;;
        system )
            while [[ "$2" != "" ]] ; do
                case $2 in
                    usage | df )
                      docker system df
                      exit 0
                      ;;
                    * )
                      ARGS="${ARGS} $2"
                      ;;
                esac
                shift
            done
            docker system "${ARGS}"
            ;;
        flush )
            while [[ "$2" != "" ]] ; do
                case $2 in
                    -a | --all )
                      FLUSH_ALL=1
                      ;;
                esac
                shift
            done
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
        style )
          while [[ "$2" != "" ]] ; do
            case $2 in
              python )
                headerMessage "ARC CLI STYLING PYTHON"
                CONFIG="${WORKDIR}/.yapf.cfg"
                ARC_DIR="${WORKDIR}/services/simcct"
                CELERY_DIR="${WORKDIR}/services/celery-worker"
                EXCLUDE_DIR="${WORKDIR}/services/client"
                echo "Running yapf formatter"
                echo "Current Directory: ${WORKDIR}"
                echo "Configuration used: ${CONFIG}"
                echo "Exclude directory: ${EXCLUDE_DIR}"
                yapf -ri --verbose --style=${CONFIG} --exclude=${EXCLUDE_DIR} ${ARC_DIR} ${CELERY_DIR}
                completeMessage
                exit 0
                ;;
              #eslint | js | client )
              #  headerMessage "ARC CLI STYLING PYTHON"
              #  CLIENT_DIR="${WORKDIR}/services/client"
              #  npm run lint-fix
              #  completeMessage
              #  exit 0
              #  ;;
            esac
            shift
            done

          ;;
        minikube | mk )
            headerMessage "MINIKUBE CLI"
            while [[ "$2" != "" ]] ; do
                case $2 in
                    -h | --help )
                        minikube --help
                        exit 0
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
            minikube ${ARGS}
            completeMessage
            exit 0
            ;;
        kubectl | kc )
            headerMessage "KUBECTL CLI"
            while [[ "$2" != "" ]] ; do
                case $2 in
                    help | -h | --help )
                        kubectl help
                        exit 0
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
            kubectl ${ARGS}
            completeMessage
            exit 0
            ;;
        deploy )
          # Some Defaults
          PROJECT_ID="arc-sim"
          CLUSTER_NAME="arc-sim-aust"
          KUBERNETES_MASTER_VERSION="1.13.7-gke.8"
          KUBERNETES_NODE_VERSION=${KUBERNETES_MASTER_VERSION}
          # Note: Only use one of ZONE/REGION but generally ZONE because
          # in GCP Trial account they only allow 8 CPUs and a REGION cluster
          # will deploy a node with at least 1 CPU in each Region zone.
          # There are 3 for Australia.
          REGION="australia-southeast1"
          ZONE="australia-southeast1-a"
          LOCATION_COMMAND="--region=${REGION}"
          REPLICA_ZONE_REDIS="--replica-zones=${ZONE},australia-southeast1-b"
          REPLICA_ZONE_MONGO="--replica-zones=${ZONE},australia-southeast1-c"
          IMAGE_TYPE="UBUNTU"
          RESERVED_IP_NAME="arclytics-ip"
          CLIENT_SSL_NAME="client-app-https-cert"
          SIMCCT_SSL_NAME="simcct-app-https-cert"
          CLIENT_HTTPS_TLS_NAME="client-app-https-secret"
          SIMCCT_HTTPS_TLS_NAME="simcct-app-https-secret"
          CLOUD_STORAGE_BUCKET="asia.artifacts.arc-sim.appspot.com"

          while [[ "$2" != "" ]] ; do
            case $2 in
              auth )
                gcloud container clusters get-credentials ${CLUSTER_NAME} \
                    --project=${PROJECT_ID} \
                    --zone=${ZONE}
                ;;
              config )
                gcloud compute project-info describe --project ${PROJECT_ID}
                #gcloud container clusters describe ${CLUSTER_NAME} --zone ${ZONE}
                gcloud config set project ${PROJECT_ID}
                #gcloud config set compute/zone ${ZONE}
                gcloud config set compute/region ${REGION}
                gcloud components update
                #gcloud compute project-info add-metadata --metadata google-compute-default-region=australia-southeast1,google-compute-default-zone=australia-southeast1-a
                ;;
              cluster )
                while [[ "$3" != "" ]]; do
                  case $3 in
                    create )
                      # This uses `jq` package to get the latest GKE versions for Kubernetes Master and Nodes
                      LATEST=$(\
                        gcloud container get-server-config \
                            ${LOCATION_COMMAND} \
                            --project=${PROJECT_ID} \
                            --format="json" \
                            | jq --raw-output '
                              def to_gke_semver(o):
                                capture("(?<major>[0-9]*).(?<minor>[0-9]*).(?<patch>[0-9]*)-gke.(?<gke>[0-9]*)");
                              def from_gke_semver(o):
                                .major + "." + .minor + "." + .patch + "-gke." + .gke;
                              reduce (
                                .validMasterVersions[] | to_gke_semver(.)
                              ) as $this (
                              {
                                "major":"0",
                                "minor":"0",
                                "patch": "0",
                                "gke": "0"
                              };
                              if ($this.major|tonumber) > (.major|tonumber)
                              then . = $this
                              else (
                                if ($this.major|tonumber) == (.major|tonumber)
                                then (
                                  if ($this.minor|tonumber) > (.minor|tonumber)
                                  then . = $this
                                  else (
                                    if ($this.minor|tonumber) == (.minor|tonumber)
                                    then (
                                    if ($this.patch|tonumber) > (.patch|tonumber)
                                      then . = $this
                                        else (
                                            if ($this.patch|tonumber) == (.patch|tonumber)
                                            then (
                                                if ($this.gke|tonumber) > (.gke|tonumber)
                                                then . = $this
                                                else .
                                                end
                                            )
                                            else .
                                            end
                                        )
                                        end
                                    )
                                    else .
                                    end
                                  )
                                  end
                                )
                                else .
                                end
                              )
                              end
                              ) | from_gke_semver(.)
                              ')
                      # echo ${LATEST}

                      # Create new GKE Kubernetes cluster (using host node VM images based on Ubuntu
                      # rather than ChromiumOS default & also use slightly larger VMs than default)
                      # Alternative --machine-type = [n1-standard-]
                      generalMessage "Creating cluster [${CLUSTER_NAME}] with version [${LATEST}] in region [${REGION}] and zone [${ZONE}]"
                      gcloud container clusters create ${CLUSTER_NAME} \
                          ${LOCATION_COMMAND} \
                          --image-type=${IMAGE_TYPE} \
                          --machine-type=n1-standard-2 \
                          --num-nodes=2 \
                          --min-nodes=1 \
                          --max-nodes=2 \
                          --enable-autoscaling \
                          --cluster-version=${KUBERNETES_NODE_VERSION}
                          # This may have caused the Ingress not to work with latest version
                          # --cluster-version=${LATEST} \

                      generalMessage "Getting Cluster Credentials for ${CLUSTER_NAME}"
                      gcloud container clusters get-credentials ${CLUSTER_NAME} \
                          --project=${PROJECT_ID} \
                          ${LOCATION_COMMAND}

                      # google-chrome console.cloud.google.com/kubernetes/list?project=${PROJECT_ID}
                      ;;
                    delete )
                      gcloud container clusters list
                      gcloud container clusters delete ${CLUSTER_NAME} --region ${REGION}
                      ;;
                  esac
                  shift
                done
                ;;
              secrets )
                kubectl apply -f "${WORKDIR}/kubernetes/secrets.yml"

                # For MONGO REPLICASET
                TMPFILE=$(mktemp)
                /usr/bin/openssl rand -base64 741 > ${TMPFILE}
                kubectl create secret generic shared-bootstrap-secrets --from-file=internal-auth-mongodb-keyfile=${TMPFILE}
                rm ${TMPFILE}

                # Apply the SSL certificates to GCP management as well.
                # gcloud compute ssl-certificates create ${CLIENT_SSL_NAME} \
                #    --certificate "${WORKDIR}/certs/io.arclytics.app.crt" \
                #    --private-key "${WORKDIR}/certs/io.arclytics.app.key"
                # gcloud compute ssl-certificates create ${SIMCCT_SSL_NAME} \
                #    --certificate "${WORKDIR}/certs/io.arclytics.api.crt" \
                #    --private-key "${WORKDIR}/certs/io.arclytics.api.key"

                # Apply the certificates to Kubernetes Secrets which will be used
                # by the Ingress controller.
                kubectl create secret tls ${CLIENT_HTTPS_TLS_NAME} \
                   --cert "${WORKDIR}/certs/io.arclytics.app.crt" \
                   --key "${WORKDIR}/certs/io.arclytics.app.key"
                kubectl create secret tls ${SIMCCT_HTTPS_TLS_NAME} \
                   --cert "${WORKDIR}/certs/io.arclytics.api.crt" \
                   --key "${WORKDIR}/certs/io.arclytics.api.key"
                ;;
              addresses )
                while [[ "$3" != "" ]]; do
                  case $3 in
                    create )
                      # Ensure you use a Global Address for an GCE Ingress.
                      # For a Load Balancer type service, you will need Region-based.
                      gcloud compute addresses create ${RESERVED_IP_NAME} --global
                      ;;
                    delete )
                      gcloud compute addresses delete ${RESERVED_IP_NAME} --global
                      ;;
                  esac
                  shift
                done
                ;;
              ingress )
                while [[ "$3" != "" ]]; do
                  case $3 in
                    create )
                      # Ingress that uses Multiple SSL/TLS terminations with 2 different domains.
                      kubectl apply -f "${WORKDIR}/kubernetes/app-gke-secure-ingress.yaml"
                      ;;
                    delete )
                      kubectl delete -f "${WORKDIR}/kubernetes/app-gke-secure-ingress.yaml"
                      ;;
                  esac
                  shift
                done
                ;;
              redis )
                while [[ "$3" != "" ]]; do
                  case $3 in
                    build )
                      # Prune to avoid collisions of names:tags output
                      docker system prune -af --volumes --filter 'label=service=redis'
                      docker-compose -f "${WORKDIR}/docker-compose-gke.yaml" build redis
                      TAG=$(docker image ls --format "{{.Tag}}" --filter "label=service=redis")
                      docker push asia.gcr.io/${PROJECT_ID}/arc_sim_redis:${TAG}
                      ;;
                    create )
                      gcloud compute disks create --size 50GB \
                          --type pd-ssd redis-ssd-disk \
                          ${LOCATION_COMMAND} ${REPLICA_ZONE_REDIS}
                      kubectl apply -f "${WORKDIR}/kubernetes/redis-gke-ssd-pv.yaml"
                      kubectl create -f "${WORKDIR}/kubernetes/redis-gke-service.yaml" --validate=false
                      ;;
                    delete )
                      kubectl delete -f "${WORKDIR}/kubernetes/redis-gke-service.yaml"
                      kubectl delete pvc redis-pvc-redis-0
                      kubectl delete pv redis-pv
                      sleep 15
                      gcloud compute disks delete redis-ssd-disk ${LOCATION_COMMAND}
                      ;;
                  esac
                  shift
                done
                ;;
              mongo )
                while [[ "$3" != "" ]]; do
                  case $3 in
                    build )
                      # Prune to avoid collisions of names:tags output
                      docker system prune -af --volumes --filter 'label=service=mongodb'
                      docker-compose -f "${WORKDIR}/docker-compose-gke.yaml" build mongodb
                      TAG=$(docker image ls --format "{{.Tag}}" --filter "label=service=mongodb")
                      docker push asia.gcr.io/${PROJECT_ID}/arc_sim_mongo:${TAG}
                      ;;
                    create )
                      # shellcheck disable=SC1090
                      # Configure host VM using daemonset to disable hugepages
                      kubectl apply -f "${WORKDIR}/kubernetes/hostvm-node-configurer-daemonset.yaml"

                      # Register GCE Fast SSD persistent disks and then create the persistent disks
                      generalMessage "Creating GCE disks"
                      for i in 1 2
                      do
                          gcloud compute disks create --size 200GB \
                              --type pd-standard pd-standard-disk-$i \
                              ${LOCATION_COMMAND} ${REPLICA_ZONE_MONGO}
                      done
                      sleep 3

                      # Create persistent volumes using disks created above
                      generalMessage "Creating GKE Persistent Volumes"
                      for i in 1 2
                      do
                          sed -e "s/INST/${i}/g" "${WORKDIR}/kubernetes/mongo-gke-xfs-standard-pv.yaml" > /tmp/xfs-gke-pv.yaml
                          kubectl apply -f /tmp/xfs-gke-pv.yaml
                      done
                      rm /tmp/xfs-gke-pv.yaml
                      sleep 3

                      # Create keyfile for the MongoD cluster as a Kubernetes shared secret
                      # TMPFILE=$(mktemp)
                      # /usr/bin/openssl rand -base64 741 > $TMPFILE
                      # kubectl create secret generic shared-bootstrap-secrets --from-file=internal-auth-mongodb-keyfile=$TMPFILE
                      # rm $TMPFILE

                      # Create mongodb service with mongod stateful-set
                      kubectl apply -f "${WORKDIR}/kubernetes/mongo-gke-service.yaml" --validate=false
                      echoSpace

                      # Wait until the final (2nd) mongod has started properly
                      generalMessage "Waiting for the 2 containers to come up $(date)..."
                      generalMessage " (IGNORE any reported not found & connection errors)"
                      sleep 30
                      generalMessage -n "  "
                      until kubectl --v=0 exec mongo-1 -c mongo-container -- mongo --quiet --eval 'db.getMongo()'; do
                          sleep 5
                          generalMessage -n "  "
                      done
                      generalMessage "...mongo containers are now running $(date)"
                      echo

                      # Pods and Containers should be running now
                      #read -p "Are all the mongodb-n containers ready? " -n 1 -r
                      echoSpace    # (optional) move to a new line

                      #if [[ $REPLY =~ ^[Yy]$ ]]
                      #then
                      #  . ${WORKDIR}/kubernetes/scripts/configure_repset_auth.sh
                      #fi
                      sleep 10
                      # shellcheck disable=SC1090
                      . ${WORKDIR}/kubernetes/scripts/configure_repset_auth.sh
                      ;;
                    delete )
                      kubectl delete -f "${WORKDIR}/kubernetes/mongo-gke-service.yaml"
                      kubectl delete pvc mongo-pvc-mongo-0
                      kubectl delete pvc mongo-pvc-mongo-1
                      # kubectl delete pvc mongo-pvc-mongo-2
                      kubectl delete pv mongo-pv-1
                      kubectl delete pv mongo-pv-2
                      # kubectl delete pv mongo-pv-3

                      sleep 15
                      # Wait till the PV and PVC are deleted first
                      gcloud compute disks delete pd-standard-disk-1 ${LOCATION_COMMAND}
                      gcloud compute disks delete pd-standard-disk-2 ${LOCATION_COMMAND}
                      # REMEMBER TO UPDATE scripts/configure_repset_auth.sh IF MOVING to 3
                      # gcloud compute disks delete pd-standard-disk-3 ${LOCATION_COMMAND}
                      ;;
                  esac
                  shift
                done
                ;;
              simcct )
                while [[ "$3" != "" ]]; do
                  case $3 in
                    build )
                      # Prune to avoid collisions of names:tags output
                      docker system prune -af --volumes --filter 'label=service=simcct'
                      docker-compose -f "${WORKDIR}/docker-compose-gke.yaml" build simcct
                      TAG=$(docker image ls --format "{{.Tag}}" --filter "label=service=simcct")
                      docker push asia.gcr.io/${PROJECT_ID}/arc_sim_service:"${TAG}"
                      ;;
                    create )
                      # eval $(minikube docker-env)  <-- If using Docker and self-built images
                      kubectl create -f "${WORKDIR}/kubernetes/simcct-gke-secure-ingress-service.yaml"
                      ;;
                    delete )
                      kubectl delete -f "${WORKDIR}/kubernetes/simcct-gke-secure-ingress-service.yaml"
                      ;;
                  esac
                  shift
                done
                ;;
              celery )
                while [[ "$3" != "" ]]; do
                  case $3 in
                    build )
                      # Prune to avoid collisions of names:tags output
                      docker system prune -af --volumes --filter 'label=service=celery-worker'
                      docker-compose -f "${WORKDIR}/docker-compose-gke.yaml" build celery-worker
                      TAG=$(docker image ls --format "{{.Tag}}" --filter "label=service=celery-worker")
                      docker push asia.gcr.io/${PROJECT_ID}/arc_sim_celery:"${TAG}"
                      ;;
                    create )
                      kubectl create -f "${WORKDIR}/kubernetes/celery-gke-deployment.yaml"
                      ;;
                    delete )
                      kubectl delete -f "${WORKDIR}/kubernetes/celery-gke-deployment.yaml"
                      ;;
                  esac
                  shift
                done
                ;;
              client )
                while [[ "$3" != "" ]]; do
                  case $3 in
                    build )
                      # Prune to avoid collisions of names:tags output
                      docker system prune -af --volumes --filter 'label=service=client'
                      docker-compose -f "${WORKDIR}/docker-compose-gke.yaml" build client
                      TAG=$(docker image ls --format "{{.Tag}}" --filter "label=service=client")
                      docker push asia.gcr.io/${PROJECT_ID}/arc_sim_client:${TAG}
                      ;;
                    create )
                      # eval $(minikube docker-env)
                      kubectl create -f "${WORKDIR}/kubernetes/client-gke-secure-ingress-service.yaml"
                      ;;
                    delete )
                      kubectl delete -f "${WORKDIR}/kubernetes/client-gke-secure-ingress-service.yaml"
                      ;;
                  esac
                  shift
                done
                ;;
              watch )
                watch kubectl get all -o wide
                ;;
              build )
                # Prune to avoid collisions of names:tags output
                docker system prune -af --volumes --filter 'label=service=mongodb'
                docker system prune -af --volumes --filter 'label=service=redis'
                docker system prune -af --volumes --filter 'label=service=simcct'
                docker system prune -af --volumes --filter 'label=service=client'
                docker system prune -af --volumes --filter 'label=service=celery-worker'
                docker-compose -f "${WORKDIR}/docker-compose-gke.yaml" build mongodb
                TAG=$(docker image ls --format "{{.Tag}}" --filter "label=service=mongodb")
                docker push asia.gcr.io/${PROJECT_ID}/arc_sim_mongo:${TAG}
                docker-compose -f "${WORKDIR}/docker-compose-gke.yaml" build redis
                TAG=$(docker image ls --format "{{.Tag}}" --filter "label=service=redis")
                docker push asia.gcr.io/${PROJECT_ID}/arc_sim_redis:${TAG}
                docker-compose -f "${WORKDIR}/docker-compose-gke.yaml" build simcct
                TAG=$(docker image ls --format "{{.Tag}}" --filter "label=service=simcct")
                docker push asia.gcr.io/${PROJECT_ID}/arc_sim_service:"${TAG}"
                docker-compose -f "${WORKDIR}/docker-compose-gke.yaml" build celery-worker
                TAG=$(docker image ls --format "{{.Tag}}" --filter "label=service=celery-worker")
                docker push asia.gcr.io/${PROJECT_ID}/arc_sim_celery:"${TAG}"
                docker-compose -f "${WORKDIR}/docker-compose-gke.yaml" build client
                TAG=$(docker image ls --format "{{.Tag}}" --filter "label=service=client")
                docker push asia.gcr.io/${PROJECT_ID}/arc_sim_client:${TAG}
                ;;
              ls | show | get )
                echoSpace
                headerMessage "ARCLYTICS SIM KUBERNETES ORCHESTRATION"
                echo
                kubectl cluster-info
                echo
                echoLine
                generalMessage "Persistent Volumes"
                echoLine
                kubectl get pv -o wide
                echoLine
                generalMessage "Persistent Volume Claims"
                echoLine
                kubectl get pvc -o wide
                echoLine
                generalMessage "StatefulSets"
                echoLine
                kubectl get statefulsets -o wide
                echoLine
                generalMessage "ReplicaSets"
                echoLine
                kubectl get replicasets -o wide
                echoLine
                generalMessage "Deployments"
                echoLine
                kubectl get deployments -o wide
                echoLine
                generalMessage "Pods"
                echoLine
                kubectl get pods
                echoLine
                generalMessage "Services"
                echoLine
                kubectl get services -o wide
                echoLine
                generalMessage "Ingress"
                echoLine
                kubectl get ingresses
                echoLine
                completeMessage
                echoSpace
                exit 0
                ;;
              staticfiles )
                while [[ "$3" != "" ]]; do
                  case $3 in
                    upload )
                      gsutil cp -r ${WORKDIR}/services/simcct/sim_api/static/* gs://${CLOUD_STORAGE_BUCKET}/assets/
                      ;;
                    list | ls )
                      gsutil ls gs://${CLOUD_STORAGE_BUCKET}/assets/**
                      ;;
                    public )
                      gsutil acl ch -u AllUsers:R gs://${CLOUD_STORAGE_BUCKET}/assets/imgs/email_footer_logo.png
                      ;;
                    address )
                      echo https://storage.cloud.google.com/asia.artifacts.arc-sim.appspot.com/assets/imgs/email_footer_logo.png
                      ;;
                    go )
                      google-chrome https://storage.cloud.google.com/asia.artifacts.arc-sim.appspot.com/assets/imgs/email_footer_logo.png
                      ;;
                  esac
                  shift
                done
                ;;
              # TODO(andrew@neuraldev.io) POD_NAME=$(kubectl get pod -l service=postgres -o jsonpath="{.items[0].metadata.name}")
            esac
            shift
          done
          ;;
    esac
    shift
done

# Load all .env into current shell
# export $(egrep -v '^#' .env | xargs)

