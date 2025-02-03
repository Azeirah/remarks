import glob
import os
import pytest
import fitz

import remarks
from NotebookMetadata import NotebookMetadata
from RemarkableNotebookType import ReMarkableNotebookType
from remarks.metadata import ReMarkableAnnotationsFileHeaderVersion
from remarks.warnings import scrybble_warning_only_v6_supported


def cleanup_output_folder():
    """Remove all .md and .pdf files from the tests/out folder."""
    for file_pattern in ['tests/out/*.md', 'tests/out/*.pdf']:
        for file in glob.glob(file_pattern):
            os.remove(file)

def pytest_sessionstart(session):
    cleanup_output_folder()


def with_remarks(metadata: NotebookMetadata):
    input_name = metadata.rmn_source

    input_dir = input_name
    output_dir = "tests/out"

    if not getattr(with_remarks, f"run_{input_name}", False):
        remarks.run_remarks(input_dir, output_dir)
        setattr(with_remarks, f"run_{input_name}", True)

    return fitz.open(f"tests/out/{metadata.notebook_name} _remarks.pdf")


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
        }
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
        notebook_type=ReMarkableNotebookType.NOTEBOOK
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
        }
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
        }
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
        }
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
        }
    )



@pytest.fixture
def page():
    pass
    # remarks_generated_pdf = Document(f"tests/out/{metadata.notebook_name} _remarks.pdf")
    # for file in metadata.rm_files:
    #     if "photo" in file:
    #         # show the photo next to the generated page
    #         # - [ ] Get the generated page from the output
    #         position = file["output_document_position"]
    #         img_output = remarks_generated_pdf[position].get_pixmap()
    #         img_output.save(f"tests/out/{metadata.notebook_name} - {position} - Remarks.jpg")
    #         shutil.copy(file["photo"], f"tests/out/{metadata.notebook_name} - {position} - ReMarkable.jpg")


all_notebooks = [
    "markdown_tags_document",
    "gosper_notebook",
    "highlights_document",
    "colored_document",
    "v5_document",
    "black_and_white"
]


@pytest.fixture
def notebook(request):
    """Return the notebook fixture specified in the test's parameters"""
    return request.getfixturevalue(request.param)


@pytest.fixture
def obsidian_markdown(notebook):
    with open(f"tests/out/{notebook.notebook_name} _obsidian.md") as f:
        return f.read()

@pytest.fixture
def remarks_document(notebook):
    """Run remarks on the notebook and return PDF"""
    return with_remarks(notebook)
