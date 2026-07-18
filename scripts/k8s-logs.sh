#!/usr/bin/env bash
set -euo pipefail

SERVICE="${1:-moderation-service}"
kubectl logs -f "deployment/${SERVICE}" -n moderation
