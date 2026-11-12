from shutil import rmtree

from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from mealie.core.dependencies import get_temporary_path
from mealie.services.recipe.recipe_pdf_service import RecipePdfRenderer


def pdf_file_response(renderer: RecipePdfRenderer, slug: str) -> FileResponse:
    """Writes an already-rendered PDF to a temporary file and streams it as `<slug>.pdf`."""
    with get_temporary_path(auto_unlink=False) as temp_path:
        # A slug is user data, so only the download name uses it; the path on disk never does.
        try:
            file = renderer.output(temp_path / "export.pdf")
        except Exception:
            rmtree(temp_path)
            raise

        # The file must outlive this request handler, so cleanup runs after the response is sent.
        return FileResponse(
            file,
            media_type="application/pdf",
            filename=f"{slug}.pdf",
            background=BackgroundTask(rmtree, temp_path),
        )
