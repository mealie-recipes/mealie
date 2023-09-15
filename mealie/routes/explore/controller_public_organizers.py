from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicExploreController
from mealie.schema.make_dependable import make_dependable
from mealie.schema.recipe.recipe import RecipeCategory, RecipeTag, RecipeTool
from mealie.schema.recipe.recipe_category import CategoryOut, TagOut
from mealie.schema.recipe.recipe_tool import RecipeToolOut
from mealie.schema.response.pagination import PaginationBase, PaginationQuery

base_prefix = "/organizers/{group_slug}"
categories_router = APIRouter(prefix=f"{base_prefix}/categories")
tags_router = APIRouter(prefix=f"{base_prefix}/tags")
tools_router = APIRouter(prefix=f"{base_prefix}/tools")


@controller(categories_router)
class PublicCategoriesController(BasePublicExploreController):
    @property
    def categories(self):
        return self.repos.categories.by_group(self.group.id)

    @categories_router.get("", response_model=PaginationBase[RecipeCategory])
    def get_all(
        self, q: PaginationQuery = Depends(make_dependable(PaginationQuery)), search: str | None = None
    ) -> PaginationBase[RecipeCategory]:
        response = self.categories.page_all(
            pagination=q,
            override=RecipeCategory,
            search=search,
        )

        response.set_pagination_guides(categories_router.url_path_for("get_all", group_slug=self.group.slug), q.dict())
        return response

    @categories_router.get("/{item_id}", response_model=CategoryOut)
    def get_one(self, item_id: UUID4) -> CategoryOut:
        item = self.categories.get_one(item_id)
        if not item:
            raise HTTPException(404, "category not found")

        return item


@controller(tags_router)
class PublicTagsController(BasePublicExploreController):
    @property
    def tags(self):
        return self.repos.tags.by_group(self.group.id)

    @tags_router.get("", response_model=PaginationBase[RecipeTag])
    def get_all(
        self, q: PaginationQuery = Depends(make_dependable(PaginationQuery)), search: str | None = None
    ) -> PaginationBase[RecipeTag]:
        response = self.tags.page_all(
            pagination=q,
            override=RecipeTag,
            search=search,
        )

        response.set_pagination_guides(tags_router.url_path_for("get_all", group_slug=self.group.slug), q.dict())
        return response

    @tags_router.get("/{item_id}", response_model=TagOut)
    def get_one(self, item_id: UUID4) -> TagOut:
        item = self.tags.get_one(item_id)
        if not item:
            raise HTTPException(404, "tag not found")

        return item


@controller(tools_router)
class PublicToolsController(BasePublicExploreController):
    @property
    def tools(self):
        return self.repos.tools.by_group(self.group.id)

    @tools_router.get("", response_model=PaginationBase[RecipeTool])
    def get_all(
        self, q: PaginationQuery = Depends(make_dependable(PaginationQuery)), search: str | None = None
    ) -> PaginationBase[RecipeTool]:
        response = self.tools.page_all(
            pagination=q,
            override=RecipeTool,
            search=search,
        )

        response.set_pagination_guides(tools_router.url_path_for("get_all", group_slug=self.group.slug), q.dict())
        return response

    @tools_router.get("/{item_id}", response_model=RecipeToolOut)
    def get_one(self, item_id: UUID4) -> RecipeToolOut:
        item = self.tools.get_one(item_id)
        if not item:
            raise HTTPException(404, "tool not found")

        return item
