from typing import Literal

from mealie.schema._mealie import MealieModel


class SubstitutionIngredient(MealieModel):
    raw: str
    normalized: str


class SubstitutionPredictRequest(MealieModel):
    recipe_id: str
    ingredients: list[SubstitutionIngredient]
    missing_ingredient: SubstitutionIngredient
    request_id: str | None = None
    top_k: int = 3
    recipe_title: str | None = None
    instructions: list[str] | None = None
    timestamp: str | None = None


class SubstitutionPrediction(MealieModel):
    ingredient: str
    rank: int
    embedding_score: float


class SubstitutionPredictResponse(MealieModel):
    recipe_id: str
    missing_ingredient: str
    request_id: str | None = None
    substitutions: list[SubstitutionPrediction] = []
    model_version: str | None = None
    serving_version: str | None = None
    latency_ms: int | None = None


class SubstitutionFeedbackRequest(MealieModel):
    request_id: str
    recipe_id: str
    missing_ingredient: str
    suggested_substitution: str
    user_accepted: bool
    model_version: str | None = None


class SubstitutionFeedbackResponse(MealieModel):
    status: Literal["logged"] | str
    key: str | None = None


class RecipeSubstitutionFeedbackIn(MealieModel):
    request_id: str
    suggested_substitution: str
    user_accepted: bool
    model_version: str | None = None
