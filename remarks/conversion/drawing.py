import logging

import fitz  # PyMuPDF
import shapely.geometry as geom  # Shapely

from rmscene.scene_items import PenColor

from .parsing import TLayers, TTextBlock
from ..utils import (
    RM_WIDTH,
    RM_HEIGHT,
)

# Taken from github:ricklupton/rmc:src/rmc/exporters/writing_tools.py#remarkable_palette
RM_TOOL_TO_FITZ_COLOR = {
    PenColor.BLACK: (0, 0, 0),
    PenColor.GRAY: (144/255, 144/255, 144/255),
    PenColor.WHITE: (1, 1, 1),
    PenColor.YELLOW: (251/255, 247/255, 25/255),
    PenColor.GREEN: (0, 255/255, 0),
    PenColor.PINK: (255/255, 192/255, 203/255),
    PenColor.BLUE: (78/255, 105/255, 201/255),
    PenColor.RED: (179/255, 62/255, 57/255),
    PenColor.GRAY_OVERLAP: (125/255, 125/255, 125/255),
    #! Skipped as different colors are used for highlights
    #! PenColor.HIGHLIGHT = ...
    PenColor.GREEN_2: (161/255, 216/255, 125/255),
    PenColor.CYAN: (139/255, 208/255, 229/255),
    PenColor.MAGENTA: (183/255, 130/255, 205/255),
    PenColor.YELLOW_2: (247/255, 232/255, 81/255)
}


def draw_svg(data, dims={"x": RM_WIDTH, "y": RM_HEIGHT}):
    output = f'<svg xmlns="http://www.w3.org/2000/svg" width="{dims["x"]}" height="{dims["y"]}">'

    output += """
        <script type="application/ecmascript"> <![CDATA[
            var visiblePage = 'p1';
            function goToPage(page) {
                document.getElementById(visiblePage).setAttribute('style', 'display: none');
                document.getElementById(page).setAttribute('style', 'display: inline');
                visiblePage = page;
            }
        ]]> </script>
    """

    for i, layer in enumerate(data["layers"]):
        output += f'<g id="layer-{i}" style="display:inline">'

        for st_name, st_content in layer["strokes"].items():
            output += f'<g id="stroke-{st_name}" style="display:inline">'
            st_color = RM_TOOL_TO_FITZ_COLOR[st_content["tool"]["color-code"]]

            for sg_name, sg_content in st_content["segments"].items():
                sg_width = sg_content["style"]["stroke-width"]
                sg_opacity = sg_content["style"]["opacity"]

                for segment in sg_content["points"]:
                    output += f'<polyline style="fill:none;stroke:{st_color};stroke-width:{sg_width};opacity:{sg_opacity}" points="'

                    for point in segment:
                        output += f"{point[0]},{point[1]} "

                    output += '" />\n'

            output += "</g>"  # Close stroke

        output += "</g>"  # Close layer

    # Overlay it with a clickable rect for flipping pages
    output += (
        f'<rect x="0" y="0" width="{dims["x"]}" height="{dims["y"]}" fill-opacity="0"/>'
    )

    output += "</svg>"

    return output


def prepare_segments(data: TLayers):
    segs = {}

    for layer in data["layers"]:
        for st_name, st_content in layer["strokes"].items():
            for i, sg_content in enumerate(st_content["segments"]):
                name = f"{st_name}_{i}"
                segs[name] = {}

                segs[name]["stroke-width"] = float(sg_content["style"]["stroke-width"])

                segs[name]["opacity"] = float(sg_content["style"]["opacity"])
                segs[name]["color-code"] = sg_content["style"]["color-code"]

                segs[name]["points"] = []
                segs[name]["lines"] = []
                segs[name]["rects"] = []

                for segment in sg_content["points"]:
                    points = []
                    if len(segment) <= 1:
                        # line needs at least two points, see testcase v2_notebook_complex
                        continue
                    for p in segment:
                        points.append((float(p[0]), float(p[1])))
                    if len(points) <= 1:
                        # line needs at least two points, see testcase v2_notebook_complex
                        continue

                    segs[name]["points"].append(points)
                    line = geom.LineString(points)
                    segs[name]["lines"].append(line)

                    if line.length > 0.0:
                        segs[name]["rects"].append(fitz.Rect(*line.bounds))
        for i, rmRectangle in enumerate(layer["rectangles"]):
            name = f"Highlighter_{i}"
            segs[name] = {}

            segs[name]["color-code"] = rmRectangle["color"]
            segs[name]["points"] = []
            segs[name]["lines"] = []
            segs[name]["rects"] = []
            for geomRectangle in rmRectangle["rectangles"]:
                segs[name]["rects"].append(
                    fitz.Rect(
                        geomRectangle.x,
                        geomRectangle.y,
                        geomRectangle.x + geomRectangle.w,
                        geomRectangle.y + geomRectangle.h,
                    )
                )

    return segs

