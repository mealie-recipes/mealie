from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicHouseholdExploreController
from mealie.schema.cookbook.cookbook import ReadCookBook, RecipeCookBook
from mealie.schema.make_dependable import make_dependable
from mealie.schema.response.pagination import PaginationBase, PaginationQuery

router = APIRouter(prefix="/cookbooks")


@controller(router)
class PublicCookbooksController(BasePublicHouseholdExploreController):
    @property
    def cross_household_cookbooks(self):
        return self.cross_household_repos.cookbooks

    @router.get("", response_model=PaginationBase[ReadCookBook])
    def get_all(
        self,
        q: PaginationQuery = Depends(make_dependable(PaginationQuery)),
        search: str | None = None,
    ) -> PaginationBase[ReadCookBook]:
        public_filter = "(household.preferences.privateHousehold = FALSE AND public = TRUE)"
        if q.query_filter:
            q.query_filter = f"({q.query_filter}) AND {public_filter}"
        else:
            q.query_filter = public_filter

        response = self.cross_household_cookbooks.page_all(
            pagination=q,
            override=ReadCookBook,
            search=search,
        )

        response.set_pagination_guides(self.get_explore_url_path(router.url_path_for("get_all")), q.model_dump())
        return response

    @router.get("/{item_id}", response_model=RecipeCookBook)
    def get_one(self, item_id: UUID4 | str) -> RecipeCookBook:
        NOT_FOUND_EXCEPTION = HTTPException(404, "cookbook not found")
        if isinstance(item_id, UUID):
            match_attr = "id"
        else:
            try:
                UUID(item_id)
                match_attr = "id"
            except ValueError:
                match_attr = "slug"
        cookbook = self.cross_household_cookbooks.get_one(item_id, match_attr)

        if not cookbook or not cookbook.public:
            raise NOT_FOUND_EXCEPTION
        household = self.repos.households.get_one(cookbook.household_id)
        if not household or household.preferences.private_household:
            raise NOT_FOUND_EXCEPTION

        cross_household_recipes = self.cross_household_repos.recipes
        recipes = cross_household_recipes.page_all(
            PaginationQuery(
                page=1,
                per_page=-1,
                query_filter="settings.public = TRUE AND household.preferences.privateHousehold = FALSE",
            ),
            cookbook=cookbook,
        )
        return cookbook.cast(RecipeCookBook, recipes=recipes.items)
