#!/bin/bash

# REFERENCES:
# [1] https://cloud.google.com/load-balancing/docs/https/https-load-balancer-example

# ========== # DEFAULT VARIABLES # ========== #
PROJECT_ID="arclytics-sim"
CLUSTER="arc-sim-aust"
REGION="australia-southeast1"
ZONE="australia-southeast1-a"
IMAGE_TYPE="UBUNTU"
NETWORK="arclytics-lb-network"
SSL_PROXY="arclytics-https-lb-proxy"
SUBNET="au-subnet"
IPV4_ADDRESS_NAME="arclytics-lb-ipv4-ip"
IPV6_ADDRESS_NAME="arclytics-lb-ipv6-ip"
SSL_NAME="client-app-https-cert"
URL_MAP="arclytics-map"

# ========== # VPC NETWORK # ========== #
# Create a custom VPC network
gcloud compute networks create ${NETWORK} --subnet-mode=custom

# Create a subnet (Optional)
gcloud compute networks subnets create ${SUBNET} \
    --network=${NETWORK} \
    --range=10.1.5.0/24

# ========== # FIREWALL RULES # ========== #
# `fw-allow-ssh`: ingress rule, applicable to instances being load balanced,
# that allows incoming SSH connectivity on TCP port 22 from any address.
# `fw-allow-health-check-and-proxy`: ingress rule, applicable to the instances
# being load balanced, that allows traffic from the load balancer and GCP health
# checking systems (`130.211.0.0/22` and `35.191.0.0/16`)

# `fw-allow-ssh`
gcloud compute firewall-rules create fw-allow-ssh \
    --network=${NETWORK} \
    --action=allow \
    --direction=ingress \
    --target-tags=allow-ssh \
    --rules=tcp:22
# `fw-allow-health-check-and-proxy`
gcloud compute firewall-rules create fw-allow-health-check-and-proxy \
    --network=${NETWORK} \
    --action=allow \
    --direction=ingress \
    --target-tags=allow-hc-and-proxy \
    --source-ranges=130.211.0.0/22,35.191.0.0/16 \
    --rules=tcp:80,tcp:443

# ========== # COMPUTE INSTANCES # ========== #
# Create auto-scaling GCE instances

