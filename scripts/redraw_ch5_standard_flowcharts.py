from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"D:\beauty")
DOCX = next(p for p in ROOT.glob("*_tmp_fix.docx") if not p.name.startswith("~$"))
FALLBACK = DOCX.with_name(DOCX.stem + "_第五章标准流程图" + DOCX.suffix)
ASSET_DIR = ROOT / "final_assets" / "thesis_copy_fix"
ASSET_DIR.mkdir(parents=True, exist_ok=True)

FONT_SONG = Path(r"C:\Windows\Fonts\simsun.ttc")
FONT_HEI = Path(r"C:\Windows\Fonts\simhei.ttf")

WHITE = "#ffffff"
BLACK = "#111111"
GRAY = "#4d4d4d"
LINE = "#222222"

TARGETS = {
    "word/media/image13.png": "fig_5_3_knowledge_flow_standard.png",
    "word/media/image14.png": "fig_5_4_file_flow_standard.png",
    "word/media/image15.png": "fig_5_5_graph_flow_standard.png",
    "word/media/image16.png": "fig_5_6_qa_flow_standard.png",
}


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def centered(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], lines: list[str],
             fnt: ImageFont.FreeTypeFont, fill: str = WHITE, gap: int = 6) -> None:
    x1, y1, x2, y2 = box
    dims = [draw.textbbox((0, 0), line, font=fnt) for line in lines]
    heights = [bb[3] - bb[1] for bb in dims]
    widths = [bb[2] - bb[0] for bb in dims]
    total_h = sum(heights) + gap * (len(lines) - 1)
    y = y1 + (y2 - y1 - total_h) / 2
    for line, w, h in zip(lines, widths, heights):
        x = x1 + (x2 - x1 - w) / 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += h + gap


