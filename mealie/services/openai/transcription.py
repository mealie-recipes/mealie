import functools
import re
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TypedDict

import yt_dlp
from yt_dlp.extractor.generic import GenericIE

from mealie.core import exceptions
from mealie.core.root_logger import get_logger

from .openai import OpenAIService

SUBTITLE_LANGS = ["en", "fr", "es", "de", "it"]

logger = get_logger()


class TranscribedAudio(TypedDict):
    audio: Path
    subtitle: Path | None
    title: str
    description: str
    thumbnail_url: str | None
    transcription: str


@functools.cache
def get_yt_dlp_extractors() -> list:
    """Build and cache the yt-dlp extractor list once per process lifetime."""
    return [ie for ie in yt_dlp.extractor.gen_extractors() if ie.working() and not isinstance(ie, GenericIE)]


def is_video_url(url: str) -> bool:
    """Whether yt-dlp recognizes the URL as something it can download."""

    if not url:
        return False

    return any(ie.suitable(url) for ie in get_yt_dlp_extractors())


def parse_subtitle_content(subtitle_content: str) -> str:
    # TODO: is there a better way to parse subtitles that's more efficient?

    lines = []
    for line in subtitle_content.split("\n"):
        if line.strip() and not line.startswith("WEBVTT") and "-->" not in line and not line.isdigit():
            lines.append(line.strip())

    raw_content = " ".join(lines)
    content = re.sub(r"<[^>]+>", "", raw_content)
    return content


def download_video(url: str, temp_path: Path) -> TranscribedAudio:
    """Downloads audio and subtitles from a video URL."""

    output_template = temp_path / "mealie"  # No extension here

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_template) + ".%(ext)s",
        "quiet": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": SUBTITLE_LANGS,
        "skip_download": False,
        "ignoreerrors": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "32",
            }
        ],
        "postprocessor_args": ["-ac", "1"],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if info is None:
                raise exceptions.VideoDownloadError(
                    "Failed to extract video information. The video may be unavailable or the URL is invalid."
                )

            sub_path = None
            for lang in SUBTITLE_LANGS:
                potential_path = output_template.with_suffix(f".{lang}.vtt")
                if potential_path.exists():
                    sub_path = potential_path
                    break

            return {
                "audio": output_template.with_suffix(".mp3"),
                "subtitle": sub_path,
                "title": info.get("title", ""),
                "description": info.get("description", ""),
                "thumbnail_url": info.get("thumbnail") or None,
                "transcription": "",
            }
    except exceptions.VideoDownloadError:
        raise
    except Exception as e:
        raise exceptions.VideoDownloadError(f"Failed to download video: {e}") from e


def read_subtitles(video_data: TranscribedAudio) -> str:
    """Reads the downloaded subtitle file, if there is one. Returns an empty string on failure."""

    subtitle_path = video_data["subtitle"]
    if not subtitle_path:
        return ""

    try:
        with open(subtitle_path, encoding="utf-8") as f:
            subtitle_content = f.read()

        logger.info("Using subtitles from video instead of transcription")
        return parse_subtitle_content(subtitle_content)
    except Exception:
        logger.exception("Failed to read subtitles, falling back to transcription")
        return ""


async def resolve_transcription(
    video_data: TranscribedAudio,
    openai_service: OpenAIService,
    before_transcribe: Callable[[], Awaitable[None]] | None = None,
) -> str:
    """
    Resolves a video's transcript, preferring one that's already known, then its subtitles,
    and falling back to transcribing the audio with AI. `before_transcribe` is awaited only
    if that fallback is needed.
    """

    if video_data["transcription"]:
        return video_data["transcription"]

    if subtitles := read_subtitles(video_data):
        return subtitles

    if before_transcribe:
        await before_transcribe()

    try:
        transcript = await openai_service.transcribe_audio(video_data["audio"])
    except exceptions.RateLimitError:
        raise
    except Exception as e:
        raise exceptions.OpenAIServiceError(f"Failed to transcribe audio: {e}") from e

    if not transcript:
        raise exceptions.OpenAIServiceError("No transcription returned from OpenAI")

    return transcript
