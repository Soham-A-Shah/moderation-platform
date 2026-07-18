# Content Moderation Platform

A simplified, interview-friendly event-driven content moderation platform.

## Architecture

```text
React Frontend
      |
      v
Django API Gateway
(Auth + Users + Content APIs)
      |
      v
content.submitted
      |
      v
Ingestion Service
      |
      v
content.normalized
      |
      v
ML Inference Service
      |
      v
ml.scored
      |
      v
Moderation Service
(Policy + Persistence + Audit)
      |
      v
moderation.completed
      |
      +----------------------+
      |                      |
      v                      v
Notification Service   Analytics Service
```

## Application services

1. `api-gateway` — Django REST API, authentication/users as Django modules, content submission and status APIs.
2. `ingestion-service` — validates and normalizes content.
3. `ml-inference-service` — produces mock toxicity, spam, and violence scores.
4. `moderation-service` — applies policy rules, stores the final result, and writes audit records.
5. `notification-service` — consumes completed decisions and simulates user notifications.
6. `analytics-service` — consumes completed decisions and stores aggregate event metrics.

Infrastructure:

- PostgreSQL
- Redpanda, a Kafka-compatible event broker
- React frontend
- Kafka UI for observing topics and events

## Why this structure

The project demonstrates meaningful microservice boundaries without creating many artificial services.

- Authentication and users remain Django modules because they are tightly related to the public API.
- ML inference is independently deployable and scalable.
- Moderation contains policy evaluation because they share the same decision lifecycle.
- Notifications and analytics are asynchronous consumers of the final moderation event.
- Audit records are written by the moderation service because it owns the final decision.

## Run with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Open:

```text
Frontend: http://localhost:3000
API:      http://localhost:8010/api/content/
Kafka UI: http://localhost:8080
```

Test normal content:

```bash
curl -X POST http://localhost:8010/api/content/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user-101","text":"This is a normal travel post"}'
```

Test risky content:

```bash
curl -X POST http://localhost:8010/api/content/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user-202","text":"buy now free money spam scam"}'
```

View status using the returned content ID:

```bash
curl http://localhost:8010/api/content/<content-id>/
```

## Local Kubernetes with Kind

Install tools:

```bash
brew install kind kubectl
```

Start the local cluster and application:

```bash
chmod +x scripts/*.sh
./scripts/k8s-up.sh
```

The script:

1. Creates a one-node Kind cluster.
2. Builds local images.
3. Loads images directly into Kind.
4. Applies the local Kustomize overlay.
5. Waits for all deployments.

Open:

```text
Frontend: http://localhost:3000
API:      http://localhost:8010/api/content/
Kafka UI: http://localhost:8080
```

Check status:

```bash
./scripts/k8s-status.sh
```

View logs:

```bash
./scripts/k8s-logs.sh moderation-service
./scripts/k8s-logs.sh ml-inference-service
```

Delete the local cluster:

```bash
./scripts/k8s-down.sh
```

Local deployment:

```bash
kubectl apply -k k8s/overlays/local
```

Render manifests without applying:

```bash
kubectl kustomize k8s/overlays/local
```

Delete local resources:

```bash
kubectl delete -k k8s/overlays/local
```

