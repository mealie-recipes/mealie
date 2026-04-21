# Reproduction Guide — Mealie ML Recommendations (proj18)

**Team:** Bias & Variance  
**VM:** `129.114.26.214` (KVM@TACC, Chameleon Cloud)  
**Branch:** `feature/ml-recommendations`

---

## What This System Does

Mealie is a self-hosted recipe manager extended with a personalized ML recommendation feature. The system uses ALS collaborative filtering to rank recipes by predicted user preference. A CronJob pipeline handles ETL, monthly retraining, and nightly evaluation. Prometheus + Grafana provide infrastructure monitoring with alerting.

---

## Quick Check — Everything Already Running

If the VM is live, all services should already be up. Verify:

| Service | URL |
|---|---|
| Mealie UI | http://129.114.26.214:30800 |
| Inference API | http://129.114.26.214:30090/health |
| MLflow | http://129.114.26.214:30500 |
| MinIO Console | http://129.114.26.214:30901 (minioadmin / minioadmin123) |
| Prometheus | http://129.114.26.214:30091 |
| Grafana | http://129.114.26.214:30300 (admin / admin123) |
| Alertmanager | http://129.114.26.214:30903 |

```bash
ssh cc@129.114.26.214
sudo kubectl get pods -n mealie-prod
sudo kubectl get pods -n platform
sudo kubectl get pods -n monitoring
```

---

## Full Reproduction From Scratch

### Prerequisites

- Chameleon Cloud account with access to proj18 lease on KVM@TACC
- JupyterHub on Chameleon (chi.uc.edu or chi.tacc.utexas.edu)
- The following repos cloned on Chameleon JupyterHub:
  - `https://github.com/Sharvin27/mealie` (this repo, branch `feature/ml-recommendations`)
  - `https://github.com/[bryce-repo]` — ETL/data pipeline
  - `https://github.com/[shashwat-repo]` — ALS training
  - `https://github.com/[mahima-repo]` — platform/DevOps manifests

### Step 1 — Open the Integration Notebook

Open `integration_chameleon_setup_new.ipynb` on Chameleon JupyterHub.

Run cells **in order from top to bottom**. Each cell is idempotent — safe to re-run.

### Step 2 — Cell-by-Cell Summary

| Cells | What it does |
|---|---|
| 0–1 | Markdown intro and imports |
| 2 | Connect to proj18 Chi lease |
| 3–4 | Attach to existing VM `node-integration-proj18`, get floating IP |
| 5 | Check SSH connectivity |
| 6–7 | Install Docker + K3s on VM (skips if already installed) |
| 8 | Clone all team repos into `/home/cc/proj18/` |
| 9 | Create Kubernetes namespaces: `mealie-prod`, `platform`, `monitoring` |
| 10 | Create Kubernetes Secrets: `postgres-secret`, `minio-secret` |
| 11 | Create `shared-env` ConfigMap with all service URLs |
| 12 | Apply Mahima's platform manifests (PostgreSQL, MinIO, MLflow) |
| **12.5** | **Bootstrap: generate synthetic training data → upload to MinIO → build `mealie-als-training:integration-rerun` image → run ALS training → write `production/tag_to_vector.pkl` to MinIO** |
| 13–14 | Build + deploy Inference API (`mealie-inference:latest`) |
| 15–16 | Build + deploy Mealie custom image (`mealie-custom:latest`) |
| **17** | **Apply CronJobs from `dev/cronjobs/`: ETL (batch-compile), monthly retrain, nightly eval** |
| **17.5** | **Deploy monitoring stack: Prometheus RBAC + configmap + deployment, Grafana, kube-state-metrics, Alertmanager, HPA** |
| 17.6 | Deploy staging + canary inference-api environments |
| 17.7 | Apply model-promoter CronJob (staging → canary → production) |
| 18 | Wait 60s, verify all pods running |
| 19 | Stub model artifacts (only if MinIO is empty) |
| 20 | Health checks on all endpoints |
| 21 | Print all access URLs |
| 22 | Open firewall ports via iptables |

### Step 3 — Verify CronJobs

