#!/usr/bin/env bash

set -euo pipefail

DATASET="$1"
LOG_ID="$2"

if [[ "$DATASET" != "train" && "$DATASET" != "test" ]]; then
    echo "Usage: $0 {train|test} <log_id>"
    exit 1
fi

AWS_REGION=us-east-1 s5cmd --no-sign-request cp \
    "s3://argoverse/datasets/av2/sensor/${DATASET}/${LOG_ID}/*" \
    "./data/raw/${DATASET}/${LOG_ID}/"
