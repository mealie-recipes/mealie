from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openai import OpenAI

from mealie.db.recipe_embeddings import (
    QueryEmbedding,
    embeddings_available,
    vector_literal,
)
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.ai_providers import AIProviderOut
from mealie.schema.recipe.recipe import RecipeDraft, RecipeOut
from mealie.services._base_service import BaseService
from mealie.services.openai.openai import client_options

MAX_INSTRUCTION_CHARS = 2000
MAX_TEXT_CHARS = 6000
"""Roughly 1500 tokens, which fits the context window of the small local embedding models too."""

SYNC_BATCH_SIZE = 100

EMBED_CHUNK_SIZE = 2
"""
How many recipes go to the provider in one request.

A local provider such as Ollama answers one request at a time, so a search's embedding waits
behind whatever request is running. Small requests keep that wait under QUERY_TIMEOUT_SECONDS;
with a whole batch in one request, every search made during indexing timed out.
"""

SEMANTIC_FALLBACK_HEADER = "X-Semantic-Search-Fallback"
"""Set on a recipe search response when a semantic search was asked for but the text search answered"""

QUERY_TIMEOUT_SECONDS = 10
"""How long a search waits for its embedding before it falls back to the text search."""

# unbounded growth is prevented by clearing, not by LRU eviction. Paging through one
# search's results is what this is for, and that only ever needs the latest few entries.
_query_cache: dict[tuple, QueryEmbedding] = {}
_QUERY_CACHE_SIZE = 256


def recipe_embedding_text(recipe: RecipeDraft | RecipeOut) -> str:
    """The text that represents a recipe in semantic search."""
    parts = [
        recipe.name or "",
        recipe.description or "",
        ", ".join(category.name for category in recipe.recipe_category or []),
        ", ".join(tag.name for tag in recipe.tags or []),
        "\n".join(ingredient.display for ingredient in recipe.recipe_ingredient or []),
        "\n".join(step.text for step in recipe.recipe_instructions or [])[:MAX_INSTRUCTION_CHARS],
    ]
    return "\n".join(part for part in parts if part)[:MAX_TEXT_CHARS]


class RecipeEmbeddingService(BaseService):
    """Embeds a group's recipes and search strings with the group's embedding provider."""

    def __init__(self, repos: AllRepositories) -> None:
        self.repos = repos
        self.session = repos.session
        self.group_id = repos.scoped_group_id

        settings = repos.group_ai_provider_settings.get_one(self.group_id) if self.group_id else None
        self.provider: AIProviderOut | None = (
            repos.group_ai_providers.get_one(settings.embedding_provider_id)
            if settings and settings.embedding_provider_id
            else None
        )

        super().__init__()

    @property
    def enabled(self) -> bool:
        return self.provider is not None and embeddings_available(self.session)

    @cached_property
    def _client(self) -> OpenAI:
        """One client for every request of this service, so the many small requests of a sync share a connection."""
        from openai import OpenAI

        if not self.provider:
            raise ValueError("The group has no embedding provider")

        # No retries: a search falls back to the text search, and the sync embeds stale recipes on its next run
        return OpenAI(**client_options(self.provider), max_retries=0)

    def _embed(self, provider: AIProviderOut, texts: list[str]) -> list[str]:
        # The timeout is passed with the request, since a search gets a shorter one than the client's
        response = self._client.embeddings.create(model=provider.model, input=texts, timeout=provider.timeout)
        return [vector_literal(item.embedding) for item in sorted(response.data, key=lambda item: item.index)]

    def embed_query(self, search: str) -> QueryEmbedding | None:
        """Embed a search string. None when semantic search is off or the provider fails, so callers can fall back."""
        if not self.enabled or not self.provider:
            return None

        key = (self.provider.id, self.provider.model, search)
        # Read once: another request can clear the cache between a membership test and a lookup
        if cached := _query_cache.get(key):
            return cached

        # A search waits for this, so it gets less time than the provider allows a chat completion
        provider = self.provider.model_copy(update={"timeout": min(self.provider.timeout, QUERY_TIMEOUT_SECONDS)})
        try:
            vector = self._embed(provider, [search])[0]
        except Exception:
            self.logger.exception("Could not embed the search query; falling back to text search")
            return None

        if len(_query_cache) >= _QUERY_CACHE_SIZE:
            _query_cache.clear()
        embedding = _query_cache[key] = QueryEmbedding(provider.model, vector)
        return embedding

    def sync(self, limit: int = SYNC_BATCH_SIZE) -> int:
        """
        Embed up to `limit` of the group's recipes that are new, were edited, or were embedded with
        another model. Returns how many were embedded.
        """
        import openai

        if not self.enabled or not self.provider:
            return 0

        model = self.provider.model
        stale = self.repos.recipe_embeddings.get_stale(model, limit)
        if not stale:
            return 0

        texts = [recipe_embedding_text(item.recipe) for item in stale]
        vectors: list[str | None] = []
        rejection: Exception | None = None
        failure: Exception | None = None
        try:
            for start in range(0, len(texts), EMBED_CHUNK_SIZE):
                chunk = texts[start : start + EMBED_CHUNK_SIZE]
                try:
                    vectors += self._embed(self.provider, chunk)
                except (openai.BadRequestError, openai.UnprocessableEntityError) as e:
                    # The provider refused the input, and one bad text fails the whole request. Find out which.
                    rejection = e
                    vectors += [self._embed_or_none(text) for text in chunk]
        except Exception as e:
            # e.g. a timeout. The requests before it were answered, so only the rest waits for the next run
            failure = e

        error = failure or rejection
        if error and not any(vectors):
            # Nothing works, so the provider or its model is the problem, not these recipes
            raise error

        embedded = list(zip(stale[: len(vectors)] if failure else stale, vectors, strict=True))
        rejected = [item.recipe.slug for item, vector in embedded if vector is None]
        if rejected:
            self.logger.warning(f"The embedding provider rejected these recipes, skipping them: {rejected}")

        self.repos.recipe_embeddings.save(model, embedded)
        if failure:
            raise failure
        return len(embedded) - len(rejected)

    def _embed_or_none(self, text: str) -> str | None:
        import openai

        if not self.provider:
            return None
        try:
            return self._embed(self.provider, [text])[0]
        except openai.BadRequestError, openai.UnprocessableEntityError:
            return None
