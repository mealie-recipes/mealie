from settings import USE_MONGO, USE_SQL

from db.db_base import BaseDocument
from db.mongo.recipe_models import RecipeDocument
from db.sql.db_session import create_session
from db.sql.recipe_models import (
    ApiExtras,
    Note,
    RecipeIngredient,
    RecipeInstruction,
    RecipeModel,
    Tag,
)


class _Recipes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        if USE_SQL:
            self.sql_model = RecipeModel
        else:
            self.document = RecipeDocument

    def save_new_sql(self, recipe_data: dict):
        session = create_session()
        new_recipe: RecipeModel = self.sql_model()
        new_recipe.name = recipe_data.get("name")
        new_recipe.description = recipe_data.get("description")
        new_recipe.image = recipe_data.get("image")
        new_recipe.totalTime = recipe_data.get("totalTime")
        new_recipe.slug = recipe_data.get("slug")
        new_recipe.rating = recipe_data.get("rating")
        new_recipe.orgURL = recipe_data.get("orgURL")
        new_recipe.dateAdded = recipe_data.get("dateAdded")
        new_recipe.recipeYield = recipe_data.get("recipeYield")

        for ingredient in recipe_data.get("recipeIngredient"):
            new_ingredient = RecipeIngredient()
            new_ingredient.ingredient = ingredient
            new_recipe.recipeIngredient.append(new_ingredient)

        for step in recipe_data.get("recipeInstructions"):
            new_step = RecipeInstruction()
            new_step.type = "Step"
            new_step.text = step.get("text")
            new_recipe.recipeInstructions.append(new_step)

        try:
            for tag in recipe_data.get("tags"):
                new_tag = Tag()
                new_tag.name = tag
                new_recipe.tags.append(new_tag)
        except:
            pass

        try:
            for category in recipe_data.get("category"):
                new_category = Tag()
                new_category.name = category
                new_recipe.categories.append(new_category)
        except:
            pass

        try:
            new_recipe.notes = recipe_data.get("name")
            for note in recipe_data.get("notes"):
                new_note = Note()
                new_note.title = note.get("title")
                new_note.text = note.get("text")
                new_recipe.notes.append(note)
        except:
            pass

        try:
            for key, value in recipe_data.get("extras").items():
                new_extra = ApiExtras()
                new_extra.key = key
                new_extra.key = value
                new_recipe.extras.append(new_extra)
        except:
            pass

        session.add(new_recipe)
        session.commit()

        return recipe_data

    def update(self, slug: str, new_data: dict) -> None:
        if USE_MONGO:
            document = self.document.objects.get(slug=slug)

            if document:
                document.update(set__name=new_data.get("name"))
                document.update(set__description=new_data.get("description"))
                document.update(set__image=new_data.get("image"))
                document.update(set__recipeYield=new_data.get("recipeYield"))
                document.update(set__recipeIngredient=new_data.get("recipeIngredient"))
                document.update(
                    set__recipeInstructions=new_data.get("recipeInstructions")
                )
                document.update(set__totalTime=new_data.get("totalTime"))

                document.update(set__slug=new_data.get("slug"))
                document.update(set__categories=new_data.get("categories"))
                document.update(set__tags=new_data.get("tags"))
                document.update(set__notes=new_data.get("notes"))
                document.update(set__orgURL=new_data.get("orgURL"))
                document.update(set__rating=new_data.get("rating"))
                document.update(set__extras=new_data.get("extras"))
                document.save()

                return new_data.get("slug")
        elif USE_SQL:
            pass

    def update_image(self, slug: str, extension: str) -> None:
        if USE_MONGO:
            document = self.document.objects.get(slug=slug)

            if document:
                document.update(set__image=f"{slug}.{extension}")
        elif USE_SQL:
            pass
