from __future__ import annotations

import html
import re
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(r"D:\beauty")
SOURCE_DOCX = ROOT / "毕业论文_完整草稿_已填信息.docx"
SOURCE_MD = ROOT / "毕业论文_正文提取版_按材料修订稿.md"
OUTPUT_DOCX = ROOT / "毕业论文_完整草稿_按材料修订.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


def w_tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def para_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def esc(text: str) -> str:
    return html.escape(text.strip())


def render_runs(text: str, size: int = 24, superscript_refs: bool = False) -> str:
    if not superscript_refs:
        return (
            f"<w:r><w:rPr><w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
            f"<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>"
        )
    pattern = re.compile(r"\[(\d+)\]")
    parts: list[str] = []
    last = 0
    for match in pattern.finditer(text):
        normal = text[last:match.start()]
        if normal:
            parts.append(
                f"<w:r><w:rPr><w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
                f"<w:t xml:space=\"preserve\">{esc(normal)}</w:t></w:r>"
            )
        parts.append(
            "<w:r><w:rPr><w:vertAlign w:val=\"superscript\"/><w:sz w:val=\"18\"/>"
            "<w:szCs w:val=\"18\"/></w:rPr>"
            f"<w:t>{match.group(1)}</w:t></w:r>"
        )
        last = match.end()
    tail = text[last:]
    if tail:
        parts.append(
            f"<w:r><w:rPr><w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
            f"<w:t xml:space=\"preserve\">{esc(tail)}</w:t></w:r>"
        )
    return "".join(parts)


def p_body(text: str, indent: bool = True, superscript_refs: bool = False) -> str:
    ind = "<w:ind w:firstLineChars=\"200\"/>" if indent else ""
    return (
        "<w:p><w:pPr><w:jc w:val=\"both\"/><w:spacing w:line=\"400\" w:lineRule=\"exact\"/>"
        f"{ind}</w:pPr>{render_runs(text, 24, superscript_refs)}</w:p>"
    )


def p_center(text: str, size: int = 24, bold: bool = False) -> str:
    b = "<w:b/>" if bold else ""
    return (
        "<w:p><w:pPr><w:jc w:val=\"center\"/><w:spacing w:line=\"360\" w:lineRule=\"auto\"/></w:pPr>"
        f"<w:r><w:rPr>{b}<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
        f"<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r></w:p>"
    )


def p_h1(text: str) -> str:
    return (
        "<w:p><w:pPr><w:pageBreakBefore/><w:jc w:val=\"center\"/></w:pPr>"
        "<w:r><w:rPr><w:b/><w:sz w:val=\"32\"/><w:szCs w:val=\"32\"/></w:rPr>"
        f"<w:t>{esc(text)}</w:t></w:r></w:p>"
    )


def p_h2(text: str) -> str:
    return (
        "<w:p><w:pPr><w:jc w:val=\"left\"/></w:pPr>"
        "<w:r><w:rPr><w:b/><w:sz w:val=\"28\"/><w:szCs w:val=\"28\"/></w:rPr>"
        f"<w:t>{esc(text)}</w:t></w:r></w:p>"
    )


def parse_fragment(xml_text: str) -> ET.Element:
    wrapper = f'<root xmlns:w="{W_NS}">{xml_text}</root>'
    return ET.fromstring(wrapper)[0]


def markdown_to_blocks(text: str) -> list[ET.Element]:
    lines = text.splitlines()
    blocks: list[ET.Element] = []
    i = 0
    in_body = False

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("## 中文摘要"):
            in_body = True
            blocks.append(parse_fragment(p_h1("摘    要")))
            i += 1
            continue

        if not in_body:
            i += 1
            continue

        if stripped.startswith("## Abstract"):
            blocks.append(parse_fragment(p_h1("ABSTRACT")))
            i += 1
            continue

        if stripped.startswith("## 第一章") or stripped.startswith("## 第二章") or stripped.startswith("## 第三章") or stripped.startswith("## 第四章") or stripped.startswith("## 第五章") or stripped.startswith("## 第六章"):
            blocks.append(parse_fragment(p_h1(stripped[3:].strip())))
            i += 1
            continue

        if stripped.startswith("## 结论"):
            blocks.append(parse_fragment(p_h1("结    论")))
            i += 1
            continue

        if stripped.startswith("## 参考文献"):
            blocks.append(parse_fragment(p_h1("参考文献")))
            i += 1
            continue

        if stripped.startswith("## 致谢"):
            blocks.append(parse_fragment(p_h1("致    谢")))
            i += 1
            continue

        if stripped.startswith("### "):
            blocks.append(parse_fragment(p_h2(stripped[4:].strip())))
            i += 1
            continue

        if stripped.startswith("关键词：") or stripped.startswith("Key words:"):
            blocks.append(parse_fragment(p_body(stripped, indent=False)))
            i += 1
            continue

        if stripped.startswith("- "):
            blocks.append(parse_fragment(p_body(stripped[2:].strip(), indent=False)))
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            blocks.append(build_table(table_lines))
            continue

        superscript = not (stripped.startswith("[") and "] " in stripped)
        blocks.append(parse_fragment(p_body(stripped, superscript_refs=superscript)))
        i += 1

    return blocks


def build_table(table_lines: list[str]) -> ET.Element:
    rows = []
    for idx, line in enumerate(table_lines):
        parts = [cell.strip() for cell in line.strip("|").split("|")]
        if idx == 1 and all(set(cell) <= {"-", " "} for cell in parts):
            continue
        rows.append(parts)

    col_count = max(len(r) for r in rows)
    grid = "".join('<w:gridCol w:w="1800"/>' for _ in range(col_count))
    tr_xml = []
    for r_idx, row in enumerate(rows):
        cells = []
        for cell in row:
            if r_idx == 0:
                content = p_center(cell, size=22, bold=True)
            else:
                content = p_body(cell, indent=False)
            cells.append(
                "<w:tc><w:tcPr><w:tcW w:w=\"1800\" w:type=\"dxa\"/></w:tcPr>"
                f"{content}</w:tc>"
            )
        tr_xml.append("<w:tr>" + "".join(cells) + "</w:tr>")

    tbl_xml = (
        "<w:tbl><w:tblPr>"
        "<w:tblW w:w=\"0\" w:type=\"auto\"/>"
        "<w:tblBorders>"
        "<w:top w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:left w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:right w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "</w:tblBorders></w:tblPr>"
        f"<w:tblGrid>{grid}</w:tblGrid>{''.join(tr_xml)}</w:tbl>"
    )
    return parse_fragment(tbl_xml)


def main() -> None:
    md_text = SOURCE_MD.read_text(encoding="utf-8")
    blocks = markdown_to_blocks(md_text)

    with zipfile.ZipFile(SOURCE_DOCX, "r") as zf:
        files = {name: zf.read(name) for name in zf.namelist()}

    root = ET.fromstring(files["word/document.xml"])
    body = root.find("w:body", NS)
    if body is None:
        raise RuntimeError("源文档缺少 body 节点")

    keep_nodes: list[ET.Element] = []
    sect = body.find("w:sectPr", NS)
    for node in list(body):
        if node.tag == w_tag("sectPr"):
            continue
        if node.tag == w_tag("p") and "摘 要" in para_text(node):
            break
        keep_nodes.append(deepcopy(node))

    for node in list(body):
        body.remove(node)
    for node in keep_nodes:
        body.append(node)
    for block in blocks:
        body.append(block)
    if sect is not None:
        body.append(sect)

    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(OUTPUT_DOCX, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)

    print(OUTPUT_DOCX)


if __name__ == "__main__":
    main()
