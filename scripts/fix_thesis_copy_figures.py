from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import shutil
import struct
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"D:\beauty")
DOCX_PATH = next(p for p in ROOT.glob("*.docx") if " - " in p.name and not p.name.startswith("~$"))
ASSET_DIR = ROOT / "final_assets" / "thesis_copy_fix"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W, "a": A, "r": R, "wp": WP}

ET.register_namespace("w", W)
ET.register_namespace("a", A)
ET.register_namespace("r", R)
ET.register_namespace("wp", WP)

FONT_SERIF = Path(r"C:\Windows\Fonts\simsun.ttc")
FONT_BOLD = Path(r"C:\Windows\Fonts\simhei.ttf")

BLACK = "#111111"
GRAY = "#666666"
WHITE = "#ffffff"


@dataclass(frozen=True)
class FigureSpec:
    caption_prefix: str
    asset_name: str
    width_cm: float


FIGURE_MAP = {
    "图 3-2 系统数据流图": FigureSpec("图 3-2 系统数据流图", "fig_3_2_data_flow_refined.png", 13.4),
    "图 4-1 系统整体结构图": FigureSpec("图 4-1 系统整体结构图", "fig_4_1_architecture_refined.png", 13.6),
    "图 4-2 系统功能模块设计图": FigureSpec("图 4-2 系统功能模块设计图", "fig_4_2_module_design_refined.png", 13.6),
    "图 4-3 系统 ER 图": FigureSpec("图 4-3 系统 ER 图", "fig_4_3_er_refined.png", 13.6),
    "图 5-14 前端统一路由与角色鉴权核心代码截图": FigureSpec("图 5-14 前端统一路由与角色鉴权核心代码截图", "fig_5_14_code_router_core.png", 13.2),
    "图 5-15 知识管理接口核心代码截图": FigureSpec("图 5-15 知识管理接口核心代码截图", "fig_5_15_code_knowledge_core.png", 13.2),
    "图 5-16 文件上传与任务追踪核心代码截图": FigureSpec("图 5-16 文件上传与任务追踪核心代码截图", "fig_5_16_code_file_core.png", 13.2),
    "图 5-17 知识图谱治理与查询核心代码截图": FigureSpec("图 5-17 知识图谱治理与查询核心代码截图", "fig_5_17_code_kg_core.png", 13.2),
    "图 5-18 智能问答流式输出核心代码截图": FigureSpec("图 5-18 智能问答流式输出核心代码截图", "fig_5_18_code_chat_core.png", 13.2),
}


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def get_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def para_text(p: ET.Element) -> str:
    return "".join(t.text or "" for t in p.findall(".//w:t", NS)).strip()


def set_center_paragraph(p: ET.Element, spacing_before: int = 80, spacing_after: int = 80) -> None:
    ppr = p.find("w:pPr", NS)
    if ppr is None:
        ppr = ET.Element(qn(W, "pPr"))
        p.insert(0, ppr)

    for tag in ("jc", "ind", "spacing"):
        child = ppr.find(f"w:{tag}", NS)
        if child is not None:
            ppr.remove(child)

    jc = ET.SubElement(ppr, qn(W, "jc"))
    jc.set(qn(W, "val"), "center")

    ind = ET.SubElement(ppr, qn(W, "ind"))
    ind.set(qn(W, "firstLine"), "0")
    ind.set(qn(W, "left"), "0")
    ind.set(qn(W, "right"), "0")

    spacing = ET.SubElement(ppr, qn(W, "spacing"))
    spacing.set(qn(W, "before"), str(spacing_before))
    spacing.set(qn(W, "after"), str(spacing_after))


def nearest_caption(paras: list[ET.Element], idx: int) -> str | None:
    candidates: list[tuple[int, str, int]] = []
    for delta in (1, 2, 3, -1, -2, -3):
        j = idx + delta
        if 0 <= j < len(paras):
            text = para_text(paras[j])
            if text.startswith("图 "):
                priority = 0 if delta > 0 else 1
                candidates.append((priority, abs(delta), text))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        header = f.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Unsupported PNG: {path}")
    return struct.unpack(">II", header[16:24])


def cm_to_emu(cm: float) -> int:
    return int(cm * 360000)


