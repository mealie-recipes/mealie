# Safeguarding Plan — Mealie Personalized Recipe Recommender
**Team:** Bias & Variance (proj18)  
**Course:** ML Systems Design and Operations  
**Date:** April 2026

---

## Overview

Our system uses ALS (Alternating Least Squares) collaborative filtering to rank recipes in a user's personal Mealie library by predicted preference. This plan describes the concrete mechanisms we have implemented to address fairness, transparency, privacy, robustness, and accountability across all system components.

---

## 1. Fairness

**Risk:** ALS collaborative filtering has an inherent popularity bias, recipes that appear frequently in the training data receive stronger item vectors and tend to dominate recommendation scores regardless of individual user taste.

**Mechanisms implemented:**

- **Diversity filter** (`serving/app/scorer.py` ; `apply_diversity()`): Caps results at a maximum of 3 recipes per cuisine type (italian, asian, mexican, etc.) before returning the final ranked list. This prevents any single cuisine from monopolizing all 10 recommendation slots even if it dominates the user's interaction history.

- **Cold-start fallback** (`mealie/services/recommendation_service.py` ; `_baseline_recommendations()`): Users with fewer than 5 ratings have no trained taste vector. Rather than showing random or popularity-only results, the system falls back to sorting the user's own library by their existing ratings (highest rated first), then alphabetically. This ensures cold-start users still get a meaningful, personalized-to-their-library result rather than global popularity rankings.

- **Onboarding tag selection** (`frontend/app/pages/preferences.vue`): New users pick at least 2 cuisine/dietary preference tags before seeing recommendations. This seeds their taste vector with explicit preferences rather than assuming defaults, reducing cold-start bias from day one.

- **User-specific vectors**: Each user has their own taste vector stored in the `user_ml_preferences` PostgreSQL table, updated incrementally as they rate and dismiss recipes. Recommendations are personal to each user's library and interaction history, not shared global rankings.

---

## 2. Transparency

**Risk:** Users may not understand why certain recipes are recommended, or which version of the model is serving them.

**Mechanisms implemented:**

- **"Because tags" explanation** (`AppRecommendedForYou.vue`): Every recommendation card displays up to 3 tags explaining why that recipe was suggested (e.g. "italian", "pasta", "comfort-food"). These are the tags from the recipe that matched the user's taste vector.

- **Cold-start label** (`AppRecommendedForYou.vue`): When a user has fewer than 5 ratings, the panel displays a chip: *"Rate recipes to personalize this list"* so users understand their recommendations will improve as they interact more. Taste vectors are updated continuously as users rate and dismiss recipes — preference re-seeding via the onboarding page is planned for a future release.

- **Model version in every response**: The `/recommend` endpoint returns a `model_version` field in every API response. This field is logged and visible in MLflow, so any recommendation can be traced to the exact model version that produced it.

- **MLflow experiment tracking** (`mealie-recipe-recommender` experiment): Every training run logs hyperparameters, NDCG@10, training time, dataset version, and git sha. The full lineage from raw data to deployed model is queryable in the MLflow UI at `http://129.114.26.214:30500`.

- **Labeled UI panel**: The recommendation panel is explicitly labeled "Recommended for You" and is visually distinct from the default recipe list, so users always know they are viewing a personalized view.

---

## 3. Privacy

**Risk:** User interaction data and taste vectors could expose personal preferences or be leaked through API responses.

**Mechanisms implemented:**

- **Vectors never exposed externally**: User taste vectors are stored only in the PostgreSQL `user_ml_preferences` table inside the cluster. They are never included in API responses, frontend payloads, or application logs.

- **Minimal interaction schema**: The `user_ml_preferences` table stores only `user_id`, `taste_vector`, `onboarding_tags`, and `rating_count`. No PII (names, emails, passwords, IP addresses) is stored. Individual rating events update the taste vector in-place via a weighted sum, raw events are not persisted.

- **Pseudonymization**: All vectors and preference records are keyed by `user_id` (an internal UUID), not by email or username. The mapping between UUID and identity lives only in Mealie's user table and is never passed to the recommendation pipeline.

- **On-premises inference**: All model inference runs inside the Kubernetes cluster on Chameleon infrastructure. No user data, interaction events, or recipe content is sent to any external service or third-party API.

- **Secrets management**: All credentials (PostgreSQL, MinIO, MLflow) are injected via Kubernetes Secrets managed by `create-secrets.sh`. No credentials are hardcoded in any Git repository.

