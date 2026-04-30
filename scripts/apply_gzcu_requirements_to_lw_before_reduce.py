from copy import deepcopy
from pathlib import Path
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


DOC_PATH = Path(r"D:\beauty\lw_before_reduce.docx")
BACKUP_PATH = Path(r"D:\beauty\lw_before_reduce_before_gzcu_req.docx")


TOP_HEADING_RE = re.compile(r"^第[一二三四五六七八九十]+章\s+.+$")
SECOND_HEADING_RE = re.compile(r"^\d+\.\d+\s+.+$")
THIRD_HEADING_RE = re.compile(r"^\d+\.\d+\.\d+\s+.+$")
FIG_CAPTION_RE = re.compile(r"^图\s*\d+-\d+")
TABLE_TITLE_RE = re.compile(r"^表\s*\d+-\d+")


def set_run_font(run, east_asia_font, ascii_font=None, size=None, bold=None):
    if ascii_font is None:
        ascii_font = east_asia_font
    run.font.name = ascii_font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), east_asia_font)
    run._element.rPr.rFonts.set(qn("w:ascii"), ascii_font)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), ascii_font)
    if size is not None:
        run.font.size = size
    if bold is not None:
        run.bold = bold


def clear_page_break_before(paragraph):
    ppr = paragraph._p.get_or_add_pPr()
    pbb = ppr.find(qn("w:pageBreakBefore"))
    if pbb is not None:
        ppr.remove(pbb)


def set_page_break_before(paragraph, enabled=True):
    clear_page_break_before(paragraph)
    if enabled:
        ppr = paragraph._p.get_or_add_pPr()
        elem = OxmlElement("w:pageBreakBefore")
        ppr.append(elem)


def normalize_paragraph(paragraph):
    text = paragraph.text.strip()
    if not text:
        return
    # remove manual page breaks embedded in a paragraph; page starts are handled on headings
    for run in paragraph.runs:
        brs = run._element.findall(".//w:br", run._element.nsmap)
        for br in brs:
            if br.get(qn("w:type")) == "page":
                run._element.remove(br)


def format_heading(paragraph, level):
    pf = paragraph.paragraph_format
    pf.first_line_indent = Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    pf.space_before = Pt(12)
    pf.space_after = Pt(12)

    if level == 1:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        size = Pt(16)
    elif level == 2:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        size = Pt(15)
    else:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        size = Pt(14)
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)

    for run in paragraph.runs:
        set_run_font(run, "宋体", ascii_font="Times New Roman", size=size, bold=True)


def format_body(paragraph, english=False):
    pf = paragraph.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.first_line_indent = Cm(0.74)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    font_cn = "宋体"
    font_en = "Times New Roman" if english else "Times New Roman"
    for run in paragraph.runs:
        set_run_font(run, font_cn, ascii_font=font_en, size=Pt(12), bold=False)


def format_keyword(paragraph, english=False):
    format_body(paragraph, english=english)
    pf = paragraph.paragraph_format
    pf.first_line_indent = Pt(0)
    for idx, run in enumerate(paragraph.runs):
        txt = run.text
        if idx == 0 and ("关键词" in txt or "Key words" in txt):
            set_run_font(run, "黑体" if not english else "Times New Roman", ascii_font="Times New Roman", size=Pt(12), bold=True)


def format_figure_caption(paragraph):
    pf = paragraph.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.first_line_indent = Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    pf.space_before = Pt(0)
    pf.space_after = Pt(6)
    for run in paragraph.runs:
        set_run_font(run, "宋体", ascii_font="Times New Roman", size=Pt(10.5), bold=False)


def format_table_title(paragraph):
    pf = paragraph.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.first_line_indent = Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    pf.space_before = Pt(6)
    pf.space_after = Pt(6)
    for run in paragraph.runs:
        set_run_font(run, "宋体", ascii_font="Times New Roman", size=Pt(10.5), bold=False)


def format_toc(paragraph):
    pf = paragraph.paragraph_format
    pf.first_line_indent = Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    for run in paragraph.runs:
        set_run_font(run, "宋体", ascii_font="Times New Roman", size=Pt(12), bold=False)


def format_table_cells(document):
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    txt = paragraph.text.strip()
                    if not txt:
                        continue
                    pf = paragraph.paragraph_format
                    pf.first_line_indent = Pt(0)
                    pf.left_indent = Pt(0)
                    pf.right_indent = Pt(0)
                    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
                    pf.line_spacing = Pt(20)
                    pf.space_before = Pt(0)
                    pf.space_after = Pt(0)
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in paragraph.runs:
                        set_run_font(run, "宋体", ascii_font="Times New Roman", size=Pt(10.5), bold=False)


def main():
    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_bytes(DOC_PATH.read_bytes())

    doc = Document(str(DOC_PATH))

    body_started = False
    english_abstract = False
    toc_mode = False

    for para in doc.paragraphs:
        text = para.text.strip()
        normalize_paragraph(para)
        if not text:
            continue

        if text == "摘    要":
            body_started = True
            english_abstract = False
            toc_mode = False
            format_heading(para, 1)
            set_page_break_before(para, False)
            continue

        if not body_started:
            # keep the first two pages and front template untouched
            continue

        if text == "ABSTRACT":
            english_abstract = True
            toc_mode = False
            format_heading(para, 1)
            continue

        if text == "目  录":
            english_abstract = False
            toc_mode = True
            format_heading(para, 1)
            continue

        if toc_mode:
            if text.startswith("第一章 "):
                toc_mode = False
            else:
                format_toc(para)
                continue

        if TOP_HEADING_RE.match(text) or text in {"结论", "结    论", "参考文献", "致谢", "致    谢"}:
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

        format_body(para, english=english_abstract)

    format_table_cells(doc)
    doc.save(str(DOC_PATH))


if __name__ == "__main__":
    main()