```bash
# Trigger ETL manually
sudo kubectl create job --from=cronjob/batch-compile-datasets manual-etl-1 -n mealie-prod
sudo kubectl logs -n mealie-prod -l job-name=manual-etl-1 -f

# Trigger retrain manually
sudo kubectl create job --from=cronjob/monthly-retrain manual-retrain-1 -n mealie-prod
sudo kubectl logs -n mealie-prod -l job-name=manual-retrain-1 -f

# Trigger nightly eval manually
sudo kubectl create job --from=cronjob/nightly-eval manual-eval-1 -n mealie-prod
sudo kubectl logs -n mealie-prod -l job-name=manual-eval-1 -f
```

Check MLflow at http://129.114.26.214:30500 — experiments `mealie-recipe-recommender` and `nightly-eval` should have runs logged.

### Step 4 — Verify ML Recommendations

1. Open Mealie UI at http://129.114.26.214:30800
2. Log in (admin / MyPassword)
3. Go to **Preferences** and select at least 2 cuisine tags
4. Navigate to **Home** — the "Recommended for You" panel should appear
5. Rate a few recipes (star rating) — recommendations update

---

## Repository Structure (ML-relevant files)

```
dev/
  cronjobs/
    mealie-prod-batch-compile-cronjob.yaml   # ETL: PostgreSQL → MinIO parquet
    mealie-prod-monthly-retrain-cronjob.yaml # ALS model retraining
    mealie-prod-nightly-eval-cronjob.yaml    # MLflow health/quality logging
  monitoring/
    prometheus-rbac.yaml                     # ServiceAccount + ClusterRole
    prometheus-configmap.yaml                # Scrape config + 5 alert rules
    prometheus-deployment.yaml               # NodePort 30091
    grafana-configmap.yaml                   # Prometheus datasource
    grafana-deployment.yaml                  # NodePort 30300
    alertmanager-configmap.yaml              # Alert routing config
    alertmanager-deployment.yaml             # NodePort 30903
    kube-state-metrics-rbac.yaml             # RBAC for cluster metrics
    kube-state-metrics.yaml                  # Deployment + Service
    inference-api-hpa.yaml                   # HPA: scale 1-3 on CPU>70%

mealie/services/recommendation_service.py   # Inference API client + fallback
frontend/app/components/AppRecommendedForYou.vue  # Recommendation UI panel
frontend/app/pages/preferences.vue          # Onboarding tag selection

SAFEGUARDING.md                             # Fairness, privacy, robustness plan
integration_chameleon_setup_new.ipynb       # Main reproduction notebook
```

---

## Alert Rules (Prometheus)

Configured in `dev/monitoring/prometheus-configmap.yaml`:

| Rule | Condition | Severity |
|---|---|---|
| PodCrashLooping | >2 restarts in 10 min | warning |
| DeploymentReplicasUnavailable | unavailable replicas > 0 for 10 min | critical |
| StatefulSetReplicasUnavailable | ready < desired for 10 min | critical |
| FailedCronJob | any job failure | warning |
| InferenceAPIDown | /metrics unreachable for 2 min | critical |

---

## Kubernetes Namespaces

| Namespace | Contents |
|---|---|
| `mealie-prod` | Mealie app, inference-api, CronJobs, HPA |
| `platform` | PostgreSQL, MinIO, MLflow |
| `monitoring` | Prometheus, Grafana, Alertmanager, kube-state-metrics |
| `mealie-staging` | Staging inference-api (staging model) |
| `mealie-canary` | Canary inference-api (canary model) |

---

## Troubleshooting

**Pod stuck in Pending:**
```bash
sudo kubectl describe pod <pod-name> -n <namespace> | tail -10
# Usually CPU/memory pressure on single-node VM
sudo kubectl patch deployment <name> -n <namespace> --type='json' \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/cpu","value":"50m"}]'
```

**CronJob fails with DB error:**
```bash
# Verify postgres secret exists
sudo kubectl get secret postgres-secret -n mealie-prod
```

**Inference API returns 503:**
```bash
# Check if model artifact exists in MinIO
# MinIO Console → mlflow-artifacts bucket → production/tag_to_vector.pkl
# If missing, run Cell 12.5 from the notebook
```
