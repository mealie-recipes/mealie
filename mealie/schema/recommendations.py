from pydantic import UUID4, Field

from mealie.schema._mealie import MealieModel


class RecommendationStatus(MealieModel):
    needs_onboarding: bool
    has_vector: bool
    rating_count: int


class RecommendationPreferencesIn(MealieModel):
    tags: list[str]


class RecommendationDismissIn(MealieModel):
    recipe_id: UUID4


class RecommendationAck(MealieModel):
    status: str = "ok"


class RecommendationItem(MealieModel):
    recipe_id: UUID4
    slug: str | None = None
    name: str
    description: str | None = None
    image: str | None = None
    rating: float | None = None
    tags: list[str] = Field(default_factory=list)
    because_tags: list[str] = Field(default_factory=list)
    score: float | None = None
    rank: int | None = None


class RecommendationResult(MealieModel):
    recommendations: list[RecommendationItem]
    cold_start: bool
    model_version: str
