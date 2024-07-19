from dataclasses import dataclass

from slugify import slugify

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe import TagOut
from mealie.schema.recipe.recipe_category import TagSave


class NoContextException(Exception):
    pass


@dataclass(slots=True)
class ScraperContext:
    repos: AllRepositories


class ScrapedExtras:
    def __init__(self) -> None:
        self._tags: list[str] = []

    def set_tags(self, tags: list[str]) -> None:
        self._tags = tags

    def use_tags(self, ctx: ScraperContext) -> list[TagOut]:
        if not self._tags:
            return []

        repo = ctx.repos.tags

        tags = []
        seen_tag_slugs: set[str] = set()
        for tag in self._tags:
            slugify_tag = slugify(tag)
            if slugify_tag in seen_tag_slugs:
                continue

            seen_tag_slugs.add(slugify_tag)

            # Check if tag exists
            if db_tag := repo.get_one(slugify_tag, "slug"):
                tags.append(db_tag)
                continue

            save_data = TagSave(name=tag, group_id=ctx.repos.group_id)
            db_tag = repo.create(save_data)

            tags.append(db_tag)

        return tags
