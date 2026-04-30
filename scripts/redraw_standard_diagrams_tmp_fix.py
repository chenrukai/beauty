from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import shutil
import struct
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(r"D:\beauty")
DOCX_PATH = next(ROOT.glob("*_tmp_fix.docx"))
ASSET_DIR = ROOT / "final_assets" / "thesis_copy_fix"
ASSET_DIR.mkdir(parents=True, exist_ok=True)

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W, "a": A, "r": R, "wp": WP}

ET.register_namespace("w", W)
ET.register_namespace("a", A)
ET.register_namespace("r", R)
ET.register_namespace("wp", WP)

FONT_SONG = Path(r"C:\Windows\Fonts\simsun.ttc")
FONT_HEI = Path(r"C:\Windows\Fonts\simhei.ttf")

BG = "#ffffff"
LINE = "#6f7682"
TEXT = "#222222"
SUB = "#5f6670"
LIGHT = "#f7f7f7"


@dataclass(frozen=True)
class FigureSpec:
    caption: str
    asset_name: str
    width_cm: float


FIGURES = [
    FigureSpec("图 3-1 系统业务流程图", "fig_3_1_business_flow_standard.png", 14.2),
    FigureSpec("图 3-2 系统数据流图", "fig_3_2_data_flow_standard.png", 14.0),
    FigureSpec("图 3-3 普通用户用例图", "fig_3_3_user_use_case_standard.png", 13.2),
    FigureSpec("图 3-4 后台管理员用例图", "fig_3_4_admin_use_case_standard.png", 13.4),
    FigureSpec("图 4-1 系统整体结构图", "fig_4_1_architecture_standard.png", 14.4),
    FigureSpec("图 4-2 系统功能模块设计图", "fig_4_2_module_tree_standard.png", 14.0),
    FigureSpec("图 4-3 系统 ER 图", "fig_4_3_er_standard.png", 14.2),
]


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def para_text(p: ET.Element) -> str:
    return "".join(t.text or "" for t in p.findall(".//w:t", NS)).strip()


def text_box(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bb = draw.textbbox((0, 0), text, font=fnt)
    return bb[2] - bb[0], bb[3] - bb[1]


def center_text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], lines: list[str],
                fnt: ImageFont.FreeTypeFont, fill: str = TEXT, gap: int = 6) -> None:
    x1, y1, x2, y2 = box
    dims = [text_box(draw, line, fnt) for line in lines]
    total_h = sum(h for _, h in dims) + gap * max(0, len(lines) - 1)
    y = y1 + (y2 - y1 - total_h) / 2
    for line, (w, h) in zip(lines, dims):
        x = x1 + (x2 - x1 - w) / 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += h + gap


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int = 18,
            fill: str = BG, outline: str = LINE, width: int = 2) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], width: int = 3, fill: str = LINE,
          head: int = 10, label: str | None = None, label_font: ImageFont.FreeTypeFont | None = None,
          label_shift: tuple[int, int] = (0, -24)) -> None:
    for a, b in zip(pts, pts[1:]):
        draw.line((a, b), fill=fill, width=width)
    x1, y1 = pts[-2]
    x2, y2 = pts[-1]
    if abs(x2 - x1) >= abs(y2 - y1):
        if x2 >= x1:
            tri = [(x2, y2), (x2 - head - 4, y2 - head), (x2 - head - 4, y2 + head)]
        else:
            tri = [(x2, y2), (x2 + head + 4, y2 - head), (x2 + head + 4, y2 + head)]
    else:
        if y2 >= y1:
            tri = [(x2, y2), (x2 - head, y2 - head - 4), (x2 + head, y2 - head - 4)]
        else:
            tri = [(x2, y2), (x2 - head, y2 + head + 4), (x2 + head, y2 + head + 4)]
    draw.polygon(tri, fill=fill)
    if label and label_font:
        sx, sy = pts[len(pts) // 2 - 1]
        ex, ey = pts[len(pts) // 2]
        lx = (sx + ex) / 2 + label_shift[0]
        ly = (sy + ey) / 2 + label_shift[1]
        w, h = text_box(draw, label, label_font)
        rounded(draw, (int(lx - w / 2 - 8), int(ly - 4), int(lx + w / 2 + 8), int(ly + h + 4)),
                radius=10, fill=BG, outline=BG, width=1)
        draw.text((lx - w / 2, ly), label, font=label_font, fill=SUB)


def line(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], width: int = 2, fill: str = LINE) -> None:
    for a, b in zip(pts, pts[1:]):
        draw.line((a, b), fill=fill, width=width)


def actor(draw: ImageDraw.ImageDraw, x: int, y: int, label: str,
          line_color: str, text_font: ImageFont.FreeTypeFont) -> None:
    draw.ellipse((x - 18, y, x + 18, y + 36), outline=line_color, width=2)
    draw.line((x, y + 36, x, y + 92), fill=line_color, width=2)
    draw.line((x - 32, y + 52, x + 32, y + 52), fill=line_color, width=2)
    draw.line((x, y + 92, x - 26, y + 132), fill=line_color, width=2)
    draw.line((x, y + 92, x + 26, y + 132), fill=line_color, width=2)
    w, h = text_box(draw, label, text_font)
    draw.text((x - w / 2, y + 142), label, font=text_font, fill=TEXT)


def ellipse_label(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], lines: list[str],
                  fnt: ImageFont.FreeTypeFont) -> None:
    draw.ellipse(box, outline=LINE, width=2, fill=BG)
    center_text(draw, box, lines, fnt)


