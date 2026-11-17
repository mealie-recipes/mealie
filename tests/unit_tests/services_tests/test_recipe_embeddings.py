from collections.abc import Generator
from uuid import UUID

import httpx
import openai
import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from mealie.core.config import get_app_settings
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.recipe_embeddings import EMBEDDINGS_TABLE, embeddings_available, vector_literal
from mealie.repos import repository_recipes
from mealie.schema.group.ai_providers import AIProviderCreate, AIProviderSettingsUpdate
from mealie.schema.recipe.recipe import RecipeDraft, RecipeOut
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_step import RecipeStep
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.backups_v2.alchemy_exporter import AlchemyExporter
from mealie.services.recipe import recipe_embedding_service
from mealie.services.recipe.recipe_embedding_service import (
    EMBED_CHUNK_SIZE,
    MAX_INSTRUCTION_CHARS,
    QUERY_TIMEOUT_SECONDS,
    SEMANTIC_FALLBACK_HEADER,
    RecipeEmbeddingService,
    recipe_embedding_text,
)
from mealie.services.scheduler.tasks.embed_recipes import embed_recipes
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

KEYWORDS = ["coconut", "miso", "chocolate"]


def fake_embed(self, provider, texts: list[str]) -> list[str]:
    """One dimension per keyword, so a text is nearest to the texts that share its keywords."""
    return [vector_literal([1.0 if keyword in text.lower() else 0.01 for keyword in KEYWORDS]) for text in texts]


def test_recipe_embedding_text():
    recipe = RecipeDraft(
        name="Coconut Curry",
        description="A warming curry",
        recipe_category=[{"name": "Dinner", "slug": "dinner"}],
        tags=[{"name": "Thai", "slug": "thai"}],
        recipe_ingredient=[RecipeIngredient(note="1 can coconut milk")],
        recipe_instructions=[RecipeStep(text="Simmer. " * 1000)],
    )

    text = recipe_embedding_text(recipe)

    for expected in ["Coconut Curry", "A warming curry", "Dinner", "Thai", "1 can coconut milk", "Simmer."]:
        assert expected in text
    assert len(text) < MAX_INSTRUCTION_CHARS + 200


@pytest.fixture()
def embedding_user(unique_user: TestUser, session: Session, monkeypatch: pytest.MonkeyPatch) -> Generator[TestUser]:
    if not embeddings_available(session):
        pytest.skip("needs PostgreSQL with pgvector")

    monkeypatch.setattr(RecipeEmbeddingService, "_embed", fake_embed)
    recipe_embedding_service._query_cache.clear()

    repos = unique_user.repos
    provider = repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="test-embedding", api_key="test-key")
    )
    no_providers = AIProviderSettingsUpdate(default_provider_id=None, audio_provider_id=None, image_provider_id=None)
    repos.group_ai_provider_settings.update(
        repos.group_id, no_providers.model_copy(update={"embedding_provider_id": provider.id})
    )

    yield unique_user

    repos.group_ai_provider_settings.update(repos.group_id, no_providers)
    session.execute(sa.text(f"DELETE FROM {EMBEDDINGS_TABLE} WHERE group_id = :id"), {"id": unique_user.group_id})
    session.commit()


def create_recipe(user: TestUser, name: str) -> RecipeOut:
    return user.repos.recipes.create(RecipeDraft(user_id=user.user_id, group_id=user.group_id, name=name))


def test_sync_embeds_new_and_edited_recipes(embedding_user: TestUser):
    repos = embedding_user.repos
    already_embedded = RecipeEmbeddingService(repos).sync()  # other tests' recipes in this group

    recipe = create_recipe(embedding_user, f"coconut soup {random_string()}")
    create_recipe(embedding_user, f"miso ramen {random_string()}")

    assert RecipeEmbeddingService(repos).sync() == 2
    assert RecipeEmbeddingService(repos).sync() == 0

    recipe.description = "now with lime"
    repos.recipes.update(recipe.slug, recipe)
    assert RecipeEmbeddingService(repos).sync() == 1

    # A different model makes every embedding stale
    repos.group_ai_providers.update(
        RecipeEmbeddingService(repos).provider.id,  # type: ignore[union-attr]
        AIProviderCreate(name=random_string(), model="another-model", api_key="test-key"),
    )
    assert RecipeEmbeddingService(repos).sync() == already_embedded + 2