def set_shape_extent(p: ET.Element, width_cm: float, img_path: Path) -> None:
    px_w, px_h = png_size(img_path)
    cx = cm_to_emu(width_cm)
    cy = int(cx * px_h / px_w)
    for extent in p.findall(".//wp:extent", NS):
        extent.set("cx", str(cx))
        extent.set("cy", str(cy))
    for ext in p.findall(".//a:ext", NS):
        ext.set("cx", str(cx))
        ext.set("cy", str(cy))


def draw_centered_text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], lines: list[str],
                       font: ImageFont.FreeTypeFont, fill: str = BLACK, gap: int = 8) -> None:
    x1, y1, x2, y2 = box
    sizes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    total_h = sum(bb[3] - bb[1] for bb in sizes) + gap * max(0, len(lines) - 1)
    y = y1 + (y2 - y1 - total_h) / 2
    for line, bb in zip(lines, sizes):
        w = bb[2] - bb[0]
        h = bb[3] - bb[1]
        draw.text((x1 + (x2 - x1 - w) / 2, y), line, fill=fill, font=font)
        y += h + gap


def draw_external_entity(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str,
                         font: ImageFont.FreeTypeFont) -> None:
    draw.rectangle(box, outline=BLACK, width=3, fill=WHITE)
    draw_centered_text(draw, box, [label], font)


def draw_process(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, details: list[str],
                 title_font: ImageFont.FreeTypeFont, body_font: ImageFont.FreeTypeFont) -> None:
    draw.ellipse(box, outline=BLACK, width=3, fill=WHITE)
    x1, y1, x2, y2 = box
    split = y1 + 52
    draw.line((x1 + 22, split, x2 - 22, split), fill=BLACK, width=2)
    draw_centered_text(draw, (x1 + 16, y1 + 8, x2 - 16, split), [title], title_font)
    draw_centered_text(draw, (x1 + 16, split + 8, x2 - 16, y2 - 10), details, body_font, fill=GRAY, gap=4)


def draw_data_store(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, details: list[str],
                    title_font: ImageFont.FreeTypeFont, body_font: ImageFont.FreeTypeFont) -> None:
    x1, y1, x2, y2 = box
    draw.rectangle(box, outline=BLACK, width=3, fill=WHITE)
    draw.line((x1 + 16, y1, x1 + 16, y2), fill=BLACK, width=3)
    draw.line((x2 - 16, y1, x2 - 16, y2), fill=BLACK, width=3)
    draw_centered_text(draw, (x1 + 22, y1 + 8, x2 - 22, y1 + 52), [title], title_font)
    draw.line((x1 + 22, y1 + 56, x2 - 22, y1 + 56), fill=BLACK, width=2)
    draw_centered_text(draw, (x1 + 22, y1 + 60, x2 - 22, y2 - 8), details, body_font, fill=GRAY, gap=4)


