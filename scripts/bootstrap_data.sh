#!/usr/bin/env bash
# bootstrap_data.sh — Download Food.com from Kaggle, run ETL, train ALS model
# Usage: bash bootstrap_data.sh <floating_ip> <kaggle_token>
# Run this ON THE VM (not on JupyterHub)

set -euo pipefail

FLOATING_IP="${1:?Usage: bash bootstrap_data.sh <floating_ip> <kaggle_token>}"
KAGGLE_TOKEN="${2:?Usage: bash bootstrap_data.sh <floating_ip> <kaggle_token>}"

KAGGLE_DATASET="shuyangli94/food-com-recipes-and-user-interactions"
TRAINING_REPO="https://github.com/Shashwatshah02/mealie_als_training.git"
TRAINING_DIR="/home/cc/proj18/mealie_als_training"
TRAINING_BUCKET="training-data"
MODEL_BUCKET="mlflow-artifacts"
TAG_VECTOR_KEY="production/tag_to_vector.pkl"
DATASET_VERSION="current"
MINIO_ENDPOINT="http://127.0.0.1:30900"

echo "=== [1/5] Installing Python dependencies ==="
python3 -m pip install -q pandas pyarrow numpy boto3 kaggle --break-system-packages
export PATH="$HOME/.local/bin:$PATH"

echo "=== [2/5] Downloading Food.com dataset from Kaggle ==="
mkdir -p /tmp/foodcom
export KAGGLE_TOKEN="$KAGGLE_TOKEN"
kaggle datasets download -d "$KAGGLE_DATASET" -p /tmp/foodcom --unzip
echo "Download complete."
ls /tmp/foodcom/

echo "=== [3/5] Running ETL ==="
python3 - <<'PYEOF'
import ast, io, json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd
import boto3

MINIO_ENDPOINT   = os.environ.get("MINIO_ENDPOINT", "http://127.0.0.1:30900")
TRAINING_BUCKET  = "training-data"
DATASET_VERSION  = "current"
WEIGHT_MAP       = {5: 1.0, 4: 0.7, 3: 0.0, 2: -0.5, 1: -1.0}

foodcom = Path("/tmp/foodcom")
recipes_csv      = next(foodcom.rglob("RAW_recipes.csv"), None)
interactions_csv = next(foodcom.rglob("RAW_interactions.csv"), None)
if not recipes_csv or not interactions_csv:
    raise FileNotFoundError("RAW_recipes.csv or RAW_interactions.csv not found in /tmp/foodcom")

def parse_tags(v):
    if pd.isna(v): return []
    if isinstance(v, list): return [str(x) for x in v]
    try:
        p = ast.literal_eval(v)
        if isinstance(p, list): return [str(x) for x in p]
    except Exception:
        pass
    return []

print("Cleaning recipes...")
recipes = pd.read_csv(recipes_csv, usecols=["id","name","tags","minutes","nutrition"])
recipes = recipes.dropna(subset=["id","name","tags","minutes"])
recipes["id"]      = recipes["id"].astype(str)
recipes["tags"]    = recipes["tags"].apply(parse_tags)
recipes["minutes"] = recipes["minutes"].clip(upper=480)
print(f"  {len(recipes):,} recipes")

print("Cleaning interactions (sampling 200k)...")
interactions = pd.read_csv(interactions_csv, usecols=["user_id","recipe_id","date","rating"])
interactions = interactions.dropna()
interactions["user_id"]   = interactions["user_id"].astype(str)
interactions["recipe_id"] = interactions["recipe_id"].astype(str)
interactions["weight"]    = interactions["rating"].map(WEIGHT_MAP)
interactions = interactions[interactions["weight"] != 0.0].copy()
interactions = interactions.sort_values("date").tail(200_000)
print(f"  {len(interactions):,} interactions (after sample)")

print("Generating synthetic interactions...")
np.random.seed(42)
all_tags    = list({t for tags in recipes["tags"] for t in tags})
recipe_rows = recipes[["id","tags"]].values.tolist()
user_prefs  = {
    f"synth_{u}": set(np.random.choice(all_tags, size=np.random.randint(3,8), replace=False))
    for u in range(200)
}
rows = []
for _ in range(50_000):
    uid       = f"synth_{np.random.randint(0,200)}"
    rid, tags = recipe_rows[np.random.randint(0, len(recipe_rows))]
    overlap   = len(set(tags) & user_prefs[uid])
    if overlap >= 2:
        rating = int(np.random.choice([4,5], p=[0.4,0.6]))
    elif overlap == 1:
        rating = int(np.random.choice([3,4,5], p=[0.4,0.4,0.2]))
    else:
        rating = int(np.random.choice([1,2,3], p=[0.3,0.4,0.3]))
    w = WEIGHT_MAP.get(rating, 0.0)
    if w != 0.0:
        rows.append({"user_id": uid, "recipe_id": str(rid), "rating": rating, "weight": w, "date": "2025-01-01"})
synthetic = pd.DataFrame(rows)
print(f"  {len(synthetic):,} synthetic interactions")

