from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.repos.public_visibility import is_cookbook_publicly_visible, public_cookbooks_clause
from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicHouseholdExploreController
from mealie.schema.cookbook.cookbook import ReadCookBook
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
        response = self.cross_household_cookbooks.page_all(
            pagination=q,
            override=ReadCookBook,
            search=search,
            extra_filter=public_cookbooks_clause(),
        )

        response.set_pagination_guides(self.get_explore_url_path(router.url_path_for("get_all")), q.model_dump())
        return response

    @router.get("/{item_id}", response_model=ReadCookBook)
    def get_one(self, item_id: UUID4 | str) -> ReadCookBook:
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

        household = cookbook and self.repos.households.get_one(cookbook.household_id)
        if not is_cookbook_publicly_visible(cookbook, household):
            raise NOT_FOUND_EXCEPTION

        return cookbook
