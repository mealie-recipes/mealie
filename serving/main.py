from contextlib import asynccontextmanager
import logging
import os
import time
from typing import Dict, List, Optional

from fastapi import FastAPI
import numpy as np
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field

try:
    from pydantic import ConfigDict
except ImportError:
    ConfigDict = None

try:
    from .model_loader import ModelArtifacts, load_model_artifacts, maybe_warm_recipe_cache
    from .scorer import get_recipe_vector, rank_recipes
except ImportError:
    from model_loader import ModelArtifacts, load_model_artifacts, maybe_warm_recipe_cache
    from scorer import get_recipe_vector, rank_recipes

log = logging.getLogger(__name__)
MODEL_VERSION_OVERRIDE = os.getenv("MODEL_VERSION")
CACHE_WARMUP_REQUEST_PATH = os.getenv("CACHE_WARMUP_REQUEST_PATH", "").strip()
RECIPE_CACHE_ENABLED = os.getenv("RECIPE_CACHE_ENABLED", "true").strip().lower() in {
    "1", "true", "yes", "on"
}

tag_to_vector: Dict[str, np.ndarray] = {}
recipe_cache: Dict[str, np.ndarray] = {}
loaded_model: Optional[ModelArtifacts] = None


def _vector_dim() -> int:
    if not tag_to_vector:
        return 0
    first_vector = next(iter(tag_to_vector.values()))
    return int(np.asarray(first_vector).shape[0])


def _model_version() -> str:
    if MODEL_VERSION_OVERRIDE:
        return MODEL_VERSION_OVERRIDE
    if loaded_model is not None:
        return loaded_model.model_version
    return "unloaded"


def _normalize_user_vector(values: List[float]) -> np.ndarray:
    user_vector = np.asarray(values, dtype=np.float32)
    target_dim = _vector_dim()
    if target_dim and user_vector.size != target_dim:
        log.warning(
            "User vector length %s does not match model dimension %s; coercing.",
            user_vector.size,
            target_dim,
        )
        if user_vector.size > target_dim:
            user_vector = user_vector[:target_dim]
        else:
            user_vector = np.pad(user_vector, (0, target_dim - user_vector.size))
    return user_vector


@asynccontextmanager
async def lifespan(app: FastAPI):
    global loaded_model, tag_to_vector, recipe_cache
    loaded_model = load_model_artifacts()
    tag_to_vector = loaded_model.tag_to_vector
    recipe_cache = {}
    if CACHE_WARMUP_REQUEST_PATH:
        recipe_cache = maybe_warm_recipe_cache(tag_to_vector, CACHE_WARMUP_REQUEST_PATH)
    yield


app = FastAPI(title="Mealie Recipe Recommender", lifespan=lifespan)
Instrumentator().instrument(app).expose(app)


class Recipe(BaseModel):
    recipe_id: str
    name: str
    tags: List[str]
    minutes: Optional[float] = None
    calories: Optional[float] = None


class Recommendation(BaseModel):
    rank: int
    recipe_id: str
    name: str
    score: float
    tags: List[str]
    because_tags: List[str] = Field(default_factory=list)


class RecommendRequest(BaseModel):
    user_id: str
    user_vector: List[float]
    library_recipes: List[Recipe]
    top_n: int = 10


class RecommendResponse(BaseModel):
    if ConfigDict is not None:
        model_config = ConfigDict(protected_namespaces=())

    user_id: str
    recommendations: List[Recommendation]
    model_version: str
    inference_time_ms: float


class TagVectorRequest(BaseModel):
    tags: List[str]


class TagVectorResponse(BaseModel):
    vector: List[float]


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_version": _model_version(),
        "artifact_bucket": loaded_model.artifact_bucket if loaded_model else None,
        "artifact_key": loaded_model.artifact_key if loaded_model else None,
        "artifact_source": loaded_model.artifact_source if loaded_model else None,
        "tags_cached": len(tag_to_vector),
        "vector_dim": _vector_dim(),
        "recipe_cache_entries": len(recipe_cache),
    }


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    t0 = time.time()
    user_vector = _normalize_user_vector(req.user_vector)
    library = [recipe.model_dump() if hasattr(recipe, "model_dump") else recipe.dict() for recipe in req.library_recipes]
    recommendations = rank_recipes(
        user_vector,
        library,
        tag_to_vector,
        req.top_n,
        recipe_cache=recipe_cache if RECIPE_CACHE_ENABLED else None,
    )
    elapsed_ms = round((time.time() - t0) * 1000, 2)
    return RecommendResponse(
        user_id=req.user_id,
        recommendations=recommendations,
        model_version=_model_version(),
        inference_time_ms=elapsed_ms,
    )


@app.post("/tag-vector", response_model=TagVectorResponse)
def tag_vector(req: TagVectorRequest):
    vector = get_recipe_vector(req.tags, tag_to_vector, vector_dim=_vector_dim() or None)
    return TagVectorResponse(vector=vector.tolist())
