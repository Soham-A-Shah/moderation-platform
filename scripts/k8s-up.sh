#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME=content-moderation-local
CONTEXT_NAME=kind-content-moderation-local

for command_name in docker kubectl kind; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing command: $command_name"
    echo "Install with: brew install kind kubectl"
    exit 1
  fi
done

if ! kind get clusters | grep -qx "$CLUSTER_NAME"; then
  kind create cluster     --name "$CLUSTER_NAME"     --config infrastructure/kind/kind-config.yaml
fi

kubectl config use-context "$CONTEXT_NAME"

./scripts/build-local-images.sh

for image in   api-gateway:latest   ingestion-service:latest   ml-inference-service:latest   moderation-service:latest   notification-service:latest   analytics-service:latest   frontend:latest
do
  kind load docker-image "$image" --name "$CLUSTER_NAME"
done

kubectl apply -k k8s/overlays/local

kubectl wait   --for=condition=Available   deployment   --all   --namespace moderation   --timeout=300s

echo
echo "Frontend: http://localhost:3000"
echo "API:      http://localhost:8010/api/content/"
echo "Kafka UI: http://localhost:8080"
kubectl get pods -n moderation
