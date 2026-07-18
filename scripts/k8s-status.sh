#!/usr/bin/env bash
set -euo pipefail

kubectl config use-context kind-content-moderation-local >/dev/null
kubectl get nodes
kubectl get pods -n moderation
kubectl get services -n moderation