def datastore(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str,
              detail: str, title_font: ImageFont.FreeTypeFont, body_font: ImageFont.FreeTypeFont) -> None:
    x1, y1, x2, y2 = box
    draw.rectangle(box, outline=LINE, width=2, fill=BG)
    draw.line((x1 + 16, y1, x1 + 16, y2), fill=LINE, width=2)
    draw.line((x2 - 16, y1, x2 - 16, y2), fill=LINE, width=2)
    center_text(draw, (x1 + 18, y1 + 8, x2 - 18, y1 + 44), [title], title_font)
    line(draw, [(x1 + 20, y1 + 48), (x2 - 20, y1 + 48)], width=1)
    center_text(draw, (x1 + 20, y1 + 56, x2 - 20, y2 - 10), [detail], body_font, fill=SUB)


def process(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, detail: str,
            title_font: ImageFont.FreeTypeFont, body_font: ImageFont.FreeTypeFont) -> None:
    draw.ellipse(box, outline=LINE, width=2, fill=BG)
    x1, y1, x2, y2 = box
    line(draw, [(x1 + 22, y1 + 46), (x2 - 22, y1 + 46)], width=1)
    center_text(draw, (x1 + 12, y1 + 6, x2 - 12, y1 + 42), [title], title_font)
    center_text(draw, (x1 + 16, y1 + 52, x2 - 16, y2 - 10), [detail], body_font, fill=SUB)


def entity(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str,
           title_font: ImageFont.FreeTypeFont, body_font: ImageFont.FreeTypeFont,
           fields: list[str] | None = None) -> None:
    rounded(draw, box)
    x1, y1, x2, y2 = box
    line(draw, [(x1, y1 + 42), (x2, y1 + 42)], width=1)
    center_text(draw, (x1 + 8, y1 + 4, x2 - 8, y1 + 38), [title], title_font)
    if fields:
        center_text(draw, (x1 + 10, y1 + 50, x2 - 10, y2 - 10), fields, body_font, fill=SUB, gap=4)


def attribute(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str,
              fnt: ImageFont.FreeTypeFont, primary: bool = False) -> None:
    draw.ellipse(box, outline=LINE, width=2, fill=BG)
    if primary:
        x1, y1, x2, y2 = box
        draw.ellipse((x1 + 7, y1 + 7, x2 - 7, y2 - 7), outline=LINE, width=1)
    center_text(draw, box, [text], fnt, fill=SUB if not primary else TEXT)


