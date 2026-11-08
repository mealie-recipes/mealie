from __future__ import annotations

import math
import re
from collections.abc import Iterable, Iterator
from datetime import timedelta
from io import BytesIO
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import Align, MethodReturnValue, XPos, YPos
from PIL import Image, ImageOps, UnidentifiedImageError

from mealie.lang.providers import Translator
from mealie.repos.repository_recipes import RepositoryRecipes
from mealie.schema.cookbook.cookbook import CookBookOut
from mealie.schema.recipe import RecipeOut
from mealie.schema.recipe.recipe_image_types import RecipeImageTypes
from mealie.schema.response.pagination import OrderDirection, PaginationQuery
from mealie.services.scraper.cleaner import pretty_print_timedelta

FONT_DIR = Path(__file__).parents[2] / "assets" / "fonts"
SANS = "NotoSans"
SERIF = "NotoSerif"

INK = (17, 17, 17)
MUTED = (105, 105, 105)
ACCENT = INK
RULE = (210, 210, 210)

MARGIN_MM = 20
BOTTOM_MM = 24
FOOTER_RULE_FROM_BOTTOM_MM = 15

# Every image is center-cropped to one banner shape so recipe pages line up. They are re-encoded
# as small JPEGs because fpdf2 stores anything that isn't JPEG as deflated raw pixels, which makes
# a cookbook with hundreds of photos balloon in size.
IMAGE_ASPECT = 2.4
IMAGE_PX = (1080, round(1080 / IMAGE_ASPECT))
IMAGE_JPEG_QUALITY = 78

STEP_GUTTER_MM = 10
TOC_ROW_MM = 8
TOC_PAGE_NUMBER_MM = 10
TOC_HEADING_BLOCK_MM = 24

# Ingredient lists shorter than this read better in a single column.
TWO_COLUMN_MIN_INGREDIENTS = 7
COLUMN_GUTTER_MM = 10
BULLET_INDENT_MM = 4.5
INGREDIENT_LINE_MM = 4.8
INGREDIENT_GAP_MM = 1.6
INGREDIENT_TITLE_GAP_MM = 3


class _RecipePdf(FPDF):
    running_title = ""
    show_footer = True

    def footer(self) -> None:
        if not self.show_footer:
            return
        y = self.h - FOOTER_RULE_FROM_BOTTOM_MM
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.set_xy(self.l_margin, y + 2)
        self.set_font(SANS, size=7.5)
        self.set_text_color(*MUTED)
        self.cell(self.epw - 20, 4, self.running_title)
        self.cell(20, 4, str(self.page_no()), align="R")
        self.set_text_color(*INK)


