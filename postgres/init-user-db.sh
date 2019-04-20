#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "postgres" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER neuraldev;
    ALTER USER neuraldev WITH PASSWORD 'THANOS';
    CREATE DATABASE arclytics;
    GRANT ALL PRIVILEGES ON DATABASE arclytics TO neuraldev;
EOSQL
