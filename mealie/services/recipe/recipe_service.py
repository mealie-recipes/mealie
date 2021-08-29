from pathlib import Path
from shutil import copytree, rmtree
from typing import Union

from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_dirs, get_settings
from mealie.core.dependencies import ReadDeps
from mealie.core.dependencies.grouped import WriteDeps
from mealie.core.root_logger import get_logger
from mealie.db.database import get_database
from mealie.db.db_setup import SessionLocal
from mealie.schema.recipe.recipe import CreateRecipe, Recipe
from mealie.schema.user.user import UserInDB
from mealie.services.events import create_recipe_event

logger = get_logger(module=__name__)


class RecipeService:
    """
    Class Methods:
        `read_existing`: Reads an existing recipe from the database.
        `write_existing`: Updates an existing recipe in the database.
        `base`: Requires write permissions, but doesn't perform recipe checks
    """

    recipe: Recipe  # Required for proper type hints

    def __init__(self, session: Session, user: UserInDB, background_tasks: BackgroundTasks = None) -> None:
        self.session = session or SessionLocal()
        self.user = user
        self.background_tasks = background_tasks
        self.recipe: Recipe = None

        # Static Globals Dependency Injection
        self.db = get_database()
        self.app_dirs = get_app_dirs()
        self.settings = get_settings()

    @classmethod
    def read_existing(cls, slug: str, deps: ReadDeps = Depends()):
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
        new_class = cls(deps.session, deps.user, deps.background_tasks)
        new_class.assert_existing(slug)
        return new_class

    @classmethod
    def write_existing(cls, slug: str, deps: WriteDeps = Depends()):
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
        new_class = cls(deps.session, deps.user, deps.background_tasks)
        new_class.assert_existing(slug)
        return new_class

    @classmethod
    def base(cls, deps: WriteDeps = Depends()) -> Recipe:
        """A Base instance to be used as a router dependency

        Raises:
            HTTPException: 400 Bad Request

        """
        return cls(deps.session, deps.user, deps.background_tasks)

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
    def create_recipe(self, create_data: Union[Recipe, CreateRecipe]) -> Recipe:
        if isinstance(create_data, CreateRecipe):
            create_data = Recipe(name=create_data.name)

        try:
            self.recipe = self.db.recipes.create(self.session, create_data)
        except IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "RECIPE_ALREADY_EXISTS"})

        self._create_event(
            "Recipe Created (URL)",
            f"'{self.recipe.name}' by {self.user.username} \n {self.settings.BASE_URL}/recipe/{self.recipe.slug}",
        )

        return self.recipe

    def update_recipe(self, update_data: Recipe) -> Recipe:
        original_slug = self.recipe.slug

        try:
            self.recipe = self.db.recipes.update(self.session, original_slug, update_data)
        except IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "RECIPE_ALREADY_EXISTS"})

        self._check_assets(original_slug)

        return self.recipe

    def patch_recipe(self, patch_data: Recipe) -> Recipe:
        original_slug = self.recipe.slug

        try:
            self.recipe = self.db.recipes.patch(
                self.session, original_slug, patch_data.dict(exclude_unset=True, exclude_defaults=True)
            )
        except IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": "RECIPE_ALREADY_EXISTS"})

        self._check_assets(original_slug)

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
            self._delete_assets()
        except Exception:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

        self._create_event("Recipe Delete", f"'{recipe.name}' deleted by {self.user.full_name}")
        return recipe

    def _create_event(self, title: str, message: str) -> None:
        self.background_tasks.add_task(create_recipe_event, title, message, self.session)

    def _check_assets(self, original_slug: str) -> None:
        """Checks if the recipe slug has changed, and if so moves the assets to a new file with the new slug."""
        if original_slug != self.recipe.slug:
            current_dir = self.app_dirs.RECIPE_DATA_DIR.joinpath(original_slug)

            try:
                copytree(current_dir, self.recipe.directory, dirs_exist_ok=True)
                logger.info(f"Renaming Recipe Directory: {original_slug} -> {self.recipe.slug}")
            except FileNotFoundError:
                logger.error(f"Recipe Directory not Found: {original_slug}")

        all_asset_files = [x.file_name for x in self.recipe.assets]

        for file in self.recipe.asset_dir.iterdir():
            file: Path
            if file.is_dir():
                continue
            if file.name not in all_asset_files:
                file.unlink()

    def _delete_assets(self) -> None:
        recipe_dir = self.recipe.directory
        rmtree(recipe_dir, ignore_errors=True)
        logger.info(f"Recipe Directory Removed: {self.recipe.slug}")
