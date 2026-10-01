# flask-k8s-cicd-pipeline

> **From `git push` to production — automated, observable, and reversible.**

A production-grade DevOps reference project that takes a Python Flask e-commerce API
through the complete software delivery lifecycle: automated testing, containerization,
CI with Jenkins, GitOps delivery with Argo CD, and full observability with
Prometheus + Grafana.

[![CI](https://github.com/<user>/flask-k8s-cicd-pipeline/actions/workflows/pr-checks.yml/badge.svg)](https://github.com/<user>/flask-k8s-cicd-pipeline/actions)
[![Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![Docker](https://img.shields.io/badge/docker-multi--stage-blue)]()
[![Kubernetes](https://img.shields.io/badge/kubernetes-1.30-blue)]()
[![GitOps](https://img.shields.io/badge/gitops-ArgoCD-orange)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## Table of Contents

- [What Is This?](#what-is-this)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Running Tests](#running-tests)
- [Docker](#docker)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI Pipeline (Jenkins)](#ci-pipeline-jenkins)
- [GitOps Delivery (Argo CD)](#gitops-delivery-argo-cd)
- [Observability](#observability)
- [Environments](#environments)
- [Rollback](#rollback)
- [API Reference](#api-reference)
- [Make Targets](#make-targets)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)

---

## What Is This?

`flask-k8s-cicd-pipeline` is a **DevOps reference project**, not just an app.

The application is a small RESTful Flask API (products, users, orders) backed by
PostgreSQL and Redis. The point of the project is the **pipeline around it** —
everything a modern engineering team needs to ship software safely:

- Automated tests with an enforced coverage gate
- Multi-stage, non-root, hardened Docker images
- Kubernetes manifests with probes, HPA, and securityContext
- Jenkins CI triggered by GitHub webhooks
- GitOps delivery via Argo CD (pull-based, self-healing)
- Prometheus metrics, Grafana dashboards, Alertmanager alerts
- Kustomize overlays for dev / staging / prod
- Zero-downtime rolling deploys and one-command rollback

**Everything is code. Everything is automated. Everything is observable.**

---

## Architecture

```mermaid
flowchart TB
    Dev[Developer] -->|git push| GH[GitHub Repo]
    GH -->|webhook| Jenkins[Jenkins CI]
    GH -->|PR trigger| GHA[GitHub Actions]

    GHA -->|lint + test| GH

    Jenkins -->|1. lint + test| Test[Test Stage]
    Jenkins -->|2. build| Docker[Docker Build]
    Docker -->|3. push| Registry[(Container Registry)]
    Jenkins -->|4. update tag| GitOps[GitOps Repo]

    GitOps -->|watch| Argo[Argo CD]
    Argo -->|sync| K8s[Kubernetes Cluster]

    subgraph K8s[Kubernetes Cluster]
        Ingress[NGINX Ingress] --> Svc[Service]
        Svc --> Pod1[Pod]
        Svc --> Pod2[Pod]
        Pod1 --> PG[(Postgres)]
        Pod2 --> PG
        Pod1 --> Redis[(Redis)]
        Pod2 --> Redis
        HPA[HPA 2-10] -.scales.-> Pod1
        HPA -.scales.-> Pod2
    end

    K8s -->|metrics| Prom[Prometheus]
    Prom --> Graf[Grafana]
    Prom --> AM[Alertmanager]
    AM --> Slack[Slack / PagerDuty]

    Users[Users] -->|HTTPS| Ingress
```

### Delivery Flow

```
Developer ─▶ GitHub PR ─▶ GitHub Actions (lint/test) ─▶ Merge
                                                          │
                                                          ▼
                                              Jenkins (build + push image)
                                                          │
                                                          ▼
                                     GitOps Repo (bump image tag)
                                                          │
                                                          ▼
                                            Argo CD (sync to cluster)
                                                          │
                                                          ▼
                                    Kubernetes (rolling update)
                                                          │
                                                          ▼
                                   Prometheus → Grafana → Alerts
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Application** | Python 3.12, Flask 3, SQLAlchemy, Alembic, Gunicorn |
| **Data** | PostgreSQL 16, Redis 7 |
| **Testing** | pytest, pytest-cov, pytest-flask |
| **Linting** | black, isort, flake8, mypy, pre-commit |
| **Containers** | Docker (multi-stage, non-root, healthcheck) |
| **Orchestration** | Kubernetes 1.30 (k3d / EKS / GKE) |
| **Packaging** | Kustomize (base + overlays) |
| **CI** | Jenkins (multibranch, declarative pipeline) |
| **PR Checks** | GitHub Actions |
| **CD** | Argo CD (GitOps, pull-based) |
| **Metrics** | Prometheus, prometheus-flask-exporter |
| **Dashboards** | Grafana (RED metrics) |
| **Alerting** | Alertmanager → Slack |
| **Local Dev** | Docker Compose, Makefile |

---

## Repository Structure

```
flask-k8s-cicd-pipeline/
├── .github/
│   └── workflows/
│       ├── pr-checks.yml              # PR lint + test
│       └── release.yml                # Tag → build + push
│
├── app/                               # Flask application
│   ├── __init__.py
│   ├── main.py                        # App factory
│   ├── config.py                      # Config classes
│   ├── extensions.py                  # db, migrate, cache
│   ├── models/                        # SQLAlchemy models
│   │   ├── product.py
│   │   ├── user.py
│   │   └── order.py
│   ├── routes/                        # Blueprints
│   │   ├── products.py
│   │   ├── users.py
│   │   ├── orders.py
│   │   └── health.py
│   ├── services/                      # Business logic
│   │   ├── product_service.py
│   │   ├── user_service.py
│   │   └── order_service.py
│   └── utils/
│       ├── logger.py                  # JSON logging
│       └── errors.py                  # Global handlers
│
├── migrations/                        # Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial.py
│
├── tests/                             # pytest suite
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_products.py
│   ├── test_users.py
│   └── test_orders.py
│
├── docker/
│   ├── Dockerfile                     # Production multi-stage
│   ├── Dockerfile.dev                 # Dev with hot reload
│   └── entrypoint.sh                  # Migrations + start
│
├── k8s/
│   ├── base/                          # Kustomize base
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   ├── hpa.yaml
│   │   └── kustomization.yaml
│   └── overlays/
│       ├── dev/
│       │   ├── kustomization.yaml
│       │   └── replicas-patch.yaml
│       ├── staging/
│       │   └── kustomization.yaml
│       └── prod/
│           ├── kustomization.yaml
│           ├── replicas-patch.yaml
│           └── resources-patch.yaml
│
├── monitoring/
│   ├── servicemonitor.yaml            # Prometheus scrape config
│   ├── prometheus-rules.yaml          # Alert rules
│   └── grafana-dashboard.json         # RED dashboard
│
├── scripts/
│   ├── bootstrap.sh                   # Local env setup
│   ├── build.sh                       # Build image
│   ├── deploy.sh                      # Deploy to env
│   ├── rollback.sh                    # Undo last deploy
│   └── seed_db.py                     # Sample data
│
├── docs/
│   ├── architecture.md
│   └── runbook.md
│
├── .dockerignore
├── .env.example
├── .flake8
├── .gitignore
├── .pre-commit-config.yaml
├── docker-compose.yml
├── Jenkinsfile
├── Makefile
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Quick Start

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.12+ | `sudo apt install python3.12` |
| Docker | 24+ | https://docs.docker.com/engine/install/ |
| kubectl | 1.30+ | https://kubernetes.io/docs/tasks/tools/ |
| k3d | 5+ | `curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh \| bash` |
| Make | any | `sudo apt install make` |

### 60-Second Setup

```bash
git clone https://github.com/<user>/flask-k8s-cicd-pipeline.git
cd flask-k8s-cicd-pipeline
cp .env.example .env
chmod +x scripts/*.sh docker/entrypoint.sh
./scripts/bootstrap.sh
make run
```

API is now at **http://localhost:5000**

```bash
curl http://localhost:5000/healthz
# {"status": "ok"}

curl http://localhost:5000/
# {"service": "shopapi", "version": "1.0.0", ...}
```

---

## Local Development

### Start the stack

```bash
make run
```

This runs `docker compose up --build`, starting:

- `api` (Flask, hot reload via volume mount) on port 5000
- `postgres` on port 5432
- `redis` on port 6379

### Run migrations

```bash
make migrate
```

### Seed sample data

```bash
make seed
```

### Stop everything

```bash
docker compose down
docker compose down -v   # also wipes volumes
```

---

## Running Tests

```bash
make test
```

Output includes:

- pytest results
- coverage summary (fails below 80%)
- HTML report in `htmlcov/index.html`

### Manually with coverage

```bash
. venv/bin/activate
pytest --cov=app --cov-report=term-missing --cov-report=html
xdg-open htmlcov/index.html
```

### Lint and format

```bash
make lint      # check only
make format    # auto-fix
```

### Pre-commit hooks

Installed by `scripts/bootstrap.sh`. To run manually:

```bash
pre-commit run --all-files
```

---

## Docker

### Build production image

```bash
make build
# or
docker build -f docker/Dockerfile -t shopapi:local .
```

The image is:

- **multi-stage** — build deps separate from runtime
- **non-root** — runs as UID 1000
- **read-only root FS** — writes only to `/tmp`
- **healthchecked** — `/healthz` probed every 30s
- **slim** — `python:3.12-slim` base, ~150 MB

### Run standalone

```bash
docker run --rm -p 5000:5000 \
  -e DATABASE_URL=postgresql://shop:shop@host.docker.internal:5432/shopapi \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  shopapi:local
```

### Multi-arch build (optional)

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile \
  -t youruser/shopapi:latest \
  --push .
```

---

## Kubernetes Deployment

### Create local cluster

```bash
k3d cluster create shopapi --agents 2
kubectl create namespace shopapi
```

### Deploy Postgres + Redis (dev only)

```bash
kubectl apply -n shopapi -f k8s/base/postgres-redis.yaml
```

### Build and load image

```bash
docker build -f docker/Dockerfile -t shopapi:local .
k3d image import shopapi:local -c shopapi
```

### Deploy the app

```bash
./scripts/deploy.sh dev
```

Verify:

```bash
kubectl get pods -n shopapi
kubectl get svc -n shopapi
kubectl get hpa -n shopapi
```

Access locally:

```bash
kubectl port-forward -n shopapi svc/shopapi 8080:80
curl http://localhost:8080/healthz
```

### Rolling update demo

```bash
# Trigger a rollout with a new image tag
kubectl set image deployment/shopapi \
  shopapi=shopapi:newtag -n shopapi

# Watch the rollout
kubectl rollout status deployment/shopapi -n shopapi

# History
kubectl rollout history deployment/shopapi -n shopapi
```

---

## CI Pipeline (Jenkins)

### Setup

1. Install Jenkins (via Docker or apt)
2. Add plugins: **Git**, **GitHub**, **Docker Pipeline**, **Kubernetes CLI**, **Blue Ocean**
3. Add credentials:
   - `dockerhub-creds` (username/password)
   - `github-token` (secret text)
   - `kubeconfig` (secret file)
4. Create a **Multibranch Pipeline** pointing at your GitHub repo
5. Add a GitHub webhook: `http://<jenkins>/github-webhook/`

### Pipeline stages

| Stage | What it does |
|---|---|
| Checkout | Clones the repo |
| Setup | Creates venv, installs deps |
| Lint | black, isort, flake8, mypy |
| Test | pytest with coverage gate at 80% |
| Build Image | Docker build, tag with `BUILD_NUMBER` |
| Push Image | Push to Docker Hub / GHCR |
| Update GitOps | Commit new image tag to gitops repo |

**Key principle:** Jenkins **never touches the cluster.** It only updates the
GitOps repo. Argo CD does the actual deployment.

---

## GitOps Delivery (Argo CD)

### Install Argo CD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Get admin password

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d && echo
```

### Access UI

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# https://localhost:8080 — admin / <password>
```

### Register the app

```bash
kubectl apply -f gitops/apps/shopapi.yaml
```

Example Application manifest:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: shopapi-dev
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/<user>/shopapi-gitops.git
    targetRevision: HEAD
    path: envs/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: shopapi
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

Now any push to the gitops repo auto-deploys.

---

## Observability

### Metrics

Every pod exposes `/metrics` with:

- `flask_http_request_total{status, method, endpoint}`
- `flask_http_request_duration_seconds_bucket`
- `flask_http_request_in_progress`
- `python_gc_*`, `process_*`

### Install Prometheus + Grafana

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### Enable scraping

```bash
kubectl apply -f monitoring/servicemonitor.yaml
kubectl apply -f monitoring/prometheus-rules.yaml
```

### Grafana dashboard

```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# http://localhost:3000 — admin / prom-operator
```

Import `monitoring/grafana-dashboard.json` for the RED dashboard.

### Alerts

| Alert | Condition | Severity |
|---|---|---|
| `HighErrorRate` | 5xx rate > 5% for 5m | critical |
| `HighLatency` | p99 > 1s for 10m | warning |
| `PodCrashLooping` | restarts > 5 in 10m | critical |
| `HPAMaxedOut` | replicas == max for 10m | warning |

Alerts route to Slack via Alertmanager.

---

## Environments

| Env | Replicas | DB | Debug | Deploy Trigger |
|---|---|---|---|---|
| **dev** | 1 | ephemeral | on | auto on merge to `main` |
| **staging** | 2 | real | off | PR to `envs/staging/values.yaml` |
| **prod** | 4 | HA + backups | off | PR to `envs/prod/values.yaml` + approval |

### Promote dev → staging

```bash
cd shopapi-gitops
yq -i '.image.tag = "1042"' envs/staging/values.yaml
git commit -am "promote shopapi to 1042 on staging"
git push
# open PR → review → merge → Argo CD syncs
```

---

## Rollback

### Option A — Fast (kubectl)

```bash
./scripts/rollback.sh
# or
kubectl rollout undo deployment/shopapi -n shopapi
```

### Option B — Proper GitOps (preferred)

```bash
cd shopapi-gitops
git revert HEAD --no-edit
git push
# Argo CD detects the revert and syncs to the previous tag
```

**Use A for emergencies. Use B for everything else** — Git stays the source of truth.

---

## API Reference

Base URL: `http://localhost:5000`

### Health

| Method | Path | Description |
|---|---|---|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness — checks DB + Redis |
| GET | `/metrics` | Prometheus metrics |

### Products

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/products/` | List all products |
| GET | `/api/v1/products/<id>` | Get a product |
| POST | `/api/v1/products/` | Create a product |
| PUT | `/api/v1/products/<id>` | Update a product |
| DELETE | `/api/v1/products/<id>` | Delete a product |

### Users

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/users/` | List users |
| GET | `/api/v1/users/<id>` | Get a user |
| POST | `/api/v1/users/` | Register a user |

### Orders

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/orders/` | List orders |
| GET | `/api/v1/orders/<id>` | Get an order |
| POST | `/api/v1/orders/` | Create an order |

### Example

```bash
# Create a product
curl -X POST http://localhost:5000/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "price": 9.99, "stock": 100}'

# List products
curl http://localhost:5000/api/v1/products/
```

---

## Make Targets

```
$ make help

help            Show this help
install         Install dev dependencies
test            Run tests with coverage
lint            Run all linters
format          Auto-format code
run             Run local stack with docker compose
build           Build docker image
deploy          Deploy to k8s dev
rollback        Rollback deployment
migrate         Run DB migrations
seed            Seed database
clean           Clean caches
```

---

## Troubleshooting

### `terraform -version` not found

```bash
# Use tfenv instead of apt
git clone --depth=1 https://github.com/tfutils/tfenv.git ~/.tfenv
echo 'export PATH="$HOME/.tfenv/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
tfenv install latest && tfenv use latest
```

### Pod stuck in `CrashLoopBackOff`

```bash
kubectl logs -n shopapi <pod> --previous
kubectl describe pod -n shopapi <pod>
```

Common causes: missing Secret, DB unreachable, migration failure.

### `readyz` returns 503

```bash
kubectl exec -n shopapi <pod> -- curl localhost:5000/readyz
```

Check Postgres and Redis connectivity from inside the pod.

### Argo CD shows `OutOfSync` forever

```bash
kubectl -n argocd get application shopapi-dev -o yaml | grep -A5 status
```

Common causes: kubectl drift, CRD not installed, RBAC issue.

### Port 5000 already in use

```bash
sudo lsof -i :5000
kill <pid>
```

Or change the port in `docker-compose.yml`.

---

## Roadmap

- [ ] Replace Kustomize with Helm
- [ ] Add Terraform for EKS provisioning
- [ ] Add Trivy image scanning to Jenkins
- [ ] Sign images with Cosign
- [ ] Add Loki for centralized logs
- [ ] Add OpenTelemetry tracing → Tempo
- [ ] Add Argo Rollouts for canary deploys
- [ ] Add k6 load tests as a pre-prod gate
- [ ] Add Kyverno policies (no latest tag, no root)
- [ ] Add Vault for secrets

---

## Contributing

PRs welcome. Please:

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-thing`
3. Ensure `make lint && make test` pass
4. Open a PR — the CI will run automatically

---

## License

MIT — see [LICENSE](LICENSE).

---

## Author

**Ansh** — DevOps / Platform Engineering

- GitHub: [@<user>](https://github.com/<user>)
- LinkedIn: [<profile>](https://linkedin.com/in/<profile>)

---

<p align="center">
  <em>Built to demonstrate real DevOps — not tutorials.</em><br>
  <strong>Everything as code. Everything automated. Everything observable.</strong>
</p>
