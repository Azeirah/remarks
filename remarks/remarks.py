import logging
import pathlib
import sys

import fitz  # PyMuPDF

from .Document import Document
from .conversion.drawing import (
    draw_annotations_on_pdf,
    add_smart_highlight_annotations,
)
from .conversion.parsing import (
    parse_rm_file,
    rescale_parsed_data,
    get_ann_max_bound, determine_document_dimensions,
)
from .conversion.text import (
    extract_groups_from_smart_hl,
)
from .dimensions import REMARKABLE_PDF_EXPORT, REMARKABLE_DOCUMENT
from .output.ObsidianMarkdownFile import ObsidianMarkdownFile
from .utils import (
    is_document,
    get_document_filetype,
    get_visible_name,
    get_ui_path,
    load_json_file,
    RM_WIDTH,
    RM_HEIGHT,
)


def run_remarks(
    input_dir, output_dir
):
    num_docs = sum(1 for _ in pathlib.Path(f"{input_dir}/").glob("*.metadata"))

    if num_docs == 0:
        logging.warning(
            f'No .metadata files found in "{input_dir}". Are you sure you\'re running remarks on a valid xochitl-like directory? See: https://github.com/lucasrla/remarks#1-copy-remarkables-raw-document-files-to-your-computer'
        )
        sys.exit(1)

    logging.info(
        f'\nFound {num_docs} documents in "{input_dir}", will process them now',
    )

    for metadata_path in pathlib.Path(f"{input_dir}/").glob("*.metadata"):
        if not is_document(metadata_path):
            continue

        doc_type = get_document_filetype(metadata_path)
        # Both "Quick Sheets" and "Notebooks" have doc_type="notebook"
        supported_types = ["pdf", "epub", "notebook"]

        doc_name = get_visible_name(metadata_path)

        if not doc_name:
            continue

        if doc_type in supported_types:
            logging.info(f'\nFile: "{doc_name}.{doc_type}" ({metadata_path.stem})')

            in_device_dir = get_ui_path(metadata_path)
            out_path = pathlib.Path(f"{output_dir}/{in_device_dir}/{doc_name}/")

            process_document(metadata_path, out_path)
        else:
            logging.info(
                f'\nFile skipped: "{doc_name}" ({metadata_path.stem}) due to unsupported filetype: {doc_type}. remarks only supports: {", ".join(supported_types)}'
            )

    logging.info(
        f'\nDone processing "{input_dir}"',
    )


def process_document(
    metadata_path,
    out_path,
):
    document = Document(metadata_path)
    pdf_src = document.open_source_pdf()

    obsidian_markdown = ObsidianMarkdownFile(document)
    obsidian_markdown.add_document_header()

    for (
        page_uuid,
        page_idx,
        rm_annotation_file,
        has_annotations,
        rm_highlights_file,
        has_smart_highlights,
    ) in document.pages():
        print(f"processing page {page_idx}, {page_uuid}")

        # Create a new PDF document to hold the page that will be annotated
        work_doc = fitz.open()

        # Get document page dimensions and calculate what scale should be
        # applied to fit it into the device (given the device's own dimensions)
        if rm_annotation_file:
            try:
                dims = determine_document_dimensions(rm_annotation_file)
            except ValueError:
                dims = REMARKABLE_PDF_EXPORT
        else:
            dims = REMARKABLE_PDF_EXPORT
        ann_page = work_doc.new_page(
            width=dims.width,
            height=dims.height,
        )

        pdf_src_page_rect = fitz.Rect(
            0, 0, REMARKABLE_PDF_EXPORT.width, REMARKABLE_PDF_EXPORT.height
        )

        # This check is necessary because PyMuPDF doesn't let us
        # "show_pdf_page" from an empty (blank) page
        # - https://github.com/pymupdf/PyMuPDF/blob/9d2af43230f6d9944734320813acc79abe95d514/fitz/utils.py#L185-L186
        if len(pdf_src[page_idx].get_contents()) != 0:
            # Resize content of original page and copy it to the page that will
            # be annotated
            ann_page.show_pdf_page(pdf_src_page_rect, pdf_src, pno=page_idx)

            # `show_pdf_page()` works as a way to copy and resize content from
            # one doc/page/rect into another, but unlike `insert_pdf()` it will
            # not carry over in-PDF links, annotations, etc:
            # - https://pymupdf.readthedocs.io/en/latest/page.html#Page.show_pdf_page
            # - https://pymupdf.readthedocs.io/en/latest/document.html#Document.insert_pdf

        (ann_data, has_ann_hl), version = parse_rm_file(rm_annotation_file)
        x_max, y_max, x_min, y_min = get_ann_max_bound(ann_data)
        offset_x = 0
        offset_y = 0
        is_ann_out_page = True
        if version == "V6":
            offset_x = RM_WIDTH / 2
        if dims.height >= (RM_HEIGHT + 88 * 3):
            offset_y = 3 * 88  # why 3 * text_offset? No clue, ask ReMarkable.
        if abs(x_min) + abs(x_max) > 1872:
            scale = REMARKABLE_DOCUMENT.width / (max(x_max, 1872) - min(x_min, 0))
            ann_data = rescale_parsed_data(ann_data, scale, offset_x, offset_y)
        else:
            scale = REMARKABLE_DOCUMENT.height / (max(y_max, 2048) - min(y_min, 0))
            ann_data = rescale_parsed_data(ann_data, scale, offset_x, offset_y)


        if ann_data:
            if "text" in ann_data:
                obsidian_markdown.add_text(page_idx, ann_data['text'])
            if "highlights" in ann_data:
                obsidian_markdown.add_highlights(page_idx, ann_data["highlights"])

        if has_annotations:
            ann_page = draw_annotations_on_pdf(ann_data, ann_page)

        if has_smart_highlights:
            smart_hl_data = load_json_file(rm_highlights_file)
            add_smart_highlight_annotations(smart_hl_data, ann_page, scale)
            extract_groups_from_smart_hl(smart_hl_data)

        # If there are annotations outside the original page limits
        # that we've just (re)created from scratch
        if is_ann_out_page:
            pdf_src.insert_pdf(work_doc, start_at=page_idx)
            pdf_src.delete_page(page_idx + 1)

        # Else, draw annotations on the original PDF page (in-place) to do
        # our best to preserve in-PDF links and the original page size
        if has_annotations:
            draw_annotations_on_pdf(
                ann_data,
                pdf_src[page_idx],
                inplace=True,
            )

        if has_smart_highlights:
            add_smart_highlight_annotations(
                smart_hl_data,
                pdf_src[page_idx],
                scale,
                inplace=True,
            )

        work_doc.close()

    out_doc_path_str = f"{out_path.parent}/{out_path.name}"

    pdf_src.save(f"{out_doc_path_str} _remarks.pdf")

    obsidian_markdown.save(out_doc_path_str)

    pdf_src.close()
