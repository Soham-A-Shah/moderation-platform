#!/usr/bin/env bash
set -euo pipefail

curl -X POST http://localhost:8010/api/content/   -H "Content-Type: application/json"   -d '{"user_id":"demo-user","text":"buy now free money spam scam"}'
