from fitz import Document, PDF_ANNOT_FREE_TEXT

from remarks.warnings import ScrybbleWarning


def is_valid_pdf(document: Document) -> bool:
    return document.is_pdf

def pdf_has_num_pages(document: Document, num_pages: int) -> bool:
    return document.page_count == num_pages


def assert_warning_exists(document: Document, page_number: int, warning: ScrybbleWarning):
    """
    @param warning:
    @param document:
    @param page_number: 0-indexed page number
    @return:
    """
    page = document[page_number]
    for annotation in page.annots(PDF_ANNOT_FREE_TEXT):
        assert warning.exists_in_pdf_annotation(annotation)
        return

    assert False, f"No Scrybble warning found on page {page_number}"


def assert_page_renders_without_warnings(document: Document, page_number: int):
    """
    @param document:
    @param page_number: 0-indexed page number
    @return:
    """
    page = document[page_number]
    for annotation in page.annots(PDF_ANNOT_FREE_TEXT):
        if "Scrybble warning" in annotation.get_text():
            assert False, f"Found a warning on page {page_number}"

    assert True