def draw_arrow(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], *, label: str | None = None,
               font: ImageFont.FreeTypeFont | None = None) -> None:
    for start, end in zip(points, points[1:]):
        draw.line((start, end), fill=BLACK, width=3)

    x1, y1 = points[-2]
    x2, y2 = points[-1]
    if x1 == x2:
        if y2 > y1:
            head = [(x2, y2), (x2 - 9, y2 - 14), (x2 + 9, y2 - 14)]
        else:
            head = [(x2, y2), (x2 - 9, y2 + 14), (x2 + 9, y2 + 14)]
    else:
        if x2 > x1:
            head = [(x2, y2), (x2 - 14, y2 - 9), (x2 - 14, y2 + 9)]
        else:
            head = [(x2, y2), (x2 + 14, y2 - 9), (x2 + 14, y2 + 9)]
    draw.polygon(head, fill=BLACK)

    if label and font:
        mid_idx = max(0, len(points) // 2 - 1)
        sx, sy = points[mid_idx]
        ex, ey = points[mid_idx + 1]
        lx = (sx + ex) / 2
        ly = (sy + ey) / 2 - 22
        bb = draw.textbbox((0, 0), label, font=font)
        w = bb[2] - bb[0]
        h = bb[3] - bb[1]
        draw.rounded_rectangle((lx - w / 2 - 8, ly - 3, lx + w / 2 + 8, ly + h + 3), radius=10, fill=WHITE)
        draw.text((lx - w / 2, ly), label, fill=GRAY, font=font)


def draw_attribute(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str,
                   font: ImageFont.FreeTypeFont, primary: bool = False) -> None:
    draw.ellipse(box, outline=BLACK, width=3, fill=WHITE)
    if primary:
        x1, y1, x2, y2 = box
        draw.ellipse((x1 + 8, y1 + 8, x2 - 8, y2 - 8), outline=BLACK, width=2)
    draw_centered_text(draw, box, [label], font, fill=GRAY if not primary else BLACK)


def draw_relationship(draw: ImageDraw.ImageDraw, center: tuple[int, int], size: tuple[int, int], label: str,
                      font: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    cx, cy = center
    w, h = size
    points = [(cx, cy - h // 2), (cx + w // 2, cy), (cx, cy + h // 2), (cx - w // 2, cy)]
    draw.polygon(points, outline=BLACK, fill=WHITE, width=3)
    draw_centered_text(draw, (cx - w // 2 + 8, cy - h // 2 + 8, cx + w // 2 - 8, cy + h // 2 - 8), [label], font)
    return (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)


def draw_line(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]]) -> None:
    for start, end in zip(points, points[1:]):
        draw.line((start, end), fill=BLACK, width=3)


def draw_cardinality(draw: ImageDraw.ImageDraw, position: tuple[int, int], text: str, font: ImageFont.FreeTypeFont) -> None:
    bb = draw.textbbox((0, 0), text, font=font)
    x, y = position
    draw.rounded_rectangle((x - 6, y - 4, x + (bb[2] - bb[0]) + 6, y + (bb[3] - bb[1]) + 4), radius=8, fill=WHITE)
    draw.text((x, y), text, fill=BLACK, font=font)


def draw_line_to_attribute(draw: ImageDraw.ImageDraw, entity_box: tuple[int, int, int, int],
                           attr_box: tuple[int, int, int, int]) -> None:
    ex1, ey1, ex2, ey2 = entity_box
    ax1, ay1, ax2, ay2 = attr_box
    ecx = (ex1 + ex2) // 2
    ecy = (ey1 + ey2) // 2
    acx = (ax1 + ax2) // 2
    acy = (ay1 + ay2) // 2
    draw.line((ecx, ecy, acx, acy), fill=BLACK, width=2)


def create_standard_dfd() -> Path:
    output = ASSET_DIR / "fig_3_2_data_flow_refined.png"
    img = Image.new("RGB", (1750, 980), WHITE)
    draw = ImageDraw.Draw(img)
    title_font = get_font(FONT_BOLD, 28)
    body_font = get_font(FONT_SERIF, 19)
    entity_font = get_font(FONT_BOLD, 24)
    flow_font = get_font(FONT_SERIF, 18)

    draw_external_entity(draw, (120, 90, 320, 170), "普通用户", entity_font)
    draw_external_entity(draw, (1430, 90, 1630, 170), "管理员", entity_font)

    draw_process(draw, (250, 240, 500, 360), "登录鉴权", ["登录信息", "身份校验"], title_font, body_font)
    draw_process(draw, (560, 240, 810, 360), "知识检索", ["检索条件", "知识结果"], title_font, body_font)
    draw_process(draw, (870, 240, 1120, 360), "文件处理", ["上传文件", "任务生成"], title_font, body_font)
    draw_process(draw, (1180, 240, 1430, 360), "实体审核", ["候选审核", "审核结果"], title_font, body_font)
    draw_process(draw, (760, 520, 1010, 640), "智能问答", ["问答请求", "问答结果"], title_font, body_font)

    draw_data_store(draw, (320, 780, 610, 890), "业务数据库", ["用户、知识、分类、任务"], title_font, body_font)
    draw_data_store(draw, (730, 780, 1020, 890), "对象存储", ["原始文件与附件"], title_font, body_font)
    draw_data_store(draw, (1140, 780, 1430, 890), "向量库", ["切片向量与召回结果"], title_font, body_font)

    draw_arrow(draw, [(320, 130), (375, 130), (375, 240)], label="登录信息", font=flow_font)
    draw_arrow(draw, [(1430, 300), (1580, 300), (1580, 170)], label="审核操作", font=flow_font)
    draw_arrow(draw, [(1010, 580), (1150, 580), (1150, 170), (1430, 170)], label="问答结果 / 任务状态", font=flow_font)

    draw_arrow(draw, [(500, 300), (560, 300)], label="检索请求", font=flow_font)
    draw_arrow(draw, [(810, 300), (870, 300)], label="上传文件", font=flow_font)
    draw_arrow(draw, [(1120, 300), (1180, 300)], label="候选数据", font=flow_font)
    draw_arrow(draw, [(685, 360), (685, 450), (840, 450), (840, 520)], label="知识上下文", font=flow_font)
    draw_arrow(draw, [(995, 360), (995, 450), (930, 450), (930, 520)], label="问答请求", font=flow_font)

    draw_arrow(draw, [(685, 360), (685, 710), (465, 710), (465, 780)], label="知识结果 / 任务记录", font=flow_font)
    draw_arrow(draw, [(995, 360), (995, 710), (875, 710), (875, 780)], label="原始文件", font=flow_font)
    draw_arrow(draw, [(1305, 360), (1305, 710), (1285, 710), (1285, 780)], label="审核回写", font=flow_font)
    draw_arrow(draw, [(885, 640), (885, 780)], label="附件摘要", font=flow_font)
    draw_arrow(draw, [(1010, 580), (1195, 580), (1195, 780)], label="向量检索结果", font=flow_font)
    draw_arrow(draw, [(1285, 780), (1285, 660), (1010, 660)], label="召回片段", font=flow_font)

    img.save(output)
    return output


def create_architecture_placeholder() -> Path:
    path = ASSET_DIR / "fig_4_1_architecture_refined.png"
    if not path.exists():
        img = Image.new("RGB", (1600, 900), WHITE)
        img.save(path)
    return path


def create_module_placeholder() -> Path:
    path = ASSET_DIR / "fig_4_2_module_design_refined.png"
    if not path.exists():
        img = Image.new("RGB", (1600, 900), WHITE)
        img.save(path)
    return path


def create_standard_er() -> Path:
    output = ASSET_DIR / "fig_4_3_er_refined.png"
    img = Image.new("RGB", (1860, 1160), WHITE)
    draw = ImageDraw.Draw(img)
    entity_font = get_font(FONT_BOLD, 24)
    attr_font = get_font(FONT_SERIF, 18)
    rel_font = get_font(FONT_SERIF, 20)
    card_font = get_font(FONT_SERIF, 17)

    entities = {
        "分类": (120, 120, 320, 200),
        "知识": (820, 120, 1020, 200),
        "文件": (1420, 120, 1620, 200),
        "任务": (1600, 430, 1800, 510),
        "图谱实体": (420, 520, 640, 600),
        "图谱关系": (860, 860, 1080, 940),
        "会话": (1220, 520, 1420, 600),
        "消息": (1540, 860, 1740, 940),
    }
    for label, box in entities.items():
        draw_external_entity(draw, box, label, entity_font)

    attributes = {
        "分类": [((30, 70, 180, 130), "PK 分类ID", True), ((20, 190, 170, 250), "名称", False), ((250, 215, 420, 275), "排序号", False)],
        "知识": [((760, 20, 910, 80), "PK 知识ID", True), ((1030, 20, 1180, 80), "标题", False), ((680, 215, 840, 275), "状态", False), ((1010, 215, 1180, 275), "摘要", False)],
        "文件": [((1340, 20, 1490, 80), "PK 文件ID", True), ((1605, 20, 1770, 80), "文件类型", False)],
        "任务": [((1590, 550, 1750, 610), "PK 任务ID", True), ((1660, 360, 1820, 420), "任务状态", False)],
        "图谱实体": [((240, 470, 390, 530), "PK 实体ID", True), ((240, 600, 390, 660), "实体名称", False), ((640, 470, 800, 530), "实体类型", False)],
        "图谱关系": [((850, 1010, 1000, 1070), "PK 关系ID", True), ((1030, 780, 1180, 840), "关系类型", False)],
        "会话": [((1160, 420, 1310, 480), "PK 会话ID", True), ((1100, 600, 1250, 660), "用户ID", False), ((1390, 600, 1540, 660), "标题", False)],
        "消息": [((1500, 780, 1650, 840), "PK 消息ID", True), ((1450, 1010, 1600, 1070), "角色", False), ((1630, 1010, 1810, 1070), "内容", False)],
    }
    for entity_name, attrs in attributes.items():
        for box, label, primary in attrs:
            draw_attribute(draw, box, label, attr_font, primary)
            draw_line_to_attribute(draw, entities[entity_name], box)

    rel_category = draw_relationship(draw, (570, 160), (120, 80), "归属", rel_font)
    rel_file = draw_relationship(draw, (1220, 160), (120, 80), "包含", rel_font)
    rel_task = draw_relationship(draw, (1600, 310), (120, 80), "产生", rel_font)
    rel_extract = draw_relationship(draw, (730, 390), (150, 90), "抽取", rel_font)
    rel_session = draw_relationship(draw, (1520, 650), (120, 80), "发送", rel_font)
    rel_source = draw_relationship(draw, (730, 900), (150, 90), "源实体", rel_font)
    rel_target = draw_relationship(draw, (1210, 900), (150, 90), "目标实体", rel_font)

    draw_line(draw, [(320, 160), (510, 160)])
    draw_line(draw, [(630, 160), (820, 160)])
    draw_cardinality(draw, (365, 128), "1", card_font)
    draw_cardinality(draw, (735, 128), "N", card_font)

    draw_line(draw, [(1020, 160), (1160, 160)])
    draw_line(draw, [(1280, 160), (1420, 160)])
    draw_cardinality(draw, (1060, 128), "1", card_font)
    draw_cardinality(draw, (1360, 128), "N", card_font)

    draw_line(draw, [(1560, 200), (1560, 270), (1600, 270)])
    draw_line(draw, [(1660, 430), (1660, 350), (1600, 350)])
    draw_cardinality(draw, (1530, 230), "1", card_font)
    draw_cardinality(draw, (1670, 360), "N", card_font)

    draw_line(draw, [(920, 200), (920, 300), (785, 300), (785, 390)])
    draw_line(draw, [(530, 520), (530, 435), (655, 435)])
    draw_cardinality(draw, (885, 248), "1", card_font)
    draw_cardinality(draw, (565, 438), "N", card_font)

    draw_line(draw, [(1420, 560), (1520, 560), (1520, 610)])
    draw_line(draw, [(1640, 860), (1640, 690), (1520, 690)])
    draw_cardinality(draw, (1450, 528), "1", card_font)
    draw_cardinality(draw, (1642, 728), "N", card_font)

    draw_line(draw, [(530, 600), (530, 730), (655, 730), (655, 900)])
    draw_line(draw, [(860, 900), (805, 900)])
    draw_cardinality(draw, (560, 760), "1", card_font)
    draw_cardinality(draw, (815, 868), "N", card_font)

    draw_line(draw, [(640, 560), (760, 560), (760, 840), (1135, 840), (1135, 900)])
    draw_line(draw, [(1080, 900), (1135, 900)])
    draw_cardinality(draw, (750, 588), "1", card_font)
    draw_cardinality(draw, (1090, 868), "N", card_font)

    img.save(output)
    return output


def create_all_assets() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    create_standard_dfd()
    create_standard_er()
    create_architecture_placeholder()
    create_module_placeholder()


def patch_docx() -> None:
    with ZipFile(DOCX_PATH, "r") as zin:
        doc_root = ET.fromstring(zin.read("word/document.xml"))
        rel_root = ET.fromstring(zin.read("word/_rels/document.xml.rels"))
        rels = {r.attrib["Id"]: r.attrib["Target"].replace("../", "") for r in rel_root}
        body = doc_root.find("w:body", NS)
        if body is None:
            raise RuntimeError("word body not found")

        paras = body.findall("w:p", NS)
        replacements: dict[str, Path] = {}

        for p in paras:
            text = para_text(p)
            if any(text.startswith(prefix) for prefix in FIGURE_MAP):
                set_center_paragraph(p, 0, 80)

        for idx, p in enumerate(paras):
            blip = p.find(".//a:blip", NS)
            if blip is None:
                continue
            rid = blip.attrib.get(f"{{{R}}}embed")
            target = rels.get(rid, "")
            if not target.startswith("media/"):
                continue

            caption = nearest_caption(paras, idx)
            if not caption:
                continue

            spec = next((value for prefix, value in FIGURE_MAP.items() if caption.startswith(prefix)), None)
            if spec is None:
                continue

            asset = ASSET_DIR / spec.asset_name
            if not asset.exists():
                continue
            replacements[f"word/{target}"] = asset
            set_shape_extent(p, spec.width_cm, asset)
            set_center_paragraph(p, 80, 80)

        updated_xml = ET.tostring(doc_root, encoding="utf-8", xml_declaration=True)
        tmp_path = DOCX_PATH.with_name(DOCX_PATH.stem + "._tmp_fix.docx")
        with ZipFile(tmp_path, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    data = updated_xml
                elif item.filename in replacements:
                    data = replacements[item.filename].read_bytes()
                zout.writestr(item, data)
    shutil.move(tmp_path, DOCX_PATH)


def main() -> None:
    create_all_assets()
    patch_docx()
    print(DOCX_PATH)


if __name__ == "__main__":
    main()
