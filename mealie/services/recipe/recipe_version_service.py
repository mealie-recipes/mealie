"""Recipe version history: snapshot creation, diff computation, and restore."""

import json
import logging
from typing import Any

from pydantic import UUID4
from sqlalchemy import func, select

from mealie.db.models.recipe.recipe_version import RecipeVersion
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_version import (
    FieldDiff,
    IngredientDiff,
    InstructionDiff,
    RecipeDiff,
    RecipeVersionOut,
    RecipeVersionSummary,
)

logger = logging.getLogger(__name__)

# Fields to include in the snapshot (exclude volatile/computed/binary fields)
_SNAPSHOT_FIELDS = {
    "name",
    "description",
    "recipe_yield",
    "recipe_yield_quantity",
    "recipe_servings",
    "total_time",
    "prep_time",
    "cook_time",
    "perform_time",
    "org_url",
    "recipe_ingredient",
    "recipe_instructions",
    "recipe_category",
    "tags",
    "tools",
    "nutrition",
    "settings",
    "notes",
    "extras",
}

# Simple fields to diff (display label → field name)
_SIMPLE_DIFF_FIELDS = {
    "name": "Name",
    "description": "Description",
    "recipe_yield": "Yield",
    "recipe_yield_quantity": "Yield Quantity",
    "recipe_servings": "Servings",
    "total_time": "Total Time",
    "prep_time": "Prep Time",
    "cook_time": "Cook Time",
    "perform_time": "Perform Time",
    "org_url": "Source URL",
}


def _serialize_recipe(recipe: Recipe) -> str:
    """Serialize a recipe to a JSON snapshot."""
    data = recipe.model_dump(mode="json")
    # Keep only the snapshot fields
    snapshot = {k: v for k, v in data.items() if k in _SNAPSHOT_FIELDS}
    return json.dumps(snapshot, default=str, ensure_ascii=False)


def _ingredient_to_text(ing: dict) -> str:
    """Convert an ingredient dict to a human-readable string."""
    parts = []
    if ing.get("quantity"):
        q = ing["quantity"]
        parts.append(str(int(q)) if q == int(q) else str(q))
    if ing.get("unit") and ing["unit"].get("name"):
        parts.append(ing["unit"]["name"])
    if ing.get("food") and ing["food"].get("name"):
        parts.append(ing["food"]["name"])
    if ing.get("note"):
        if parts:
            parts.append(f"- {ing['note']}")
        else:
            parts.append(ing["note"])
    if ing.get("title"):
        return f"[{ing['title']}]"
    return " ".join(p for p in parts if p).strip() or ing.get("original_text", "")


def _instruction_to_text(step: dict) -> str:
    """Convert an instruction dict to text."""
    text = step.get("text", "")
    if step.get("title"):
        return f"[{step['title']}] {text}"
    return text


def _normalize_value(val: Any) -> str:
    """Normalize a value for comparison — treat None, empty, 0, 0.0 as equivalent."""
    if val is None:
        return ""
    if isinstance(val, float) and val == 0.0:
        return ""
    if isinstance(val, int) and val == 0:
        return ""
    s = str(val).strip()
    return s if s != "None" else ""


