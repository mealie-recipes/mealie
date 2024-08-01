from textwrap import dedent

from pydantic import Field

from ._base import OpenAIBase


class OpenAIRecipeIngredient(OpenAIBase):
    title: str | None = Field(
        None,
        description=dedent(
            """
            The title of the section of the recipe that the ingredient is found in. Recipes may not specify
            ingredient sections, in which case this should be left blank.
            Only the first item in the section should have this set,
            whereas subsuquent items should have their titles left blank (unless they start a new section).
            """
        ),
    )

    text: str = Field(
        ...,
        description=dedent(
            """
            The text of the ingredient. This should represent the entire ingredient, such as "1 cup of flour" or
            "2 cups of onions, chopped". If the ingredient is completely blank, skip it and do not add the ingredient,
            since this field is required.

            If the ingredient has no text, but has a title, include the title on the
            next ingredient instead.
            """
        ),
    )


class OpenAIRecipeInstruction(OpenAIBase):
    title: str | None = Field(
        None,
        description=dedent(
            """
            The title of the section of the recipe that the instruction is found in. Recipes may not specify
            instruction sections, in which case this should be left blank.
            Only the first instruction in the section should have this set,
            whereas subsuquent instructions should have their titles left blank (unless they start a new section).
            """
        ),
    )

    text: str = Field(
        ...,
        description=dedent(
            """
            The text of the instruction. This represents one step in the recipe, such as "Preheat the oven to 350",
            or "Sauté the onions for 20 minutes". Sometimes steps can be longer, such as "Bring a large pot of lightly
            salted water to a boil. Add ditalini pasta and cook for 8 minutes or until al dente; drain.".

            Sometimes, but not always, recipes will include their number in front of the text, such as
            "1.", "2.", or "Step 1", "Step 2", or "First", "Second". In the case where they are directly numbered
            ("1.", "2.", "Step one", "Step 1", "Step two", "Step 2", etc.), you should not include the number in
            the text. However, if they use words ("First", "Second", etc.), then those should be included.

            If the instruction is completely blank, skip it and do not add the instruction, since this field is
            required. If the ingredient has no text, but has a title, include the title on the next
            instruction instead.
            """
        ),
    )


class OpenAIRecipeNotes(OpenAIBase):
    title: str | None = Field(
        None,
        description=dedent(
            """
            The title of the note. Notes may not specify a title, and just have a body of text. In this case,
            title should be left blank, and all content should go in the note text. If the note title is just
            "note" or "info", you should ignore it and leave the title blank.
            """
        ),
    )

    text: str = Field(
        ...,
        description=dedent(
            """
            The text of the note. This should represent the entire note, such as "This recipe is great for
            a summer picnic" or "This recipe is a family favorite". They may also include additional prep
            instructions such as "to make this recipe gluten free, use gluten free flour", or "you may prepare
            the dough the night before and refrigerate it until ready to bake".

            If the note is completely blank, skip it and do not add the note, since this field is required.
            """
        ),
    )


class OpenAIRecipe(OpenAIBase):
    name: str = Field(
        ...,
        description=dedent(
            """
            The name or title of the recipe. If you're unable to determine the name of the recipe, you should
            make your best guess based upon the ingredients and instructions provided.
            """
        ),
    )

    description: str | None = Field(
        ...,
        description=dedent(
            """
            A long description of the recipe. This should be a string that describes the recipe in a few words
            or sentences. If the recipe doesn't have a description, you should return None.
            """
        ),
    )

    recipe_yield: str | None = Field(
        None,
        description=dedent(
            """
            The yield of the recipe. For instance, if the recipe makes 12 cookies, the yield is "12 cookies".
            If the recipe makes 2 servings, the yield is "2 servings". Typically yield consists of a number followed
            by the word "serving" or "servings", but it can be any string that describes the yield. If the yield
            isn't specified, you should return None.
            """
        ),
    )

    total_time: str | None = Field(
        None,
        description=dedent(
            """
            The total time it takes to make the recipe. This should be a string that describes a duration of time,
            such as "1 hour and 30 minutes", "90 minutes", or "1.5 hours". If the recipe has multiple times, choose
            the longest time. If the recipe doesn't specify a total time or duration, or it specifies a prep time or
            perform time but not a total time, you should return None. Do not duplicate times between total time, prep
            time and perform time.
            """
        ),
    )

    prep_time: str | None = Field(
        None,
        description=dedent(
            """
            The time it takes to prepare the recipe. This should be a string that describes a duration of time,
            such as "30 minutes", "1 hour", or "1.5 hours". If the recipe has a total time, the prep time should be
            less than the total time. If the recipe doesn't specify a prep time, you should return None. If the recipe
            supplies only one time, it should be the total time. Do not duplicate times between total time, prep
            time and coperformok time.
            """
        ),
    )

    perform_time: str | None = Field(
        None,
        description=dedent(
            """
            The time it takes to cook the recipe. This should be a string that describes a duration of time,
            such as "30 minutes", "1 hour", or "1.5 hours". If the recipe has a total time, the perform time should be
            less than the total time. If the recipe doesn't specify a perform time, you should return None. If the
            recipe specifies a cook time, active time, or other time besides total or prep, you should use that
            time as the perform time. If the recipe supplies only one time, it should be the total time, and not the
            perform time. Do not duplicate times between total time, prep time and perform time.
            """
        ),
    )

    ingredients: list[OpenAIRecipeIngredient] = Field(
        [],
        description=dedent(
            """
            A list of ingredients used in the recipe. Ingredients should be inserted in the order they appear in the
            recipe. If the recipe has no ingredients, you should return an empty list.

            Often times, but not always, ingredients are separated by line breaks. Use these as a guide to
            separate ingredients.
            """
        ),
    )

    instructions: list[OpenAIRecipeInstruction] = Field(
        [],
        description=dedent(
            """
            A list of ingredients used in the recipe. Ingredients should be inserted in the order they appear in the
            recipe. If the recipe has no ingredients, you should return an empty list.

            Often times, but not always, instructions are separated by line breaks and/or separated by paragraphs.
            Use these as a guide to separate instructions. They also may be separated by numbers or words, such as
            "1.", "2.", "Step 1", "Step 2", "First", "Second", etc.
            """
        ),
    )

    notes: list[OpenAIRecipeNotes] = Field(
        [],
        description=dedent(
            """
            A list of notes found in the recipe. Notes should be inserted in the order they appear in the recipe.
            They may appear anywhere on the recipe, though they are typically found under the instructions.
            """
        ),
    )
