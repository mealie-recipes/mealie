import httpx

from mealie.core.config import get_app_settings
from mealie.schema.recipe.recipe_substitution import (
    SubstitutionFeedbackRequest,
    SubstitutionFeedbackResponse,
    SubstitutionPredictRequest,
    SubstitutionPredictResponse,
)


class SubstitutionService:
    def __init__(self) -> None:
        settings = get_app_settings()
        self.predict_url = settings.SUBSTITUTION_API_URL
        self.feedback_url = settings.SUBSTITUTION_FEEDBACK_URL

    async def predict(self, payload: SubstitutionPredictRequest) -> SubstitutionPredictResponse:
        if not self.predict_url:
            raise ValueError("SUBSTITUTION_API_URL is not configured")

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                self.predict_url,
                json=payload.model_dump(mode="json", exclude_none=True),
            )
            response.raise_for_status()

        return SubstitutionPredictResponse.model_validate(response.json())

    async def feedback(self, payload: SubstitutionFeedbackRequest) -> SubstitutionFeedbackResponse:
        if not self.feedback_url:
            raise ValueError("SUBSTITUTION_FEEDBACK_URL is not configured")

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                self.feedback_url,
                json=payload.model_dump(mode="json", exclude_none=True),
            )
            response.raise_for_status()

        return SubstitutionFeedbackResponse.model_validate(response.json())
