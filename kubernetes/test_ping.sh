#!/bin/bash

for ((i=1;i<=100000;i++)); do curl http://api.arclytics.io/v1/sim/ping; done
