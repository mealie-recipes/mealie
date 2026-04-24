#!/usr/bin/env bash
# deploy.sh — Full Mealie ML stack deploy on an existing K3s VM
# Usage: bash deploy.sh <floating_ip>
# Assumes: K3s installed, Docker installed, all team repos cloned under /home/cc/proj18/

set -euo pipefail

FLOATING_IP="${1:?Usage: bash deploy.sh <floating_ip>}"

MEALIE_DIR="/home/cc/proj18/mealie"
SERVING_DIR="/home/cc/proj18/mealie-serving/serving"
DEVOPS_DIR="/home/cc/proj18/mlops-devops/infrastructure/k8s"

echo "=== [1/9] Pulling latest code ==="
for repo in mealie mealie-serving mealie_als_training mlops-devops; do
    dir="/home/cc/proj18/$repo"
    if [ -d "$dir" ]; then
        git -C "$dir" pull --ff-only || true
    fi
done

echo "=== [2/9] Creating namespaces ==="
for ns in mealie-prod platform monitoring mealie-staging mealie-canary; do
    sudo kubectl create namespace "$ns" --dry-run=client -o yaml | sudo kubectl apply -f -
done

echo "=== [3/9] Creating secrets and ConfigMaps ==="
sudo kubectl create secret generic postgres-secret \
    --from-literal=username=mealie \
    --from-literal=password=mealie_pass \
    -n mealie-prod --dry-run=client -o yaml | sudo kubectl apply -f -

sudo kubectl create secret generic minio-secret \
    --from-literal=access-key=minioadmin \
    --from-literal=secret-key=minioadmin123 \
    -n platform --dry-run=client -o yaml | sudo kubectl apply -f -

sudo kubectl create configmap shared-env \
    --from-literal=MINIO_ENDPOINT="http://minio-service.platform.svc.cluster.local:9000" \
    --from-literal=MINIO_ACCESS_KEY="minioadmin" \
    --from-literal=MINIO_SECRET_KEY="minioadmin123" \
    --from-literal=MLFLOW_TRACKING_URI="http://mlflow-service.platform.svc.cluster.local:5000" \
    --from-literal=MLFLOW_S3_ENDPOINT_URL="http://minio-service.platform.svc.cluster.local:9000" \
    --from-literal=AWS_ACCESS_KEY_ID="minioadmin" \
    --from-literal=AWS_SECRET_ACCESS_KEY="minioadmin123" \
    --from-literal=DB_HOST="postgres.platform.svc.cluster.local" \
    --from-literal=DB_PORT="5432" \
    --from-literal=DB_NAME="mealie" \
    --from-literal=DB_USER="mealie" \
    --from-literal=DB_PASSWORD="mealie_pass" \
    -n mealie-prod --dry-run=client -o yaml | sudo kubectl apply -f -

echo "=== [4/9] Applying platform manifests (postgres, minio, mlflow) ==="
sudo kubectl apply -f "$DEVOPS_DIR/postgres-statefulset.yaml"
sudo kubectl apply -f "$DEVOPS_DIR/minio-deployment.yaml"
sudo kubectl apply -f "$DEVOPS_DIR/mlflow-deployment.yaml"
echo "Waiting 45s for platform pods..."
sleep 45
sudo kubectl get pods -n platform

echo "Installing metrics-server for HPA resource metrics..."
sudo kubectl apply -f "$MEALIE_DIR/dev/monitoring/metrics-server.yaml"
sudo kubectl wait -n kube-system --for=condition=Available deployment/metrics-server --timeout=180s || true

echo "Creating MinIO buckets..."
python3 - <<'PYEOF'
import boto3, time
for attempt in range(10):
    try:
        s3 = boto3.client("s3", endpoint_url="http://127.0.0.1:30900",
                          aws_access_key_id="minioadmin", aws_secret_access_key="minioadmin123")
        for bucket in ["training-data", "mlflow-artifacts"]:
            try:
                s3.create_bucket(Bucket=bucket)
                print(f"  created: {bucket}")
            except Exception:
                print(f"  exists:  {bucket}")
        break
    except Exception as e:
        print(f"  MinIO not ready (attempt {attempt+1}/10): {e}")
        time.sleep(10)
PYEOF

