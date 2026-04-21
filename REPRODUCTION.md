# Reproduction Guide — Mealie ML Recommendations (proj18)

**Team:** Bias & Variance  
**Branch:** `feature/ml-recommendations`  
**Estimated time:** ~45–60 minutes end-to-end

---

## Prerequisites

- Chameleon Cloud account with access to project **CHI-251409**
- Access to Chameleon JupyterHub at https://jupyter.chameleoncloud.org
- The following GitHub repos cloned on JupyterHub (the notebook clones them automatically onto the VM):
  - `https://github.com/Sharvin27/mealie` — this repo (branch `feature/ml-recommendations`)
  - Sharvin's serving 
  - Bryce's data pipeline repo
  - Shashwat's ALS training repo
  - Mahima's DevOps/platform repo

---

## Step 1 — Open the Integration Notebook on Chameleon JupyterHub

1. Log into https://jupyter.chameleoncloud.org
2. Clone this repo or upload `integration_chameleon_setup_new.ipynb`
3. Open the notebook and run cells **top to bottom in order**

---

## Step 2 — Cell-by-Cell Guide

| Cell | What it does | Notes |
|---|---|---|
| 1 | Imports + project context | Select CHI-251409, site KVM@TACC |
| 2 | **Create new lease** on KVM@TACC | 48-hour lease, m1.xlarge flavor |
| 3 | **Launch new VM** (CC-Ubuntu24.04) | Polls until ACTIVE (~2 min) |
| 4 | **Add OpenStack security groups** | Opens ports 22, 30090, 30800, 30500, 30900, 30901, 30091, 30300, 30903 |
| 5 | Associate floating IP + verify SSH | Stores `floating_ip` variable used throughout |
| 6 | Install Docker on VM | Skips if already installed |
| 7 | Install K3s (Kubernetes) | Skips if already installed |
| 8 | Clone all team repos into `/home/cc/proj18/` | mealie, mealie-serving, mlops-devops, mealie_als_training |
| 9 | Create Kubernetes namespaces | mealie-prod, platform, monitoring |
| 10 | Create Kubernetes Secrets | postgres-secret, minio-secret |
| 11 | Create `shared-env` ConfigMap | All service URLs and MinIO credentials |
| 12 | Apply Mahima's platform manifests | Deploys PostgreSQL, MinIO, MLflow |
| **12.5** | **Bootstrap training data + ALS model** | Generates synthetic data → MinIO → builds training image → runs ALS → saves `production/tag_to_vector.pkl` |
| 13–14 | Build + deploy Inference API | `mealie-inference:latest`, NodePort 30800 |
| 15–16 | Build + deploy Mealie | `mealie-custom:latest`, NodePort 30090 |
| **17** | **Apply CronJobs** | ETL (2am daily), retrain (4am 1st of month), nightly-eval (3am) |
| **17.5** | **Deploy monitoring stack** | Prometheus (30091), Grafana (30300), Alertmanager (30903), kube-state-metrics, HPA |
| 17.6 | Staging + Canary environments | mealie-staging and mealie-canary namespaces |
| 17.7 | Model-promoter CronJob | Auto-promotes staging→canary→production every 6h |
| 18 | Wait 60s + verify all pods | `kubectl get pods --all-namespaces` |
| 19 | Stub model artifacts | Only runs if MinIO has no model artifact yet |
| 20 | Health checks | Inference API /health, /tag-vector, /recommend |
| 21 | Print all access URLs | Shows all service URLs with the dynamic floating IP |
| 22 | Open iptables firewall ports | Opens all NodePorts via iptables on the VM |

> **Cell 12.5 is critical** — it bootstraps the initial model artifact so the inference API has something to load. Without it, recommendations return empty.

---

## Step 3 — Verify Services

After the notebook completes, all services are accessible at `http://<floating_ip>:<port>`:

| Service | Port | Credentials |
|---|---|---|
| Mealie UI | 30090 | admin / MyPassword |
| Inference API health | 30800/health | — |
| MLflow | 30500 | — |
| MinIO Console | 30901 | minioadmin / minioadmin123 |
| Prometheus | 30091 | — |
| Grafana | 30300 | admin / admin123 |
| Alertmanager | 30903 | — |

