#!/bin/bash

##
# Script to deploy a Kubernetes project with a StatefulSet running a Reedis Cluster Set, to GKE.
##

REGION="australia-southeast1"
ZONE="australia-southeast1-a"
LOCATION_COMMAND="--region=${REGION}"
REPLICA_ZONE_MONGO="--replica-zones=${ZONE},australia-southeast1-c"

# Register GCE Fast SSD persistent disks and then create the persistent disks
echo "Creating GCE disks"
for i in 1 2
do
    gcloud compute disks create --size 30GB \
        --type pd-ssd redis-ssd-disk-$i \
        ${LOCATION_COMMAND} ${REPLICA_ZONE_MONGO}
done
sleep 3

# Create persistent volumes using disks created above
echo "Creating GKE Persistent redis-ssd-disk volumes"
for i in 1 2
do
    sed -e "s/INST/${i}/g" ./redis-cluster-gke-ssd-pv.yaml > /tmp/redis-gke-ssd-pv.yaml
    kubectl apply -f /tmp/redis-gke-ssd-pv.yaml
done
rm /tmp/redis-gke-ssd-pv.yaml
sleep 3
