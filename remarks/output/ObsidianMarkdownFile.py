import re
from typing import List

import yaml
from rmscene.scene_items import GlyphRange

from remarks.Document import Document


class ObsidianMarkdownFile:
    def __init__(self, document: Document):
        self.content = ""
        self.page_content = {}
        self.document = document

    def add_document_header(self):
        frontmatter = {}
        if self.document.rm_tags:
            frontmatter["tags"] = list(
                map(lambda tag: f"#remarkable/{tag}", self.document.rm_tags)
            )

        frontmatter_md = ""
        if len(frontmatter) > 0:
            frontmatter_md = f"""---
{yaml.dump(frontmatter, indent=2)}
---"""

        self.content += f"""{frontmatter_md}

# {self.document.name}

> [!WARNING] **Do not modify** this file
> This file is automatically generated by scrybble and will be overwritten whenever this file in synchronized.
> Treat it as a reference.

"""

    def save(self, location: str):
        if len(self.page_content):
            self.content += "## Pages\n\n"

            for page_idx in sorted(self.page_content.keys()):
                self.content += self.page_content[page_idx]

        # don't write if the file is empty
        if len(self.document.rm_tags) or len(self.page_content):
            with open(f"{location} _obsidian.md", "w") as f:
                f.write(self.content)

    def add_highlights(
        self, page_idx: int, highlights: List[GlyphRange], doc: Document
    ):
        page_idx += 1
        highlight_content = ""
        joined_highlights = []
        highlights = sorted(
            [highlight for highlight in highlights if highlight.start is not None],
            key=lambda h: h.start,
        )
        if len(highlights) > 0:
            if len(highlights) == 1:
                highlight_content += f"""### [[{doc.name}.pdf#page={page_idx}|{doc.name}, page {page_idx}]]

> {highlights[0].text}

"""
            else:
                # first, highlights may be disjointed. We want to join highlights that belong together
                paired_highlights = [
                    (highlights[i], highlights[i + 1])
                    for i, _ in enumerate(highlights[:-1])
                ]
                assert len(paired_highlights) > 0
                joined_highlight = []
                for current, next in paired_highlights:
                    distance = next.start - (current.start + current.length)
                    joined_highlight.append(current.text)
                    if distance > 2:
                        joined_highlights.append(joined_highlight)
                        joined_highlight = []

                highlight_content += f"### [[{doc.name}.pdf#page={page_idx}|{doc.name}, page {page_idx}]]\n"

                for joined_highlight in joined_highlights:
                    highlight_text = " ".join(joined_highlight)
                    highlight_content += f"\n> {highlight_text}\n"

                highlight_content += "\n"

        if highlight_content:
            self.page_content[page_idx] = highlight_content
