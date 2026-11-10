from pathlib import Path

import pypdfium2 as pdfium

PDF_MAGIC = b"%PDF-"


def is_pdf(path: Path) -> bool:
    with path.open("rb") as f:
        return f.read(len(PDF_MAGIC)) == PDF_MAGIC


def render_pdf(path: Path, *, max_pages: int = 10, scale: float = 2.0) -> tuple[list[Path], str]:
    """
    Renders each page of a PDF to a PNG file next to the PDF and extracts the text layer.

    Returns the image paths and the text of all pages. The text is empty for a scanned PDF.
    """
    images: list[Path] = []
    texts: list[str] = []

    pdf = pdfium.PdfDocument(path)
    try:
        for index in range(min(len(pdf), max_pages)):
            page = pdf[index]
            try:
                image_path = path.with_name(f"{path.stem}-page-{index + 1}.png")
                page.render(scale=scale).to_pil().save(image_path)
                images.append(image_path)

                textpage = page.get_textpage()
                try:
                    text = textpage.get_text_bounded().strip()
                finally:
                    textpage.close()
                if text:
                    texts.append(text)
            finally:
                page.close()
    finally:
        pdf.close()

    return images, "\n\n".join(texts)
