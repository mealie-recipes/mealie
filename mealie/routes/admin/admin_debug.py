import os
import shutil
from pathlib import Path

from fastapi import APIRouter, File, UploadFile
from pydantic import UUID4

from mealie.core.dependencies.dependencies import get_temporary_path
from mealie.routes._base import BaseAdminController, controller
from mealie.schema.admin.debug import DebugResponse
from mealie.schema.openai.general import OpenAIText
from mealie.services.openai import OpenAILocalImage, OpenAIService

router = APIRouter(prefix="/debug")


@controller(router)
class AdminDebugController(BaseAdminController):
    @router.post("/openai/{provider_id}", response_model=DebugResponse)
    async def debug_openai(self, provider_id: UUID4, image: UploadFile | None = File(None)):
        provider = self.repos.group_ai_providers.get_one(provider_id)
        if not provider:
            return DebugResponse(success=False, response="Provider not found")

        with get_temporary_path() as temp_path:
            if image:
                if not image.filename:
                    return DebugResponse(success=False, response="Invalid image filename")
                safe_filename = Path(image.filename).name
                local_image_path = temp_path.joinpath(safe_filename)
                with local_image_path.open("wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                local_images = [OpenAILocalImage(filename=os.path.basename(local_image_path), path=local_image_path)]
            else:
                local_images = None

            try:
                openai_service = OpenAIService(self.repos)
                prompt = openai_service.get_prompt("general.debug")

                message = "Hello, checking to see if I can reach you."
                if local_images:
                    message = f"{message} Here is an image to test with:"

                response = await openai_service.get_response(
                    prompt, message, response_schema=OpenAIText, attachments=local_images, provider=provider
                )

                if not response:
                    raise Exception("No response received from OpenAI")

                return DebugResponse(success=True, response=f'OpenAI is working. Response: "{response.text}"')

            except Exception as e:
                self.logger.exception(e)
                return DebugResponse(
                    success=False,
                    response=f'OpenAI request failed. Full error has been logged. {e.__class__.__name__}: "{e}"',
                )
