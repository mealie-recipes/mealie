from pathlib import Path

from fpdf import FPDF
from PIL import Image

from mealie.pkgs.img.pdf import is_pdf, render_pdf
from mealie.services.recipe.ai_recipe_service import AIRecipeService


def _make_pdf(dest: Path, pages: list[str]) -> Path:
    pdf = FPDF()
    pdf.set_font("helvetica", size=14)
    for text in pages:
        pdf.add_page()
        pdf.cell(text=text)
    pdf.output(str(dest))
    return dest


def _make_image(dest: Path) -> Path:
    Image.new("RGB", (64, 64), "white").save(dest, format="JPEG")
    return dest


def test_is_pdf(tmp_path: Path):
    assert is_pdf(_make_pdf(tmp_path / "recipe.pdf", ["Pancakes"]))
    assert not is_pdf(_make_image(tmp_path / "photo.jpg"))


def test_is_pdf_ignores_extension(tmp_path: Path):
    assert is_pdf(_make_pdf(tmp_path / "upload", ["Pancakes"]))
    assert not is_pdf(_make_image(tmp_path / "photo.pdf"))


def test_render_pdf_returns_one_image_per_page(tmp_path: Path):
    pdf = _make_pdf(tmp_path / "recipe.pdf", ["Pancakes", "200 g flour"])

    images, text = render_pdf(pdf)

    assert len(images) == 2
    for image in images:
        with Image.open(image) as img:
            assert img.width > 0 and img.height > 0
    assert "Pancakes" in text
    assert "200 g flour" in text


def test_render_pdf_respects_max_pages(tmp_path: Path):
    pdf = _make_pdf(tmp_path / "recipe.pdf", ["one", "two", "three"])

    images, text = render_pdf(pdf, max_pages=2)

    assert len(images) == 2
    assert "three" not in text


def test_render_pdf_without_text_layer(tmp_path: Path):
    pdf = FPDF()
    pdf.add_page()
    pdf.output(str(tmp_path / "scan.pdf"))

    images, text = render_pdf(tmp_path / "scan.pdf")

    assert len(images) == 1
    assert text == ""


def test_expand_pdfs_keeps_images_and_order(tmp_path: Path):
    photo = _make_image(tmp_path / "photo.jpg")
    pdf = _make_pdf(tmp_path / "recipe.pdf", ["Pancakes", "200 g flour"])

    images, text = AIRecipeService._expand_pdfs([photo, pdf])

    assert images[0] == photo
    assert len(images) == 3
    assert all(not is_pdf(image) for image in images)
    assert "Text from recipe.pdf" in text
    assert "200 g flour" in text


def test_expand_pdfs_without_pdfs(tmp_path: Path):
    photo = _make_image(tmp_path / "photo.jpg")

    images, text = AIRecipeService._expand_pdfs([photo])

    assert images == [photo]
    assert text == ""
