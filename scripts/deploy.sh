#!/usr/bin/env bash
# deploy.sh - Full Mealie stack deploy on an existing K3s VM
# Usage: bash deploy.sh <floating_ip>
# Assumes: K3s installed, Docker installed, and the monorepo is present on the VM.

set -euo pipefail

FLOATING_IP="${1:?Usage: bash deploy.sh <floating_ip>}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVING_DIR="$REPO_ROOT/serving"
K8S_DIR="$REPO_ROOT/k8s"
PLATFORM_DIR="$K8S_DIR/platform"
MEALIE_K8S_DIR="$K8S_DIR/mealie"
SERVING_K8S_DIR="$K8S_DIR/serving"
MONITORING_DIR="$K8S_DIR/monitoring"

require_dir() {
    local dir="$1"
    local hint="$2"
    if [[ ! -d "$dir" ]]; then
        echo "Missing directory: $dir" >&2
        echo "$hint" >&2
        exit 1
    fi
}

require_file() {
    local file="$1"
    local hint="$2"
    if [[ ! -f "$file" ]]; then
        echo "Missing file: $file" >&2
        echo "$hint" >&2
        exit 1
    fi
}

create_postgres_secret() {
    local namespace="$1"
    sudo kubectl create secret generic postgres-secret \
        --from-literal=username=mealie \
        --from-literal=password=mealie_pass \
        -n "$namespace" \
        --dry-run=client -o yaml | sudo kubectl apply -f -
}

create_minio_secret() {
    local namespace="$1"
    sudo kubectl create secret generic minio-secret \
        --from-literal=accesskey=minioadmin \
        --from-literal=secretkey=minioadmin123 \
        -n "$namespace" \
        --dry-run=client -o yaml | sudo kubectl apply -f -
}

wait_for_rollout() {
    local kind="$1"
    local name="$2"
    local namespace="$3"
    sudo kubectl rollout status "$kind/$name" -n "$namespace" --timeout=300s
}

echo "=== [1/8] Validating monorepo layout ==="
require_dir "$SERVING_DIR" "Add the serving folder at $SERVING_DIR before running deploy.sh."
require_dir "$K8S_DIR" "Add the k8s folder at $K8S_DIR before running deploy.sh."
require_file "$SERVING_DIR/Dockerfile" "Expected the inference Dockerfile at $SERVING_DIR/Dockerfile."
require_file "$K8S_DIR/namespaces.yaml" "Expected namespace manifests at $K8S_DIR/namespaces.yaml."
require_file "$PLATFORM_DIR/postgres-statefulset.yaml" "Expected PostgreSQL manifests under $PLATFORM_DIR."
require_file "$PLATFORM_DIR/minio-deployment.yaml" "Expected MinIO manifests under $PLATFORM_DIR."
require_file "$PLATFORM_DIR/minio-init-job.yaml" "Expected the MinIO init job under $PLATFORM_DIR."
require_file "$PLATFORM_DIR/mlflow-deployment.yaml" "Expected MLflow manifests under $PLATFORM_DIR."
require_file "$PLATFORM_DIR/shared-configmap.yaml" "Expected shared ConfigMaps under $PLATFORM_DIR."
require_file "$SERVING_K8S_DIR/inference-deployment.yaml" "Expected inference manifests under $SERVING_K8S_DIR."
require_file "$MEALIE_K8S_DIR/mealie-deployment.yaml" "Expected Mealie manifests under $MEALIE_K8S_DIR."
require_file "$MONITORING_DIR/prometheus-configmap.yaml" "Expected monitoring manifests under $MONITORING_DIR."
require_file "$MONITORING_DIR/grafana-dashboards.yaml" "Expected Grafana dashboard manifests under $MONITORING_DIR."

echo "=== [2/8] Creating namespaces and secrets ==="
sudo kubectl apply -f "$K8S_DIR/namespaces.yaml"
for namespace in platform mealie serving data training; do
    create_postgres_secret "$namespace"
    create_minio_secret "$namespace"
done

echo "=== [3/8] Applying platform manifests ==="
sudo kubectl apply -f "$PLATFORM_DIR/shared-configmap.yaml"
sudo kubectl apply -f "$PLATFORM_DIR/postgres-statefulset.yaml"
sudo kubectl apply -f "$PLATFORM_DIR/minio-deployment.yaml"
wait_for_rollout statefulset postgres platform
wait_for_rollout deployment minio platform

POSTGRES_POD="$(sudo kubectl get pod -n platform -l app=postgres -o jsonpath='{.items[0].metadata.name}')"
if [[ -z "$POSTGRES_POD" ]]; then
    echo "Postgres pod not found in namespace platform." >&2
    exit 1
