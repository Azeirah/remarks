from dataclasses import dataclass
from typing import Optional

from RemarkableNotebookType import ReMarkableNotebookType

from rmscene.scene_items import PenColor


@dataclass
class NotebookMetadata:
    """Notebook metadata is meant to describe the inputs and the outputs for a test scenario"""

    notebook_name: str
    """The name of the notebook, as rendered on the ReMarkable tablet software itself"""

    rmn_source: str
    """Where the ReMarkable notebook file (.rmn) can be found."""

    description: str
    """A description of the notebook"""

    notebook_type: ReMarkableNotebookType
    """What 'kind of' notebook this is, is it a PDF? Quick sheets? Epub?"""

    pdf_pages: int
    """How many pages the PDF has in total when viewed on a ReMarkable tablet."""

    rm_files: list[dict]
    """A list of ReMarkable files"""

    export_properties: Optional[dict]
    """Metadata on what happens when the notebook is exported by Remarks."""
    
    smart_highlights: list[list[str]]
    """For each page in the document, a list of expected highlights. Each highlight is a string of text."""