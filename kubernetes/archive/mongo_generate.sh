#!/bin/sh
##
# Script to deploy a Kubernetes project with a StatefulSet running a MongoDB Replica Set, to GKE.
##

# Create new GKE Kubernetes cluster (using host node VM images based on Ubuntu
# rather than ChromiumOS default & also use slightly larger VMs than default)
#gcloud container clusters create "arclytics-sim-cluster" --image-type=UBUNTU --machine-type=n1-standard-2

# Configure host VM using daemonset to disable hugepages
kubectl apply -f ./hostvm-node-configurer-daemonset.yaml

# Define storage class for dynamically generated persistent volumes
# NOT USED IN THIS EXAMPLE AS EXPLICITLY CREATING DISKS FOR USE BY PERSISTENT
# VOLUMES, HENCE COMMENTED OUT BELOW
#kubectl apply -f ../resources/gce-ssd-storageclass.yaml

# Register GCE Fast SSD persistent disks and then create the persistent disks 
echo "Creating GCE disks"
for i in 1 2
do
    gcloud compute disks create --size 30GB --type pd-ssd pd-ssd-disk-$i
done
sleep 3

# Create persistent volumes using disks created above
echo "Creating GKE Persistent Vopd-ssd-disk-1lumes"
for i in 1 2
do
    sed -e "s/INST/${i}/g" ./mongo-gke-xfs-ssd-pv.yaml > /tmp/xfs-gke-ssd-pv.yaml
    kubectl apply -f /tmp/xfs-gke-ssd-pv.yaml
done
rm /tmp/xfs-gke-ssd-pv.yaml
sleep 3

# Create keyfile for the MongoD cluster as a Kubernetes shared secret
TMPFILE=$(mktemp)
/usr/bin/openssl rand -base64 741 > $TMPFILE
kubectl create secret generic shared-bootstrap-secrets --from-file=internal-auth-mongodb-keyfile=$TMPFILE
rm $TMPFILE

# Create mongodb service with mongod stateful-set
kubectl apply -f ./mongo-gke-service.yaml
echo

# Wait until the final (2nd) mongod has started properly
echo "Waiting for the 2 containers to come up (`date`)..."
echo " (IGNORE any reported not found & connection errors)"
sleep 30
echo -n "  "
until kubectl --v=0 exec mongo-1 -c mongo-container -- mongo --quiet --eval 'db.getMongo()'; do
    sleep 5
    echo -n "  "
done
echo "...mongo containers are now running (`date`)"
echo

# Print current deployment state
kubectl get persistentvolumes
echo
kubectl get all 
