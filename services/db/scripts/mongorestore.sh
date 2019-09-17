# REFERENCES:
# [1] https://docs.mongodb.com/manual/reference/program/mongodump/#bin.mongodump
# [2] https://docs.mongodb.com/manual/tutorial/backup-and-restore-tools/
# [3] https://docs.mongodb.com/manual/reference/program/mongorestore/

# Connect to mongodb container
# docker exec -it arc_mongodb_1 bash

docker cp ./services/db/production_data/dump_data \
    arc_mongodb_1:/data/backups/

docker-compose -p arc exec mongodb \
    mongorestore --host localhost \
    --port 27017 \
    /data/backups/dump_data
