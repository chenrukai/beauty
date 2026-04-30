from __future__ import annotations

import html
import re
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(r"D:\beauty")
MD_PATH = ROOT / "毕业论文_正文提取版_按材料修订稿.md"
SOURCE_DOCX = ROOT / "毕业论文_完整草稿_按材料修订_补用例.docx"
OUTPUT_DOCX = ROOT / "毕业论文_完整草稿_按材料修订_补图版.docx"
ASSET_DIR = ROOT / "论文图表素材"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}

ASSETS = {
    "fig_4_1_detail_collaboration.spec.yaml": """meta:
  title: "图4-1 系统详细设计模块协作图"
  source: "thesis"
diagram:
  type: architecture
  style: grayscale
  modules:
    - 前端交互层
    - 接口服务层
    - 业务处理层
    - 智能服务层
    - 数据与存储层
""",
    "fig_4_1_detail_collaboration.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="520" viewBox="0 0 1080 520">
  <rect width="1080" height="520" fill="#ffffff"/>
  <g fill="none" stroke="#000000" stroke-width="2" font-family="SimSun, serif" text-anchor="middle">
    <rect x="70" y="200" width="160" height="90"/><text x="150" y="252" font-size="22">前端交互层</text>
    <rect x="280" y="200" width="160" height="90"/><text x="360" y="252" font-size="22">接口服务层</text>
    <rect x="490" y="200" width="160" height="90"/><text x="570" y="252" font-size="22">业务处理层</text>
    <rect x="700" y="200" width="160" height="90"/><text x="780" y="252" font-size="22">智能服务层</text>
    <rect x="910" y="200" width="120" height="90"/><text x="970" y="240" font-size="20">数据与</text><text x="970" y="268" font-size="20">存储层</text>
    <rect x="70" y="70" width="160" height="70"/><text x="150" y="112" font-size="20">用户端页面</text>
    <rect x="70" y="360" width="160" height="70"/><text x="150" y="402" font-size="20">管理端页面</text>
    <rect x="490" y="70" width="160" height="70"/><text x="570" y="112" font-size="20">认证与权限</text>
    <rect x="490" y="360" width="160" height="70"/><text x="570" y="402" font-size="20">知识与文件处理</text>
    <rect x="700" y="70" width="160" height="70"/><text x="780" y="112" font-size="20">图谱服务</text>
    <rect x="700" y="360" width="160" height="70"/><text x="780" y="402" font-size="20">问答服务</text>
  </g>
  <g stroke="#000000" stroke-width="2" marker-end="url(#arrow)">
    <defs>
      <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
        <path d="M0,0 L0,6 L9,3 z" fill="#000000"/>
      </marker>
    </defs>
    <line x1="230" y1="245" x2="280" y2="245"/>
    <line x1="440" y1="245" x2="490" y2="245"/>
    <line x1="650" y1="245" x2="700" y2="245"/>
    <line x1="860" y1="245" x2="910" y2="245"/>
    <line x1="150" y1="140" x2="150" y2="200"/>
    <line x1="150" y1="360" x2="150" y2="290"/>
    <line x1="570" y1="140" x2="570" y2="200"/>
    <line x1="570" y1="360" x2="570" y2="290"/>
    <line x1="780" y1="140" x2="780" y2="200"/>
    <line x1="780" y1="360" x2="780" y2="290"/>
  </g>
</svg>""",
    "fig_4_2_frontend_navigation.spec.yaml": """meta:
  title: "图4-2 用户端页面跳转关系图"
  source: "thesis"
diagram:
  type: flow
  style: grayscale
""",
    "fig_4_2_frontend_navigation.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="980" height="420" viewBox="0 0 980 420">
  <rect width="980" height="420" fill="#ffffff"/>
  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#000000"/></marker></defs>
  <g fill="none" stroke="#000000" stroke-width="2" font-family="SimSun, serif" text-anchor="middle">
    <rect x="60" y="150" width="150" height="70"/><text x="135" y="193" font-size="22">首页</text>
    <rect x="280" y="60" width="170" height="70"/><text x="365" y="103" font-size="22">知识列表/搜索</text>
    <rect x="280" y="240" width="170" height="70"/><text x="365" y="283" font-size="22">公告与推荐入口</text>
    <rect x="530" y="60" width="150" height="70"/><text x="605" y="103" font-size="22">知识详情</text>
    <rect x="530" y="240" width="150" height="70"/><text x="605" y="283" font-size="22">收藏管理</text>
    <rect x="760" y="150" width="160" height="70"/><text x="840" y="193" font-size="22">智能问答</text>
    <rect x="760" y="300" width="160" height="70"/><text x="840" y="343" font-size="22">附件追问</text>
  </g>
  <g stroke="#000000" stroke-width="2" marker-end="url(#arrow)">
    <line x1="210" y1="170" x2="280" y2="110"/>
    <line x1="210" y1="200" x2="280" y2="275"/>
    <line x1="450" y1="95" x2="530" y2="95"/>
    <line x1="450" y1="275" x2="530" y2="275"/>
    <line x1="680" y1="95" x2="760" y2="170"/>
    <line x1="680" y1="275" x2="760" y2="205"/>
    <line x1="840" y1="220" x2="840" y2="300"/>
  </g>
</svg>""",
    "fig_4_3_knowledge_manage_flow.spec.yaml": """meta:
  title: "图4-3 知识管理模块处理流程图"
  source: "thesis"
diagram:
  type: flow
  style: grayscale
""",
    "fig_4_3_knowledge_manage_flow.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="300" viewBox="0 0 1100 300">
  <rect width="1100" height="300" fill="#ffffff"/>
  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#000000"/></marker></defs>
  <g fill="none" stroke="#000000" stroke-width="2" font-family="SimSun, serif" text-anchor="middle">
    <rect x="40" y="110" width="130" height="70"/><text x="105" y="153" font-size="20">知识录入</text>
    <rect x="220" y="110" width="150" height="70"/><text x="295" y="153" font-size="20">分类与状态校验</text>
    <rect x="420" y="110" width="150" height="70"/><text x="495" y="153" font-size="20">写入知识主表</text>
    <rect x="620" y="110" width="150" height="70"/><text x="695" y="153" font-size="20">关联附件与切片</text>
    <rect x="820" y="110" width="120" height="70"/><text x="880" y="153" font-size="20">分页检索</text>
    <rect x="970" y="110" width="90" height="70"/><text x="1015" y="153" font-size="20">详情展示</text>
  </g>
  <g stroke="#000000" stroke-width="2" marker-end="url(#arrow)">
    <line x1="170" y1="145" x2="220" y2="145"/>
    <line x1="370" y1="145" x2="420" y2="145"/>
    <line x1="570" y1="145" x2="620" y2="145"/>
    <line x1="770" y1="145" x2="820" y2="145"/>
    <line x1="940" y1="145" x2="970" y2="145"/>
  </g>
</svg>""",
    "fig_4_4_file_processing_flow.spec.yaml": """meta:
  title: "图4-4 文件处理模块流程图"
  source: "thesis"
diagram:
  type: flow
  style: grayscale
""",
    "fig_4_4_file_processing_flow.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="320" viewBox="0 0 1180 320">
  <rect width="1180" height="320" fill="#ffffff"/>
  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#000000"/></marker></defs>
  <g fill="none" stroke="#000000" stroke-width="2" font-family="SimSun, serif" text-anchor="middle">
    <rect x="30" y="120" width="120" height="70"/><text x="90" y="163" font-size="20">文件上传</text>
    <rect x="190" y="120" width="140" height="70"/><text x="260" y="163" font-size="20">对象存储与登记</text>
    <polygon points="390,115 470,155 390,195 310,155" fill="none"/><text x="390" y="161" font-size="18">文件类型判断</text>
    <rect x="510" y="60" width="130" height="60"/><text x="575" y="97" font-size="18">OCR 解析</text>
    <rect x="510" y="190" width="130" height="60"/><text x="575" y="227" font-size="18">Whisper 转写</text>
    <rect x="700" y="120" width="130" height="70"/><text x="765" y="163" font-size="18">文本清洗</text>
    <rect x="870" y="120" width="130" height="70"/><text x="935" y="163" font-size="18">切片处理</text>
    <rect x="1040" y="120" width="110" height="70"/><text x="1095" y="163" font-size="18">进入抽取</text>
  </g>
  <g stroke="#000000" stroke-width="2" marker-end="url(#arrow)">
    <line x1="150" y1="155" x2="190" y2="155"/>
    <line x1="330" y1="155" x2="310" y2="155"/>
    <line x1="470" y1="145" x2="510" y2="90"/>
    <line x1="470" y1="165" x2="510" y2="220"/>
    <line x1="640" y1="90" x2="700" y2="145"/>
    <line x1="640" y1="220" x2="700" y2="165"/>
    <line x1="830" y1="155" x2="870" y2="155"/>
    <line x1="1000" y1="155" x2="1040" y2="155"/>
  </g>
</svg>""",
    "fig_4_5_graph_query_flow.spec.yaml": """meta:
  title: "图4-5 知识图谱查询流程图"
  source: "thesis"
diagram:
  type: flow
  style: grayscale
""",
    "fig_4_5_graph_query_flow.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="320" viewBox="0 0 1080 320">
  <rect width="1080" height="320" fill="#ffffff"/>
  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#000000"/></marker></defs>
  <g fill="none" stroke="#000000" stroke-width="2" font-family="SimSun, serif" text-anchor="middle">
    <rect x="40" y="120" width="140" height="70"/><text x="110" y="163" font-size="20">输入实体条件</text>
    <rect x="240" y="120" width="150" height="70"/><text x="315" y="163" font-size="20">查询图谱节点</text>
    <rect x="450" y="50" width="150" height="70"/><text x="525" y="93" font-size="20">邻居查询</text>
    <rect x="450" y="190" width="150" height="70"/><text x="525" y="233" font-size="20">路径查询</text>
    <rect x="670" y="120" width="150" height="70"/><text x="745" y="163" font-size="20">证据文本回填</text>
    <rect x="880" y="120" width="150" height="70"/><text x="955" y="163" font-size="20">图谱结果展示</text>
  </g>
  <g stroke="#000000" stroke-width="2" marker-end="url(#arrow)">
    <line x1="180" y1="155" x2="240" y2="155"/>
    <line x1="390" y1="145" x2="450" y2="85"/>
    <line x1="390" y1="165" x2="450" y2="225"/>
    <line x1="600" y1="85" x2="670" y2="145"/>
    <line x1="600" y1="225" x2="670" y2="165"/>
    <line x1="820" y1="155" x2="880" y2="155"/>
  </g>
</svg>""",
    "fig_4_6_qa_flow.spec.yaml": """meta:
  title: "图4-6 智能问答模块流程图"
  source: "thesis"
diagram:
  type: flow
  style: grayscale
""",
    "fig_4_6_qa_flow.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="320" viewBox="0 0 1180 320">
  <rect width="1180" height="320" fill="#ffffff"/>
  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#000000"/></marker></defs>
  <g fill="none" stroke="#000000" stroke-width="2" font-family="SimSun, serif" text-anchor="middle">
    <rect x="30" y="120" width="120" height="70"/><text x="90" y="163" font-size="18">问题输入</text>
    <rect x="180" y="120" width="130" height="70"/><text x="245" y="163" font-size="18">关键词检索</text>
    <rect x="340" y="120" width="130" height="70"/><text x="405" y="163" font-size="18">向量召回</text>
    <rect x="500" y="120" width="130" height="70"/><text x="565" y="163" font-size="18">融合排序</text>
    <rect x="660" y="120" width="140" height="70"/><text x="730" y="163" font-size="18">上下文构建</text>
    <rect x="840" y="120" width="130" height="70"/><text x="905" y="163" font-size="18">流式生成</text>
    <rect x="1000" y="120" width="140" height="70"/><text x="1070" y="150" font-size="18">返回答案与</text><text x="1070" y="176" font-size="18">来源证据</text>
  </g>
  <g stroke="#000000" stroke-width="2" marker-end="url(#arrow)">
    <line x1="150" y1="155" x2="180" y2="155"/>
    <line x1="310" y1="155" x2="340" y2="155"/>
    <line x1="470" y1="155" x2="500" y2="155"/>
    <line x1="630" y1="155" x2="660" y2="155"/>
    <line x1="800" y1="155" x2="840" y2="155"/>
    <line x1="970" y1="155" x2="1000" y2="155"/>
  </g>
</svg>""",
}


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
            "<w:r><w:rPr><w:vertAlign w:val=\"superscript\"/><w:sz w:val=\"18\"/><w:szCs w:val=\"18\"/></w:rPr>"
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
    bold_xml = "<w:b/>" if bold else ""
    return (
        "<w:p><w:pPr><w:jc w:val=\"center\"/><w:spacing w:line=\"360\" w:lineRule=\"auto\"/></w:pPr>"
        f"<w:r><w:rPr>{bold_xml}<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
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
            content = p_center(cell, size=22, bold=True) if r_idx == 0 else p_body(cell, indent=False)
            cells.append("<w:tc><w:tcPr><w:tcW w:w=\"1800\" w:type=\"dxa\"/></w:tcPr>" f"{content}</w:tc>")
        tr_xml.append("<w:tr>" + "".join(cells) + "</w:tr>")

    tbl_xml = (
        "<w:tbl><w:tblPr><w:tblW w:w=\"0\" w:type=\"auto\"/>"
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


def markdown_to_blocks(text: str) -> list[ET.Element]:
    lines = text.splitlines()
    blocks: list[ET.Element] = []
    i = 0
    in_body = False
    while i < len(lines):
        stripped = lines[i].strip()
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
        if stripped.startswith("## "):
            blocks.append(parse_fragment(p_h1(stripped[3:].strip())))
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
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            blocks.append(build_table(table_lines))
            continue
        blocks.append(parse_fragment(p_body(stripped, superscript_refs=True)))
        i += 1
    return blocks


def write_assets() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in ASSETS.items():
        (ASSET_DIR / name).write_text(content, encoding="utf-8")


def rebuild_docx() -> None:
    md_text = MD_PATH.read_text(encoding="utf-8")
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
        if node.tag == w_tag("p") and "摘要" in para_text(node).replace(" ", ""):
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


def main() -> None:
    write_assets()
    rebuild_docx()
    print(OUTPUT_DOCX)


if __name__ == "__main__":
    main()