---

## 4. Robustness

**Risk:** The recommendation feature could fail in ways that degrade the core Mealie experience.

**Mechanisms implemented:**

- **Graceful degradation in serving** (`recommendation_service.py`): If the inference API is unreachable or returns an error, the system automatically falls back to `_baseline_recommendations()` — sorting the user's library by their own ratings. The Mealie UI continues to function normally; users see a reasonable list rather than an error.

- **MinIO fallback in model loader** (`serving/app/model_loader.py`): If `tag_to_vector.pkl` cannot be loaded from MinIO at startup (e.g. MinIO is temporarily unavailable), the serving container falls back to a local `/artifacts` copy. The container does not crash.

- **Input validation**: All API endpoints use Pydantic models for strict input validation. Malformed requests return 422 errors rather than causing unhandled exceptions.

- **Data quality gates** (`nightly-eval` CronJob): The nightly evaluation job checks three conditions and exits with code 1 on failure, preventing bad state from going undetected:
  - **Dataset presence**: verifies `train.parquet` and `val.parquet` exist in MinIO and have non-zero rows
  - **Model artifact**: verifies `production/tag_to_vector.pkl` exists in MinIO
  - **Inference health**: calls `/health` on the inference API and flags if it returns non-200

- **Training quality gate** (`scripts/train.py`): Models are only registered to the MLflow Model Registry and promoted to Production if `NDCG@10 >= NDCG_THRESHOLD`. Models that fail the gate are logged but not deployed.

- **Request timeout** (`recommendation_service.py`): All calls from Mealie to the inference API have a 2-second timeout (`REQUEST_TIMEOUT = 2.0`). A slow inference API will not hang the Mealie UI.

---

## 5. Accountability

**Risk:** It may be unclear which model version produced a given recommendation, or how to roll back if a bad model is deployed.

**Mechanisms implemented:**

- **MLflow Model Registry**: Every model that passes the quality gate is registered under `mealie-als-recommender` in MLflow with its version number, NDCG@10 score, training dataset version, training time, and git sha of the training code. Only models in the `Production` stage are served.

- **Versioned training datasets**: The batch pipeline uploads training data to MinIO under `training-data/datasets/{version}/` (default: `current`). Each MLflow training run records which dataset version it used, so any deployed model can be traced back to the exact data it was trained on.

- **Audit trail via Git**: All pipeline code, K8s manifests, serving code, and Mealie integration code are version-controlled in Git. The full system can be reproduced from the repositories.

- **Nightly evaluation logs to MLflow** (`nightly-eval` experiment): Every nightly eval run is logged as an MLflow experiment with pass/fail status and metrics for each of the 3 quality checkpoints. This creates a historical record of data health over time.

- **Automated rollback** (`model-promoter` CronJob): The model-promoter runs every 6 hours and checks the latest nightly-eval results. If the inference API is unhealthy, it automatically restores the previous `production/tag_to_vector.pkl` from a backup before promoting any new artifact. This prevents a bad model from staying in production undetected.

- **Role ownership**: Each component has a clear owner (Data: Bryce, Training: Shashwat, Serving: Sharvin, DevOps: Mahima). Incidents can be routed to the appropriate owner based on which component failed.

---

## Summary Table

| Principle | Key Mechanism | Where |
|---|---|---|
| Fairness | Diversity filter (max 3 per cuisine) | `scorer.py` |
| Fairness | Cold-start fallback to rating-sorted library | `recommendation_service.py` |
| Transparency | "Because tags" on every recommendation card | `AppRecommendedForYou.vue` |
| Transparency | Model version in every API response | `/recommend` endpoint |
| Privacy | Vectors never in API responses or logs | `recommendation_service.py` |
| Privacy | On-premises inference, no external calls | Chameleon K8s cluster |
| Robustness | Graceful degradation if inference API down | `recommendation_service.py` |
| Robustness | 3-point nightly data quality gates | `nightly_eval.py` |
| Robustness | Training quality gate (NDCG threshold) | `train.py` |
| Accountability | MLflow Model Registry with full lineage | MLflow `mealie-als-recommender` |
| Accountability | Nightly eval logged to MLflow `nightly-eval` experiment | `nightly_eval.py` |
| Accountability | Versioned training datasets in MinIO | `batch.py` |
| Accountability | Automated rollback via model-promoter CronJob | `model-promoter` CronJob |
