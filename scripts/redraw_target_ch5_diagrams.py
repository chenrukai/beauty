from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import os
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"D:\beauty")
DEFAULT_DOCX = ROOT / "毕业论文_最终稿_规范达标版 - 副本._tmp_fix_第五章标准流程图.docx"
DOCX = Path(os.environ.get("TARGET_DOCX", str(DEFAULT_DOCX)))
ASSET_DIR = ROOT / "final_assets" / "thesis_copy_fix"
ASSET_DIR.mkdir(parents=True, exist_ok=True)

FONT_SONG = Path(r"C:\Windows\Fonts\simsun.ttc")
FONT_HEI = Path(r"C:\Windows\Fonts\simhei.ttf")

WHITE = "#ffffff"
BLACK = "#111111"
LINE = "#222222"
SOFT = "#f7f7f7"
YELLOW = "#f6f0b2"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def canvas(title: str, size: tuple[int, int]) -> tuple[Image.Image, ImageDraw.ImageDraw, dict[str, ImageFont.FreeTypeFont]]:
    img = Image.new("RGB", size, WHITE)
    draw = ImageDraw.Draw(img)
    fonts = {
        "title": font(FONT_HEI, 30),
        "node": font(FONT_SONG, 22),
        "small": font(FONT_SONG, 18),
        "tiny": font(FONT_SONG, 16),
    }
    bb = draw.textbbox((0, 0), title, font=fonts["title"])
    draw.text(((size[0] - (bb[2] - bb[0])) / 2, 24), title, font=fonts["title"], fill=BLACK)
    return img, draw, fonts


def centered(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], lines: list[str],
             fnt: ImageFont.FreeTypeFont, fill: str = BLACK, gap: int = 6) -> None:
    x1, y1, x2, y2 = box
    bbs = [draw.textbbox((0, 0), line, font=fnt) for line in lines]
    heights = [bb[3] - bb[1] for bb in bbs]
    widths = [bb[2] - bb[0] for bb in bbs]
    total_h = sum(heights) + gap * max(0, len(lines) - 1)
    y = y1 + (y2 - y1 - total_h) / 2
    for line, w, h in zip(lines, widths, heights):
        x = x1 + (x2 - x1 - w) / 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += h + gap


def box(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], lines: list[str],
        fnt: ImageFont.FreeTypeFont, rounded: bool = False) -> tuple[int, int, int, int]:
    if rounded:
        draw.rounded_rectangle(rect, radius=18, fill=WHITE, outline=BLACK, width=3)
    else:
        draw.rectangle(rect, fill=WHITE, outline=BLACK, width=3)
    centered(draw, rect, lines, fnt)
    return rect


