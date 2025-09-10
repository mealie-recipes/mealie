from functools import cached_property

from fastapi import APIRouter, Depends
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema import mapper
from mealie.schema.recipe.recipe import RecipeTool, RecipeToolPagination
from mealie.schema.recipe.recipe_tool import RecipeToolCreate, RecipeToolResponse, RecipeToolSave
from mealie.schema.response.pagination import PaginationQuery

router = APIRouter(prefix="/tools", tags=["Organizer: Tools"])


@controller(router)
class RecipeToolController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.tools

    @property
    def mixins(self) -> HttpRepo:
        return HttpRepo[RecipeToolCreate, RecipeTool, RecipeToolCreate](self.repo, self.logger)

    @router.get("", response_model=RecipeToolPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery), search: str | None = None):
        response = self.repo.page_all(
            pagination=q,
            override=RecipeTool,
            search=search,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=RecipeTool, status_code=201)
    def create_one(self, data: RecipeToolCreate):
        save_data = mapper.cast(data, RecipeToolSave, group_id=self.group_id)
        return self.mixins.create_one(save_data)

    @router.get("/{item_id}", response_model=RecipeTool)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=RecipeTool)
    def update_one(self, item_id: UUID4, data: RecipeToolCreate):
        data = mapper.cast(data, RecipeToolSave, group_id=self.group_id)
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=RecipeTool)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)  # type: ignore

    @router.get("/slug/{tool_slug}", response_model=RecipeToolResponse)
    async def get_one_by_slug(self, tool_slug: str):
        return self.repo.get_one(tool_slug, "slug", override_schema=RecipeToolResponse)
