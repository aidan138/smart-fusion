#!/usr/bin/env bash

DATASET="$1"

if [[ "$DATASET" != "train" && "$DATASET" != "test" ]]; then
    echo "Usage: $0 {train|test}"
    exit 1
fi

AWS_REGION=us-east-1 s5cmd --no-sign-request ls \
    "s3://argoverse/datasets/av2/sensor/${DATASET}/"
