import pytest

from tests.pdf_test_support import assert_page_renders_without_warnings, assert_warning_exists, extract_annot
from tests.notebook_fixtures import *


r"""
 _____  _____  ______
|  __ \|  __ \|  ____|
| |__) | |  | | |__
|  ___/| |  | |  __|
| |    | |__| | |
|_|    |_____/|_|
"""
@pytest.mark.pdf
@pytest.mark.parametrize("notebook", all_notebooks, indirect=True)
def test_valid_pdf(notebook, remarks_document):
    assert remarks_document.is_pdf


@pytest.mark.pdf
@pytest.mark.parametrize("notebook", all_notebooks, indirect=True)
def test_correct_output_page_count(notebook, remarks_document):
    assert remarks_document.page_count == notebook.export_properties["merged_pages"]


@pytest.mark.pdf
@pytest.mark.parametrize("notebook", all_notebooks, indirect=True)
def test_warnings_match_specification(notebook, remarks_document):
    # Get expected warnings from metadata
    expected_warnings = notebook.export_properties.get("warnings", [])

    # For each page, verify warnings
    for page_num in range(remarks_document.page_count):
        page_warnings = [w for w in expected_warnings
                         if w["output_document_position"] == page_num]

        if page_warnings:
            # Verify each expected warning exists
            for warning_spec in page_warnings:
                for warning in warning_spec["warning"]:
                    assert_warning_exists(remarks_document, page_num, warning)
        else:
            # If no warnings specified for this page, verify page is clean
            assert_page_renders_without_warnings(remarks_document, page_num)

@pytest.mark.pdf
@pytest.mark.parametrize("notebook", all_notebooks, indirect=True)
def test_smart_highlights(notebook, remarks_document):
    for page_num, page_highlights in enumerate(notebook.smart_highlights):
        page = remarks_document[page_num]
        words_on_page = page.get_textpage().extractWORDS()
        for i, annotation in enumerate(page.annots()):
            text = extract_annot(annotation, words_on_page)
            assert text == page_highlights[i]
            # We should implement the colour check as well, once that is ready.
