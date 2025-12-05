from zipfile import ZipFile

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.orm.session import Session
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from mealie.core.dependencies import get_temporary_zip_path
from mealie.core.root_logger import get_logger
from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe_image_types import RecipeImageTypes
from mealie.schema.response import ErrorResponse

router = APIRouter()

logger = get_logger()


@router.get("/shared/{token_id}", response_model=Recipe)
def get_shared_recipe(token_id: UUID4, session: Session = Depends(generate_session)) -> Recipe:
    db = get_repositories(session, group_id=None, household_id=None)

    token_summary = db.recipe_share_tokens.get_one(token_id)
    if token_summary and token_summary.is_expired:
        try:
            db.recipe_share_tokens.delete(token_id)
            session.commit()
        except Exception:
            logger.exception(f"Failed to delete expired token {token_id}")
            session.rollback()
        token_summary = None

    if token_summary is None:
        raise HTTPException(status_code=404, detail=ErrorResponse.respond("Token Not Found"))

    return token_summary.recipe


@router.get("/shared/{token_id}/zip", response_class=FileResponse)
def get_shared_recipe_as_zip(token_id: UUID4, session: Session = Depends(generate_session)) -> FileResponse:
    """Get a recipe and its original image as a Zip file"""

    recipe = get_shared_recipe(token_id=token_id, session=session)
    image_asset = recipe.image_dir.joinpath(RecipeImageTypes.original.value)

    with get_temporary_zip_path(auto_unlink=False) as temp_path:
        with ZipFile(temp_path, "w") as myzip:
            myzip.writestr(f"{recipe.slug}.json", recipe.model_dump_json())

            if image_asset.is_file():
                myzip.write(image_asset, arcname=image_asset.name)

        return FileResponse(
            temp_path, filename=f"{recipe.slug}.zip", background=BackgroundTask(temp_path.unlink, missing_ok=True)
        )
