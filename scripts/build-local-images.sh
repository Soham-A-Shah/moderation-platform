#!/usr/bin/env bash
set -euo pipefail

docker build -t api-gateway:latest -f backend/api-gateway/Dockerfile .
docker build -t ingestion-service:latest -f backend/services/ingestion-service/Dockerfile .
docker build -t ml-inference-service:latest -f backend/services/ml-inference-service/Dockerfile .
docker build -t moderation-service:latest -f backend/services/moderation-service/Dockerfile .
docker build -t notification-service:latest -f backend/services/notification-service/Dockerfile .
docker build -t analytics-service:latest -f backend/services/analytics-service/Dockerfile .
docker build -t frontend:latest -f frontend/Dockerfile .

echo "All application images were built."
