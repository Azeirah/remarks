import pytest
from tests.NotebookMetadata import NotebookMetadata
from RemarkableNotebookType import ReMarkableNotebookType
from remarks.metadata import ReMarkableAnnotationsFileHeaderVersion
from remarks.warnings import scrybble_warning_only_v6_supported
from rmscene.scene_items import PenColor


@pytest.fixture
def markdown_tags_document():
    return NotebookMetadata(
        description="""A document with a few tags""",
        notebook_name="tags test",
        rmn_source="tests/in/v3 markdown tags.rmn",
        pdf_pages=0,
        rm_files=[],
        notebook_type=ReMarkableNotebookType.NOTEBOOK,
        export_properties={
            "merged_pages": 2
        },
        smart_highlights=[],
    )


@pytest.fixture
def gosper_notebook():
    return NotebookMetadata(
        description="""A document with complex hand-drawn annotations""",
        notebook_name="Gosper",
        rmn_source="tests/in/v2 notebook complex.rmn",
        pdf_pages=0,
        rm_files=[
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V3,
                "output_document_position": 0,
                "input_document_position": 0
            },
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V3,
                "output_document_position": 1,
                "input_document_position": 1
            },
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V3,
                "output_document_position": 2,
                "input_document_position": 2
            }
        ],
        export_properties={
            "merged_pages": 3,
            "warnings": [
                {
                    "output_document_position": 0,
                    "warning": [scrybble_warning_only_v6_supported]
                },
                {
                    "output_document_position": 1,
                    "warning": [scrybble_warning_only_v6_supported]
                },
                {
                    "output_document_position": 2,
                    "warning": [scrybble_warning_only_v6_supported]
                }
            ]
        },
        notebook_type=ReMarkableNotebookType.NOTEBOOK,
        smart_highlights=[],
    )


@pytest.fixture
def highlights_document():
    return NotebookMetadata(
        description="""
        This document contains smart highlights in all colors on the first page.
        Similarly, it contains regular highlights on the second page.
        """,
        notebook_name="On computable numbers",
        rmn_source="tests/in/on computable numbers - RMPP - highlighter tool v6.rmn",
        notebook_type=ReMarkableNotebookType.PDF,
        pdf_pages=36,
        rm_files=[
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V6,
                "output_document_position": 0,
                "photo": "tests/in/on computable numbers - RMPP - highlighter tool v6 - page 1.jpeg"
            },
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V6,
                "output_document_position": 1,
                "photo": "tests/in/on computable numbers - RMPP - highlighter tool v6 - page 2.jpeg"
            }
        ],
        export_properties={
            "merged_pages": 36
        },
        smart_highlights=[[
            "numbers may be described briefly as the real",
            "numbers whose expressions as a decimal are calculable by finite means.",
            "theory of functions",
            "According to my definition, a number is computable",
            "if its decimal can be written down by a machine.",
            "In particular, I show that certain large classes",
            "of numbers are computable.",
            "The computable numbers do not, however, include",
            "all definable numbers,",
            "Although the class of computable numbers is so great, and in many",
            # Avays is due to an OCR error
            "Avays similar to the class of real numbers, it is nevertheless enumerable.",
        ]],
    )

@pytest.fixture
def highlights_multiline_document():
    return NotebookMetadata(
        description="""
        This document contains a multi-line smart highlight and multiple columns.
        """,
        notebook_name="multi column pdf.pdf",
        rmn_source="tests/in/multi-line highlights.rmn",
        notebook_type=ReMarkableNotebookType.PDF,
        pdf_pages=1,
        rm_files=[
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V6,
                "output_document_position": 0,
            }
        ],
        export_properties={
            "merged_pages": 1
        },
        smart_highlights=[[ 
            "suddenly there came a tapping,",
            "Eagerly I wished the morrow;—vainly I",
            "had sought to borrow",
            "Let my heart be still a moment and this",
            "But, with mien of lord or lady, perched",
            "above my chamber door—"
        ]],
    )

@pytest.fixture
def v5_document():
    return NotebookMetadata(
        notebook_name="1936 On Computable Numbers, with an Application to the Entscheidungsproblem - A. M. Turing",
        description="",  # No description provided; set it as an empty string
        rmn_source="tests/in/on computable numbers - v5.rmn",
        notebook_type=ReMarkableNotebookType.PDF,
        pdf_pages=36,
        rm_files=[
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V5,
                "output_document_position": 0,
            },
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V5,
                "output_document_position": 1,
            },
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V5,
                "output_document_position": 27
            }
        ],
        export_properties={
            "merged_pages": 36,
            "warnings": [
                {
                    "warning": [scrybble_warning_only_v6_supported],
                    "output_document_position": 0,
                },
                {
                    "warning": [scrybble_warning_only_v6_supported],
                    "output_document_position": 1,
                },
                {
                    "warning": [scrybble_warning_only_v6_supported],
                    "output_document_position": 27
                }
            ]
        },
        smart_highlights=[],
    )


@pytest.fixture
def black_and_white():
    return NotebookMetadata(
        notebook_name="B&W rmpp",
        description="""
        A simple notebook with only black and white on one page
        """,
        rmn_source="tests/in/rmpp - v6 - black and white only.rmn",
        notebook_type=ReMarkableNotebookType.NOTEBOOK,
        pdf_pages=1,
        rm_files=[
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V6,
                "output_document_position": 0
            }
        ],
        export_properties={
            "merged_pages": 1
        },
        smart_highlights=[],
    )


@pytest.fixture
def colored_document():
    return NotebookMetadata(
        notebook_name="Biological relativity",
        description="""
        A notebook with a few pages and various drawings.
        """,
        rmn_source="tests/in/rmpp - v6 - various colors.rmn",
        notebook_type=ReMarkableNotebookType.NOTEBOOK,
        pdf_pages=4,
        rm_files=[
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V6,
                "output_document_position": 0
            },
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V6,
                "output_document_position": 1
            },
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V6,
                "output_document_position": 2
            },
            {
                ".rm_file_version": ReMarkableAnnotationsFileHeaderVersion.V6,
                "output_document_position": 3
            }
        ],
        export_properties={
            "merged_pages": 4
        },
        smart_highlights=[],
    )

all_notebooks = [
    "markdown_tags_document",
    "gosper_notebook",
    "highlights_document",
    "highlights_multiline_document",
    "colored_document",
    "v5_document",
    "black_and_white"
]
