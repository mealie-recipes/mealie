"""Extracts plain text from uploaded document files, for recipe import."""

import io

import odf.teletype
import odf.text
from docx import Document
from odf.opendocument import load as load_odf
from pypdf import PdfReader
from striprtf.striprtf import rtf_to_text

from mealie.services.openai.content import extract_page_content

MIN_TEXT_LENGTH = 20
"""Below this many characters (after stripping whitespace), extracted text is treated as unreadable."""

MAX_PDF_IMAGES = 30
"""Cap on embedded images extracted from one PDF, so an oversized scan can't flood the vision API."""


class DocumentExtractionError(ValueError):
    """Raised when text can't be extracted from an uploaded document."""


class EmptyPdfTextError(DocumentExtractionError):
    """
    Raised when a PDF's text layer is empty or too short.

    Unlike other DocumentExtractionErrors, this one is specific to PDFs and recoverable: a
    scanned PDF has no text layer at all, so the caller may fall back to reading its embedded
    page images instead of failing the import outright.
    """


def _extract_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_images_from_pdf(file_bytes: bytes) -> list[tuple[str, bytes]]:
    """
    Extracts every image embedded in a PDF, in page order, as (filename, image_bytes) pairs.

    Used as a fallback for scanned PDFs, whose pages are photographs with no text layer: the
    images are meant to be handed to the same vision pipeline a photo upload would go through,
    not read with OCR.

    Iterating a malformed PDF's images can fail on the first broken one, so each image is
    retrieved independently and skipped on error rather than aborting the whole PDF. Raises
    DocumentExtractionError if there are more than MAX_PDF_IMAGES embedded images.
    """
    reader = PdfReader(io.BytesIO(file_bytes))

    images: list[tuple[str, bytes]] = []
    for page in reader.pages:
        for name in page.images.keys():  # noqa: SIM118
            if len(images) >= MAX_PDF_IMAGES:
                raise DocumentExtractionError(
                    f"This PDF has too many embedded images to process (more than {MAX_PDF_IMAGES})."
                )

            try:
                image_file_object = page.images[name]
                images.append((image_file_object.name, image_file_object.data))
            except Exception:
                continue

    return images


def _extract_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _extract_odt(file_bytes: bytes) -> str:
    document = load_odf(io.BytesIO(file_bytes))
    paragraphs = document.getElementsByType(odf.text.P)
    return "\n".join(odf.teletype.extractText(paragraph) for paragraph in paragraphs)


def _extract_plain_text(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8")


def _extract_rtf(file_bytes: bytes) -> str:
    return rtf_to_text(file_bytes.decode("utf-8", errors="replace"))


def _extract_html(file_bytes: bytes) -> str:
    text, _ = extract_page_content(file_bytes.decode("utf-8", errors="replace"))
    return text


_EXTRACTORS = {
    "pdf": _extract_pdf,
    "docx": _extract_docx,
    "odt": _extract_odt,
    "md": _extract_plain_text,
    "txt": _extract_plain_text,
    "rtf": _extract_rtf,
    "html": _extract_html,
}


def extract_text_from_document(file_bytes: bytes, filename: str) -> str:
    """
    Extracts plain text from a document file, dispatching by the filename's extension
    (case-insensitive). Supported formats: pdf, docx, odt, md, txt, rtf, html.

    Raises DocumentExtractionError if the extension is unsupported, the file can't be
    parsed, or the extracted text is empty or too short to plausibly be a recipe.
    """

    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    extractor = _EXTRACTORS.get(extension)
    if extractor is None:
        raise DocumentExtractionError(f"Unsupported file type: .{extension}" if extension else "Unsupported file type")

    try:
        text = extractor(file_bytes)
    except DocumentExtractionError:
        raise
    except Exception as e:
        raise DocumentExtractionError(
            "This file could not be read. It may be corrupted or in an unsupported format."
        ) from e

    if len(text.strip()) < MIN_TEXT_LENGTH:
        if extension == "pdf":
            raise EmptyPdfTextError(
                "This file doesn't appear to contain readable text. Scanned/image-only documents aren't supported."
            )

        raise DocumentExtractionError(
            "This file doesn't appear to contain readable text. Scanned/image-only documents aren't supported."
        )

    return text