def rejecting_embed(rejected_word: str):
    """An embedder whose provider refuses any request that has a text containing `rejected_word`."""

    def embed(self, provider, texts: list[str]) -> list[str]:
        if any(rejected_word in text for text in texts):
            response = httpx.Response(400, request=httpx.Request("POST", "http://provider.test/embeddings"))
            raise openai.BadRequestError("input too long", response=response, body=None)
        return fake_embed(self, provider, texts)

    return embed


def test_sync_skips_recipes_the_provider_rejects(embedding_user: TestUser, monkeypatch: pytest.MonkeyPatch):
    repos = embedding_user.repos
    RecipeEmbeddingService(repos).sync(limit=10000)

    rejected_word = random_string()
    rejected = create_recipe(embedding_user, f"coconut {rejected_word}")
    create_recipe(embedding_user, f"coconut soup {random_string()}")
    monkeypatch.setattr(RecipeEmbeddingService, "_embed", rejecting_embed(rejected_word))

    # One bad recipe doesn't keep the rest of its batch from being embedded, and isn't retried
    service = RecipeEmbeddingService(repos)
    assert service.sync() == 1
    assert service.sync() == 0

    # Its name doesn't match this search, so only an embedding could have put it in the results
    query = service.embed_query("miso")
    assert query
    page = repos.recipes.page_all(PaginationQuery(page=1, per_page=-1), search="miso", semantic=query)
    assert rejected.id not in [item.id for item in page.items]

    # Until it is edited
    rejected.name = f"coconut rice {random_string()}"
    repos.recipes.update(rejected.slug, rejected)
    assert service.sync() == 1


def test_sync_fails_when_the_provider_rejects_everything(embedding_user: TestUser, monkeypatch: pytest.MonkeyPatch):
    repos = embedding_user.repos
    RecipeEmbeddingService(repos).sync(limit=10000)
    create_recipe(embedding_user, f"miso ramen {random_string()}")
    create_recipe(embedding_user, f"chocolate cake {random_string()}")

    # e.g. a chat model was picked as the embedding provider: no recipe is at fault, so none is skipped
    monkeypatch.setattr(RecipeEmbeddingService, "_embed", rejecting_embed(""))
    with pytest.raises(openai.BadRequestError):
        RecipeEmbeddingService(repos).sync()

    monkeypatch.setattr(RecipeEmbeddingService, "_embed", fake_embed)
    assert RecipeEmbeddingService(repos).sync() == 2


def test_sync_sends_small_requests(embedding_user: TestUser, monkeypatch: pytest.MonkeyPatch):
    RecipeEmbeddingService(embedding_user.repos).sync(limit=10000)
    for _ in range(EMBED_CHUNK_SIZE + 1):
        create_recipe(embedding_user, f"miso ramen {random_string()}")

    request_sizes = []

    def record_request(self, provider, texts: list[str]) -> list[str]:
        request_sizes.append(len(texts))
        return fake_embed(self, provider, texts)

    monkeypatch.setattr(RecipeEmbeddingService, "_embed", record_request)

    # A search waits behind one request at most, so no request may hold the whole batch
    assert RecipeEmbeddingService(embedding_user.repos).sync() == EMBED_CHUNK_SIZE + 1
    assert request_sizes == [EMBED_CHUNK_SIZE, 1]


def test_sync_keeps_what_was_embedded_before_a_failure(embedding_user: TestUser, monkeypatch: pytest.MonkeyPatch):
    repos = embedding_user.repos
    RecipeEmbeddingService(repos).sync(limit=10000)
    for _ in range(EMBED_CHUNK_SIZE + 1):
        create_recipe(embedding_user, f"miso ramen {random_string()}")

    requests = 0

    def fails_after_the_first_request(self, provider, texts: list[str]) -> list[str]:
        nonlocal requests
        requests += 1
        if requests > 1:
            raise TimeoutError
        return fake_embed(self, provider, texts)

    monkeypatch.setattr(RecipeEmbeddingService, "_embed", fails_after_the_first_request)
    with pytest.raises(TimeoutError):
        RecipeEmbeddingService(repos).sync()

    # Only the recipe of the failed request is left for the next run
    monkeypatch.setattr(RecipeEmbeddingService, "_embed", fake_embed)
    assert RecipeEmbeddingService(repos).sync() == 1