def cursor_newline(cursor: fitz.Point, font, fontsize):
    HORIZONTAL_START = 40
    line_height = get_line_height(font, fontsize)
    return fitz.Point(HORIZONTAL_START, cursor.y + line_height)

def get_line_height(font, font_size):
    ascender = font.ascender
    descender = font.descender

    line_height = (ascender - descender) * font_size

    return line_height

def layout_text(text, page_width, margin_x, font, fontsize):
    words = text.split()
    lines = []
    current_line = []
    line_width = 0
    max_width = page_width - margin_x * 2

    space_width = fitz.get_text_length(" ", font.name, fontsize=fontsize)

    for word in words:
        word_with = fitz.get_text_length(word, font.name, fontsize=fontsize)
        if line_width + word_with <= max_width:
            current_line.append(word)
            line_width += word_with + space_width
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            line_width = word_with + space_width

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def draw_annotations_on_pdf(data: TLayers, page, inplace=False):
    FONT_SIZE_PLAIN = 11
    FONT_SIZE_HEADING = 22
    segments = prepare_segments(data)

    # def visit_span(
    #     span: CrdtStr,
    #     cursor: fitz.Point,
    #     font: fitz.Font,
    #     fontsize=11,
    # ):
    #     # font = plain_font
    #     # lines = layout_text(str(span), 445, 40, font, fontsize)
    #     # for line in lines:
    #     #     _, cursor = plain_writer.append(cursor, line, font=font, fontsize=fontsize)
    #     #     cursor = cursor_newline(cursor, font, fontsize=fontsize)
    #     #
    #     # return cursor

    # plain_writer = fitz.TextWriter(page.rect)
    # plain_font = fitz.Font("helv")
    # italic_font = fitz.Font("helvetica-oblique", is_italic=True)
    # bold_font = fitz.Font("helvetica-bold", is_bold=True)
    # bold_italic_font = fitz.Font(
    #     "helvetica-boldoblique",
    #     is_bold=True,
    #     is_italic=True,
    # )

    # if data['text']:
    #     text_block: TTextBlock = data['text']
    #     text = data['text']['text']
    #     # Initialize cursor
    #     horizontal_start_position = text_block['pos_x'] / 3.155
    #     cursor = fitz.Point(horizontal_start_position, text_block['pos_y'] / 3.155)
    #     print(f"There are {len(text.contents)} paragraphs on this page")
    #     print(f"The text starts at ({text_block['pos_x'] / 3.155}, {text_block['pos_y'] / 3.155})")
    #     for paragraph in text.contents:
    #         if len(str(paragraph)) > 0:
    #             for span in paragraph.contents:
    #                 if paragraph.style.value == ParagraphStyle.HEADING:
    #                     cursor = visit_span(span, cursor, plain_font, fontsize=FONT_SIZE_HEADING)
    #                 else:
    #                     cursor = visit_span(span, cursor, plain_font, fontsize=FONT_SIZE_PLAIN)
    #                     cursor = cursor_newline(cursor, plain_font, fontsize=FONT_SIZE_PLAIN)
    #
    # plain_writer.write_text(page)

    # annot.update() calls have a lot of overhead.
    # We can batch tools with equal settings to reduce the amount of calls drastically
    batched_lines_per_tool = {}
    for seg_name, seg_data in segments.items():
        seg_type = seg_name.split("_")[0]

        # Highlights that were not recognized by reMarkable's own software,
        # these ones are "old style" and we must handle them ourselves

        # By "old style" I mean before Software releases 2.7 and 2.11
        # - https://support.remarkable.com/s/article/Software-release-2-7
        # - https://support.remarkable.com/s/article/Software-release-2-11

        if seg_type == "Highlighter":
            # If there are multiple rectangles per segment, do not want to
            # loop over them. Instead, just send them all to addHighlightAnnot.
            # It can handle a list of rectangles and will join them into one
            # annotation.

            # Sometimes small highlights will not be valid. If so, just print
            # a warning and carry on
            try:
                # https://pymupdf.readthedocs.io/en/latest/recipes-annotations.html#how-to-add-and-modify-annotations
                annot = page.add_highlight_annot(seg_data["rects"])

                try:
                    color_array = fitz.utils.getColor(
                        RM_TOOL_TO_FITZ_COLOR[seg_data["color-code"]]
                    )
                except KeyError:
                    # Defaults to yellow if color hasn't been defined yet
                    color_array = fitz.utils.getColor("yellow")

                annot.set_colors(stroke=color_array)

                annot.set_opacity(seg_data["opacity"])
                annot.set_border(width=seg_data["stroke-width"])
                annot.update()
            except Exception as e:
                logging.warning(
                    f"- Just ran into an exception while adding a highlight. It probably happened because of a small highlight that PyMuPDF couldn't handle well enough: {e}"
                )

        # Scribbles
        else:
            # add all lines with the same tool-configuration to the same batch, using a key for their config
            if seg_type == "Eraser":
                # overwrite color to always be white for erasers
                batch_key = (seg_data["stroke-width"], seg_data["opacity"], 2)
            else:
                batch_key = (
                    seg_data["stroke-width"],
                    seg_data["opacity"],
                    seg_data["color-code"],
                )

            if batch_key in batched_lines_per_tool:
                batch_points = batched_lines_per_tool[batch_key]
            else:
                batch_points = []
                batched_lines_per_tool[batch_key] = batch_points

            for seg_points in seg_data["points"]:
                batch_points.append(seg_points)

    # draw the batched lines
    for (stroke_width, opacity, color_code), points in batched_lines_per_tool.items():
        annot = page.add_ink_annot(points)
        annot.set_border(width=stroke_width)
        annot.set_opacity(opacity)

        color_array = RM_TOOL_TO_FITZ_COLOR[color_code]
        annot.set_colors(stroke=color_array)

        annot.update()

    if not inplace:
        return page


