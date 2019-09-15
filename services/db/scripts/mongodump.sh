# REFERENCES:
# [1] https://docs.mongodb.com/manual/reference/program/mongodump/#bin.mongodump
# [2] https://docs.mongodb.com/manual/tutorial/backup-and-restore-tools/
# [3] https://docs.mongodb.com/manual/reference/program/mongorestore/

# Connect to mongodb container
# docker exec -it arc_mongodb_1 bash

docker-compose -p arc exec mongodb \
    mongodump --host localhost \
    --port 27017 \
    --db arc_dev \
    --out /data/backups/dump_data

# shellcheck disable=SC1101
docker cp arc_mongodb_1:/data/backups/dump_data \
    ./services/db/production_data/