fi

MLFLOW_DB_EXISTS="$(sudo kubectl exec -n platform "$POSTGRES_POD" -- sh -lc "PGPASSWORD='mealie_pass' psql -U mealie -d postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='mlflow'\"")"
if [[ "$MLFLOW_DB_EXISTS" != "1" ]]; then
    echo "Creating mlflow database..."
    sudo kubectl exec -n platform "$POSTGRES_POD" -- sh -lc "PGPASSWORD='mealie_pass' psql -U mealie -d postgres -c 'CREATE DATABASE mlflow;'"
fi

sudo kubectl delete job minio-init -n platform --ignore-not-found
sudo kubectl apply -f "$PLATFORM_DIR/minio-init-job.yaml"
sudo kubectl wait --for=condition=complete job/minio-init -n platform --timeout=300s

sudo kubectl apply -f "$PLATFORM_DIR/mlflow-deployment.yaml"
wait_for_rollout deployment mlflow platform

echo "=== [4/8] Building inference API image ==="
cd "$REPO_ROOT"
sudo docker build -f serving/Dockerfile -t proj18biasvariance/mealie-serving:local .
sudo docker save proj18biasvariance/mealie-serving:local | sudo k3s ctr images import -
echo "Inference image imported."

echo "=== [5/8] Building Mealie image ==="
sudo docker build --file docker/Dockerfile -t proj18biasvariance/mealie-custom:local .
sudo docker save proj18biasvariance/mealie-custom:local | sudo k3s ctr images import -
echo "Mealie image imported."

echo "=== [6/8] Deploying serving and Mealie ==="
sudo kubectl apply -f "$SERVING_K8S_DIR/inference-deployment.yaml"
sudo kubectl apply -f "$MEALIE_K8S_DIR/mealie-deployment.yaml"
wait_for_rollout deployment inference-api serving
wait_for_rollout deployment mealie-app mealie

echo "=== [7/8] Applying monitoring manifests ==="
sudo kubectl apply -f "$MONITORING_DIR/prometheus-rbac.yaml"
sudo kubectl apply -f "$MONITORING_DIR/kube-state-metrics-rbac.yaml"
sudo kubectl apply -f "$MONITORING_DIR/kube-state-metrics.yaml"
sudo kubectl apply -f "$MONITORING_DIR/blackbox-exporter-configmap.yaml"
sudo kubectl apply -f "$MONITORING_DIR/blackbox-exporter-deployment.yaml"
sudo kubectl apply -f "$MONITORING_DIR/alertmanager-configmap.yaml"
sudo kubectl apply -f "$MONITORING_DIR/alertmanager-deployment.yaml"
sudo kubectl apply -f "$MONITORING_DIR/prometheus-configmap.yaml"
sudo kubectl apply -f "$MONITORING_DIR/prometheus-pvc.yaml"
sudo kubectl apply -f "$MONITORING_DIR/prometheus-deployment.yaml"
sudo kubectl apply -f "$MONITORING_DIR/grafana-configmap.yaml"
sudo kubectl apply -f "$MONITORING_DIR/grafana-dashboards.yaml"
sudo kubectl apply -f "$MONITORING_DIR/grafana-deployment.yaml"
wait_for_rollout deployment kube-state-metrics monitoring
wait_for_rollout deployment blackbox-exporter monitoring
wait_for_rollout deployment alertmanager monitoring
wait_for_rollout deployment prometheus monitoring
wait_for_rollout deployment grafana monitoring

echo "=== [8/8] Opening iptables firewall ports ==="
for port in 22 30090 30800 30500 30900 30901 30091 30300 30903; do
    sudo iptables -I INPUT -p tcp --dport "$port" -j ACCEPT 2>/dev/null || true
done

echo ""
echo "=== Deploy complete ==="
echo "Mealie UI:        http://${FLOATING_IP}:30090  (admin / MyPassword)"
echo "Inference API:    http://${FLOATING_IP}:30800/health"
echo "MLflow:           http://${FLOATING_IP}:30500"
echo "MinIO Console:    http://${FLOATING_IP}:30901  (minioadmin / minioadmin123)"
echo "Prometheus:       http://${FLOATING_IP}:30091"
echo "Grafana:          http://${FLOATING_IP}:30300  (admin / admin123)"
echo "Alertmanager:     http://${FLOATING_IP}:30903"
echo ""
echo "Next: check the cluster state:"
echo "  sudo kubectl get pods --all-namespaces"