```bash
# SSH into the VM
ssh cc@<floating_ip>

# Check all pods
sudo kubectl get pods --all-namespaces

# Check CronJobs
sudo kubectl get cronjobs -n mealie-prod
```

---

## Step 4 — Test the ML Pipeline End-to-End

```bash
# 1. Trigger ETL manually (compiles PostgreSQL ratings → MinIO parquet)
sudo kubectl create job --from=cronjob/batch-compile-datasets manual-etl-1 -n mealie-prod
sudo kubectl logs -n mealie-prod -l job-name=manual-etl-1 -f

# 2. Trigger ALS retraining
sudo kubectl create job --from=cronjob/monthly-retrain manual-retrain-1 -n mealie-prod
sudo kubectl logs -n mealie-prod -l job-name=manual-retrain-1 -f

# 3. Trigger nightly evaluation (logs to MLflow)
sudo kubectl create job --from=cronjob/nightly-eval manual-eval-1 -n mealie-prod
sudo kubectl logs -n mealie-prod -l job-name=manual-eval-1 -f
```

Check MLflow at `http://<floating_ip>:30500` — experiments `mealie-recipe-recommender` and `nightly-eval` should have new runs.

---

## Step 5 — Verify ML Recommendations in UI

1. Open Mealie at `http://<floating_ip>:30090`
2. Log in, go to **Preferences**, select at least 2 cuisine tags
3. Go to **Home** — "Recommended for You" panel appears
4. Rate recipes — interactions are captured for the next training cycle

---

## Repository Structure (ML-relevant files)

```
integration_chameleon_setup_new.ipynb   # Main reproduction notebook (run this)

dev/
  cronjobs/
    mealie-prod-batch-compile-cronjob.yaml   # ETL: PostgreSQL → MinIO parquet
    mealie-prod-monthly-retrain-cronjob.yaml # ALS retraining
    mealie-prod-nightly-eval-cronjob.yaml    # MLflow quality logging
  monitoring/
    prometheus-rbac.yaml                     # RBAC for cluster metrics
    prometheus-configmap.yaml                # Scrape config + 5 alert rules
    prometheus-deployment.yaml               # NodePort 30091
    grafana-configmap.yaml                   # Prometheus datasource
    grafana-deployment.yaml                  # NodePort 30300
    alertmanager-configmap.yaml              # Alert routing
    alertmanager-deployment.yaml             # NodePort 30903
    kube-state-metrics-rbac.yaml
    kube-state-metrics.yaml
    inference-api-hpa.yaml                   # HPA: scale 1-3 on CPU>70%

mealie/services/recommendation_service.py   # Inference client + fallback logic
frontend/app/components/AppRecommendedForYou.vue  # Recommendation UI panel
frontend/app/pages/preferences.vue          # Onboarding tag selection

SAFEGUARDING.md                             # Fairness, privacy, robustness plan
```

---

## Alert Rules (Prometheus)

| Rule | Condition | Severity |
|---|---|---|
| PodCrashLooping | >2 restarts in 10 min | warning |
| DeploymentReplicasUnavailable | unavailable replicas > 0 for 10 min | critical |
| StatefulSetReplicasUnavailable | ready < desired for 10 min | critical |
| FailedCronJob | any job failure | warning |
| InferenceAPIDown | /metrics unreachable for 2 min | critical |

---

## Troubleshooting

**Pod stuck in Pending (memory/CPU):**
```bash
sudo kubectl describe pod <pod-name> -n <namespace> | tail -5
# Reduce resource requests if needed:
sudo kubectl patch deployment <name> -n <namespace> --type='json' \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/memory","value":"256Mi"}]'
```

**CronJob pod fails with ErrImageNeverPull:**
```bash
# Image not imported into K3s — import it:
sudo docker save <image>:latest | sudo k3s ctr images import -
```

**Inference API returns 503 / recommendations empty:**
```bash
# Check model artifact exists in MinIO
# MinIO Console → mlflow-artifacts bucket → production/tag_to_vector.pkl
# If missing, re-run Cell 12.5 from the notebook
```

**VM has insufficient CPU/memory for all pods (single-node constraint):**
```bash
sudo kubectl describe nodes | grep -A5 "Allocated resources"
# Delete completed job pods to free resources:
sudo kubectl delete pods -n mealie-prod --field-selector=status.phase=Succeeded
```
