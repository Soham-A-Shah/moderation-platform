#!/usr/bin/env bash
set -euo pipefail

kind delete cluster --name content-moderation-local