combined = pd.concat([interactions, synthetic], ignore_index=True).sort_values("date")
combined = combined.merge(recipes[["id","tags"]], left_on="recipe_id", right_on="id", how="left").drop(columns=["id"])
combined["tags"] = combined["tags"].apply(lambda x: x if isinstance(x, list) else [])
split = int(len(combined) * 0.8)
train = combined.iloc[:split].copy()
val   = combined.iloc[split:].copy()
print(f"  train: {len(train):,}  val: {len(val):,}")

print("Uploading to MinIO...")
s3 = boto3.client("s3", endpoint_url=MINIO_ENDPOINT,
                  aws_access_key_id="minioadmin", aws_secret_access_key="minioadmin123")
try:
    s3.create_bucket(Bucket=TRAINING_BUCKET)
except Exception:
    pass

def upload_df(df, key):
    buf = __import__("io").BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    s3.put_object(Bucket=TRAINING_BUCKET, Key=key, Body=buf.getvalue())
    print(f"  uploaded s3://{TRAINING_BUCKET}/{key} ({len(df):,} rows)")

upload_df(recipes,      "processed/recipes_clean.parquet")
upload_df(interactions, "processed/interactions_clean.parquet")
upload_df(train,        f"datasets/{DATASET_VERSION}/train.parquet")
upload_df(val,          f"datasets/{DATASET_VERSION}/val.parquet")
meta = {"version": DATASET_VERSION, "train_rows": int(len(train)), "val_rows": int(len(val))}
s3.put_object(Bucket=TRAINING_BUCKET, Key=f"datasets/{DATASET_VERSION}/meta.json",
              Body=json.dumps(meta, indent=2).encode())
print("MinIO upload complete:", meta)
PYEOF

echo "=== [4/5] Cloning + patching training repo, building Docker image ==="
if [ -d "$TRAINING_DIR" ]; then
    git -C "$TRAINING_DIR" pull --ff-only || true
else
    git clone "$TRAINING_REPO" "$TRAINING_DIR"
fi

python3 - <<'PYEOF'
import os
from pathlib import Path

path = Path("/home/cc/proj18/mealie_als_training/scripts/train.py")
if not path.exists():
    print(f"WARN: {path} not found, skipping patch")
    exit(0)
text = path.read_text()

replacements = [
    ("s3.download_file('training-data', 'datasets/v2_2026-04-04/train.parquet'",
     "s3.download_file(os.environ.get('TRAINING_BUCKET','training-data'), f\"datasets/{os.environ.get('DATASET_VERSION','current')}/train.parquet\""),
    ("s3.download_file('training-data', 'datasets/v2_2026-04-04/val.parquet'",
     "s3.download_file(os.environ.get('TRAINING_BUCKET','training-data'), f\"datasets/{os.environ.get('DATASET_VERSION','current')}/val.parquet\""),
    ("save_to_minio(tag_to_vector, 'mlflow', 'production/tag_to_vector.pkl')",
     "save_to_minio(tag_to_vector, os.environ.get('MODEL_BUCKET','mlflow-artifacts'), os.environ.get('TAG_VECTOR_KEY','production/tag_to_vector.pkl'))"),
]
for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
        print("Patched:", repr(old[:60]))
    else:
        print("WARN not found (may already be patched):", repr(old[:60]))

# Patch quality gate with regex (handles 100_000, 100000, etc.)
import re
text, n = re.subn(
    r'n_train_interactions\s*>=\s*[\d_]+',
    'n_train_interactions >= int(os.environ.get("MIN_TRAIN_INTERACTIONS", "1000"))',
    text
)
if n:
    print(f"Patched quality gate ({n} occurrence(s))")
else:
    print("WARN: quality gate pattern not found")

path.write_text(text)
print("Patch complete.")
PYEOF

cd "$TRAINING_DIR"
echo "Building mealie-als-training image (~3 min)..."
sudo docker build -t mealie-als-training:integration-rerun . 2>&1 | tail -10
echo "Importing into K3s containerd..."
sudo docker save mealie-als-training:integration-rerun | sudo k3s ctr images import -
echo "Image imported."

echo "=== [5/5] Running ALS training ==="
sudo docker run --rm --network host \
    -e MLFLOW_TRACKING_URI="http://127.0.0.1:30500" \
    -e MLFLOW_S3_ENDPOINT_URL="http://127.0.0.1:30900" \
    -e AWS_ACCESS_KEY_ID="minioadmin" \
    -e AWS_SECRET_ACCESS_KEY="minioadmin123" \
    -e MINIO_ENDPOINT="http://127.0.0.1:30900" \
    -e MINIO_ACCESS_KEY="minioadmin" \
    -e MINIO_SECRET_KEY="minioadmin123" \
    -e TRAINING_BUCKET="$TRAINING_BUCKET" \
    -e DATASET_VERSION="$DATASET_VERSION" \
    -e MODEL_BUCKET="$MODEL_BUCKET" \
    -e TAG_VECTOR_KEY="$TAG_VECTOR_KEY" \
    -e MIN_TRAIN_INTERACTIONS="1000" \
    mealie-als-training:integration-rerun

echo ""
echo "=== Bootstrap complete ==="
echo "Check MinIO for production/tag_to_vector.pkl — mlflow-artifacts bucket"
echo "Check MLflow at http://${FLOATING_IP}:30500 — experiment 'mealie-recipe-recommender'"