def diamond(draw: ImageDraw.ImageDraw, center: tuple[int, int], size: tuple[int, int], text: str,
            fnt: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    cx, cy = center
    w, h = size
    pts = [(cx, cy - h // 2), (cx + w // 2, cy), (cx, cy + h // 2), (cx - w // 2, cy)]
    draw.polygon(pts, outline=LINE, fill=BG, width=2)
    center_text(draw, (cx - w // 2 + 8, cy - h // 2 + 8, cx + w // 2 - 8, cy + h // 2 - 8), [text], fnt)
    return cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2


def cardinality(draw: ImageDraw.ImageDraw, pos: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont) -> None:
    x, y = pos
    w, h = text_box(draw, text, fnt)
    rounded(draw, (x - 6, y - 4, x + w + 6, y + h + 4), radius=8, fill=BG, outline=BG, width=1)
    draw.text((x, y), text, font=fnt, fill=TEXT)


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        data = f.read(24)
    return struct.unpack(">II", data[16:24])


def recenter_asset(path: Path, padding: int = 40) -> None:
    img = Image.open(path).convert("RGB")
    bg = Image.new("RGB", img.size, BG)
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if not bbox:
        return
    x1, y1, x2, y2 = bbox
    crop = img.crop((max(0, x1 - padding), max(0, y1 - padding), min(img.width, x2 + padding), min(img.height, y2 + padding)))
    canvas = Image.new("RGB", img.size, BG)
    px = max(0, (canvas.width - crop.width) // 2)
    py = max(0, (canvas.height - crop.height) // 2)
    canvas.paste(crop, (px, py))
    canvas.save(path)


def cm_to_emu(cm: float) -> int:
    return int(cm * 360000)


def set_center_paragraph(p: ET.Element, before: int = 80, after: int = 80) -> None:
    ppr = p.find("w:pPr", NS)
    if ppr is None:
        ppr = ET.Element(qn(W, "pPr"))
        p.insert(0, ppr)
    for tag in ("jc", "spacing", "ind"):
        node = ppr.find(f"w:{tag}", NS)
        if node is not None:
            ppr.remove(node)
    jc = ET.SubElement(ppr, qn(W, "jc"))
    jc.set(qn(W, "val"), "center")
    spacing = ET.SubElement(ppr, qn(W, "spacing"))
    spacing.set(qn(W, "before"), str(before))
    spacing.set(qn(W, "after"), str(after))
    ind = ET.SubElement(ppr, qn(W, "ind"))
    ind.set(qn(W, "firstLine"), "0")
    ind.set(qn(W, "left"), "0")
    ind.set(qn(W, "right"), "0")


def nearest_caption(paras: list[ET.Element], idx: int) -> str | None:
    found: list[tuple[int, int, str]] = []
    for delta in (1, 2, 3, -1, -2, -3):
        j = idx + delta
        if 0 <= j < len(paras):
            txt = para_text(paras[j])
            if txt.startswith("图 "):
                found.append((0 if delta > 0 else 1, abs(delta), txt))
    return sorted(found)[0][2] if found else None


def set_extent(p: ET.Element, width_cm: float, img_path: Path) -> None:
    pw, ph = png_size(img_path)
    cx = cm_to_emu(width_cm)
    cy = int(cx * ph / pw)
    for extent in p.findall(".//wp:extent", NS):
        extent.set("cx", str(cx))
        extent.set("cy", str(cy))
    for ext in p.findall(".//a:ext", NS):
        ext.set("cx", str(cx))
        ext.set("cy", str(cy))


def make_business_flow() -> Path:
    path = ASSET_DIR / "fig_3_1_business_flow_standard.png"
    img = Image.new("RGB", (1850, 1080), BG)
    draw = ImageDraw.Draw(img)
    ft_title = font(FONT_HEI, 26)
    ft_lane = font(FONT_HEI, 24)
    ft_text = font(FONT_SONG, 20)
    ft_small = font(FONT_SONG, 18)

    lane_x = [80, 510, 940, 1370, 1770]
    top, bottom = 90, 990
    lane_titles = ["普通用户", "后台管理员", "系统处理服务", "知识资源/结果输出"]
    for i in range(4):
        rounded(draw, (lane_x[i], top, lane_x[i + 1] - 20, bottom), radius=14, fill=BG, outline="#c8ccd2", width=2)
        draw.rectangle((lane_x[i], top, lane_x[i + 1] - 20, top + 54), fill=LIGHT, outline="#c8ccd2", width=1)
        center_text(draw, (lane_x[i], top + 2, lane_x[i + 1] - 20, top + 50), [lane_titles[i]], ft_lane)

    def step(box: tuple[int, int, int, int], lines: list[str]) -> None:
        rounded(draw, box, radius=16)
        center_text(draw, box, lines, ft_text)

    o1 = (160, 165, 410, 235)
    o2 = (160, 315, 410, 385)
    o3 = (160, 475, 410, 545)
    o4 = (160, 635, 410, 705)
    a1 = (590, 205, 840, 275)
    a2 = (590, 425, 840, 495)
    s1 = (1020, 165, 1270, 235)
    s2 = (1020, 315, 1270, 385)
    s3 = (1020, 465, 1270, 535)
    s4 = (1020, 615, 1270, 685)
    r1 = (1450, 235, 1700, 305)
    r2 = (1450, 425, 1700, 495)
    r3 = (1450, 635, 1700, 705)

    for box, lines in [
        (o1, ["登录/进入系统"]),
        (o2, ["知识浏览", "或发起问答"]),
        (o3, ["上传资料", "或附件文件"]),
        (o4, ["查看检索/问答结果"]),
        (a1, ["维护分类、知识", "并发布内容"]),
        (a2, ["审核实体", "处理任务与公告"]),
        (s1, ["文件解析", "抽取文本与媒体信息"]),
        (s2, ["切片处理", "实体识别与候选生成"]),
        (s3, ["知识入库", "图谱更新与索引构建"]),
        (s4, ["执行检索召回", "生成问答响应"]),
        (r1, ["业务数据库", "保存分类/知识/用户"]),
        (r2, ["对象存储 + 向量库", "保存文件与索引"]),
        (r3, ["知识图谱与问答结果", "支撑服务输出"]),
    ]:
        step(box, lines)

    arrow(draw, [(285, 235), (285, 315)])
    arrow(draw, [(285, 385), (285, 475)])
    arrow(draw, [(285, 545), (285, 635)])
    arrow(draw, [(410, 510), (520, 510), (520, 200), (1020, 200)], label="资料接入", label_font=ft_small)
    arrow(draw, [(715, 275), (715, 315), (1020, 315)], label="内容处理", label_font=ft_small)
    arrow(draw, [(715, 495), (715, 505), (1020, 505)], label="审核控制", label_font=ft_small)
    arrow(draw, [(1270, 200), (1370, 200), (1370, 270), (1450, 270)])
    arrow(draw, [(1270, 350), (1370, 350), (1370, 460), (1450, 460)])
    arrow(draw, [(1270, 500), (1370, 500), (1370, 670), (1450, 670)], label="知识沉淀", label_font=ft_small)
    arrow(draw, [(1700, 670), (1735, 670), (1735, 780), (1145, 780), (1145, 685)], label="服务输出", label_font=ft_small)
    arrow(draw, [(1020, 650), (760, 650), (760, 740), (285, 740), (285, 705)])
    arrow(draw, [(410, 200), (500, 200), (500, 240), (590, 240)])
    arrow(draw, [(840, 460), (930, 460), (930, 500), (1020, 500)])

    center_text(draw, (0, 20, 1850, 70), ["系统业务流程图"], ft_title)
    img.save(path)
    return path


def make_dfd() -> Path:
    path = ASSET_DIR / "fig_3_2_data_flow_standard.png"
    img = Image.new("RGB", (1820, 1000), BG)
    draw = ImageDraw.Draw(img)
    ft_title = font(FONT_HEI, 26)
    ft_node = font(FONT_HEI, 23)
    ft_text = font(FONT_SONG, 18)
    ft_label = font(FONT_SONG, 16)

    entity(draw, (80, 120, 260, 200), "普通用户", ft_node, ft_text)
    entity(draw, (1540, 120, 1720, 200), "管理员", ft_node, ft_text)

    process(draw, (250, 270, 520, 420), "用户信息管理/认证", "登录鉴权、角色识别", ft_node, ft_text)
    process(draw, (560, 270, 830, 420), "知识检索", "关键词检索、详情查看", ft_node, ft_text)
    process(draw, (870, 270, 1140, 420), "文件处理", "上传解析、切片与抽取", ft_node, ft_text)
    process(draw, (1180, 270, 1450, 420), "实体审核", "候选确认、图谱修正", ft_node, ft_text)
    process(draw, (715, 560, 985, 710), "智能问答", "语义召回、生成响应", ft_node, ft_text)

    datastore(draw, (350, 790, 630, 900), "业务数据库", "用户、分类、知识、任务", ft_node, ft_text)
    datastore(draw, (770, 790, 1050, 900), "对象存储", "原始文件与处理产物", ft_node, ft_text)
    datastore(draw, (1190, 790, 1470, 900), "向量库", "切片向量与召回索引", ft_node, ft_text)

    arrow(draw, [(260, 160), (385, 160), (385, 270)], label="登录信息", label_font=ft_label)
    arrow(draw, [(1540, 160), (1315, 160), (1315, 270)], label="审核指令", label_font=ft_label)
    arrow(draw, [(520, 330), (560, 330)], label="身份信息", label_font=ft_label)
    arrow(draw, [(520, 375), (220, 375), (220, 180), (80, 180)], label="登录结果", label_font=ft_label)
    arrow(draw, [(260, 180), (695, 180), (695, 270)], label="检索条件", label_font=ft_label)
    arrow(draw, [(830, 330), (560, 330)], label="知识结果", label_font=ft_label, label_shift=(0, 16))
    arrow(draw, [(260, 190), (1005, 190), (1005, 270)], label="上传文件", label_font=ft_label)
    arrow(draw, [(1140, 330), (1180, 330)], label="候选实体", label_font=ft_label)
    arrow(draw, [(1450, 375), (1720, 375), (1720, 180)], label="审核结果", label_font=ft_label)
    arrow(draw, [(260, 195), (850, 195), (850, 560)], label="问答请求", label_font=ft_label)
    arrow(draw, [(715, 635), (260, 635), (260, 200)], label="问答结果", label_font=ft_label)

    arrow(draw, [(480, 420), (480, 790)], label="业务数据", label_font=ft_label)
    arrow(draw, [(910, 420), (910, 790)], label="文件对象", label_font=ft_label)
    arrow(draw, [(1310, 420), (1310, 790)], label="审核写回", label_font=ft_label)
    arrow(draw, [(850, 710), (850, 790)], label="会话消息", label_font=ft_label)
    arrow(draw, [(630, 845), (715, 845), (715, 635)], label="知识信息", label_font=ft_label)
    arrow(draw, [(1050, 845), (985, 845), (985, 635)], label="附件内容", label_font=ft_label)
    arrow(draw, [(1190, 845), (985, 845), (985, 670)], label="向量检索结果", label_font=ft_label, label_shift=(0, 16))

    center_text(draw, (0, 22, 1820, 68), ["系统数据流图"], ft_title)
    img.save(path)
    return path


def make_use_case(path: Path, actor_name: str, title: str, cases: list[tuple[tuple[int, int, int, int], list[str]]],
                  links: list[tuple[tuple[int, int], tuple[int, int], bool, str | None]]) -> Path:
    img = Image.new("RGB", (1700, 980), BG)
    draw = ImageDraw.Draw(img)
    ft_title = font(FONT_HEI, 26)
    ft_actor = font(FONT_SONG, 22)
    ft_case = font(FONT_SONG, 20)
    ft_inc = font(FONT_SONG, 16)

    actor(draw, 180, 390, actor_name, LINE, ft_actor)
    rounded(draw, (320, 90, 1560, 860), radius=22, fill=BG, outline="#c9ced5", width=2)
    center_text(draw, (320, 98, 1560, 140), [title], ft_title)

    for box, lines in cases:
        ellipse_label(draw, box, lines, ft_case)

    for start, end, dashed, label in links:
        if dashed:
            sx, sy = start
            ex, ey = end
            steps = 16
            for i in range(steps):
                t1 = i / steps
                t2 = min(1, t1 + 0.035)
                if i % 2 == 0:
                    draw.line((sx + (ex - sx) * t1, sy + (ey - sy) * t1, sx + (ex - sx) * t2, sy + (ey - sy) * t2),
                              fill=LINE, width=2)
            arrow(draw, [start, end], width=1, fill=LINE)
        else:
            arrow(draw, [start, end], width=2, fill=LINE)
        if label:
            w, h = text_box(draw, label, ft_inc)
            mx = (start[0] + end[0]) / 2
            my = (start[1] + end[1]) / 2 - 24
            rounded(draw, (int(mx - w / 2 - 6), int(my - 4), int(mx + w / 2 + 6), int(my + h + 4)),
                    radius=8, fill=BG, outline=BG, width=1)
            draw.text((mx - w / 2, my), label, font=ft_inc, fill=SUB)

    img.save(path)
    return path


def make_user_use_case() -> Path:
    path = ASSET_DIR / "fig_3_3_user_use_case_standard.png"
    cases = [
        ((470, 180, 770, 250), ["首页浏览"]),
        ((470, 300, 770, 370), ["知识检索"]),
        ((470, 420, 770, 490), ["查看知识详情"]),
        ((470, 540, 770, 610), ["收藏管理"]),
        ((920, 220, 1250, 290), ["智能问答"]),
        ((920, 380, 1250, 450), ["上传附件摘要"]),
        ((920, 540, 1250, 610), ["基于附件继续追问"]),
        ((1290, 220, 1510, 290), ["问题提交"]),
        ((1290, 380, 1510, 450), ["附件上传"]),
        ((1290, 540, 1510, 610), ["会话追问"]),
    ]
    links = [
        ((214, 408), (470, 215), False, None),
        ((214, 408), (470, 335), False, None),
        ((214, 408), (470, 455), False, None),
        ((214, 408), (470, 575), False, None),
        ((214, 408), (920, 255), False, None),
        ((214, 408), (920, 415), False, None),
        ((214, 408), (920, 575), False, None),
        ((1250, 255), (1290, 255), True, "<<include>>"),
        ((1250, 415), (1290, 415), True, "<<include>>"),
        ((1250, 575), (1290, 575), True, "<<include>>"),
    ]
    return make_use_case(path, "普通用户", "普通用户用例图", cases, links)


def make_admin_use_case() -> Path:
    path = ASSET_DIR / "fig_3_4_admin_use_case_standard.png"
    cases = [
        ((470, 150, 770, 220), ["查看概览"]),
        ((470, 270, 770, 340), ["知识管理"]),
        ((470, 390, 770, 460), ["分类管理"]),
        ((470, 510, 770, 580), ["文件上传"]),
        ((470, 630, 770, 700), ["任务监控"]),
        ((920, 180, 1250, 250), ["实体确认"]),
        ((920, 320, 1250, 390), ["知识图谱维护"]),
        ((920, 460, 1250, 530), ["公告管理"]),
        ((920, 600, 1250, 670), ["用户管理"]),
        ((1290, 180, 1510, 250), ["统计报表查看"]),
    ]
    links = [
        ((214, 408), (470, 185), False, None),
        ((214, 408), (470, 305), False, None),
        ((214, 408), (470, 425), False, None),
        ((214, 408), (470, 545), False, None),
        ((214, 408), (470, 665), False, None),
        ((214, 408), (920, 215), False, None),
        ((214, 408), (920, 355), False, None),
        ((214, 408), (920, 495), False, None),
        ((214, 408), (920, 635), False, None),
        ((770, 185), (1290, 215), True, "<<include>>"),
    ]
    return make_use_case(path, "管理员", "后台管理员用例图", cases, links)


def make_architecture() -> Path:
    path = ASSET_DIR / "fig_4_1_architecture_standard.png"
    img = Image.new("RGB", (1820, 1080), BG)
    draw = ImageDraw.Draw(img)
    ft_title = font(FONT_HEI, 26)
    ft_layer = font(FONT_HEI, 24)
    ft_box = font(FONT_SONG, 19)
    ft_small = font(FONT_SONG, 17)

    layers = [
        ("访问层", (120, 110, 1700, 230)),
        ("接口/应用层", (120, 290, 1700, 470)),
        ("业务服务层", (120, 530, 1700, 760)),
        ("数据与 AI 支撑层", (120, 820, 1700, 950)),
    ]
    for name, box in layers:
        rounded(draw, box, radius=18, fill=BG, outline="#c8ccd2", width=2)
        draw.rectangle((box[0], box[1], box[0] + 160, box[3]), fill=LIGHT, outline="#c8ccd2", width=1)
        center_text(draw, (box[0] + 10, box[1], box[0] + 150, box[3]), [name], ft_layer)

    for box, lines in [
        ((360, 135, 650, 205), ["用户端 Vue3"]),
        ((880, 135, 1170, 205), ["管理端 Vue3"]),
        ((260, 330, 490, 400), ["认证授权"]),
        ((530, 330, 760, 400), ["知识管理"]),
        ((800, 330, 1030, 400), ["文件处理"]),
        ((1070, 330, 1300, 400), ["图谱服务"]),
        ((1340, 330, 1570, 400), ["问答服务"]),
        ((640, 560, 900, 640), ["Spring Boot / WebFlux"]),
        ((280, 660, 540, 730), ["统计报表"]),
        ((580, 660, 840, 730), ["任务调度"]),
        ((880, 660, 1140, 730), ["实体确认"]),
        ((1180, 660, 1440, 730), ["系统公告 / 用户管理"]),
        ((220, 845, 420, 915), ["MySQL"]),
        ((470, 845, 670, 915), ["Redis"]),
        ((720, 845, 920, 915), ["RabbitMQ"]),
        ((970, 845, 1170, 915), ["MinIO"]),
        ((1220, 845, 1420, 915), ["Milvus"]),
        ((1470, 845, 1640, 915), ["OCR / Whisper ASR"]),
    ]:
        rounded(draw, box)
        center_text(draw, box, lines, ft_box)

    for x in (505, 1025):
        arrow(draw, [(x, 205), (x, 290)], label="HTTP / SSE", label_font=ft_small)
    for x in (375, 645, 915, 1185, 1455):
        arrow(draw, [(x, 400), (x, 530)])
    for x in (410, 710, 1010, 1310):
        arrow(draw, [(x, 730), (x, 820)])

    center_text(draw, (0, 25, 1820, 70), ["系统整体结构图"], ft_title)
    img.save(path)
    return path


def make_module_tree() -> Path:
    path = ASSET_DIR / "fig_4_2_module_tree_standard.png"
    img = Image.new("RGB", (1820, 1060), BG)
    draw = ImageDraw.Draw(img)
    ft_title = font(FONT_HEI, 26)
    ft_root = font(FONT_HEI, 24)
    ft_box = font(FONT_SONG, 18)

    root = (700, 90, 1120, 165)
    rounded(draw, root)
    center_text(draw, root, ["美业多媒体知识服务系统"], ft_root)

    level1 = [
        ("用户端模块", (120, 280, 300, 350)),
        ("管理端模块", (340, 280, 520, 350)),
        ("知识治理模块", (560, 280, 740, 350)),
        ("文件处理模块", (780, 280, 960, 350)),
        ("实体确认模块", (1000, 280, 1180, 350)),
        ("问答服务模块", (1220, 280, 1400, 350)),
        ("统计分析模块", (1440, 280, 1620, 350)),
        ("基础设施模块", (840, 700, 1020, 770)),
    ]
    level2 = {
        "用户端模块": ["首页浏览", "知识检索", "收藏管理"],
        "管理端模块": ["概览看板", "用户管理", "公告管理"],
        "知识治理模块": ["知识管理", "分类管理", "知识详情"],
        "文件处理模块": ["文件上传", "任务监控", "处理追踪"],
        "实体确认模块": ["候选确认", "图谱维护", "关系修订"],
        "问答服务模块": ["智能问答", "附件问答", "会话管理"],
        "统计分析模块": ["统计报表", "行为记录", "运行分析"],
        "基础设施模块": ["MySQL/Redis", "MinIO/Milvus", "RabbitMQ/OCR/ASR"],
    }
    centers = {}
    root_cx = (root[0] + root[2]) // 2
    for title, box in level1:
        rounded(draw, box)
        center_text(draw, box, [title], ft_box)
        cx = (box[0] + box[2]) // 2
        centers[title] = cx
        if box[1] < 500:
            arrow(draw, [(root_cx, root[3]), (root_cx, 220), (cx, 220), (cx, box[1])], width=2, head=8)
        else:
            arrow(draw, [(root_cx, root[3]), (root_cx, 650), (cx, 650), (cx, box[1])], width=2, head=8)
        subs = level2[title]
        if box[1] < 500:
            y = 470
        else:
            y = 860
        for i, txt in enumerate(subs):
            sub = (box[0] - 10, y + i * 78, box[2] + 10, y + i * 78 + 56)
            rounded(draw, sub, radius=12)
            center_text(draw, sub, [txt], ft_box)
            arrow(draw, [(cx, box[3]), (cx, sub[1])], width=2, head=8)

    center_text(draw, (0, 22, 1820, 68), ["系统功能模块设计图"], ft_title)
    img.save(path)
    return path


def make_er() -> Path:
    path = ASSET_DIR / "fig_4_3_er_standard.png"
    img = Image.new("RGB", (1900, 1180), BG)
    draw = ImageDraw.Draw(img)
    ft_title = font(FONT_HEI, 26)
    ft_entity = font(FONT_HEI, 20)
    ft_attr = font(FONT_SONG, 16)
    ft_rel = font(FONT_SONG, 18)
    ft_card = font(FONT_SONG, 16)

    entities = {
        "分类": (130, 170, 300, 250),
        "知识": (520, 170, 690, 250),
        "文件": (910, 170, 1080, 250),
        "任务": (1300, 170, 1470, 250),
        "图谱实体": (390, 690, 580, 770),
        "图谱关系": (900, 690, 1090, 770),
        "会话": (1270, 690, 1440, 770),
        "消息": (1600, 690, 1770, 770),
    }
    for title, box in entities.items():
        entity(draw, box, title, ft_entity, ft_attr)

    attrs = [
        ((40, 95, 170, 145), "category_id", True, "分类"),
        ((250, 95, 380, 145), "name", False, "分类"),
        ((430, 95, 560, 145), "knowledge_id", True, "知识"),
        ((650, 95, 780, 145), "title", False, "知识"),
        ((820, 95, 950, 145), "file_id", True, "文件"),
        ((1040, 95, 1170, 145), "file_name", False, "文件"),
        ((1210, 95, 1340, 145), "task_id", True, "任务"),
        ((1430, 95, 1560, 145), "task_status", False, "任务"),
        ((270, 820, 410, 870), "entity_id", True, "图谱实体"),
        ((560, 820, 700, 870), "entity_name", False, "图谱实体"),
        ((790, 820, 930, 870), "relation_id", True, "图谱关系"),
        ((1060, 820, 1200, 870), "relation_type", False, "图谱关系"),
        ((1180, 820, 1320, 870), "session_id", True, "会话"),
        ((1390, 820, 1530, 870), "user_id", False, "会话"),
        ((1530, 820, 1670, 870), "message_id", True, "消息"),
        ((1740, 820, 1860, 870), "role", False, "消息"),
    ]
    centers = {k: ((v[0] + v[2]) // 2, (v[1] + v[3]) // 2) for k, v in entities.items()}
    for box, txt, primary, owner in attrs:
        attribute(draw, box, txt, ft_attr, primary)
        line(draw, [centers[owner], ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)], width=1)

    r1 = diamond(draw, (410, 210), (100, 70), "归属", ft_rel)
    r2 = diamond(draw, (800, 210), (100, 70), "关联", ft_rel)
    r3 = diamond(draw, (1190, 210), (100, 70), "生成", ft_rel)
    r4 = diamond(draw, (730, 565), (120, 76), "抽取产生", ft_rel)
    r5 = diamond(draw, (780, 730), (120, 76), "源/目标参与", ft_rel)
    r6 = diamond(draw, (1520, 730), (100, 70), "包含", ft_rel)

    line(draw, [(300, 210), (360, 210)])
    line(draw, [(460, 210), (520, 210)])
    line(draw, [(690, 210), (750, 210)])
    line(draw, [(850, 210), (910, 210)])
    line(draw, [(1080, 210), (1140, 210)])
    line(draw, [(1240, 210), (1300, 210)])
    line(draw, [(605, 250), (605, 565), (670, 565)])
    line(draw, [(485, 690), (485, 650), (670, 650), (670, 602)])
    line(draw, [(995, 690), (995, 650), (790, 650), (790, 602)])
    line(draw, [(1440, 730), (1470, 730)])
    line(draw, [(1570, 730), (1600, 730)])

    for pos, txt in [
        ((325, 186), "1"), ((487, 186), "N"),
        ((715, 186), "1"), ((877, 186), "N"),
        ((1105, 186), "1"), ((1268, 186), "N"),
        ((630, 525), "1"), ((565, 650), "N"),
        ((835, 650), "N"), ((1450, 706), "1"),
        ((1585, 706), "N"),
    ]:
        cardinality(draw, pos, txt, ft_card)

    center_text(draw, (0, 22, 1900, 68), ["系统 ER 图"], ft_title)
    img.save(path)
    return path


def generate_assets() -> dict[str, Path]:
    assets = {
        "图 3-1 系统业务流程图": make_business_flow(),
        "图 3-2 系统数据流图": make_dfd(),
        "图 3-3 普通用户用例图": make_user_use_case(),
        "图 3-4 后台管理员用例图": make_admin_use_case(),
        "图 4-1 系统整体结构图": make_architecture(),
        "图 4-2 系统功能模块设计图": make_module_tree(),
        "图 4-3 系统 ER 图": make_er(),
    }
    for path in assets.values():
        recenter_asset(path)
    return assets


TEXT_REPLACEMENTS = {
    "从整体业务链路看，系统运行过程可概括为“资料接入、内容处理、知识沉淀、服务输出”四个阶段。无论是管理员直接录入知识，还是通过文件上传触发处理流程，最终都需要回归到统一知识库与图谱资源中，再由用户端完成检索、浏览和问答调用。系统主要业务流程如图 3-1 所示。":
        "从整体业务链路看，系统运行过程可概括为“资料接入、内容处理、知识沉淀、服务输出”四个阶段。为体现各参与方之间的职责划分与流转顺序，本文采用标准业务流程图描述普通用户、管理员与系统处理链路之间的协同关系，系统主要业务流程如图 3-1 所示。",
    "如图 3-2 所示，系统在接收用户请求后，会先经过登录鉴权与角色识别，再根据业务类型进入知识检索、文件处理、实体审核或问答服务链路。在数据支撑层面，关系型数据库负责业务实体与状态管理，对象存储负责原始文件保存，向量索引负责语义召回支撑。该数据流模型说明，本系统的需求分析已经从单纯功能罗列提升为面向多源数据协同与知识治理闭环的工程建模。":
        "如图 3-2 所示，系统数据流图采用外部实体、处理过程、数据存储与数据流四类标准元素进行表达。系统在接收用户请求后，会先经过登录鉴权与角色识别，再根据业务类型进入知识检索、文件处理、实体审核或智能问答链路，业务数据库、对象存储与向量库共同构成后台数据支撑。",
    "图中将普通用户、管理员、业务处理模块及三类核心数据存储进行统一表达，能够说明系统需求分析阶段已经考虑了资料接入、知识沉淀与问答输出之间的完整闭环。":
        "图中将普通用户、管理员、各处理过程以及三类核心数据存储进行统一表达，能够说明系统需求分析阶段已经考虑了资料接入、知识沉淀与问答输出之间的数据闭环。",
    "为了更准确地界定系统角色边界与功能职责，本文采用标准 UML 用例图描述普通用户与后台管理员的典型交互行为，并分别建立角色视角下的功能集合。":
        "为了更准确地界定系统角色边界与功能职责，本文采用标准 UML 用例图描述普通用户与后台管理员的典型交互行为，并分别建立角色视角下的功能集合。",
    "如图 3-3 所示，普通用户是系统面向服务输出的核心参与者，其主要使用场景集中在知识浏览、搜索、收藏与智能问答等交互功能上。":
        "如图 3-3 所示，普通用户用例图重点描述首页浏览、知识检索、知识详情查看、收藏管理以及智能问答等核心交互场景，并通过包含关系体现提问、附件上传与会话追问等公共子行为。",
    "如图 3-4 所示，后台管理员承担知识治理与系统维护职责，需要围绕分类、知识、文件、任务、实体和系统配置等对象进行统一管理。":
        "如图 3-4 所示，后台管理员承担知识治理与系统维护职责，需要围绕概览看板、知识管理、分类管理、文件上传、任务监控、实体确认、图谱维护、公告管理、用户管理和统计查看等对象进行统一管理。",
    "如图 4-1 所示，系统整体结构按照“前端表示层、业务处理层、基础设施支撑层”进行组织。用户端与管理端均通过统一接口进入后台服务，业务层分别承担认证授权、知识治理、文件处理、图谱管理、问答编排与统计分析等职责，基础设施模块则对存储、缓存、消息调度和向量检索提供统一支撑。这种拆分方式能够降低模块间直接耦合，使同步页面交互与异步处理任务可以在统一架构下协同运行。":
        "如图 4-1 所示，系统整体结构采用分层架构表达，可划分为访问层、接口/应用层、业务服务层以及数据与 AI 支撑层。用户端与管理端通过统一接口访问后台服务，业务层分别承担认证授权、知识治理、文件处理、图谱服务、问答编排与统计分析等职责，MySQL、Redis、RabbitMQ、MinIO、Milvus、OCR 与 Whisper ASR 等组件共同提供底层支撑。",
    "在总体设计层面，为了把系统的角色入口、治理链路和服务链路对应到可实现的模块边界，本文进一步绘制了功能模块设计图。":
        "在总体设计层面，为了把系统的角色入口、治理链路和服务链路对应到可实现的模块边界，本文进一步采用树状分解方式绘制了功能模块设计图。",
    "图 4-2 将系统划分为用户端、管理端、知识治理、文件处理、实体确认、问答服务和基础设施支撑等核心模块，各模块在职责上相对独立、在服务链路上相互衔接，能够支撑美业多媒体知识服务系统的整体运行。":
        "图 4-2 将系统划分为用户端模块、管理端模块、知识治理模块、文件处理模块、实体确认模块、问答服务模块、统计分析模块和基础设施模块，各模块在职责上相对独立、在服务链路上相互衔接，能够支撑美业多媒体知识服务系统的整体运行。",
    "如图 4-3 所示，系统数据库结构围绕知识治理、文件处理、图谱组织与问答会话四类核心业务对象进行设计。":
        "如图 4-3 所示，系统 ER 图围绕知识治理、文件处理、图谱组织与问答会话四类核心业务对象进行设计，并通过实体、属性、联系及基数表达数据库中的关键结构关系。",
    "图中以分类、知识、文件、任务、图谱实体、图谱关系、会话和消息等实体为核心，反映了系统从资料接入到知识沉淀、再到服务输出的主要数据组织方式。":
        "图中以分类、知识、文件、任务、图谱实体、图谱关系、会话和消息等实体为核心，通过“归属、关联、生成、抽取产生、包含”等联系表达系统从资料接入到知识沉淀、再到服务输出的主要数据组织方式。",
    "在该架构中，用户端与管理端共享统一的服务后端，但在页面入口和业务职责上保持相互独立。后端以认证授权、知识管理、文件处理、图谱服务和问答服务为核心，围绕实际业务流程进行模块组织。数据层通过结构化存储与向量检索相结合的方式，同时支持传统业务数据管理和智能问答场景下的语义检索需求。整体而言，该架构既满足日常知识管理要求，也为图谱分析和检索增强生成问答提供了技术基础。系统整体结构如图 4-1 所示。":
        "在该架构中，用户端与管理端共享统一的服务后端，但在页面入口和业务职责上保持相互独立。整体结构按照访问层、接口/应用层、业务服务层和数据与 AI 支撑层进行组织，其中认证授权、知识管理、文件处理、图谱服务、问答服务与统计分析共同构成核心业务能力，MySQL、Redis、RabbitMQ、MinIO、Milvus、OCR 与 Whisper ASR 等组件提供底层支撑。系统整体结构如图 4-1 所示。",
    "图 4-2 将系统划分为用户端、管理端、知识治理、文件处理、实体确认、知识图谱、问答服务和基础设施八个模块。这种划分与项目当前的前后端目录结构和控制器职责基本一致，能够为后续详细设计章节提供稳定的结构基础。":
        "图 4-2 将系统划分为用户端模块、管理端模块、知识治理模块、文件处理模块、实体确认模块、问答服务模块、统计分析模块和基础设施模块。这种划分与项目当前的前后端目录结构和控制器职责基本一致，能够为后续详细设计章节提供稳定的结构基础。",
    "从数据组织方式看，系统既保留了传统关系型数据库在事务管理和业务数据存储方面的优势，又通过切片数据与向量库协同支持检索增强场景下的语义检索需求。数据库结构不仅服务于基础的增删改查操作，还需要适配文件处理、知识抽取、图谱查询和问答证据回填等复合业务场景。因此，在总体设计中，数据库不只是底层存储结构，更是系统各类业务能力得以协同实现的重要支撑。系统主要实体及关系组织如图 4-3 所示。":
        "从数据组织方式看，系统既保留了传统关系型数据库在事务管理和业务数据存储方面的优势，又通过切片数据与向量库协同支持检索增强场景下的语义检索需求。为更清晰地表达数据库中的关键结构关系，本文采用标准 ER 图对分类、知识、文件、任务、图谱实体、图谱关系、会话和消息等核心实体及其联系进行说明，系统主要实体及关系组织如图 4-3 所示。",
    "从论文表达角度看，数据库设计也是衔接总体设计与详细实现的重要环节。只有当表结构、主外键关系和关键字段语义足够清晰时，后续关于模块实现、接口调用和测试验证的描述才能形成自洽逻辑。因此，本系统的数据库设计既体现业务对象的静态组织方式，也体现处理流程的动态支撑能力。":
        "从论文表达角度看，数据库设计也是衔接总体设计与详细实现的重要环节。只有当实体、属性、联系、主外键关系和关键字段语义足够清晰时，后续关于模块实现、接口调用和测试验证的描述才能形成自洽逻辑。因此，本系统的数据库设计既体现业务对象的静态组织方式，也体现处理流程的动态支撑能力。",
}


def replace_docx(assets: dict[str, Path]) -> None:
    tmp = DOCX_PATH.with_suffix(".tmp")
    shutil.copy2(DOCX_PATH, tmp)
    with ZipFile(tmp) as zin:
        doc_xml = zin.read("word/document.xml")
        rel_xml = zin.read("word/_rels/document.xml.rels")

    doc_root = ET.fromstring(doc_xml)
    rel_root = ET.fromstring(rel_xml)
    rel_map = {rel.get("Id"): rel.get("Target") for rel in rel_root}
    paragraphs = doc_root.findall(".//w:body/w:p", NS)
    targets: dict[str, str] = {}

    for p in paragraphs:
        txt = para_text(p)
        if txt in TEXT_REPLACEMENTS:
            texts = p.findall(".//w:t", NS)
            if texts:
                texts[0].text = TEXT_REPLACEMENTS[txt]
                for t in texts[1:]:
                    t.text = ""
        blips = p.findall(".//a:blip", NS)
        if not blips:
            continue
        cap = nearest_caption(paragraphs, paragraphs.index(p))
        if cap in assets:
            set_center_paragraph(p)
            set_extent(p, next(f.width_cm for f in FIGURES if f.caption == cap), assets[cap])
            for blip in blips:
                rid = blip.get(qn(R, "embed"))
                if rid and rid in rel_map:
                    target = rel_map[rid]
                    if not target.startswith("word/"):
                        target = f"word/{target.lstrip('./')}"
                    targets[target] = cap

    with ZipFile(tmp) as zin, ZipFile(DOCX_PATH, "w", ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "word/document.xml":
                data = ET.tostring(doc_root, encoding="utf-8", xml_declaration=True)
            elif info.filename in targets:
                data = assets[targets[info.filename]].read_bytes()
            zout.writestr(info, data)
    tmp.unlink(missing_ok=True)


def main() -> None:
    assets = generate_assets()
    replace_docx(assets)
    print("Updated:", DOCX_PATH)
    for caption, path in assets.items():
        print(caption, "->", path)


if __name__ == "__main__":
    main()
