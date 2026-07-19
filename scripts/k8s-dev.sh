#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME=content-moderation-local
CONTEXT_NAME=kind-content-moderation-local

for command_name in docker kubectl kind skaffold; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing command: $command_name"
    echo "Install local k8s dev tools with: brew install kind kubectl skaffold"
    exit 1
  fi
done

if ! kind get clusters | grep -qx "$CLUSTER_NAME"; then
  kind create cluster \
    --name "$CLUSTER_NAME" \
    --config infrastructure/kind/kind-config.yaml
fi

kubectl config use-context "$CONTEXT_NAME"

echo "Starting continuous k8s development loop."
echo "Skaffold will rebuild and redeploy changed frontend/backend images."
echo "Press Ctrl+C to stop watching."
echo

skaffold dev --filename skaffold.yaml --cleanup=false