echo "=== [5/9] Building inference API image ==="
cd "$SERVING_DIR"
sudo docker build -f Dockerfile.cached -t mealie-inference:latest .
sudo docker save mealie-inference:latest | sudo k3s ctr images import -
echo "Inference image imported."

echo "=== [6/9] Building Mealie image ==="
cd "$MEALIE_DIR"
sudo docker build --file docker/Dockerfile -t mealie-custom:latest .
sudo docker save mealie-custom:latest | sudo k3s ctr images import -
echo "Mealie image imported."

echo "=== [7/9] Deploying inference API and Mealie ==="
# Inference API deployment (NodePort 30800)
cat <<EOF | sudo kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inference-api
  namespace: mealie-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: inference-api
  template:
    metadata:
      labels:
        app: inference-api
    spec:
      containers:
        - name: inference-api
          image: mealie-inference:latest
          imagePullPolicy: Never
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: shared-env
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: inference-api
  namespace: mealie-prod
spec:
  type: NodePort
  selector:
    app: inference-api
  ports:
    - port: 8000
      targetPort: 8000
      nodePort: 30800
EOF

# Mealie deployment (NodePort 30090)
cat <<EOF | sudo kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mealie
  namespace: mealie-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mealie
  template:
    metadata:
      labels:
        app: mealie
    spec:
      containers:
        - name: mealie
          image: mealie-custom:latest
          imagePullPolicy: Never
          ports:
            - containerPort: 9000
          envFrom:
            - configMapRef:
                name: shared-env
          env:
            - name: DB_ENGINE
              value: postgres
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: username
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
            - name: POSTGRES_SERVER
              value: postgres.platform.svc.cluster.local
            - name: POSTGRES_PORT
              value: "5432"
            - name: POSTGRES_DB
              value: mealie
            - name: INFERENCE_API_URL
              value: "http://inference-api.mealie-prod.svc.cluster.local:8000"
            - name: ALLOW_SIGNUP
              value: "true"
          resources:
            requests:
              cpu: 200m
              memory: 512Mi
            limits:
              cpu: 1000m
              memory: 1Gi
---
apiVersion: v1
kind: Service
metadata:
  name: mealie
  namespace: mealie-prod
spec:
  type: NodePort
  selector:
    app: mealie
  ports:
    - port: 9000
      targetPort: 9000
      nodePort: 30090
EOF

echo "=== [8/9] Applying CronJobs and monitoring ==="
CRONJOB_DIR="$MEALIE_DIR/dev/cronjobs"
sudo kubectl apply -f "$CRONJOB_DIR/mealie-prod-batch-compile-cronjob.yaml"
sudo kubectl apply -f "$CRONJOB_DIR/mealie-prod-monthly-retrain-cronjob.yaml"
sudo kubectl apply -f "$CRONJOB_DIR/mealie-prod-nightly-eval-cronjob.yaml"

MONITORING_DIR="$MEALIE_DIR/dev/monitoring"
sudo kubectl apply -f "$MONITORING_DIR/prometheus-rbac.yaml"
sudo kubectl apply -f "$MONITORING_DIR/blackbox-exporter-configmap.yaml"
sudo kubectl apply -f "$MONITORING_DIR/blackbox-exporter-deployment.yaml"
sudo kubectl apply -f "$MONITORING_DIR/prometheus-configmap.yaml"
sudo kubectl apply -f "$MONITORING_DIR/prometheus-deployment.yaml"
sudo kubectl apply -f "$MONITORING_DIR/grafana-configmap.yaml"
sudo kubectl apply -f "$MONITORING_DIR/grafana-dashboards.yaml"
sudo kubectl apply -f "$MONITORING_DIR/grafana-deployment.yaml"
sudo kubectl apply -f "$MONITORING_DIR/alertmanager-configmap.yaml"
sudo kubectl apply -f "$MONITORING_DIR/alertmanager-deployment.yaml"
sudo kubectl apply -f "$MONITORING_DIR/kube-state-metrics-rbac.yaml"
sudo kubectl apply -f "$MONITORING_DIR/kube-state-metrics.yaml"
sudo kubectl apply -f "$MONITORING_DIR/inference-api-hpa.yaml"

echo "=== [9/9] Opening iptables firewall ports ==="
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
echo "Next: run bootstrap_data.sh to seed the ALS model, then check pods:"
echo "  sudo kubectl get pods --all-namespaces"
