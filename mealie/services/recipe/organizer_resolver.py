from collections.abc import Callable

from pydantic import BaseModel
from slugify import slugify

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import RecipeCategory, RecipeTag, RecipeTool
from mealie.schema.recipe.recipe_category import CategorySave, TagSave
from mealie.schema.recipe.recipe_tool import RecipeToolSave
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.matching import find_match

ORGANIZER_FUZZY_MATCH_THRESHOLD = 90
"""
Deliberately stricter than the ingredient parser's thresholds. Attaching the wrong organizer is
worse than missing one, and near-misses are common among organizer names ("Vegan"/"Vegetarian").
"""


class OrganizerResolver:
    """
    Turns organizer names into database entities, matching against the group's existing
    organizers before creating anything new.
    """

    def __init__(self, repos: AllRepositories, fuzzy_match_threshold: int = ORGANIZER_FUZZY_MATCH_THRESHOLD) -> None:
        self.repos = repos
        self.fuzzy_match_threshold = fuzzy_match_threshold

        self._tags: dict[str, RecipeTag] | None = None
        self._categories: dict[str, RecipeCategory] | None = None
        self._tools: dict[str, RecipeTool] | None = None

    @staticmethod
    def _normalize(name: str) -> str:
        return slugify(name)

    def _load[T: BaseModel](self, repo, schema: type[T]) -> dict[str, T]:
        query = PaginationQuery(page=1, per_page=-1)
        items = repo.page_all(query).items
        return {self._normalize(item.name): schema.model_validate(item, from_attributes=True) for item in items}

    @property
    def tags(self) -> dict[str, RecipeTag]:
        if self._tags is None:
            self._tags = self._load(self.repos.tags, RecipeTag)

        return self._tags

    @property
    def categories(self) -> dict[str, RecipeCategory]:
        if self._categories is None:
            self._categories = self._load(self.repos.categories, RecipeCategory)

        return self._categories

    @property
    def tools(self) -> dict[str, RecipeTool]:
        if self._tools is None:
            self._tools = self._load(self.repos.tools, RecipeTool)

        return self._tools

    def existing_names(self) -> dict[str, list[str]]:
        """The group's existing organizer names, for injecting into a prompt."""

        return {
            "tags": [tag.name for tag in self.tags.values()],
            "categories": [category.name for category in self.categories.values()],
            "tools": [tool.name for tool in self.tools.values()],
        }

    def _resolve[T: BaseModel](
        self,
        names: list[str],
        store: dict[str, T],
        create_missing: bool,
        create: Callable[[str], T],
    ) -> list[T]:
        resolved: list[T] = []
        seen: set[str] = set()

        for name in names:
            name = name.strip()
            if not name:
                continue

            normalized = self._normalize(name)
            if not normalized or normalized in seen:
                continue

            seen.add(normalized)

            match = find_match(normalized, store_map=store, fuzzy_match_threshold=self.fuzzy_match_threshold)
            if match:
                resolved.append(match)
                continue

            if not create_missing:
                continue

            created = create(name)
            store[normalized] = created
            resolved.append(created)

        return resolved

    def resolve_tags(self, names: list[str], create_missing: bool) -> list[RecipeTag]:
        def create(name: str) -> RecipeTag:
            saved = self.repos.tags.create(TagSave(name=name, group_id=self.repos.group_id))
            return RecipeTag.model_validate(saved, from_attributes=True)

        return self._resolve(names, self.tags, create_missing, create)

    def resolve_categories(self, names: list[str], create_missing: bool) -> list[RecipeCategory]:
        def create(name: str) -> RecipeCategory:
            saved = self.repos.categories.create(CategorySave(name=name, group_id=self.repos.group_id))
            return RecipeCategory.model_validate(saved, from_attributes=True)

        return self._resolve(names, self.categories, create_missing, create)

    def resolve_tools(self, names: list[str], create_missing: bool) -> list[RecipeTool]:
        def create(name: str) -> RecipeTool:
            saved = self.repos.tools.create(RecipeToolSave(name=name, group_id=self.repos.group_id))
            return RecipeTool.model_validate(saved, from_attributes=True)

        return self._resolve(names, self.tools, create_missing, create)
