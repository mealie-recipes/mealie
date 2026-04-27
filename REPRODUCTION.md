# Reproduction Guide - Mealie ML Recommendations (proj18)

**Team:** Bias & Variance
**Branch:** `feature/ml-recommendations`
**Scope:** VM provisioning plus monorepo deploy
**Estimated time:** ~20-30 minutes before any data bootstrap or model training

This guide now covers only the current monorepo path:
1. provision the VM and install Docker/K3s from JupyterHub
2. run `scripts/deploy.sh` from this repo to build and deploy the stack

The old Terraform, Ansible, and multi-repo checkout flow has been removed from this repo.

## Prerequisites

- Chameleon Cloud account with access to project **CHI-251409**
- Access to Chameleon JupyterHub at https://jupyter.chameleoncloud.org
- This repo copied to the VM at `/home/cc/proj18/mealie`
- The monorepo already contains these folders before you run `deploy.sh`:
  - `serving/`
  - `k8s/`

Expected VM layout:

```text
/home/cc/proj18/mealie/
  scripts/
  serving/
  k8s/
```

## Step 1 - Provision the VM on JupyterHub

Open `integration_chameleon_setup_new.ipynb` on JupyterHub and run only the cells that provision the VM and install the base runtime.

Run cells **1 through 7** in order. Skip the later cells because they belong to the old multi-repo and manual manifest flow that `deploy.sh` now handles.

| Cell | What it does |
|---|---|
| 1 | Imports plus select project CHI-251409, site KVM@TACC |
| 2 | Create new 48-hour lease (m1.xlarge flavor) |
| 3 | Launch new VM (CC-Ubuntu24.04), poll until ACTIVE |
| 4 | Add OpenStack security groups (ports 22, 30090, 30800, 30500, 30900, 30901, 30091, 30300, 30903) |
| 5 | Associate floating IP and verify SSH, saving the `floating_ip` value |
| 6 | Install Docker on the VM |
| 7 | Install K3s (Kubernetes) |

After cell 7, note the `floating_ip` printed in the output.

## Step 2 - Run deploy.sh from the monorepo

SSH into the VM, make sure this repo is at `/home/cc/proj18/mealie`, and confirm that the `serving/` and `k8s/` folders are already present inside the repo.

```bash
ssh cc@<floating_ip>
cd /home/cc/proj18/mealie
bash scripts/deploy.sh <floating_ip>
```

This script (~10-15 min) does:
1. Validates the monorepo layout
2. Creates namespaces and per-namespace secrets
3. Applies platform manifests from `k8s/platform/` and initializes MinIO and MLflow
4. Builds the inference API image from `serving/` and imports it into K3s
5. Builds the Mealie image and imports it into K3s
6. Deploys the inference API and Mealie from `k8s/serving/` and `k8s/mealie/`
7. Applies monitoring manifests from `k8s/monitoring/`
8. Opens the required firewall ports

## Verify Services

After `deploy.sh` completes, the main services should be reachable at `http://<floating_ip>:<port>`:

| Service | Port | Credentials |
|---|---|---|
| Mealie UI | 30090 | admin / MyPassword |
| Inference API health | 30800/health | - |
| MLflow | 30500 | - |
| MinIO Console | 30901 | minioadmin / minioadmin123 |
| Prometheus | 30091 | - |
| Grafana | 30300 | admin / admin123 |
| Alertmanager | 30903 | - |

```bash
sudo kubectl get pods --all-namespaces
sudo kubectl get deployments --all-namespaces
```

## Out of Scope for This Guide

- Data and training workloads under `k8s/data/` and `k8s/training/`
- Any Terraform or Ansible workflow