def draw_terminal(draw: ImageDraw.ImageDraw, center_x: int, top: int, width: int, height: int,
                  text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    box = (center_x - width // 2, top, center_x + width // 2, top + height)
    draw.rounded_rectangle(box, radius=height // 2, fill=WHITE, outline=BLACK, width=3)
    centered(draw, box, [text], fnt, BLACK)
    return box


def draw_process(draw: ImageDraw.ImageDraw, center_x: int, top: int, width: int, height: int,
                 lines: list[str], fnt: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    box = (center_x - width // 2, top, center_x + width // 2, top + height)
    draw.rectangle(box, fill=WHITE, outline=BLACK, width=3)
    centered(draw, box, lines, fnt, BLACK)
    return box


def draw_decision(draw: ImageDraw.ImageDraw, center_x: int, top: int, width: int, height: int,
                  lines: list[str], fnt: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    cx, cy = center_x, top + height // 2
    pts = [(cx, top), (cx + width // 2, cy), (cx, top + height), (cx - width // 2, cy)]
    draw.polygon(pts, fill=WHITE, outline=BLACK, width=3)
    centered(draw, (cx - width // 2 + 18, top + 12, cx + width // 2 - 18, top + height - 12), lines, fnt, BLACK, gap=4)
    return (cx - width // 2, top, cx + width // 2, top + height)


def arrow(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], width: int = 4, fill: str = LINE) -> None:
    for a, b in zip(pts, pts[1:]):
        draw.line((a, b), fill=fill, width=width)
    x1, y1 = pts[-2]
    x2, y2 = pts[-1]
    head = 10
    if abs(x2 - x1) >= abs(y2 - y1):
        if x2 >= x1:
            tri = [(x2, y2), (x2 - 16, y2 - head), (x2 - 16, y2 + head)]
        else:
            tri = [(x2, y2), (x2 + 16, y2 - head), (x2 + 16, y2 + head)]
    else:
        if y2 >= y1:
            tri = [(x2, y2), (x2 - head, y2 - 16), (x2 + head, y2 - 16)]
        else:
            tri = [(x2, y2), (x2 - head, y2 + 16), (x2 + head, y2 + 16)]
    draw.polygon(tri, fill=fill)


def label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fnt: ImageFont.FreeTypeFont) -> None:
    bb = draw.textbbox((0, 0), text, font=fnt)
    draw.rectangle((x - 6, y - 4, x + bb[2] - bb[0] + 6, y + bb[3] - bb[1] + 4), fill=WHITE)
    draw.text((x, y), text, font=fnt, fill=LINE)


def make_canvas(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw, dict[str, ImageFont.FreeTypeFont]]:
    img = Image.new("RGB", (1600, 1280), WHITE)
    draw = ImageDraw.Draw(img)
    fonts = {
        "title": font(FONT_HEI, 30),
        "node": font(FONT_SONG, 23),
        "small": font(FONT_SONG, 20),
    }
    bb = draw.textbbox((0, 0), title, font=fonts["title"])
    draw.text(((1600 - (bb[2] - bb[0])) / 2, 28), title, font=fonts["title"], fill=LINE)
    return img, draw, fonts


def build_knowledge_flow() -> Path:
    path = ASSET_DIR / TARGETS["word/media/image13.png"]
    img, draw, ft = make_canvas("知识管理模块处理流程图")
    cx = 800
    start = draw_terminal(draw, cx, 90, 220, 56, "开始", ft["node"])
    p1 = draw_process(draw, cx, 185, 360, 72, ["进入知识管理页面"], ft["node"])
    p2 = draw_process(draw, cx, 300, 420, 84, ["录入标题、分类、摘要、正文"], ft["node"])
    d1 = draw_decision(draw, cx, 425, 360, 112, ["信息是否完整？"], ft["node"])
    p3 = draw_process(draw, 330, 575, 300, 84, ["补充或修改", "知识信息"], ft["node"])
    p4 = draw_process(draw, cx, 575, 320, 74, ["保存知识内容"], ft["node"])
    d2 = draw_decision(draw, cx, 705, 360, 112, ["是否包含附件？"], ft["node"])
    p5 = draw_process(draw, 1240, 845, 320, 84, ["上传并关联附件", "登记文件信息"], ft["node"])
    p6 = draw_process(draw, cx, 845, 360, 84, ["写入知识表/文件表", "并更新索引"], ft["node"])
    p7 = draw_process(draw, cx, 980, 380, 78, ["用户检索并查看详情"], ft["node"])
    end = draw_terminal(draw, cx, 1095, 240, 58, "结束", ft["node"])

    for top_box, next_box in [(start, p1), (p1, p2), (p2, d1), (p4, d2), (p6, p7), (p7, end)]:
        arrow(draw, [((top_box[0]+top_box[2])//2, top_box[3]), ((next_box[0]+next_box[2])//2, next_box[1])])
    arrow(draw, [(cx, d1[3]), (cx, p4[1])])
    arrow(draw, [(d1[0], (d1[1]+d1[3])//2), (180, (d1[1]+d1[3])//2), (180, 617), (480, 617)])
    label(draw, 205, 476, "否", ft["small"])
    arrow(draw, [(480, 617), (650, 617)])
    label(draw, 855, 548, "是", ft["small"])
    arrow(draw, [(cx, d2[3]), (cx, p6[1])])
    label(draw, 855, 826, "否", ft["small"])
    arrow(draw, [(d2[2], (d2[1]+d2[3])//2), (1450, (d2[1]+d2[3])//2), (1450, 887), (1400, 887)])
    label(draw, 1320, 756, "是", ft["small"])
    arrow(draw, [(1080, 887), (980, 887)])
    img.save(path)
    return path


def build_file_flow() -> Path:
    path = ASSET_DIR / TARGETS["word/media/image14.png"]
    img, draw, ft = make_canvas("文件处理模块流程图")
    cx = 800
    start = draw_terminal(draw, cx, 90, 220, 56, "开始", ft["node"])
    p1 = draw_process(draw, cx, 185, 320, 72, ["上传原始文件"], ft["node"])
    p2 = draw_process(draw, cx, 300, 420, 84, ["写入对象存储", "并登记文件/任务记录"], ft["node"])
    d1 = draw_decision(draw, cx, 430, 360, 112, ["文件类型是否可识别？"], ft["node"])
    p3 = draw_process(draw, 325, 590, 300, 84, ["记录失败原因", "等待人工重试"], ft["node"])
    p4 = draw_process(draw, cx, 590, 420, 84, ["按类型执行 OCR", "或 Whisper 转写"], ft["node"])
    p5 = draw_process(draw, cx, 720, 360, 72, ["文本清洗与切片"], ft["node"])
    p6 = draw_process(draw, cx, 835, 360, 72, ["生成候选实体"], ft["node"])
    d2 = draw_decision(draw, cx, 955, 360, 112, ["处理是否成功？"], ft["node"])
    p7 = draw_process(draw, 1240, 1090, 320, 82, ["更新失败状态", "支持再次重试"], ft["node"])
    p8 = draw_process(draw, cx, 1090, 380, 82, ["保存文本结果", "进入后续治理链路"], ft["node"])
    end = draw_terminal(draw, cx, 1195, 240, 58, "结束", ft["node"])

    for top_box, next_box in [(start, p1), (p1, p2), (p2, d1), (p4, p5), (p5, p6), (p6, d2), (p8, end)]:
        arrow(draw, [((top_box[0]+top_box[2])//2, top_box[3]), ((next_box[0]+next_box[2])//2, next_box[1])])
    arrow(draw, [(d1[0], (d1[1]+d1[3])//2), (170, (d1[1]+d1[3])//2), (170, 632), (475, 632)])
    label(draw, 205, 482, "否", ft["small"])
    arrow(draw, [(cx, d1[3]), (cx, p4[1])])
    label(draw, 855, 555, "是", ft["small"])
    arrow(draw, [(cx, d2[3]), (cx, p8[1])])
    label(draw, 855, 1070, "是", ft["small"])
    arrow(draw, [(d2[2], (d2[1]+d2[3])//2), (1450, (d2[1]+d2[3])//2), (1450, 1130), (1400, 1130)])
    label(draw, 1320, 995, "否", ft["small"])
    arrow(draw, [(1080, 1130), (990, 1130)])
    img.save(path)
    return path


def build_graph_flow() -> Path:
    path = ASSET_DIR / TARGETS["word/media/image15.png"]
    img, draw, ft = make_canvas("知识图谱查询流程图")
    cx = 800
    start = draw_terminal(draw, cx, 90, 220, 56, "开始", ft["node"])
    p1 = draw_process(draw, cx, 185, 360, 72, ["进入实体审核/图谱查询"], ft["node"])
    p2 = draw_process(draw, cx, 300, 420, 84, ["生成候选实体", "与候选关系"], ft["node"])
    d1 = draw_decision(draw, cx, 430, 360, 112, ["审核是否通过？"], ft["node"])
    p3 = draw_process(draw, 325, 590, 320, 84, ["修订、驳回或补充", "候选结果"], ft["node"])
    p4 = draw_process(draw, cx, 590, 380, 82, ["写入图谱实体", "与关系数据"], ft["node"])
    p5 = draw_process(draw, cx, 715, 360, 72, ["发起邻居/路径/证据查询"], ft["node"])
    d2 = draw_decision(draw, cx, 835, 360, 112, ["是否命中图谱结果？"], ft["node"])
    p6 = draw_process(draw, 1240, 985, 320, 84, ["调整查询条件", "重新发起查询"], ft["node"])
    p7 = draw_process(draw, cx, 985, 400, 82, ["返回图谱结果", "及证据文本"], ft["node"])
    end = draw_terminal(draw, cx, 1100, 240, 58, "结束", ft["node"])

    for top_box, next_box in [(start, p1), (p1, p2), (p2, d1), (p4, p5), (p5, d2), (p7, end)]:
        arrow(draw, [((top_box[0]+top_box[2])//2, top_box[3]), ((next_box[0]+next_box[2])//2, next_box[1])])
    arrow(draw, [(d1[0], (d1[1]+d1[3])//2), (165, (d1[1]+d1[3])//2), (165, 632), (485, 632)])
    label(draw, 200, 482, "否", ft["small"])
    arrow(draw, [(cx, d1[3]), (cx, p4[1])])
    label(draw, 855, 555, "是", ft["small"])
    arrow(draw, [(cx, d2[3]), (cx, p7[1])])
    label(draw, 855, 960, "是", ft["small"])
    arrow(draw, [(d2[2], (d2[1]+d2[3])//2), (1450, (d2[1]+d2[3])//2), (1450, 1027), (1400, 1027)])
    label(draw, 1320, 875, "否", ft["small"])
    arrow(draw, [(1080, 1027), (980, 1027), (980, 751)])
    img.save(path)
    return path


def build_qa_flow() -> Path:
    path = ASSET_DIR / TARGETS["word/media/image16.png"]
    img, draw, ft = make_canvas("智能问答模块流程图")
    cx = 800
    start = draw_terminal(draw, cx, 90, 220, 56, "开始", ft["node"])
    p1 = draw_process(draw, cx, 185, 360, 72, ["输入问题或上传附件"], ft["node"])
    p2 = draw_process(draw, cx, 300, 340, 72, ["问题预处理"], ft["node"])
    p3 = draw_process(draw, cx, 415, 420, 84, ["关键词检索", "与向量召回"], ft["node"])
    d1 = draw_decision(draw, cx, 545, 360, 112, ["证据是否充足？"], ft["node"])
    p4 = draw_process(draw, 1240, 685, 320, 84, ["扩展检索范围", "或生成附件摘要"], ft["node"])
    p5 = draw_process(draw, cx, 685, 360, 72, ["融合排序"], ft["node"])
    p6 = draw_process(draw, cx, 800, 360, 72, ["构建问答上下文"], ft["node"])
    p7 = draw_process(draw, cx, 915, 360, 72, ["生成流式回答"], ft["node"])
    d2 = draw_decision(draw, cx, 1035, 360, 112, ["用户是否继续追问？"], ft["node"])
    p8 = draw_process(draw, 330, 1110, 320, 84, ["保留会话上下文", "返回问题输入"], ft["node"])
    end = draw_terminal(draw, cx, 1160, 240, 58, "结束", ft["node"])

    for top_box, next_box in [(start, p1), (p1, p2), (p2, p3), (p5, p6), (p6, p7)]:
        arrow(draw, [((top_box[0]+top_box[2])//2, top_box[3]), ((next_box[0]+next_box[2])//2, next_box[1])])
    arrow(draw, [(cx, d1[3]), (cx, p5[1])])
    label(draw, 855, 650, "是", ft["small"])
    arrow(draw, [(d1[2], (d1[1]+d1[3])//2), (1450, (d1[1]+d1[3])//2), (1450, 727), (1400, 727)])
    label(draw, 1320, 585, "否", ft["small"])
    arrow(draw, [(1080, 727), (980, 727)])
    arrow(draw, [((p7[0]+p7[2])//2, p7[3]), (cx, d2[1])])
    arrow(draw, [(cx, d2[3]), (cx, end[1])])
    label(draw, 855, 1115, "否", ft["small"])
    arrow(draw, [(d2[0], (d2[1]+d2[3])//2), (90, (d2[1]+d2[3])//2), (90, 1152), (490, 1152)])
    label(draw, 195, 1082, "是", ft["small"])
    arrow(draw, [(490, 1152), (250, 1152), (250, 221), (620, 221)])
    img.save(path)
    return path


def build_assets() -> dict[str, bytes]:
    files = [
        build_knowledge_flow(),
        build_file_flow(),
        build_graph_flow(),
        build_qa_flow(),
    ]
    return {f"word/media/{path.name.replace('fig_5_3_knowledge_flow_standard', 'image13').replace('fig_5_4_file_flow_standard', 'image14').replace('fig_5_5_graph_flow_standard', 'image15').replace('fig_5_6_qa_flow_standard', 'image16')}": path.read_bytes() for path in files}


def rewrite_to(output_path: Path, media_map: dict[str, bytes]) -> None:
    tmp = output_path.with_suffix(".ch5flow.tmp")
    shutil.copy2(DOCX, tmp)
    with ZipFile(tmp) as zin, ZipFile(output_path, "w", ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename in media_map:
                data = media_map[info.filename]
            zout.writestr(info, data)
    tmp.unlink(missing_ok=True)


def main() -> None:
    media_map = build_assets()
    try:
        rewrite_to(DOCX, media_map)
        print("Updated", DOCX)
    except PermissionError:
        rewrite_to(FALLBACK, media_map)
        print("Locked source, wrote fallback", FALLBACK)


if __name__ == "__main__":
    main()
