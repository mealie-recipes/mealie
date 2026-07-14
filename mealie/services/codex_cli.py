import asyncio
import json
from pathlib import Path

from pydantic import BaseModel

from mealie.core.config import get_app_settings
from mealie.core.dependencies.dependencies import get_temporary_path
from mealie.core.root_logger import get_logger

logger = get_logger()


class CodexCLIError(Exception):
    pass


class CodexCLIService:
    def _build_command(self, schema_path: Path, output_path: Path) -> list[str]:
        settings = get_app_settings()
        command = [
            settings.CODEX_CLI_BINARY,
            "exec",
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output_path),
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
        ]

        if settings.CODEX_CLI_MODEL:
            command.extend(["--model", settings.CODEX_CLI_MODEL])

        if settings.CODEX_CLI_PROFILE:
            command.extend(["--profile", settings.CODEX_CLI_PROFILE])

        command.append(
            "Extract one cooking recipe from the supplied source content.\n\n"
            "Rules:\n"
            "- Return data matching the supplied JSON Schema exactly.\n"
            "- Never invent an ingredient, quantity, temperature, duration, or serving count.\n"
            "- When a value is not present, use null.\n"
            "- Keep original ingredient text in originalText.\n"
            "- Parse quantity, unit, food, and note when reasonably clear.\n"
            "- If an ingredient line contains an explicit numeric, decimal, or fractional quantity, "
            "quantity must not be null.\n"
            "- If an ingredient line contains a clear unit such as tbsp, tsp, g, kg, ml, L, cup, clove, "
            "large, or small, unit must not be null.\n"
            "- If an ingredient line contains a clear ingredient name, food must not be null.\n"
            "- Convert fractions to decimal numbers only in the parsed quantity field.\n"
            "- Preserve the original measurement system.\n"
            "- Put each distinct action into a separate instruction.\n"
            "- Remove promotional text, hashtags, personal anecdotes, and calls to action.\n"
            "- Include source ambiguities or missing critical information in warnings.\n"
            "- Set confidence to low when the source does not contain a complete recipe.\n"
            "- If there is no usable recipe, return empty ingredient and instruction arrays, "
            "explain why in warnings, and set confidence to low."
        )
        return command

    async def extract_structured[T: BaseModel](self, raw_content: str, schema_model: type[T]) -> T:
        settings = get_app_settings()

        with get_temporary_path() as temp_path:
            schema_path = temp_path / "recipe-schema.json"
            output_path = temp_path / "recipe.json"
            schema_path.write_text(json.dumps(schema_model.model_json_schema(), separators=(",", ":")), encoding="utf-8")

            process = await asyncio.create_subprocess_exec(
                *self._build_command(schema_path, output_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(raw_content.encode("utf-8")),
                    timeout=settings.CODEX_CLI_TIMEOUT,
                )
            except TimeoutError as e:
                process.kill()
                await process.wait()
                raise CodexCLIError("Codex CLI recipe extraction timed out") from e

            if process.returncode != 0:
                stderr_text = stderr.decode("utf-8", errors="replace").strip()
                stdout_text = stdout.decode("utf-8", errors="replace").strip()
                logger.error(f"Codex CLI failed: {stderr_text or stdout_text}")
                raise CodexCLIError(stderr_text or stdout_text or "Codex CLI recipe extraction failed")

            try:
                response_text = output_path.read_text(encoding="utf-8")
                return schema_model.model_validate_json(response_text)
            except Exception as e:
                raise CodexCLIError("Codex CLI returned invalid recipe JSON") from e
