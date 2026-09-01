# Automated Canary Deployment with LGTM Observability & Automated Rollback

An enterprise-grade, GitOps-ready Kubernetes deployment framework featuring automated **Canary releases**, **real-time LGTM telemetry (Logs, Metrics, Traces, Dashboards)**, and **metric-driven automated rollbacks**.

---

## 📌 Table of Contents
- [What It Does](#-what-it-does)
- [Why Do We Need It?](#-why-do-we-need-it)
- [Architecture & Tech Stack](#-architecture--tech-stack)
- [Component Start/Stop & Feature Flags](#-component-startstop--feature-flags)
- [Security & Governance](#-security--governance)
- [Real-World Usage & Deployment Guide](#-real-world-usage--deployment-guide)
- [Repository Structure](#-repository-structure)

---

## 🎯 What It Does

This platform orchestrates a complete **Canary Deployment lifecycle with Automated Rollback**:

1. **Traffic Splitting:** Routes a small percentage of production traffic (e.g., 10–20%) to the new **Canary** version while keeping the **Stable** version handling the majority of user traffic.
2. **Unified LGTM Observability:**
   - **Loki:** Ingests and indexes structured application and cluster logs.
   - **Grafana:** Visualizes metrics, logs, and distributed traces in a unified pane of glass.
   - **Tempo:** Distributed tracing backend capturing end-to-end request journeys across microservices.
   - **Mimir:** High-availability, long-term storage Prometheus-compatible metrics database.
   - **Alloy:** OpenTelemetry Collector / Telemetry Agent for logs, metrics, and trace forwarding.
3. **Real-Time Health Evaluation:** Continuously evaluates error rates, latency (p95/p99), and HTTP 5xx responses using OpenTelemetry metrics.
4. **Automated Rollback:** If the Canary deployment breaches health thresholds (e.g. error rate > 2%), the pipeline automatically terminates the Canary pods and restores 100% traffic to Stable within seconds without human intervention.

---

## 💡 Why Do We Need It?

| Traditional Deployment Risk | Automated Canary & Rollback Solution |
|---|---|
| **High Blast Radius:** A buggy release affects 100% of users immediately. | **Minimal Blast Radius:** Only a small subset of traffic reaches the new release during evaluation. |
| **Manual Monitoring Delays:** Engineers must stare at dashboards and manually run rollback commands. | **Automated Decision Engine:** CI/CD runners automatically roll back immediately upon metric violation. |
| **Silent Failures & Memory Leaks:** Issues like slow memory leaks or upstream API errors go unnoticed until outage. | **Distributed Tracing & Exemplars:** Tempo and Mimir link traces directly to log spikes in Grafana. |
| **Downtime During Upgrades:** Deploying monolithic updates causes service disruptions. | **Zero Downtime:** Seamless traffic routing via Kubernetes Services and Ingress annotations. |

---

## 🏛️ Architecture & Tech Stack

```
 ┌─────────────────────────────────────────────────────────────┐
 │                       USERS / CLIENTS                       │
 └──────────────────────────────┬──────────────────────────────┘
                                │ (Traffic Splitting via Ingress)
                    ┌───────────┴───────────┐
                    │ 90% Traffic           │ 10% Traffic
                    ▼                       ▼
          ┌──────────────────┐    ┌──────────────────┐
          │  Stable Service  │    │  Canary Service  │
          │  (v1.0.0 Stable) │    │  (v1.1.0 Canary) │
          └─────────┬────────┘    └─────────┬────────┘
                    │                       │
                    └───────────┬───────────┘
                                │ OpenTelemetry OTLP
                                ▼
          ┌──────────────────────────────────────────┐
          │          Grafana Alloy Agent             │
          └─────┬───────────────┬──────────────┬─────┘
                │ Metrics       │ Logs         │ Traces
                ▼               ▼              ▼
          ┌───────────┐   ┌───────────┐  ┌───────────┐
          │   Mimir   │   │   Loki    │  │   Tempo   │
          └─────┬─────┘   └─────┬─────┘  └─────┬─────┘
                └───────────────┼──────────────┘
                                ▼
          ┌──────────────────────────────────────────┐
          │           Grafana Dashboards             │
          └──────────────────────────────────────────┘
```

---

## 🎛️ Component Start/Stop & Feature Flags

Every component in the `helm/lgtm-stack` Helm chart can be individually enabled or disabled via `values.yaml` or `--set` command-line flags.

### In `values.yaml`:
```yaml
# Enable or disable individual components
grafana:
  enabled: true

alloy:
  enabled: true

loki:
  enabled: true

mimir:
  enabled: true

tempo:
  enabled: true

nodeApp:
  enabled: true

pythonApp:
  enabled: true
```

### Examples of Command-Line Overrides:

```bash
# 1. Deploy ONLY the Observability Stack (Disable sample apps)
helm upgrade --install lgtm helm/lgtm-stack \
  --set nodeApp.enabled=false \
  --set pythonApp.enabled=false

# 2. Deploy without Heavy Tracing (Disable Tempo & Alloy tracing)
helm upgrade --install lgtm helm/lgtm-stack \
  --set tempo.enabled=false

# 3. Deploy ONLY the Python Sample Application
helm upgrade --install python-app helm/lgtm-stack \
  --set grafana.enabled=false \
  --set alloy.enabled=false \
  --set loki.enabled=false \
  --set mimir.enabled=false \
  --set tempo.enabled=false \
  --set nodeApp.enabled=false \
  --set pythonApp.enabled=true
```

---

## 🔒 Security & Governance

1. **Least-Privilege RBAC:**
   - The Alloy agent uses a scoped `ClusterRole` restricted to read-only `get`, `list`, `watch` on pods, services, and endpoints for service discovery.
2. **Non-Root & Hardened Containers:**
   - Applications and telemetry collectors run as non-privileged users with dropped root capabilities.
3. **Zero Plaintext Credentials in Git:**
   - All environment variables, cloud credentials, and kubeconfig tokens are managed via GitHub Secrets and OIDC.
4. **Isolated Workloads:**
   - Ephemeral canary instances share identical NetworkPolicies and resource limits to ensure fair resource allocation.

---

## 🚀 Real-World Usage & Deployment Guide

### Step 1: Deploy the LGTM Observability Stack
```bash
# Verify Helm chart
helm lint helm/lgtm-stack

# Install full stack
helm upgrade --install lgtm-stack helm/lgtm-stack
```

### Step 2: Access Grafana Dashboard
```bash
# Port forward Grafana UI
kubectl port-forward svc/grafana 3000:80

# Open in browser: http://localhost:3000
# Default Login: admin / admin
```

### Step 3: Trigger a Canary Deployment
Deploy a new version to the canary pool:
```bash
kubectl apply -f k8s/canary-deployment.yaml
```

### Step 4: Simulate Error Spikes & Watch Automated Rollback
Run the error simulator to trigger 500 errors and memory leaks:
```bash
python3 app/error_leak.py
```

When error rates exceed the defined SLO (e.g., > 2%), the GitHub Actions workflow (`.github/workflows/canary-deployment.yml`) automatically executes:
```bash
kubectl scale deployment/canary-deployment --replicas=0
```
Restoring 100% stable traffic with zero user disruption.

---

## 📁 Repository Structure

```
rollbackproject/
├── .gitignore                   # Ignores Terraform states, Python venvs, and secrets
├── README.md                    # Complete project guide and operational runbook
├── app/                         # Microservice source code & error leak simulator
│   ├── main.py                  # Python app with OpenTelemetry instrumentation
│   ├── error_leak.py            # Script simulating memory leaks and HTTP errors
│   ├── requirements.txt         # App dependencies (Flask, opentelemetry-sdk)
│   └── Dockerfile               # Container build file
│
├── helm/
│   └── lgtm-stack/              # Unified LGTM Observability & Apps Helm Chart
│       ├── Chart.yaml           # Chart metadata
│       ├── values.yaml          # Master configuration with start/stop enabled flags
│       └── templates/
│           ├── alloy.yaml       # OpenTelemetry agent & pipelines (conditional)
│           ├── grafana.yaml     # Grafana & automated datasources (conditional)
│           ├── loki.yaml        # Loki logging database (conditional)
│           ├── mimir.yaml       # Mimir metrics database (conditional)
│           ├── tempo.yaml       # Tempo tracing backend (conditional)
│           ├── node-app.yaml    # Sample Node.js microservice (conditional)
│           └── python-app.yaml  # Sample Python microservice (conditional)
│
├── k8s/                         # Kubernetes manifests
│   ├── canary-deployment.yaml   # Canary workload definition
│   ├── stable-deployment.yaml   # Stable workload definition
│   └── ingress.yaml             # Traffic splitting ingress rules
│
├── infra-setup/                 # Foundational cloud & cluster setup
│   └── main.tf                  # Terraform cluster provisioning
│
└── .github/
    └── workflows/
        ├── canary-deployment.yml# Canary rollout & automated rollback workflow
        └── infra-setup.yml      # CI/CD infrastructure deployment
```

