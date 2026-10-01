#!/usr/bin/env bash

set -euo pipefail

NAMESPACE="${NAMESPACE:-shopapi}"

echo "Rolling back ShopAPI..."

kubectl rollout undo \
    deployment/shopapi \
    -n "${NAMESPACE}"

kubectl rollout status \
    deployment/shopapi \
    -n "${NAMESPACE}" \
    --timeout=180s

echo "Rollback complete."