def test_sync_skips_recipes_without_an_owner(embedding_user: TestUser):
    repos = embedding_user.repos
    RecipeEmbeddingService(repos).sync(limit=10000)

    orphan = create_recipe(embedding_user, f"miso ramen {random_string()}")
    create_recipe(embedding_user, f"chocolate cake {random_string()}")

    def set_owner(user_id: UUID | None) -> None:
        repos.session.execute(sa.update(RecipeModel).where(RecipeModel.id == orphan.id).values(user_id=user_id))
        repos.session.commit()

    # e.g. its user was deleted. No list shows such a recipe, and it can't be read as a RecipeOut
    set_owner(None)
    try:
        assert RecipeEmbeddingService(repos).sync() == 1
    finally:
        set_owner(embedding_user.user_id)


def test_semantic_search_route_reports_fallback(
    embedding_user: TestUser, api_client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    params = {"search": random_string(), "semantic": True}
    response = api_client.get(api_routes.recipes, params=params, headers=embedding_user.token)
    assert SEMANTIC_FALLBACK_HEADER not in response.headers

    def provider_is_down(self, provider, texts: list[str]) -> list[str]:
        raise TimeoutError

    monkeypatch.setattr(RecipeEmbeddingService, "_embed", provider_is_down)
    params = {"search": random_string(), "semantic": True}
    response = api_client.get(api_routes.recipes, params=params, headers=embedding_user.token)
    assert response.status_code == 200
    assert response.headers[SEMANTIC_FALLBACK_HEADER] == "true"

    # Not asked for, so nothing fell back
    response = api_client.get(api_routes.recipes, params={"search": random_string()}, headers=embedding_user.token)
    assert SEMANTIC_FALLBACK_HEADER not in response.headers


def test_scheduled_task_embeds_recipes(embedding_user: TestUser, session: Session):
    recipe = create_recipe(embedding_user, f"chocolate cake {random_string()}")

    embed_recipes()

    session.expire_all()
    count = session.execute(
        sa.text(f"SELECT count(*) FROM {EMBEDDINGS_TABLE} WHERE recipe_id = :id"), {"id": recipe.id}
    ).scalar()
    assert count == 1


def test_semantic_search_orders_by_meaning(embedding_user: TestUser, monkeypatch: pytest.MonkeyPatch):
    # The group is shared with the other tests here, so results are checked by name, not by id
    repos = embedding_user.repos
    create_recipe(embedding_user, f"coconut soup {random_string()}")
    create_recipe(embedding_user, f"miso ramen {random_string()}")

    service = RecipeEmbeddingService(repos)
    service.sync(limit=10000)

    search = "something with coconut"
    query = service.embed_query(search)
    assert query

    page = repos.recipes.page_all(PaginationQuery(page=1, per_page=-1), search=search, semantic=query)
    is_coconut = ["coconut" in item.name for item in page.items]
    assert is_coconut[0]
    assert not is_coconut[-1]
    assert is_coconut == sorted(is_coconut, reverse=True)

    # Only the nearest few count as results
    monkeypatch.setattr(repository_recipes, "SEMANTIC_RESULT_LIMIT", 1)
    page = repos.recipes.page_all(PaginationQuery(page=1, per_page=10), search=search, semantic=query)
    assert len(page.items) == 1
    assert "coconut" in page.items[0].name
    assert page.total == 1
    assert page.total_pages == 1
    assert repos.recipes.page_all(PaginationQuery(page=2, per_page=10), search=search, semantic=query).items == []

    # The last page is the last page of those few, not of every embedded recipe
    last_page = repos.recipes.page_all(PaginationQuery(page=-1, per_page=1), search=search, semantic=query)
    assert last_page.page == 1
    assert len(last_page.items) == 1


def test_hybrid_search_also_ranks_by_name(embedding_user: TestUser):
    repos = embedding_user.repos
    unique_name = random_string(12)
    create_recipe(embedding_user, f"miso ramen {random_string()}")
    named = create_recipe(embedding_user, f"miso {unique_name}")

    service = RecipeEmbeddingService(repos)
    service.sync(limit=10000)
    not_embedded_yet = create_recipe(embedding_user, f"chocolate {unique_name}")

    def search_ids(search: str) -> list:
        query = service.embed_query(search)
        assert query
        page = repos.recipes.page_all(PaginationQuery(page=1, per_page=-1), search=search, semantic=query)
        return [item.id for item in page.items]

    # Every miso recipe is equally near in meaning, so the name decides which one is first
    assert search_ids(f"miso {unique_name}")[0] == named.id

    # A name match finds a recipe that has no embedding yet
    assert not_embedded_yet.id in search_ids(f"chocolate {unique_name}")


def test_hybrid_search_ranks_equal_names_by_meaning(embedding_user: TestUser, monkeypatch: pytest.MonkeyPatch):
    repos = embedding_user.repos
    word = random_string(12)

    def embed(self, provider, texts: list[str]) -> list[str]:
        """The higher the number after `word`, the further a text is from the search, which has no number."""
        return [
            vector_literal([1.0, int(text.removeprefix(word) or 0) / 10, 0.0])
            if text.startswith(word)
            else fake_embed(self, provider, [text])[0]
            for text in texts
        ]

    monkeypatch.setattr(RecipeEmbeddingService, "_embed", embed)

    # Furthest first, so the order they are stored in is not the order they should come back in
    furthest_first = [create_recipe(embedding_user, f"{word} {number}") for number in (3, 2, 1)]
    service = RecipeEmbeddingService(repos)
    service.sync(limit=10000)

    query = service.embed_query(word)
    assert query
    page = repos.recipes.page_all(PaginationQuery(page=1, per_page=-1), search=word, semantic=query)

    # Each name has the whole search in it, so they match it equally well and only the meaning tells them apart
    ids = [recipe.id for recipe in furthest_first]
    assert [item.id for item in page.items if item.id in ids] == ids[::-1]


def test_search_embedding_gets_a_short_timeout(embedding_user: TestUser, monkeypatch: pytest.MonkeyPatch):
    timeouts: list[int] = []

    def record_timeout(self, provider, texts: list[str]) -> list[str]:
        timeouts.append(provider.timeout)
        return fake_embed(self, provider, texts)

    monkeypatch.setattr(RecipeEmbeddingService, "_embed", record_timeout)

    service = RecipeEmbeddingService(embedding_user.repos)
    assert service.provider and service.provider.timeout > QUERY_TIMEOUT_SECONDS
    assert service.embed_query(random_string())
    assert timeouts == [QUERY_TIMEOUT_SECONDS]


def test_semantic_search_route(embedding_user: TestUser, api_client: TestClient):
    create_recipe(embedding_user, f"miso ramen {random_string()}")
    create_recipe(embedding_user, f"chocolate cake {random_string()}")
    RecipeEmbeddingService(embedding_user.repos).sync(limit=10000)

    # The text search finds nothing for this, so a result can only have come from the embedding
    params = {"search": "a MISO-flavoured dinner", "semantic": True}
    response = api_client.get(api_routes.recipes, params=params, headers=embedding_user.token)
    assert response.status_code == 200
    assert "miso" in response.json()["items"][0]["name"]

    response = api_client.get(api_routes.recipes, params=params | {"semantic": False}, headers=embedding_user.token)
    assert response.json()["items"] == []


def test_semantic_search_falls_back_without_provider(unique_user: TestUser, api_client: TestClient):
    name = random_string(20)
    recipe = create_recipe(unique_user, name)

    response = api_client.get(api_routes.recipes, params={"search": name, "semantic": True}, headers=unique_user.token)
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == [str(recipe.id)]


def test_backup_skips_embeddings(embedding_user: TestUser):
    create_recipe(embedding_user, f"coconut soup {random_string()}")
    RecipeEmbeddingService(embedding_user.repos).sync()

    dump = AlchemyExporter(get_app_settings().DB_URL).dump()  # type: ignore[arg-type]
    assert "recipes" in dump
    assert EMBEDDINGS_TABLE not in dump
