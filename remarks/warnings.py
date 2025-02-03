from dataclasses import dataclass
from fitz.fitz import Page, PDF_ANNOT_FREE_TEXT
import fitz


@dataclass
class ScrybbleWarning:
    message: str

    def __str__(self):
        return f"Scrybble warning: {self.message}"

    def render_as_annotation(self, pdf_page: Page):
        pdf_page.add_freetext_annot(
            rect=fitz.Rect(10, 10, 300, 30),
            text=str(self),
            fontsize=11,
            text_color=(0, 0, 0),
            fill_color=(1, 1, 1)
        )

    def exists_in_pdf_annotation(self, annotation: PDF_ANNOT_FREE_TEXT) -> bool:
        return str(self) in annotation.get_text()


scrybble_warning_only_v6_supported = ScrybbleWarning("This page is not V6")
