from fitz import Document, Rect, Quad, PDF_ANNOT_FREE_TEXT

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

# Following two functions are lifted almost directly from https://github.com/pymupdf/PyMuPDF/issues/318#issuecomment-658781494.
def check_contain(r_word, points):
    """If `r_word` is contained in the rectangular area.

    The area of the intersection should be large enough compared to the
    area of the given word.

    Args:
        r_word (fitz.Rect): rectangular area of a single word.
        points (list): list of points in the rectangular area of the
            given part of a highlight.

    Returns:
        bool: whether `r_word` is contained in the rectangular area.
    """
    # `r` is mutable, so everytime a new `r` should be initiated.
    r = Quad(points).rect
    r.intersect(r_word)

    if r.get_area() >= r_word.get_area() * 0.5:
        contain = True
    else:
        contain = False
    return contain


def extract_annot(annot, words_on_page):
    """Extract words in a given highlight.

    Args:
        annot (fitz.Annot): [description]
        words_on_page (list): [description]

    Returns:
        str: words in the entire highlight.
    """
    quad_points = annot.vertices
    quad_count = int(len(quad_points) / 4)
    sentences = ['' for i in range(quad_count)]
    for i in range(quad_count):
        points = quad_points[i * 4: i * 4 + 4]
        words = [
            w for w in words_on_page if
            check_contain(Rect(w[:4]), points)
        ]
        sentences[i] = ' '.join(w[4] for w in words)
    sentence = ' '.join(sentences)

    return sentence