def _compute_diff(old_data: dict, new_data: dict) -> RecipeDiff:
    """Compute a structured diff between two recipe snapshots."""
    diff = RecipeDiff()

    # 1. Simple field diffs
    for field, label in _SIMPLE_DIFF_FIELDS.items():
        old_val = _normalize_value(old_data.get(field))
        new_val = _normalize_value(new_data.get(field))
        if old_val != new_val:
            diff.fields_changed.append(FieldDiff(
                field_name=field,
                label=label,
                old_value=old_val or None,
                new_value=new_val or None,
            ))

    # 2. Ingredient diffs (set-based to handle reordering)
    old_ings = old_data.get("recipe_ingredient") or []
    new_ings = new_data.get("recipe_ingredient") or []
    old_texts = [t for t in (_ingredient_to_text(i) or "" for i in old_ings) if t]
    new_texts = [t for t in (_ingredient_to_text(i) or "" for i in new_ings) if t]

    old_set = set(old_texts)
    new_set = set(new_texts)
    diff.ingredients_removed = sorted(old_set - new_set)
    diff.ingredients_added = sorted(new_set - old_set)
    # No "changed" items — ingredients are either present or not

    # 3. Instruction diffs (set-based to handle reordering)
    old_steps = old_data.get("recipe_instructions") or []
    new_steps = new_data.get("recipe_instructions") or []
    old_step_texts = [t for t in (_instruction_to_text(s) or "" for s in old_steps) if t.strip()]
    new_step_texts = [t for t in (_instruction_to_text(s) or "" for s in new_steps) if t.strip()]

    old_step_set = set(old_step_texts)
    new_step_set = set(new_step_texts)
    diff.instructions_removed = sorted(old_step_set - new_step_set)
    diff.instructions_added = sorted(new_step_set - old_step_set)

    # 4. Category/tag diffs
    old_cats = {c.get("name", c.get("slug", "")) for c in (old_data.get("recipe_category") or [])}
    new_cats = {c.get("name", c.get("slug", "")) for c in (new_data.get("recipe_category") or [])}
    diff.categories_added = sorted(new_cats - old_cats)
    diff.categories_removed = sorted(old_cats - new_cats)

    old_tags = {t.get("name", t.get("slug", "")) for t in (old_data.get("tags") or [])}
    new_tags = {t.get("name", t.get("slug", "")) for t in (new_data.get("tags") or [])}
    diff.tags_added = sorted(new_tags - old_tags)
    diff.tags_removed = sorted(old_tags - new_tags)

    return diff


class RecipeVersionService:
    def __init__(self, repos: AllRepositories) -> None:
        self.repos = repos
        self.session = repos.session

    def _get_next_version_number(self, recipe_id: UUID4) -> int:
        """Get the next version number for a recipe."""
        stmt = select(func.coalesce(func.max(RecipeVersion.version_number), 0)).where(
            RecipeVersion.recipe_id == recipe_id
        )
        result = self.session.execute(stmt).scalar()
        return (result or 0) + 1

    def save_snapshot(self, recipe: Recipe, user_id: UUID4 | None = None) -> RecipeVersion | None:
        """Create a version snapshot of the current recipe state."""
        try:
            snapshot = _serialize_recipe(recipe)
            version_number = self._get_next_version_number(recipe.id)

            version = RecipeVersion(
                session=self.session,
                recipe_id=recipe.id,
                user_id=user_id,
                group_id=recipe.group_id,
                version_number=version_number,
                name=recipe.name or "",
                snapshot=snapshot,
            )
            self.session.add(version)
            self.session.commit()
            self.session.refresh(version)

            logger.info("Saved recipe version %d for '%s'", version_number, recipe.name)
            return version
        except Exception:
            self.session.rollback()
            logger.exception("Failed to save recipe version for '%s'", recipe.name)
            return None

    def get_versions(self, recipe_id: UUID4) -> list[RecipeVersionSummary]:
        """List all versions for a recipe (no snapshots)."""
        stmt = (
            select(RecipeVersion)
            .where(RecipeVersion.recipe_id == recipe_id)
            .order_by(RecipeVersion.version_number.desc())
        )
        results = self.session.execute(stmt).scalars().all()
        return [RecipeVersionSummary.model_validate(v) for v in results]

    def get_version(self, version_id: UUID4) -> RecipeVersionOut | None:
        """Get a single version with its snapshot."""
        stmt = select(RecipeVersion).where(RecipeVersion.id == version_id)
        result = self.session.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return RecipeVersionOut.model_validate(result)

    def compute_diff(self, version_id: UUID4, compare_to: str = "current", current_recipe: Recipe | None = None) -> RecipeDiff | None:
        """Compute diff between a version and another version or current state."""
        version = self.get_version(version_id)
        if version is None:
            return None

        old_data = json.loads(version.snapshot)

        if compare_to == "current" and current_recipe:
            new_data = json.loads(_serialize_recipe(current_recipe))
        elif compare_to != "current":
            other_version = self.get_version(UUID4(compare_to))
            if other_version is None:
                return None
            new_data = json.loads(other_version.snapshot)
        else:
            return None

        diff = _compute_diff(old_data, new_data)
        diff.version_id = version_id
        diff.compare_to = compare_to
        return diff
