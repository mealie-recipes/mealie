from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mealie.db.models.recipe.recipe import RecipeModel
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.recommendations import (
    RecommendationAck,
    RecommendationDismissIn,
    RecommendationPreferencesIn,
    RecommendationResult,
    RecommendationStatus,
)
from mealie.services.recommendation_service import (
    fetch_recommendations,
    fetch_tag_vector,
    get_or_create_prefs,
    get_prefs,
    update_vector_on_rating,
)

router = UserAPIRouter(prefix="/recommendations", tags=["Recommendations"])


@controller(router)
class RecommendationController(BaseUserController):
    def _get_group_recipes(self) -> list[RecipeModel]:
        return (
            self.session.execute(
                select(RecipeModel)
                .options(selectinload(RecipeModel.tags))
                .filter(RecipeModel.group_id == self.group_id)
                .order_by(RecipeModel.name)
            )
            .scalars()
            .unique()
            .all()
        )

    @router.get("/status", response_model=RecommendationStatus)
    def status(self):
        prefs = get_prefs(self.session, self.user.id)
        return RecommendationStatus(
            needs_onboarding=prefs is None or not prefs.onboarding_tags,
            has_vector=bool(prefs and prefs.taste_vector),
            rating_count=prefs.rating_count if prefs else 0,
        )

    @router.post("/preferences", response_model=RecommendationAck)
    def set_preferences(self, body: RecommendationPreferencesIn):
        prefs = get_or_create_prefs(self.session, self.user.id)
        prefs.onboarding_tags = list(dict.fromkeys(tag.strip() for tag in body.tags if tag.strip()))
        prefs.taste_vector = fetch_tag_vector(prefs.onboarding_tags)
        self.session.commit()
        return RecommendationAck()

    @router.get("", response_model=RecommendationResult)
    async def get_recommendations(self):
        recipes = self._get_group_recipes()
        return RecommendationResult(**await fetch_recommendations(self.session, self.user.id, recipes))

    @router.post("/dismiss", response_model=RecommendationAck)
    def dismiss(self, body: RecommendationDismissIn, background_tasks: BackgroundTasks):
        recipe = (
            self.session.execute(
                select(RecipeModel)
                .options(selectinload(RecipeModel.tags))
                .filter(
                    RecipeModel.id == body.recipe_id,
                    RecipeModel.group_id == self.group_id,
                )
            )
            .scalars()
            .first()
        )
        if recipe:
            background_tasks.add_task(
                update_vector_on_rating,
                self.user.id,
                [tag.name for tag in recipe.tags],
                2,
            )
        return RecommendationAck()