class RecipePdfRenderer:
    """
    Draws recipes straight to PDF with fpdf2. Recipe text is only ever written as plain text, so
    nothing in a recipe is parsed as markup, and images are only read from the recipe's own
    image directory.
    """

    def __init__(self, translator: Translator, include_images: bool = True) -> None:
        self.translator = translator
        self.t = translator.t
        self.include_images = include_images

        pdf = _RecipePdf(format="A4")
        pdf.set_auto_page_break(auto=True, margin=BOTTOM_MM)
        pdf.set_margins(MARGIN_MM, MARGIN_MM, MARGIN_MM)
        # fpdf2 pads cell text by 1mm by default, which pushes text off the margin that rules and
        # images align to.
        pdf.c_margin = 0
        pdf.add_font(SANS, style="", fname=FONT_DIR / "NotoSans-Regular.ttf")
        pdf.add_font(SANS, style="B", fname=FONT_DIR / "NotoSans-SemiBold.ttf")
        pdf.add_font(SANS, style="I", fname=FONT_DIR / "NotoSans-Italic.ttf")
        pdf.add_font(SERIF, style="B", fname=FONT_DIR / "NotoSerif-SemiBold.ttf")
        pdf.add_font(SERIF, style="I", fname=FONT_DIR / "NotoSerif-Italic.ttf")
        pdf.set_text_color(*INK)
        self.pdf = pdf
        self._next_recipe_needs_page = True
        self._toc_page_count = 0

    def render_cookbook(
        self, name: str, description: str, recipes: Iterable[RecipeOut], recipe_count: int
    ) -> RecipePdfRenderer:
        pdf = self.pdf
        pdf.set_title(name)
        pdf.running_title = name
        self._cover(name, description)
        if recipe_count == 0:
            return self

        pdf.add_page()
        # fpdf2 draws a page's footer when the next page starts, so the cover's footer has already
        # been skipped by now and every later page gets one.
        pdf.show_footer = True
        # The ToC spans a fixed, precomputed number of pages. Letting fpdf2 add pages on overflow
        # (allow_extra_pages) inserts them after the footers are drawn, so every printed page
        # number after the ToC would be wrong.
        self._toc_page_count = self._toc_pages(recipe_count)
        pdf.insert_toc_placeholder(self._render_toc, pages=self._toc_page_count)
        # The placeholder already broke onto a fresh page for the first recipe.
        self._next_recipe_needs_page = False

        for recipe in recipes:
            self._recipe(recipe)

        return self

    def render_recipe(self, recipe: RecipeOut) -> RecipePdfRenderer:
        self.pdf.set_title(recipe.name)
        self.pdf.running_title = recipe.name
        self._recipe(recipe)
        return self

    def output(self, path: Path) -> Path:
        self.pdf.output(str(path))
        return path

    # ==============================================================================================
    # Cover and contents

    def _cover(self, name: str, description: str) -> None:
        pdf = self.pdf
        pdf.show_footer = False
        pdf.add_page()
        pdf.set_y(pdf.h * 0.36)

        self._label(self.t("recipe.pdf.cookbook"))
        pdf.ln(4)
        pdf.set_font(SERIF, "B", 34)
        pdf.multi_cell(0, 14, name, align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        self._rule(width=24, color=ACCENT, thickness=0.8)
        if description:
            pdf.ln(7)
            pdf.set_font(SERIF, "I", 13)
            pdf.set_text_color(*MUTED)
            pdf.multi_cell(pdf.epw * 0.8, 6.5, description, align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(*INK)

    def _toc_rows_per_page(self) -> tuple[int, int]:
        usable = self.pdf.h - self.pdf.t_margin - BOTTOM_MM
        return int((usable - TOC_HEADING_BLOCK_MM) // TOC_ROW_MM), int(usable // TOC_ROW_MM)

    def _toc_pages(self, entries: int) -> int:
        first_page, other_pages = self._toc_rows_per_page()
        if entries <= first_page:
            return 1
        return 1 + math.ceil((entries - first_page) / other_pages)

    def _render_toc(self, pdf: FPDF, outline: list) -> None:
        # Page breaks are done by hand so the ToC fills exactly the pages _toc_pages reserved.
        pdf.set_auto_page_break(False)
        start_page = pdf.page

        pdf.set_xy(pdf.l_margin, pdf.t_margin)
        pdf.set_font(SERIF, "B", 26)
        pdf.cell(0, 12, self.t("recipe.pdf.contents"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)
        self._rule(width=24, color=ACCENT, thickness=0.8)
        pdf.set_y(pdf.t_margin + TOC_HEADING_BLOCK_MM)

        rows_left, rows_per_page = self._toc_rows_per_page()
        for section in outline:
            if rows_left == 0:
                pdf.page += 1
                pdf.set_xy(pdf.l_margin, pdf.t_margin)
                # A page's content stream must select its own font; fpdf2 only re-emits it when
                # it thinks the page has none yet.
                pdf.current_font_is_set_on_page = False
                rows_left = rows_per_page
            rows_left -= 1
            self._toc_row(section.name, section.page_number)

        # Fewer entries than reserved rows (a recipe deleted mid-render) leaves trailing ToC pages
        # blank; fpdf2 still requires the ToC to end on its last reserved page.
        pdf.page = start_page + self._toc_page_count - 1
        pdf.set_auto_page_break(True, margin=BOTTOM_MM)

    def _toc_row(self, name: str, page_number: int) -> None:
        pdf = self.pdf
        link = pdf.add_link(page=page_number)
        title_room = pdf.epw - TOC_PAGE_NUMBER_MM - 6

        pdf.set_font(SANS, size=10.5)
        pdf.set_text_color(*INK)
        title = self._fit(name, title_room)
        title_width = pdf.get_string_width(title) + 1.5
        pdf.cell(title_width, TOC_ROW_MM, title, link=link)

        leader_width = pdf.epw - TOC_PAGE_NUMBER_MM - title_width
        dot = pdf.get_string_width(" .")
        pdf.set_text_color(*RULE)
        pdf.cell(leader_width, TOC_ROW_MM, " ." * int((leader_width - 2) / dot), align="R", link=link)

        pdf.set_text_color(*MUTED)
        pdf.cell(
            TOC_PAGE_NUMBER_MM,
            TOC_ROW_MM,
            str(page_number),
            align="R",
            link=link,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        pdf.set_text_color(*INK)

    def _fit(self, text: str, width: float) -> str:
        if self.pdf.get_string_width(text) <= width:
            return text
        while text and self.pdf.get_string_width(text + "…") > width:
            text = text[:-1]
        return text.rstrip() + "…"

    # ==============================================================================================
    # Recipe pages

    def _recipe(self, recipe: RecipeOut) -> None:
        pdf = self.pdf
        if self._next_recipe_needs_page:
            pdf.add_page()
        self._next_recipe_needs_page = True
        pdf.start_section(recipe.name)

        pdf.set_font(SERIF, "B", 24)
        pdf.multi_cell(0, 10.5, recipe.name, align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2.5)
        self._meta(recipe)
        pdf.ln(5)

        if self.include_images:
            self._image(recipe)

        if recipe.description:
            pdf.set_font(SERIF, "I", 11)
            pdf.set_text_color(*MUTED)
            pdf.multi_cell(0, 5.8, recipe.description, align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(*INK)
            pdf.ln(6)

        if recipe.recipe_ingredient:
            self._section_heading(self.t("recipe.pdf.ingredients"))
            self._ingredients(recipe)
            pdf.ln(6)

        if recipe.recipe_instructions:
            self._section_heading(self.t("recipe.pdf.instructions"))
            self._instructions(recipe)
            pdf.ln(4)

        if recipe.notes:
            self._section_heading(self.t("recipe.pdf.notes"))
            for note in recipe.notes:
                if note.title:
                    pdf.set_font(SANS, "B", 9.5)
                    pdf.multi_cell(0, 5.2, note.title, align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font(SANS, size=9.5)
                pdf.set_text_color(*MUTED)
                pdf.multi_cell(0, 5.2, note.text, align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_text_color(*INK)
                pdf.ln(2.5)

    def _meta(self, recipe: RecipeOut) -> None:
        items: list[tuple[str, str]] = []
        if recipe.recipe_servings:
            items.append((self.t("recipe.servings-text.servings"), f"{recipe.recipe_servings:g}"))
        if recipe.recipe_yield_quantity or recipe.recipe_yield:
            qty = f"{recipe.recipe_yield_quantity:g} " if recipe.recipe_yield_quantity else ""
            items.append((self.t("recipe.servings-text.yield"), f"{qty}{recipe.recipe_yield or ''}".strip()))
        for key, seconds, text in (
            ("recipe.pdf.prep-time", recipe.prep_time_seconds, recipe.prep_time),
            ("recipe.pdf.cook-time", recipe.perform_time_seconds, recipe.perform_time),
            ("recipe.pdf.total-time", recipe.total_time_seconds, recipe.total_time),
        ):
            if value := self._time(seconds, text):
                items.append((self.t(key), value))

        pdf = self.pdf
        if items:
            for label, value in items:
                pdf.set_font(SANS, "B", 7)
                pdf.set_char_spacing(0.8)
                label_text = label.upper()
                label_width = pdf.get_string_width(label_text) + 2
                pdf.set_font(SANS, size=9.5)
                pdf.set_char_spacing(0)
                value_width = pdf.get_string_width(value) + 7
                if pdf.get_x() + label_width + value_width > pdf.w - pdf.r_margin:
                    pdf.ln(6)
                self._label(label_text, width=label_width, height=6, color=MUTED)
                pdf.set_font(SANS, size=9.5)
                pdf.cell(value_width, 6, value)
            pdf.ln(7)
        self._rule()

    def _time(self, seconds: int | None, text: str | None) -> str:
        """The structured time followed by the recipe's free text, matching the recipe page."""
        duration = pretty_print_timedelta(timedelta(seconds=seconds), self.translator) if seconds else ""
        return " ".join(part for part in (duration, (text or "").strip()) if part)

    def _image(self, recipe: RecipeOut) -> None:
        image_path = RecipeOut.image_dir_from_id(recipe.id) / RecipeImageTypes.min.value
        if not image_path.is_file():
            return

        try:
            with Image.open(image_path) as img:
                banner = ImageOps.fit(img.convert("RGB"), IMAGE_PX)
                buffer = BytesIO()
                banner.save(buffer, "JPEG", quality=IMAGE_JPEG_QUALITY)
        except OSError, UnidentifiedImageError:
            return

        pdf = self.pdf
        height = pdf.epw / IMAGE_ASPECT
        if pdf.will_page_break(height):
            pdf.add_page()
        pdf.image(buffer, x=pdf.l_margin, w=pdf.epw, h=height)
        pdf.ln(7)

    def _ingredients(self, recipe: RecipeOut) -> None:
        rows: list[tuple[bool, str]] = []
        for ingredient in recipe.recipe_ingredient:
            if ingredient.title:
                rows.append((True, ingredient.title))
            if text := ingredient.display or ingredient.original_text or "":
                rows.append((False, text))

        pdf = self.pdf
        column_width = (pdf.epw - COLUMN_GUTTER_MM) / 2
        if len(rows) >= TWO_COLUMN_MIN_INGREDIENTS:
            heights = [self._ingredient_row_height(row, column_width, first=i == 0) for i, row in enumerate(rows)]
            split = self._balanced_split(rows, heights)
            column_height = max(sum(heights[:split]), sum(heights[split:]))
            if column_height <= pdf.h - pdf.t_margin - BOTTOM_MM:
                if pdf.will_page_break(column_height):
                    pdf.add_page()
                top = pdf.get_y()
                self._ingredient_column(rows[:split], pdf.l_margin, column_width)
                pdf.set_y(top)
                self._ingredient_column(rows[split:], pdf.l_margin + column_width + COLUMN_GUTTER_MM, column_width)
                pdf.set_xy(pdf.l_margin, top + column_height)
                return

        self._ingredient_column(rows, pdf.l_margin, pdf.epw)

    @staticmethod
    def _balanced_split(rows: list[tuple[bool, str]], heights: list[float]) -> int:
        total = sum(heights)
        best_split, best_height = 1, total
        running = 0.0
        for split in range(1, len(rows)):
            running += heights[split - 1]
            # A section title must not end the left column.
            if rows[split - 1][0]:
                continue
            tallest = max(running, total - running)
            if tallest < best_height:
                best_split, best_height = split, tallest
        return best_split

    def _ingredient_row_height(self, row: tuple[bool, str], width: float, first: bool) -> float:
        is_title, text = row
        pdf = self.pdf
        if is_title:
            pdf.set_font(SANS, "B", 9.5)
            lines = pdf.multi_cell(width, INGREDIENT_LINE_MM, text, dry_run=True, output=MethodReturnValue.LINES)
            return (0 if first else INGREDIENT_TITLE_GAP_MM) + len(lines) * INGREDIENT_LINE_MM + INGREDIENT_GAP_MM
        pdf.set_font(SANS, size=9.5)
        lines = pdf.multi_cell(
            width - BULLET_INDENT_MM, INGREDIENT_LINE_MM, text, dry_run=True, output=MethodReturnValue.LINES
        )
        return len(lines) * INGREDIENT_LINE_MM + INGREDIENT_GAP_MM

    def _ingredient_column(self, rows: list[tuple[bool, str]], x: float, width: float) -> None:
        pdf = self.pdf
        for index, (is_title, text) in enumerate(rows):
            if is_title:
                if index > 0:
                    pdf.ln(INGREDIENT_TITLE_GAP_MM)
                pdf.set_font(SANS, "B", 9.5)
                pdf.set_x(x)
                pdf.multi_cell(width, INGREDIENT_LINE_MM, text, align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                pdf.set_font(SANS, size=9.5)
                pdf.set_text_color(*MUTED)
                pdf.set_x(x)
                pdf.cell(BULLET_INDENT_MM, INGREDIENT_LINE_MM, "•")
                pdf.set_text_color(*INK)
                pdf.multi_cell(
                    width - BULLET_INDENT_MM,
                    INGREDIENT_LINE_MM,
                    text,
                    align=Align.L,
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                )
            pdf.ln(INGREDIENT_GAP_MM)

    def _instructions(self, recipe: RecipeOut) -> None:
        pdf = self.pdf
        text_x = pdf.l_margin + STEP_GUTTER_MM
        text_width = pdf.epw - STEP_GUTTER_MM

        for number, step in enumerate(recipe.recipe_instructions, start=1):
            if step.title:
                # Keep a section title with at least the first lines of its step.
                if pdf.will_page_break(22):
                    pdf.add_page()
                pdf.ln(1.5)
                pdf.set_font(SERIF, "B", 12)
                pdf.multi_cell(0, 6, step.title, align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(1.5)

            if pdf.will_page_break(12):
                pdf.add_page()

            top = pdf.get_y()
            pdf.set_font(SERIF, "B", 13)
            pdf.set_text_color(*ACCENT)
            pdf.set_xy(pdf.l_margin, top - 0.6)
            pdf.cell(STEP_GUTTER_MM, 6, str(number))
            pdf.set_text_color(*INK)

            pdf.set_xy(text_x, top)
            if step.summary:
                pdf.set_font(SANS, "B", 10)
                pdf.multi_cell(text_width, 5.4, step.summary, align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_x(text_x)
            pdf.set_font(SANS, size=10)
            pdf.multi_cell(
                text_width,
                5.4,
                self._strip_step_number(step.text, number),
                align=Align.L,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            pdf.ln(3.5)

    @staticmethod
    def _strip_step_number(text: str, number: int) -> str:
        # Scraped steps often carry their own "3." prefix, which would print next to our number.
        return re.sub(rf"^\s*{number}[.)]\s+", "", text, count=1)

    # ==============================================================================================
    # Shared pieces

    def _section_heading(self, text: str) -> None:
        pdf = self.pdf
        # Keep a heading with at least a few lines of what follows it.
        if pdf.will_page_break(24):
            pdf.add_page()
        self._label(text, size=8, color=ACCENT, spacing=1.4, height=5)
        pdf.ln(5.5)
        self._rule()
        pdf.ln(3.5)

    def _label(
        self,
        text: str,
        width: float = 0,
        height: float = 5,
        size: float = 7,
        color: tuple[int, int, int] = ACCENT,
        spacing: float = 0.8,
    ) -> None:
        pdf = self.pdf
        pdf.set_font(SANS, "B", size)
        pdf.set_char_spacing(spacing)
        pdf.set_text_color(*color)
        pdf.cell(width, height, text.upper())
        pdf.set_char_spacing(0)
        pdf.set_text_color(*INK)

    def _rule(self, width: float | None = None, color: tuple[int, int, int] = RULE, thickness: float = 0.25) -> None:
        pdf = self.pdf
        y = pdf.get_y()
        pdf.set_draw_color(*color)
        pdf.set_line_width(thickness)
        pdf.line(pdf.l_margin, y, pdf.l_margin + (width if width is not None else pdf.epw), y)


def render_cookbook_pdf(
    renderer: RecipePdfRenderer, recipes: RepositoryRecipes, cookbook: CookBookOut
) -> RecipePdfRenderer:
    """
    Renders every recipe in a cookbook, sorted by name. Only summaries are listed up front; full
    recipes are loaded one at a time so a large cookbook never sits in memory all at once.
    """
    query = PaginationQuery(page=1, per_page=-1, order_by="name", order_direction=OrderDirection.asc)
    summaries = recipes.page_all(query, cookbook=cookbook).items

    def load() -> Iterator[RecipeOut]:
        for summary in summaries:
            if recipe := recipes.get_one(summary.id, "id"):
                yield recipe

    return renderer.render_cookbook(cookbook.name, cookbook.description, load(), recipe_count=len(summaries))