# Highlights from reMarkable's own "smart" highlighting (introduced in 2.7)
def add_smart_highlight_annotations(hl_data, page, scale, inplace=False):
    hl_list = hl_data["highlights"][0]

    for hl in hl_list:
        quads = page.search_for(hl["text"], quads=True)
        # Allowing for some padding around the hl["rects"]
        padding = 2

        # If page.search_for finds too many occurences of hl["text"]
        #
        # This often happens when hl["text"] is a very short string (e.g. "re")
        # - https://github.com/lucasrla/remarks/issues/57
        if len(quads) > len(hl["rects"]):
            logging.debug(
                "- Found several occurences of highlighted text on the same page. Will restrict search to their clip area"
            )

            points = []
            for r in hl["rects"]:
                points.append((r["x"] - padding, r["y"] - padding))
                points.append((r["x"] + r["width"] + padding, r["y"] - padding))
                points.append((r["x"] - padding, r["y"] + r["height"] + padding))
                points.append(
                    (
                        r["x"] + r["width"] + padding,
                        r["y"] + r["height"] + padding,
                    )
                )

            envelope = geom.MultiPoint(points).bounds
            # `bounds` returns minimum bounding region (minx, miny, maxx, maxy)

            scaled_envelope = [float(coord) * scale for coord in envelope]

            quads = page.search_for(
                hl["text"], quads=True, clip=fitz.Rect(scaled_envelope)
            )

        # If page.search_for cannot find hl["text"] in the PDF page
        # This fix was inspired by @danieluhricek posts at
        # - https://github.com/lucasrla/remarks/issues/52
        if not quads:
            logging.debug(
                "- Couldn't get the highlighted text on the PDF. Will annotate based on their rects"
            )

            quads = [
                fitz.Rect(
                    (rect["x"] - padding) * scale,
                    (rect["y"] - padding) * scale,
                    (rect["x"] + rect["width"] + padding) * scale,
                    (rect["y"] + rect["height"] + padding) * scale,
                )
                for rect in hl["rects"]
            ]

        annot = page.add_highlight_annot(quads)

        # Support to colors
        try:
            color_array =RM_TOOL_TO_FITZ_COLOR[hl["color"]]
        except KeyError:
            # Defaults to yellow if color hasn't been defined yet
            color_array = fitz.utils.getColor("yellow")

        annot.set_colors(stroke=color_array)

        annot.update()

    if not inplace:
        return page
