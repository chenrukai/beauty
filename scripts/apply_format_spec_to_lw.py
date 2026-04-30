from pathlib import Path
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


DOC_PATH = Path(r"D:\beauty\lw.docx")
BACKUP_PATH = Path(r"D:\beauty\lw_before_format_spec.docx")


TOP_HEADING_RE = re.compile(r"^第[一二三四五六七八九十]+章\s*.+$")
SECOND_HEADING_RE = re.compile(r"^\d+\.\d+\s+.+$")
THIRD_HEADING_RE = re.compile(r"^\d+\.\d+\.\d+\s+.+$")
FIG_CAPTION_RE = re.compile(r"^图\s*\d+-\d+")
TABLE_TITLE_RE = re.compile(r"^表\s*\d+-\d+")
REF_LINE_RE = re.compile(r"^\[\d+\]")


def set_run_font(run, east_asia_font, ascii_font="Times New Roman", size=None, bold=None):
    run.font.name = ascii_font
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), east_asia_font)
    rfonts.set(qn("w:ascii"), ascii_font)
    rfonts.set(qn("w:hAnsi"), ascii_font)
    if size is not None:
        run.font.size = size
    if bold is not None:
        run.bold = bold


def set_page_break_before(paragraph, enabled=True):
    ppr = paragraph._p.get_or_add_pPr()
    elem = ppr.find(qn("w:pageBreakBefore"))
    if elem is not None:
        ppr.remove(elem)
    if enabled:
        pb = OxmlElement("w:pageBreakBefore")
        ppr.append(pb)


def format_heading(paragraph, level):
    pf = paragraph.paragraph_format
    pf.first_line_indent = Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    if level == 1:
        pf.space_before = Pt(12)
        pf.space_after = Pt(12)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        size = Pt(16)
    elif level == 2:
        pf.space_before = Pt(12)
        pf.space_after = Pt(12)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        size = Pt(15)
    else:
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        size = Pt(14)
    for run in paragraph.runs:
        set_run_font(run, "宋体", size=size, bold=True)


def format_body(paragraph, size=Pt(12), first_indent=True, center=False):
    pf = paragraph.paragraph_format
    pf.first_line_indent = Cm(0.74) if first_indent else Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY
    for run in paragraph.runs:
        set_run_font(run, "宋体", size=size, bold=False)


def format_abstract_title(paragraph, english=False):
    pf = paragraph.paragraph_format
    pf.first_line_indent = Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    pf.space_before = Pt(12)
    pf.space_after = Pt(12)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in paragraph.runs:
        set_run_font(run, "黑体" if not english else "Times New Roman", size=Pt(16), bold=True)


def format_keyword(paragraph, english=False):
    format_body(paragraph, size=Pt(12), first_indent=False)
    for idx, run in enumerate(paragraph.runs):
        if idx == 0:
            set_run_font(run, "黑体" if not english else "Times New Roman", size=Pt(12), bold=True)


def format_toc_title(paragraph):
    pf = paragraph.paragraph_format
    pf.first_line_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    pf.space_before = Pt(12)
    pf.space_after = Pt(12)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in paragraph.runs:
        set_run_font(run, "宋体", size=Pt(15), bold=True)


def format_toc_line(paragraph):
    pf = paragraph.paragraph_format
    pf.first_line_indent = Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    bold = paragraph.text.strip().startswith("第") or "摘要" in paragraph.text or "ABSTRACT" in paragraph.text or "目  录" in paragraph.text
    for run in paragraph.runs:
        set_run_font(run, "宋体", size=Pt(12), bold=bold)


def format_figure_caption(paragraph):
    pf = paragraph.paragraph_format
    pf.first_line_indent = Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    pf.space_before = Pt(0)
    pf.space_after = Pt(6)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in paragraph.runs:
        set_run_font(run, "宋体", size=Pt(10.5), bold=False)


def format_table_title(paragraph):
    pf = paragraph.paragraph_format
    pf.first_line_indent = Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    pf.space_before = Pt(6)
    pf.space_after = Pt(6)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in paragraph.runs:
        set_run_font(run, "宋体", size=Pt(10.5), bold=False)


def main():
    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_bytes(DOC_PATH.read_bytes())

    doc = Document(str(DOC_PATH))

    # Page setup from main body onward
    for sec in doc.sections:
        sec.top_margin = Cm(2.54)
        sec.bottom_margin = Cm(2.54)
        sec.left_margin = Cm(2.2)
        sec.right_margin = Cm(2.2)
        sec.header_distance = Cm(1.5)
        sec.footer_distance = Cm(1.5)

    body_started = False
    english_abstract = False
    toc_mode = False
    ref_mode = False
    ack_mode = False

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        if text == "摘    要":
            body_started = True
            english_abstract = False
            toc_mode = False
            ref_mode = False
            ack_mode = False
            format_abstract_title(para, english=False)
            set_page_break_before(para, False)
            continue

        if not body_started:
            continue

        if text == "ABSTRACT":
            english_abstract = True
            toc_mode = False
            ref_mode = False
            ack_mode = False
            format_abstract_title(para, english=True)
            set_page_break_before(para, True)
            continue

        if text == "目  录":
            english_abstract = False
            toc_mode = True
            ref_mode = False
            ack_mode = False
            format_toc_title(para)
            set_page_break_before(para, True)
            continue

        if text in {"结    论", "结论"}:
            toc_mode = False
            ref_mode = False
            ack_mode = False
            format_heading(para, 1)
            set_page_break_before(para, True)
            continue

        if text == "参考文献":
            toc_mode = False
            ref_mode = True
            ack_mode = False
            format_heading(para, 1)
            set_page_break_before(para, True)
            continue

        if text in {"致    谢", "致谢"}:
            toc_mode = False
            ref_mode = False
            ack_mode = True
            format_heading(para, 1)
            set_page_break_before(para, True)
            continue

        if toc_mode:
            # TOC content ends at first level-1 chapter title
            if text.startswith("第一章 "):
                toc_mode = False
            else:
                format_toc_line(para)
                continue

        if TOP_HEADING_RE.match(text):
            english_abstract = False
            ref_mode = False
            ack_mode = False
            format_heading(para, 1)
            set_page_break_before(para, True)
            continue

        if THIRD_HEADING_RE.match(text):
            format_heading(para, 3)
            continue

        if SECOND_HEADING_RE.match(text):
            format_heading(para, 2)
            continue

        if FIG_CAPTION_RE.match(text):
            format_figure_caption(para)
            continue

        if TABLE_TITLE_RE.match(text):
            format_table_title(para)
            continue

        if text.startswith("关键词："):
            format_keyword(para, english=False)
            continue

        if text.startswith("Key words:"):
            format_keyword(para, english=True)
            continue

        if ref_mode or REF_LINE_RE.match(text):
            format_body(para, size=Pt(10.5), first_indent=False)
            continue

        if ack_mode:
            format_body(para, size=Pt(10.5), first_indent=True)
            continue

        format_body(para, size=Pt(12), first_indent=True)

    # Table cell font
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if para.text.strip():
                        format_body(para, size=Pt(10.5), first_indent=False, center=True)

    doc.save(str(DOC_PATH))


if __name__ == "__main__":
    main()
