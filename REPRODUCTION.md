# Reproduction Guide — Mealie ML Recommendations (proj18)

**Team:** Bias & Variance  
**Branch:** `feature/ml-recommendations`  
**Estimated time:** ~45–60 minutes end-to-end

---

## Prerequisites

- Chameleon Cloud account with access to project **CHI-251409**
- Access to Chameleon JupyterHub at https://jupyter.chameleoncloud.org
- A Kaggle account and API token (for downloading Food.com dataset)

---

## Step 1 — Provision VM on JupyterHub

Open `integration_chameleon_setup_new.ipynb` on JupyterHub and run cells **1 through 12** in order (skip Cell 12.5 for now):

| Cell | What it does |
|---|---|
| 1 | Imports + select project CHI-251409, site KVM@TACC |
| 2 | Create new 48-hour lease (m1.xlarge flavor) |
| 3 | Launch new VM (CC-Ubuntu24.04), poll until ACTIVE |
| 4 | Add OpenStack security groups (ports 22, 30090, 30800, 30500, 30900, 30901, 30091, 30300, 30903) |
| 5 | Associate floating IP + verify SSH — saves `floating_ip` variable |
| 6 | Install Docker on VM |
| 7 | Install K3s (Kubernetes) |
| 8 | Clone all team repos into `/home/cc/proj18/` |
| 9 | Create Kubernetes namespaces |
| 10 | Create Kubernetes Secrets |
| 11 | Create `shared-env` ConfigMap |
| 12 | Apply Mahima's platform manifests (PostgreSQL, MinIO, MLflow) |

After Cell 12, note the `floating_ip` printed in the output.

---

## Step 2 — Run deploy.sh (builds images + deploys full stack)

SSH into the VM and run the deploy script:

```bash
ssh cc@<floating_ip>
cd /home/cc/proj18/mealie
bash scripts/deploy.sh <floating_ip>
```

This script (~10–15 min) does:
1. Pulls latest code for all repos
2. Creates namespaces, secrets, ConfigMaps
3. Applies platform manifests (postgres, minio, mlflow)
4. Builds inference API Docker image + imports to K3s
5. Builds Mealie Docker image + imports to K3s
6. Deploys inference API (NodePort 30800) and Mealie (NodePort 30090)
7. Applies all CronJobs (ETL, retrain, nightly-eval, model-promoter)
8. Deploys monitoring stack (Prometheus, Grafana, Alertmanager, kube-state-metrics, HPA)
9. Opens iptables firewall ports

---

## Step 3 — Bootstrap the ALS model

Still on the VM, run the bootstrap script with your Kaggle token:

```bash
bash /home/cc/proj18/mealie/scripts/bootstrap_data.sh <floating_ip> <kaggle_token>
```

This script (~10–15 min) does:
1. Downloads Food.com CSVs from Kaggle
2. Runs Bryce's ETL (cleans + combines real + synthetic interactions)
3. Uploads `train.parquet` / `val.parquet` to MinIO at `datasets/current/`
4. Patches Shashwat's `train.py` + builds `mealie-als-training:integration-rerun` image
5. Runs ALS training, saves `production/tag_to_vector.pkl` to MinIO

> **Note:** The Kaggle token format is `KGAT_xxxxxxxx`. Find yours at https://www.kaggle.com/settings → API → Create New Token.

---

## Step 4 — Verify Services

After both scripts complete, all services are accessible at `http://<floating_ip>:<port>`:

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
# Check all pods
sudo kubectl get pods --all-namespaces

# Check CronJobs
sudo kubectl get cronjobs -n mealie-prod
```

---

## Step 5 — Test the ML Pipeline End-to-End

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

## Step 6 — Verify ML Recommendations in UI

1. Open Mealie at `http://<floating_ip>:30090`
2. Log in, go to **Preferences**, select at least 2 cuisine tags
3. Go to **Home** — "Recommended for You" panel appears
4. Rate recipes — interactions are captured for the next training cycle

---

## Repository Structure (ML-relevant files)

```
integration_chameleon_setup_new.ipynb   # Notebook: VM provisioning (Cells 1-12 only)
scripts/
  deploy.sh          # Full K8s stack deploy (run on VM after K3s is up)
  bootstrap_data.sh  # ETL + ALS training (run on VM after deploy.sh)

dev/
  cronjobs/
    mealie-prod-batch-compile-cronjob.yaml   # ETL: PostgreSQL → MinIO parquet
    mealie-prod-monthly-retrain-cronjob.yaml # ALS retraining
    mealie-prod-nightly-eval-cronjob.yaml    # MLflow quality logging
  monitoring/
    prometheus-rbac.yaml
    prometheus-configmap.yaml                # Scrape config + 5 alert rules
    prometheus-deployment.yaml               # NodePort 30091
    grafana-configmap.yaml
    grafana-deployment.yaml                  # NodePort 30300
    alertmanager-configmap.yaml
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
# Image not imported into K3s — re-import it:
sudo docker save <image>:latest | sudo k3s ctr images import -
```

**Inference API returns 503 / recommendations empty:**
```bash
# Check model artifact exists in MinIO
# MinIO Console → mlflow-artifacts bucket → production/tag_to_vector.pkl
# If missing, re-run bootstrap_data.sh
```

**StatefulSet postgres "spec: Forbidden" on re-apply:**
```bash
sudo kubectl delete statefulset postgres -n platform --ignore-not-found
sudo kubectl apply -f /home/cc/proj18/mlops-devops/infrastructure/k8s/postgres-statefulset.yaml
```

**VM has insufficient CPU/memory for all pods:**
```bash
sudo kubectl describe nodes | grep -A5 "Allocated resources"
# Delete completed job pods to free resources:
sudo kubectl delete pods -n mealie-prod --field-selector=status.phase=Succeeded
```
