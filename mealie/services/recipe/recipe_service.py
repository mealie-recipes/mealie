from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from mealie.core.config import get_settings
from mealie.db.database import get_database
from mealie.db.db_setup import SessionLocal
from mealie.schema.recipe.recipe import CreateRecipe, Recipe
from mealie.schema.user.user import UserInDB
from mealie.services.events import create_recipe_event
from mealie.services.recipe.media import delete_assets

from .common_deps import CommonDeps, _read_deps, _write_deps


class RecipeService:
    recipe: Recipe

    def __init__(self, session: Session, user: UserInDB, background_tasks: BackgroundTasks = None) -> None:
        self.session = session or SessionLocal()
        self.user = user
        self.background_tasks = background_tasks
        self.recipe: Recipe = None

        # Static Globals
        self.db = get_database()
        self.settings = get_settings()

    @classmethod
    def read_existing(cls, slug: str, local_deps: CommonDeps = Depends(_read_deps)):
        """
        Used for dependency injection for routes that require an existing recipe. If the recipe doesn't exist
        or the user doens't not have the required permissions, the proper HTTP Status code will be raised.

        Args:
            slug (str): Recipe Slug used to query the database
            session (Session, optional): The Injected SQLAlchemy Session.
            user (bool, optional): The injected determination of is_logged_in.

        Raises:
            HTTPException: 404 Not Found
            HTTPException: 403 Forbidden

        Returns:
            RecipeService: The Recipe Service class with a populated recipe attribute
        """
        new_class = cls(local_deps.session, local_deps.user, local_deps.background_tasks)
        new_class.assert_existing(slug)
        return new_class

    @classmethod
    def write_existing(cls, slug: str, local_deps: CommonDeps = Depends(_write_deps)):
        """
        Used for dependency injection for routes that require an existing recipe. The only difference between
        read_existing and write_existing is that the user is required to be logged in on write_existing method.

        Args:
            slug (str): Recipe Slug used to query the database
            session (Session, optional): The Injected SQLAlchemy Session.
            user (bool, optional): The injected determination of is_logged_in.

        Raises:
            HTTPException: 404 Not Found
            HTTPException: 403 Forbidden

        Returns:
            RecipeService: The Recipe Service class with a populated recipe attribute
        """
        new_class = cls(local_deps.session, local_deps.user, local_deps.background_tasks)
        new_class.assert_existing(slug)
        return new_class

    @classmethod
    def base(cls, local_deps: CommonDeps = Depends(_write_deps)) -> Recipe:
        """A Base instance to be used as a router dependency

        Raises:
            HTTPException: 400 Bad Request

        """
        return cls(local_deps.session, local_deps.user, local_deps.background_tasks)

    def pupulate_recipe(self, slug: str) -> Recipe:
        """Populates the recipe attribute with the recipe from the database.

        Returns:
            Recipe: The populated recipe
        """
        self.recipe = self.db.recipes.get(self.session, slug)
        return self.recipe

    def assert_existing(self, slug: str):
        self.pupulate_recipe(slug)

        if not self.recipe:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if not self.recipe.settings.public and not self.user:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

    # CRUD METHODS
    def create_recipe(self, new_recipe: CreateRecipe) -> Recipe:

        try:
            create_data = Recipe(name=new_recipe.name)
            self.recipe = self.db.recipes.create(self.session, create_data)
        except IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "RECIPE_ALREADY_EXISTS"})

        self._create_event(
            "Recipe Created (URL)",
            f"'{self.recipe.name}' by {self.user.username} \n {self.settings.BASE_URL}/recipe/{self.recipe.slug}",
        )

        return self.recipe

    def delete_recipe(self) -> Recipe:
        """removes a recipe from the database and purges the existing files from the filesystem.

        Raises:
            HTTPException: 400 Bad Request

        Returns:
            Recipe: The deleted recipe
        """

        try:
            recipe: Recipe = self.db.recipes.delete(self.session, self.recipe.slug)
            delete_assets(recipe_slug=self.recipe.slug)
        except Exception:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

        self._create_event("Recipe Delete", f"'{recipe.name}' deleted by {self.user.full_name}")
        return recipe

    def _create_event(self, title: str, message: str) -> None:
        self.background_tasks.add_task(create_recipe_event, title, message, self.session)
