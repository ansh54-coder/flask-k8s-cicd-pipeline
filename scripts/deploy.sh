#!/usr/bin/env bash

set -euo pipefail

NAMESPACE="${NAMESPACE:-shopapi}"
OVERLAY="${OVERLAY:-prod}"

echo "Deploying ShopAPI"
echo "Namespace: ${NAMESPACE}"
echo "Overlay: ${OVERLAY}"

kubectl apply \
    -k "k8s/overlays/${OVERLAY}"

kubectl rollout status \
    deployment/shopapi \
    -n "${NAMESPACE}" \
    --timeout=180s

echo "Deployment complete."
