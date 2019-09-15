# REFERENCES:
# [1] https://docs.mongodb.com/manual/reference/program/mongoexport/

# Connect to mongodb container
# docker exec -it arc_mongodb_1 bash

docker-compose -p arc exec mongodb \
    mongoexport --host localhost \
    --port 27017 \
    --db arc_dev \
    --collection users \
    --out /data/backups/production_user_data.json

docker-compose -p arc exec mongodb \
    mongoexport --host localhost \
    --port 27017 \
    --db arc_dev \
    --collection alloys \
    --out /data/backups/production_global_alloys.json

docker cp arc_mongodb_1:/data/backups/production_user_data.json \
    ./services/db/production_data/

docker cp arc_mongodb_1:/data/backups/production_global_alloys.json \
    ./services/db/production_data/
