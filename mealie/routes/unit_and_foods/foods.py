from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import MealieCrudRoute
from mealie.schema import mapper
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    EdamamFoodResult,
    IngredientFood,
    IngredientFoodPagination,
    MergeFood,
    SaveIngredientFood,
    UsdaBulkUpdateResult,
    UsdaFoodResult,
    UsdaNutritionData,
)
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.responses import SuccessResponse
from mealie.services.recipe import edamam_service, usda_service

router = APIRouter(prefix="/foods", tags=["Recipes: Foods"], route_class=MealieCrudRoute)


@controller(router)
class IngredientFoodsController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.ingredient_foods

    @cached_property
    def mixins(self):
        return HttpRepo[SaveIngredientFood, IngredientFood, CreateIngredientFood](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=IngredientFoodPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery), search: str | None = None):
        response = self.repo.page_all(
            pagination=q,
            override=IngredientFood,
            search=search,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=IngredientFood, status_code=201)
    def create_one(self, data: CreateIngredientFood):
        save_data = mapper.cast(data, SaveIngredientFood, group_id=self.group_id)
        return self.mixins.create_one(save_data)

    @router.put("/merge", response_model=SuccessResponse)
    def merge_one(self, data: MergeFood):
        try:
            self.repo.merge(data.from_food, data.to_food)
            return SuccessResponse.respond("Successfully merged foods")
        except Exception as e:
            self.logger.error(e)
            raise HTTPException(500, "Failed to merge foods") from e

    # =========================================================
    # USDA FoodData Central integration

    @router.get("/usda/search", response_model=list[UsdaFoodResult])
    def usda_search(self, q: str = Query(..., description="Food name to search for")):
        """Search the USDA FoodData Central database for foods matching the given name.

        Requires USDA_API_KEY to be set in server settings (falls back to the DEMO_KEY with lower rate limits).
        """
        try:
            results = usda_service.search_foods(q, self.settings.usda_api_key)
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return [
            UsdaFoodResult(
                fdc_id=r.fdc_id,
                description=r.description,
                brand_owner=r.brand_owner,
                confidence=round(usda_service.score_result(q, r), 4),
            )
            for r in results
        ]

    @router.post("/usda/bulk-update", response_model=UsdaBulkUpdateResult)
    def usda_bulk_update(
        self,
        overwrite: bool = Query(False, description="Re-fetch nutrition even for foods that already have data"),
    ):
        """Bulk-populate nutrition data for all foods by searching USDA FoodData Central.

        For each food the name is used as the search query; the top result's nutrition
        is applied.  Foods that already have a ``calories`` value are skipped unless
        ``overwrite=true``.
        """
        import time

        all_foods = self.repo.get_all(override=IngredientFood)
        api_key = self.settings.usda_api_key

        updated = skipped = failed = 0
        failures: list[str] = []

        for food in all_foods:
            # Skip if already populated and not overwriting
            if not overwrite and food.calories is not None:
                skipped += 1
                continue

            try:
                results = usda_service.search_foods(food.name, api_key)
            except RuntimeError:
                failed += 1
                failures.append(food.name)
                time.sleep(0.1)
                continue

            if not results:
                skipped += 1
                continue

            # Try each ranked candidate until one returns nutrition data.
            # Some FDC IDs returned by search may no longer exist on the detail
            # endpoint (deleted/retired foods), so we fall back to the next best match.
            nutrition = None
            matched_candidate = None
            for candidate in results:
                try:
                    nutrition = usda_service.fetch_nutrition(candidate.fdc_id, api_key)
                    matched_candidate = candidate
                    break
                except RuntimeError:
                    pass
                finally:
                    # Small delay to stay well within the 1 000 req/hr rate limit
                    time.sleep(0.1)

            if nutrition is None or matched_candidate is None:
                failed += 1
                failures.append(food.name)
                continue

            # Apply nutrition fields to the food and save
            update_data = IngredientFood.model_validate(food)
            update_data.calories = nutrition.calories
            update_data.protein_content = nutrition.protein_content
            update_data.fat_content = nutrition.fat_content
            update_data.carbohydrate_content = nutrition.carbohydrate_content
            update_data.fiber_content = nutrition.fiber_content
            update_data.sugar_content = nutrition.sugar_content
            update_data.sodium_content = nutrition.sodium_content
            update_data.saturated_fat_content = nutrition.saturated_fat_content
            update_data.cholesterol_content = nutrition.cholesterol_content
            update_data.trans_fat_content = nutrition.trans_fat_content
            update_data.unsaturated_fat_content = nutrition.unsaturated_fat_content
            update_data.usda_fdc_id = matched_candidate.fdc_id
            update_data.usda_description = matched_candidate.description
            update_data.usda_confidence = round(usda_service.score_result(food.name, matched_candidate), 4)

            save_data = mapper.cast(update_data, SaveIngredientFood, group_id=self.group_id)
            self.mixins.update_one(save_data, food.id)
            updated += 1

        return UsdaBulkUpdateResult(
            total=len(all_foods),
            updated=updated,
            skipped=skipped,
            failed=failed,
            failures=failures,
        )

    @router.get("/usda/{fdc_id}/nutrition", response_model=UsdaNutritionData)
    def usda_fetch_nutrition(self, fdc_id: int):
        """Fetch nutrition data (per 100g) for a specific USDA FDC food ID.

        Returns nutrition values that can be applied to a Mealie food record.
        Does **not** modify any Mealie data — the caller is responsible for saving.
        """
        try:
            nutrition = usda_service.fetch_nutrition(fdc_id, self.settings.usda_api_key)
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return UsdaNutritionData(
            calories=nutrition.calories,
            protein_content=nutrition.protein_content,
            fat_content=nutrition.fat_content,
            carbohydrate_content=nutrition.carbohydrate_content,
            fiber_content=nutrition.fiber_content,
            sugar_content=nutrition.sugar_content,
            sodium_content=nutrition.sodium_content,
            saturated_fat_content=nutrition.saturated_fat_content,
            cholesterol_content=nutrition.cholesterol_content,
            trans_fat_content=nutrition.trans_fat_content,
            unsaturated_fat_content=nutrition.unsaturated_fat_content,
        )

    # =========================================================
    # Edamam Food Database integration

    @router.get("/edamam/search", response_model=list[EdamamFoodResult])
    def edamam_search(self, q: str = Query(..., description="Food name to search for")):
        """Search the Edamam Food Database for foods matching the given name.

        Returns food results with per-100g nutrition values already embedded —
        no second API call is required.  Requires EDAMAM_APP_ID and
        EDAMAM_APP_KEY to be set in server settings.
        """
        app_id = self.settings.EDAMAM_APP_ID
        app_key = self.settings.EDAMAM_APP_KEY
        if not app_id or not app_key:
            raise HTTPException(
                status_code=400,
                detail="EDAMAM_APP_ID and EDAMAM_APP_KEY must both be configured on this server.",
            )
        try:
            foods = edamam_service.search_foods(q, app_id, app_key)
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return [
            EdamamFoodResult(
                food_id=f.food_id,
                label=f.label,
                brand=f.brand,
                category=f.category,
                calories=f.calories,
                protein_content=f.protein_content,
                fat_content=f.fat_content,
                carbohydrate_content=f.carbohydrate_content,
                fiber_content=f.fiber_content,
                sugar_content=f.sugar_content,
                sodium_content=f.sodium_content,
                saturated_fat_content=f.saturated_fat_content,
                cholesterol_content=f.cholesterol_content,
                trans_fat_content=f.trans_fat_content,
                unsaturated_fat_content=f.unsaturated_fat_content,
            )
            for f in foods
        ]

    @router.get("/{item_id}", response_model=IngredientFood)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=IngredientFood)
    def update_one(self, item_id: UUID4, data: CreateIngredientFood):
        data = mapper.cast(data, SaveIngredientFood, group_id=self.group_id)
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=IngredientFood)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)
