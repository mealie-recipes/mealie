from dataclasses import dataclass
import io
import json
import logging
import os
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError
import joblib
import numpy as np

try:
    from .scorer import precompute_recipe_cache
except ImportError:
    from scorer import precompute_recipe_cache

log = logging.getLogger(__name__)
DEFAULT_TAG_VECTOR_KEYS = (
    "production/tag_to_vector.pkl",
    "canary/tag_to_vector.pkl",
    "staging/tag_to_vector.pkl",
)
DEFAULT_BUCKET_CANDIDATES = (
    "mlflow-artifacts",
    "mlflow",
)


@dataclass(frozen=True)
class ModelArtifacts:
    tag_to_vector: Dict[str, np.ndarray]
    model_version: str
    artifact_bucket: str
    artifact_key: str
    artifact_source: str


def _default_model_dir() -> str:
    return os.getenv("MODEL_DIR", "/artifacts")


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_vectors(tag_to_vector: Dict) -> Dict[str, np.ndarray]:
    return {key: np.asarray(value, dtype=np.float32) for key, value in tag_to_vector.items()}


def _candidate_keys() -> List[str]:
    explicit_key = (os.getenv("TAG_VECTOR_KEY") or "").strip()
    configured_candidates = [
        candidate.strip()
        for candidate in os.getenv("TAG_VECTOR_CANDIDATES", "").split(",")
        if candidate.strip()
    ]
    stage = (os.getenv("MODEL_STAGE") or "").strip().lower()

    candidates: List[str] = []
    if explicit_key:
        candidates.append(explicit_key)
    if stage:
        candidates.append(f"{stage}/tag_to_vector.pkl")
    candidates.extend(configured_candidates)
    candidates.extend(DEFAULT_TAG_VECTOR_KEYS)

    deduped: List[str] = []
    seen = set()
    for candidate in candidates:
        if candidate not in seen:
            deduped.append(candidate)
            seen.add(candidate)
    return deduped


def _candidate_buckets() -> List[str]:
    explicit_bucket = (os.getenv("MINIO_BUCKET") or "").strip()
    configured_candidates = [
        candidate.strip()
        for candidate in os.getenv("MINIO_BUCKET_CANDIDATES", "").split(",")
        if candidate.strip()
    ]

    candidates: List[str] = []
    if explicit_bucket:
        candidates.append(explicit_bucket)
    candidates.extend(configured_candidates)
    candidates.extend(DEFAULT_BUCKET_CANDIDATES)

    deduped: List[str] = []
    seen = set()
    for candidate in candidates:
        if candidate not in seen:
            deduped.append(candidate)
            seen.add(candidate)
    return deduped


def _format_model_version(key: str, source: str, last_modified: object = None) -> str:
    last_modified_text = ""
    if last_modified is not None:
        last_modified_text = f"@{str(last_modified)}"
    return f"{source}:{key}{last_modified_text}"


def _load_local_artifacts(local_path: str) -> ModelArtifacts:
    loaded = _normalize_vectors(joblib.load(local_path))
    return ModelArtifacts(
        tag_to_vector=loaded,
        model_version=_format_model_version(os.path.basename(local_path), "local"),
        artifact_bucket="local",
        artifact_key=local_path,
        artifact_source="local",
    )


def load_model_artifacts(model_dir: Optional[str] = None) -> ModelArtifacts:
    endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY") or os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("MINIO_SECRET_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY")
    model_dir = model_dir or _default_model_dir()
    local_path = os.getenv("LOCAL_TAG_VECTOR", os.path.join(model_dir, "tag_to_vector.pkl"))
    allow_local_fallback = _env_flag("ALLOW_LOCAL_ARTIFACT_FALLBACK", default=False)

    remote_errors: List[str] = []
    if endpoint and access_key and secret_key:
        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        for bucket in _candidate_buckets():
            for key in _candidate_keys():
                try:
                    obj = s3.get_object(Bucket=bucket, Key=key)
                    loaded = _normalize_vectors(joblib.load(io.BytesIO(obj["Body"].read())))
                    log.info("Loaded tag_to_vector from MinIO: %s/%s", bucket, key)
                    return ModelArtifacts(
                        tag_to_vector=loaded,
                        model_version=_format_model_version(key, "minio", obj.get("LastModified")),
                        artifact_bucket=bucket,
                        artifact_key=key,
                        artifact_source="minio",
                    )
                except ClientError as exc:
                    error_code = exc.response.get("Error", {}).get("Code", "")
                    if error_code in {"NoSuchKey", "404", "NotFound"}:
                        remote_errors.append(f"{bucket}/{key} not found")
                        continue
                    remote_errors.append(f"{bucket}/{key} failed: {exc}")
                except Exception as exc:
                    remote_errors.append(f"{bucket}/{key} failed: {exc}")
    else:
        remote_errors.append("MinIO endpoint or credentials are not configured")

    if allow_local_fallback and os.path.exists(local_path):
        log.warning(
            "Remote tag vectors unavailable (%s). Using explicit local fallback at %s.",
            "; ".join(remote_errors),
            local_path,
        )
        return _load_local_artifacts(local_path)

    error_text = "; ".join(remote_errors) if remote_errors else "no remote attempts made"
    raise RuntimeError(
        "Unable to load tag vectors from remote artifacts. "
        f"Attempts: {error_text}. "
        "Set ALLOW_LOCAL_ARTIFACT_FALLBACK=1 only for local development."
    )


def load_tag_to_vector(model_dir: Optional[str] = None) -> Dict[str, np.ndarray]:
    return load_model_artifacts(model_dir=model_dir).tag_to_vector


def load_recipe_matrix(model_dir: Optional[str] = None) -> np.ndarray:
    model_dir = model_dir or _default_model_dir()
    path = os.path.join(model_dir, "recipe_matrix.pkl")
    return joblib.load(path)


def load_sample_library(sample_request_path: str) -> List[Dict]:
    with open(sample_request_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("library_recipes", [])


def maybe_warm_recipe_cache(
    tag_to_vector: Dict[str, np.ndarray],
    sample_request_path: str,
) -> Dict[str, np.ndarray]:
    if not sample_request_path or not os.path.exists(sample_request_path):
        return {}

    library_recipes = load_sample_library(sample_request_path)
    return precompute_recipe_cache(library_recipes, tag_to_vector)
