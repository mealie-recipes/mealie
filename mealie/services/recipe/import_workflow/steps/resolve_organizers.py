from mealie.schema.openai.organizers import OpenAIOrganizers
from mealie.services.openai import OpenAIDataInjection
from mealie.services.openai.content import truncate_source_content

from ...organizer_resolver import OrganizerResolver
from ..base import WorkflowStep
from ..context import WorkflowContext

RESOLVE_ORGANIZERS_PROMPT = "recipes.resolve-organizers"

MAX_INJECTED_TAGS = 200
"""
Tag collections can get large, and every name costs tokens. Injecting a subset only weakens the
model's ability to echo an existing name back; the resolver still matches against all of them.
"""


class ResolveOrganizersStep(WorkflowStep):
    """
    Assigns tags, categories, and tools to the draft recipe, matching against the group's
    existing organizers and optionally creating the ones that don't exist yet.
    """

    name = "resolve-organizers"
    progress_key = "recipe.create-progress.organizing-recipe"
    required = False

    def _build_injections(self, resolver: OrganizerResolver) -> list[OpenAIDataInjection]:
        existing = resolver.existing_names()
        injections: list[OpenAIDataInjection] = []

        if tags := existing["tags"][:MAX_INJECTED_TAGS]:
            injections.append(
                OpenAIDataInjection(
                    description=(
                        "Below are the tags that already exist in the user's collection. Prefer these over "
                        "suggesting new ones, and return them exactly as they are written here."
                    ),
                    value=tags,
                )
            )

        if categories := existing["categories"]:
            injections.append(
                OpenAIDataInjection(
                    description=(
                        "Below are the categories that already exist in the user's collection. Prefer these "
                        "over suggesting new ones, and return them exactly as they are written here."
                    ),
                    value=categories,
                )
            )

        if tools := existing["tools"]:
            injections.append(
                OpenAIDataInjection(
                    description=(
                        "Below are the tools that already exist in the user's collection. Prefer these over "
                        "suggesting new ones, and return them exactly as they are written here."
                    ),
                    value=tools,
                )
            )

        return injections

    @staticmethod
    def _build_message(ctx: WorkflowContext) -> str:
        if ctx.compiled_source and ctx.compiled_source.content.strip():
            return truncate_source_content(ctx.compiled_source.content)

        recipe = ctx.draft_recipe
        if not recipe:
            return ""

        message_parts = [f"Name: {recipe.name}"]
        if recipe.description:
            message_parts.append(f"Description: {recipe.description}")

        if ingredients := [ingredient.note for ingredient in recipe.recipe_ingredient if ingredient.note]:
            message_parts.append("Ingredients:\n" + "\n".join(ingredients))

        if instructions := [step.text for step in recipe.recipe_instructions or [] if step.text]:
            message_parts.append("Instructions:\n" + "\n".join(instructions))

        return truncate_source_content("\n\n".join(message_parts))

    def should_run(self, ctx: WorkflowContext) -> bool:
        return ctx.options.resolve_organizers

    async def run(self, ctx: WorkflowContext) -> None:
        recipe = ctx.draft_recipe
        if not recipe:
            return

        resolver = OrganizerResolver(ctx.repos)
        create_missing = ctx.options.create_new_organizers

        existing = resolver.existing_names()
        if ctx.options.attach_organizers and not (create_missing or any(existing.values())):
            # nothing to match against and nothing may be created, so there's no work to do
            return

        response = await ctx.ai.get_response(
            ctx.ai.get_prompt(RESOLVE_ORGANIZERS_PROMPT, data_injections=self._build_injections(resolver)),
            self._build_message(ctx),
            response_schema=OpenAIOrganizers,
        )

        if not response:
            return

        ctx.organizer_names = response
        if not ctx.options.attach_organizers:
            # the caller applies these itself
            return

        recipe.tags = resolver.resolve_tags(response.tags, create_missing)
        recipe.recipe_category = resolver.resolve_categories(response.categories, create_missing)
        recipe.tools = resolver.resolve_tools(response.tools, create_missing)
