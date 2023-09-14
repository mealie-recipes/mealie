from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicExploreController
from mealie.schema.cookbook.cookbook import ReadCookBook, RecipeCookBook
from mealie.schema.make_dependable import make_dependable
from mealie.schema.response.pagination import PaginationBase, PaginationQuery

router = APIRouter(prefix="/cookbooks/{group_slug}")


@controller(router)
class PublicCookbooksController(BasePublicExploreController):
    @property
    def cookbooks(self):
        return self.repos.cookbooks.by_group(self.group.id)

    @property
    def recipes(self):
        return self.repos.recipes.by_group(self.group.id)

    @router.get("", response_model=PaginationBase[ReadCookBook])
    def get_all(
        self, q: PaginationQuery = Depends(make_dependable(PaginationQuery)), search: str | None = None
    ) -> PaginationBase[ReadCookBook]:
        public_filter = "public = TRUE"
        if q.query_filter:
            q.query_filter = f"({q.query_filter}) AND {public_filter}"
        else:
            q.query_filter = public_filter

        response = self.cookbooks.page_all(
            pagination=q,
            override=ReadCookBook,
            search=search,
        )

        response.set_pagination_guides(router.url_path_for("get_all", group_slug=self.group.slug), q.dict())
        return response

    @router.get("/{item_id}", response_model=RecipeCookBook)
    def get_one(self, item_id: UUID4 | str) -> RecipeCookBook:
        match_attr = "slug" if isinstance(item_id, str) else "id"
        cookbook = self.cookbooks.get_one(item_id, match_attr)

        if not cookbook or not cookbook.public:
            raise HTTPException(404, "cookbook not found")

        recipes = self.recipes.page_all(
            PaginationQuery(page=1, per_page=-1, query_filter="settings.public = TRUE"), cookbook=cookbook
        )
        return cookbook.cast(RecipeCookBook, recipes=recipes.items)