def terminal(draw: ImageDraw.ImageDraw, cx: int, top: int, w: int, h: int, label: str,
             fnt: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    rect = (cx - w // 2, top, cx + w // 2, top + h)
    draw.rounded_rectangle(rect, radius=h // 2, fill=WHITE, outline=BLACK, width=3)
    centered(draw, rect, [label], fnt)
    return rect


def decision(draw: ImageDraw.ImageDraw, cx: int, top: int, w: int, h: int, lines: list[str],
             fnt: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    cy = top + h // 2
    pts = [(cx, top), (cx + w // 2, cy), (cx, top + h), (cx - w // 2, cy)]
    draw.polygon(pts, fill=WHITE, outline=BLACK, width=3)
    centered(draw, (cx - w // 2 + 20, top + 10, cx + w // 2 - 20, top + h - 10), lines, fnt)
    return cx - w // 2, top, cx + w // 2, top + h


def arrow(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], width: int = 4) -> None:
    for a, b in zip(pts, pts[1:]):
        draw.line((a, b), fill=LINE, width=width)
    x1, y1 = pts[-2]
    x2, y2 = pts[-1]
    if abs(x2 - x1) >= abs(y2 - y1):
        if x2 >= x1:
            tri = [(x2, y2), (x2 - 16, y2 - 9), (x2 - 16, y2 + 9)]
        else:
            tri = [(x2, y2), (x2 + 16, y2 - 9), (x2 + 16, y2 + 9)]
    else:
        if y2 >= y1:
            tri = [(x2, y2), (x2 - 9, y2 - 16), (x2 + 9, y2 - 16)]
        else:
            tri = [(x2, y2), (x2 - 9, y2 + 16), (x2 + 9, y2 + 16)]
    draw.polygon(tri, fill=LINE)


def text_label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fnt: ImageFont.FreeTypeFont) -> None:
    bb = draw.textbbox((0, 0), text, font=fnt)
    draw.rectangle((x - 5, y - 3, x + bb[2] - bb[0] + 5, y + bb[3] - bb[1] + 3), fill=WHITE)
    draw.text((x, y), text, font=fnt, fill=BLACK)


def actor(draw: ImageDraw.ImageDraw, x: int, y: int, label_text: str, fnt: ImageFont.FreeTypeFont) -> None:
    draw.ellipse((x - 16, y, x + 16, y + 32), outline=BLACK, width=2)
    draw.line((x, y + 32, x, y + 85), fill=BLACK, width=2)
    draw.line((x - 28, y + 48, x + 28, y + 48), fill=BLACK, width=2)
    draw.line((x, y + 85, x - 22, y + 118), fill=BLACK, width=2)
    draw.line((x, y + 85, x + 22, y + 118), fill=BLACK, width=2)
    bb = draw.textbbox((0, 0), label_text, font=fnt)
    tx = x - (bb[2] - bb[0]) / 2
    ty = y + 130
    draw.text((tx, ty), label_text, font=fnt, fill=BLACK)
    draw.line((tx, ty + bb[3] - bb[1] + 3, tx + bb[2] - bb[0], ty + bb[3] - bb[1] + 3), fill=BLACK, width=1)


def object_node(draw: ImageDraw.ImageDraw, cx: int, cy: int, name: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    r = 34
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=YELLOW, outline=BLACK, width=2)
    bb = draw.textbbox((0, 0), name, font=fnt)
    tx = cx - (bb[2] - bb[0]) / 2
    ty = cy + 48
    draw.text((tx, ty), name, font=fnt, fill=BLACK)
    draw.line((tx, ty + bb[3] - bb[1] + 3, tx + bb[2] - bb[0], ty + bb[3] - bb[1] + 3), fill=BLACK, width=1)
    return cx, cy


def line_only(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], width: int = 2) -> None:
    for a, b in zip(pts, pts[1:]):
        draw.line((a, b), fill=LINE, width=width)


def page_box(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], lines: list[str], fnt: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    draw.rounded_rectangle(rect, radius=14, fill=WHITE, outline=BLACK, width=3)
    centered(draw, rect, lines, fnt)
    return rect


def build_5_1() -> Path:
    path = ASSET_DIR / "fig_5_1_collaboration_standard.png"
    img, draw, ft = canvas("系统详细设计模块协作图", (1700, 980))

    actor(draw, 180, 100, "普通用户", ft["small"])
    actor(draw, 1520, 100, "管理员", ft["small"])

    ui = object_node(draw, 430, 330, "前端交互界面", ft["small"])
    route = object_node(draw, 820, 260, "路由与权限控制", ft["small"])
    biz = object_node(draw, 1220, 330, "业务处理服务", ft["small"])
    file_obj = object_node(draw, 720, 610, "知识与文件处理", ft["small"])
    qa = object_node(draw, 1120, 610, "智能问答服务", ft["small"])
    data = object_node(draw, 1460, 610, "数据存储层", ft["small"])

    line_only(draw, [(180, 230), ui], width=2)
    line_only(draw, [(1520, 230), biz], width=2)
    line_only(draw, [ui, route], width=2)
    line_only(draw, [route, biz], width=2)
    line_only(draw, [biz, file_obj], width=2)
    line_only(draw, [biz, qa], width=2)
    line_only(draw, [biz, data], width=2)
    line_only(draw, [file_obj, data], width=2)
    line_only(draw, [qa, data], width=2)

    text_label(draw, 210, 250, "1: 发起页面请求()", ft["tiny"])
    text_label(draw, 520, 250, "2: 进行路由校验()", ft["tiny"])
    text_label(draw, 900, 250, "3: 分发业务调用()", ft["tiny"])
    text_label(draw, 1295, 250, "4: 管理入口鉴权()", ft["tiny"])
    text_label(draw, 760, 445, "5: 提交知识/文件处理()", ft["tiny"])
    text_label(draw, 1140, 445, "6: 调用问答服务()", ft["tiny"])
    text_label(draw, 1320, 445, "7: 读写业务数据()", ft["tiny"])
    text_label(draw, 980, 680, "8: 返回处理结果()", ft["tiny"])

    img.save(path)
    return path


def build_5_2() -> Path:
    path = ASSET_DIR / "fig_5_2_page_relation_standard.png"
    img, draw, ft = canvas("用户端页面跳转关系图", (1500, 900))

    home = page_box(draw, (110, 320, 310, 400), ["首页"], ft["node"])
    list_box = page_box(draw, (430, 180, 690, 260), ["知识列表/搜索"], ft["node"])
    detail = page_box(draw, (820, 180, 1040, 260), ["知识详情"], ft["node"])
    announce = page_box(draw, (430, 430, 690, 510), ["公告与推荐入口"], ft["node"])
    fav = page_box(draw, (820, 430, 1040, 510), ["收藏管理"], ft["node"])
    chat = page_box(draw, (1150, 305, 1370, 385), ["智能问答"], ft["node"])
    attach = page_box(draw, (1150, 500, 1370, 580), ["附件追问"], ft["node"])

    arrow(draw, [(310, 350), (370, 350), (370, 220), (430, 220)])
    arrow(draw, [(310, 370), (370, 370), (370, 470), (430, 470)])
    arrow(draw, [(690, 220), (820, 220)])
    arrow(draw, [(690, 470), (820, 470)])
    arrow(draw, [(1040, 220), (1090, 220), (1090, 345), (1150, 345)])
    arrow(draw, [(1040, 470), (1090, 470), (1090, 365), (1150, 365)])
    arrow(draw, [(1260, 385), (1260, 500)])

    text_label(draw, 340, 205, "进入知识浏览链路", ft["tiny"])
    text_label(draw, 342, 520, "进入推荐与公告链路", ft["tiny"])
    text_label(draw, 720, 188, "查看详情", ft["tiny"])
    text_label(draw, 725, 438, "管理收藏", ft["tiny"])
    text_label(draw, 1088, 278, "发起问答", ft["tiny"])
    text_label(draw, 1090, 430, "携带上下文问答", ft["tiny"])
    text_label(draw, 1275, 435, "继续追问", ft["tiny"])

    img.save(path)
    return path


def build_5_3() -> Path:
    path = ASSET_DIR / "fig_5_3_knowledge_flow_standard.png"
    img, draw, ft = canvas("知识管理模块处理流程图", (1600, 1280))
    cx = 800
    start = terminal(draw, cx, 90, 220, 56, "开始", ft["node"])
    p1 = box(draw, (540, 180, 1060, 258), ["进入知识管理页面"], ft["node"])
    p2 = box(draw, (500, 320, 1100, 412), ["录入标题、分类、摘要、正文"], ft["node"])
    d1 = decision(draw, cx, 490, 420, 110, ["信息是否完整？"], ft["node"])
    left_fix = box(draw, (110, 620, 420, 710), ["补充或修改", "知识信息"], ft["node"])
    save = box(draw, (600, 620, 1000, 710), ["保存知识内容"], ft["node"])
    d2 = decision(draw, cx, 805, 420, 110, ["是否包含附件？"], ft["node"])
    assoc = box(draw, (1130, 930, 1470, 1020), ["上传并关联附件", "登记文件信息"], ft["node"])
    write = box(draw, (560, 930, 1040, 1020), ["写入知识表/文件表", "并更新索引"], ft["node"])
    view = box(draw, (560, 1090, 1040, 1175), ["用户检索并查看详情"], ft["node"])
    end = terminal(draw, cx, 1215, 220, 56, "结束", ft["node"])

    for a, b in [(start, p1), (p1, p2), (p2, d1), (save, d2), (write, view), (view, end)]:
        arrow(draw, [((a[0]+a[2])//2, a[3]), ((b[0]+b[2])//2, b[1])])
    arrow(draw, [(cx, d1[3]), (cx, save[1])])
    text_label(draw, 850, 585, "是", ft["small"])
    arrow(draw, [(d1[0], (d1[1]+d1[3])//2), (80, (d1[1]+d1[3])//2), (80, 665), (420, 665)])
    text_label(draw, 105, 500, "否", ft["small"])
    arrow(draw, [(420, 665), (560, 665)])
    arrow(draw, [(cx, d2[3]), (cx, write[1])])
    text_label(draw, 850, 900, "否", ft["small"])
    arrow(draw, [(d2[2], (d2[1]+d2[3])//2), (1510, (d2[1]+d2[3])//2), (1510, 975), (1470, 975)])
    text_label(draw, 1380, 815, "是", ft["small"])
    arrow(draw, [(1130, 975), (1040, 975)])
    img.save(path)
    return path


def build_5_4() -> Path:
    path = ASSET_DIR / "fig_5_4_file_flow_standard.png"
    img, draw, ft = canvas("文件处理模块流程图", (1600, 1280))
    cx = 800
    start = terminal(draw, cx, 80, 220, 56, "开始", ft["node"])
    p1 = box(draw, (600, 170, 1000, 248), ["上传原始文件"], ft["node"])
    p2 = box(draw, (500, 310, 1100, 406), ["写入对象存储", "并登记文件/任务记录"], ft["node"])
    d1 = decision(draw, cx, 485, 430, 110, ["文件类型是否可识别？"], ft["node"])
    fail1 = box(draw, (90, 620, 420, 710), ["记录失败原因", "等待人工重试"], ft["node"])
    parse = box(draw, (500, 620, 1100, 712), ["按类型执行 OCR", "或 Whisper 转写"], ft["node"])
    clean = box(draw, (590, 780, 1010, 860), ["文本清洗与切片"], ft["node"])
    entity = box(draw, (590, 930, 1010, 1010), ["生成候选实体"], ft["node"])
    d2 = decision(draw, cx, 1085, 420, 110, ["处理是否成功？"], ft["node"])
    fail2 = box(draw, (1090, 1180, 1470, 1270), ["更新失败状态", "支持再次重试"], ft["node"])
    ok = box(draw, (530, 1180, 1070, 1270), ["保存文本结果", "进入后续治理链路"], ft["node"])
    end = terminal(draw, cx, 1295, 220, 56, "结束", ft["node"])

    for a, b in [(start, p1), (p1, p2), (p2, d1), (parse, clean), (clean, entity), (entity, d2), (ok, end)]:
        arrow(draw, [((a[0]+a[2])//2, a[3]), ((b[0]+b[2])//2, b[1])])
    arrow(draw, [(d1[0], (d1[1]+d1[3])//2), (70, (d1[1]+d1[3])//2), (70, 665), (420, 665)])
    text_label(draw, 96, 496, "否", ft["small"])
    arrow(draw, [(cx, d1[3]), (cx, parse[1])])
    text_label(draw, 850, 585, "是", ft["small"])
    arrow(draw, [(cx, d2[3]), (cx, ok[1])])
    text_label(draw, 850, 1160, "是", ft["small"])
    arrow(draw, [(d2[2], (d2[1]+d2[3])//2), (1510, (d2[1]+d2[3])//2), (1510, 1225), (1470, 1225)])
    text_label(draw, 1380, 1090, "否", ft["small"])
    arrow(draw, [(1090, 1225), (1070, 1225)])
    img.save(path)
    return path


def build_5_5() -> Path:
    path = ASSET_DIR / "fig_5_5_graph_flow_standard.png"
    img, draw, ft = canvas("知识图谱查询流程图", (1600, 1280))
    cx = 800
    start = terminal(draw, cx, 80, 220, 56, "开始", ft["node"])
    p1 = box(draw, (520, 170, 1080, 248), ["进入实体审核/图谱查询"], ft["node"])
    p2 = box(draw, (500, 310, 1100, 406), ["生成候选实体", "与候选关系"], ft["node"])
    d1 = decision(draw, cx, 485, 420, 110, ["审核是否通过？"], ft["node"])
    revise = box(draw, (80, 620, 430, 710), ["修订、驳回或补充", "候选结果"], ft["node"])
    write = box(draw, (560, 620, 1040, 710), ["写入图谱实体", "与关系数据"], ft["node"])
    query = box(draw, (560, 775, 1040, 855), ["发起邻居/路径/证据查询"], ft["node"])
    d2 = decision(draw, cx, 930, 420, 110, ["是否命中图谱结果？"], ft["node"])
    retry = box(draw, (1120, 1070, 1480, 1160), ["调整查询条件", "重新发起查询"], ft["node"])
    show = box(draw, (520, 1070, 1080, 1160), ["返回图谱结果", "及证据文本"], ft["node"])
    end = terminal(draw, cx, 1190, 220, 56, "结束", ft["node"])

    for a, b in [(start, p1), (p1, p2), (p2, d1), (write, query), (show, end)]:
        arrow(draw, [((a[0]+a[2])//2, a[3]), ((b[0]+b[2])//2, b[1])])
    arrow(draw, [(d1[0], (d1[1]+d1[3])//2), (60, (d1[1]+d1[3])//2), (60, 665), (430, 665)])
    text_label(draw, 86, 498, "否", ft["small"])
    arrow(draw, [(cx, d1[3]), (cx, write[1])])
    text_label(draw, 850, 585, "是", ft["small"])
    arrow(draw, [((query[0]+query[2])//2, query[3]), (cx, d2[1])])
    arrow(draw, [(cx, d2[3]), (cx, show[1])])
    text_label(draw, 850, 1045, "是", ft["small"])
    arrow(draw, [(d2[2], (d2[1]+d2[3])//2), (1510, (d2[1]+d2[3])//2), (1510, 1115), (1480, 1115)])
    text_label(draw, 1380, 940, "否", ft["small"])
    arrow(draw, [(1120, 1115), (1090, 1115), (1090, 815), (1040, 815)])
    img.save(path)
    return path


def build_5_6() -> Path:
    path = ASSET_DIR / "fig_5_6_qa_flow_standard.png"
    img, draw, ft = canvas("智能问答模块流程图", (1600, 1280))
    cx = 800
    start = terminal(draw, cx, 80, 220, 56, "开始", ft["node"])
    p1 = box(draw, (560, 170, 1040, 248), ["输入问题或上传附件"], ft["node"])
    p2 = box(draw, (570, 310, 1030, 388), ["问题预处理"], ft["node"])
    p3 = box(draw, (500, 450, 1100, 546), ["关键词检索", "与向量召回"], ft["node"])
    d1 = decision(draw, cx, 620, 420, 110, ["证据是否充足？"], ft["node"])
    expand = box(draw, (1100, 760, 1470, 850), ["扩展检索范围", "或生成附件摘要"], ft["node"])
    rank = box(draw, (590, 760, 1010, 840), ["融合排序"], ft["node"])
    context = box(draw, (590, 915, 1010, 995), ["构建问答上下文"], ft["node"])
    answer = box(draw, (590, 1070, 1010, 1150), ["生成流式回答"], ft["node"])
    d2 = decision(draw, cx, 1200, 420, 110, ["用户是否继续追问？"], ft["node"])
    again = box(draw, (70, 1190, 420, 1280), ["保留会话上下文", "返回问题输入"], ft["node"])
    end = terminal(draw, cx, 1320, 220, 56, "结束", ft["node"])

    for a, b in [(start, p1), (p1, p2), (p2, p3), (rank, context), (context, answer)]:
        arrow(draw, [((a[0]+a[2])//2, a[3]), ((b[0]+b[2])//2, b[1])])
    arrow(draw, [(cx, d1[3]), (cx, rank[1])])
    text_label(draw, 850, 720, "是", ft["small"])
    arrow(draw, [(d1[2], (d1[1]+d1[3])//2), (1510, (d1[1]+d1[3])//2), (1510, 805), (1470, 805)])
    text_label(draw, 1380, 655, "否", ft["small"])
    arrow(draw, [(1100, 805), (1010, 805)])
    arrow(draw, [((answer[0]+answer[2])//2, answer[3]), (cx, d2[1])])
    arrow(draw, [(cx, d2[3]), (cx, end[1])])
    text_label(draw, 850, 1290, "否", ft["small"])
    arrow(draw, [(d2[0], (d2[1]+d2[3])//2), (50, (d2[1]+d2[3])//2), (50, 1235), (420, 1235)])
    text_label(draw, 80, 1168, "是", ft["small"])
    arrow(draw, [(420, 1235), (460, 1235), (460, 209), (560, 209)])
    img.save(path)
    return path


def build_assets() -> dict[str, bytes]:
    assets = {
        "word/media/image11.png": build_5_1().read_bytes(),
        "word/media/image12.png": build_5_2().read_bytes(),
        "word/media/image13.png": build_5_3().read_bytes(),
        "word/media/image14.png": build_5_4().read_bytes(),
        "word/media/image15.png": build_5_5().read_bytes(),
        "word/media/image16.png": build_5_6().read_bytes(),
    }
    return assets


def rewrite_docx(media_map: dict[str, bytes]) -> None:
    tmp = DOCX.with_suffix(".targetch5.tmp")
    shutil.copy2(DOCX, tmp)
    with ZipFile(tmp) as zin, ZipFile(DOCX, "w", ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename in media_map:
                data = media_map[info.filename]
            zout.writestr(info, data)
    tmp.unlink(missing_ok=True)


def main() -> None:
    rewrite_docx(build_assets())
    print("Updated", DOCX)


if __name__ == "__main__":
    main()