# GET the Latest version of Kubernetes for the Compute Instances
LATEST=$(gcloud container get-server-config \
        --region=${REGION} \
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

gcloud container clusters create ${CLUSTER} \
    --cluster-version="${LATEST}" \
    --zone ${ZONE} \
    --num-nodes=2 \
    --min-nodes=2 \
    --max-nodes=12 \
    --image-type=${IMAGE_TYPE} \
    --machine-type=n1-standard-2 \
    --disk-type=pd-standard \
    --disk-size=100GB \
    --enable-autorepair \
    --enable-autoscaling \
    --enable-autoupgrade \
    --enable-stackdriver-kubernetes \
    --addons=KubernetesDashboard \
    --addons=HttpLoadBalancing \
    --addons=HorizontalPodAutoscaling \
    --tags=allow-ssh,allow-hc-and-proxy \
    --network=${NETWORK} \
    --subnetwork=${SUBNET}

# ========== # IP ADDRESSES # ========== #
# Reserve global static external IP addresses

# IPv4
# Note: aldready one.
gcloud compute addresses create ${IPV4_ADDRESS_NAME} \
    --ip-version=IPV4 \
    --global

# Note the IPv4 address that was reserved
IPV4_ADDRESS=$(gcloud compute addresses describe ${IPV4_ADDRESS_NAME} \
    --format="get(address)" \
    --global
    )
echo "${IPV4_ADDRESS}"

# IPv6
gcloud compute addresses create ${IPV6_ADDRESS_NAME} \
    --ip-version=IPV4 \
    --global

# Note the IPv6 address that was reserved
IPV6_ADDRESS=$(gcloud compute addresses describe ${IPV6_ADDRESS_NAME} \
    --format="get(address)" \
    --global
    )
echo "${IPV6_ADDRESS}"

# ========== # INSTANCE CONFIGURATIONS # ========== #
# Define a HTTP service and map a port name to the relevant port.

# !!!!!!! Get the automatically created instance group.
gcloud compute instance-groups list --format="get(name)" --global
read -p "What is the name of the instance group? " -r RESPONSE
echo "Instance Group: ${RESPONSE}"
INSTANCE_GROUP="${RESPONSE}"

gcloud compute instance-groups managed set-named-ports "${INSTANCE_GROUP}" \
    --named-ports http:80 \
    --zone ${ZONE}

# Create a health check.
gcloud compute health-checks create http http-basic-check --port 80

# Create a backend service for each content provider
# -- Set the `--protocol` field to `HTTP` because we are using HTTP to go to
# the instances.
# Client NGINX service
gcloud compute backend-services create client-service \
    --protocol HTTP \
    --health-checks http-basic-check \
    --global

# SimCCT Flask Gunicorn service
gcloud compute backend-services create simcct-service \
    --protocol HTTP \
    --health-checks http-basic-check \
    --global

# Add your instance groups as backends to the backend services.
# A backend defines the capacity (max CPU utilization or max queries per second)
# of the instance groups it contains. In this example, set balancing-mode to
# the value `UTILIZATION`, max-utilization to 0.8, and `capacity-scaler` to 1.
# Set `capacity-scaler` to 0 if you wish to drain a backend service.


gcloud compute backend-services add-backend client-service \
    --balancing-mode=UTILIZATION \
    --max-utilization=0.8 \
    --capacity-scaler=1 \
    --instance-group="${INSTANCE_GROUP}" \
    --instance-group-zone=${ZONE} \
    --global

gcloud compute backend-services add-backend simcct-service \
    --balancing-mode=UTILIZATION \
    --max-utilization=0.8 \
    --capacity-scaler=1 \
    --instance-group="${INSTANCE_GROUP}" \
    --instance-group-zone=${ZONE} \
    --global

# Create a URL map to route the incoming requests to the appropriate backend
# services. In this case, the request path mappings defined via the `--path-rules`
# flag split traffic according to the URL path in each request to your site.
# Traffic that does not match an entry in the `--path-rules` list is sent to
# the entry in the `--default-service` flag.

# Create the URL Map
gcloud compute url-maps create ${URL_MAP} \
    --default-service client-service

gcloud compute url-maps add-path-matcher ${URL_MAP} \
    --default-service client-service \
    --path-matcher-name pathmap \
    --path-rules="/api=simcct-service,/api/*=simcct-service"

# ========== # HTTPS SSL # ========== #
# create a self-managed SSL certificate resource
gcloud compute ssl-certificates create ${SSL_NAME} \
    --certificate certs/io.arclytics.app.crt \
    --private-key certs/io.arclytics.app.key

# Create a target HTTPS proxy to route requests to your URL map. The proxy is
# the portion of the load balancer that holds the SSL certificate for HTTPS
# Load Balancing, so you also load your certificate in this step.
gcloud compute target-https-proxies create ${SSL_PROXY} \
    --url-map ${URL_MAP} \
    --ssl-certificates ${SSL_NAME}

# Create two global forwarding rules to route incoming requests to the proxy,
# one for each of the IP addresses you created.
gcloud compute forwarding-rules create https-content-rule \
    --address=${IPV4_ADDRESS_NAME} \
    --global \
    --target-https-proxy=${SSL_PROXY} \
    --ports=443

gcloud compute forwarding-rules create https-content-ipv6-rule \
    --address=${IPV6_ADDRESS_NAME} \
    --global \
    --target-https-proxy=${SSL_PROXY} \
    --ports=443

curl -k https://"${IPV4_ADDRESS}"
curl -k https://"${IPV4_ADDRESS}"/api/

curl -k -g -6 https://"${IPV6_ADDRESS}"
curl -k -g -6 https://"${IPV6_ADDRESS}"/api/
