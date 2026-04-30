from __future__ import annotations

import html
import subprocess
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring


ROOT = Path(r"D:\beauty")
OUT_DIR = ROOT / "final_assets" / "er_from_sql"
RENDER_MJS = Path(r"C:\Users\YLDN\.codex\skills\drawio\scripts\_render_svg_to_png.mjs")

SVG_PATH = OUT_DIR / "beauty_knowledge_er_chen.svg"
PNG_PATH = OUT_DIR / "beauty_knowledge_er_chen.png"
DRAWIO_PATH = OUT_DIR / "beauty_knowledge_er_chen.drawio"


ENTITIES = {
    "user": {"label": "系统用户", "x": 120, "y": 120},
    "category": {"label": "知识分类", "x": 560, "y": 120},
    "knowledge": {"label": "知识内容", "x": 980, "y": 120},
    "file": {"label": "知识文件", "x": 1420, "y": 120},
    "task": {"label": "处理任务", "x": 1820, "y": 120},
    "session": {"label": "会话", "x": 120, "y": 640},
    "message": {"label": "消息", "x": 560, "y": 640},
    "attachment": {"label": "会话附件", "x": 980, "y": 640},
    "product": {"label": "产品", "x": 120, "y": 1080},
    "ingredient": {"label": "成分", "x": 760, "y": 1080},
    "effect": {"label": "功效", "x": 1400, "y": 1080},
}


ATTRS = {
    "user": [("id", -110, -120), ("username", -170, -10), ("role", -120, 110), ("status", 90, 110)],
    "category": [("id", -100, -120), ("name", -150, -10), ("parent_id", 120, -10), ("sort_order", 110, 110)],
    "knowledge": [("id", -110, -120), ("title", -170, -10), ("type", 150, -10), ("status", 120, 110)],
    "file": [("id", -100, -120), ("original_name", -190, -10), ("file_type", 150, -10), ("process_status", 150, 110)],
    "task": [("id", -80, -120), ("task_type", -150, -10), ("status", 110, -10), ("progress", 90, 110)],
    "session": [("id", -90, -120), ("title", -150, -10), ("status", 110, -10), ("updated_at", 110, 110)],
    "message": [("id", -90, -120), ("role", -130, -10), ("content", 120, -10), ("created_at", 110, 110)],
    "attachment": [("id", -90, -120), ("file_name", -160, -10), ("minio_path", 150, -10), ("content_type", 150, 110)],
    "product": [("id", -90, -120), ("name", -150, -10), ("brand", 120, -10), ("product_type", 110, 110)],
    "ingredient": [("id", -90, -120), ("name", -150, -10), ("alias_name", 150, -10), ("category", 110, 110)],
    "effect": [("id", -90, -120), ("name", -150, -10), ("scene", 120, -10), ("status", 100, 110)],
}


RELATIONSHIPS = [
    ("创建", "user", "knowledge", "1", "N", 550, 120),
    ("归属", "category", "knowledge", "1", "N", 770, 120),
    ("包含", "knowledge", "file", "1", "N", 1200, 120),
    ("生成", "file", "task", "1", "N", 1640, 120),
    ("拥有", "user", "session", "1", "N", 120, 380),
    ("包含", "session", "message", "1", "N", 340, 640),
    ("上传", "session", "attachment", "1", "N", 780, 640),
    ("收藏", "user", "knowledge", "N", "N", 360, 380),
    ("包含", "product", "ingredient", "N", "N", 440, 1080),
    ("具有", "ingredient", "effect", "N", "N", 1080, 1080),
    ("对应", "product", "effect", "N", "N", 760, 900),
]


ENTITY_W = 160
ENTITY_H = 72
ATTR_W = 138
ATTR_H = 48
FONT = "Microsoft YaHei, SimSun, Arial"


def entity_center(key: str) -> tuple[int, int]:
    e = ENTITIES[key]
    return e["x"] + ENTITY_W // 2, e["y"] + ENTITY_H // 2


def line(a: tuple[int, int], b: tuple[int, int], stroke="#476aa8", width=2) -> str:
    return f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{stroke}" stroke-width="{width}"/>'


def entity_svg(key: str) -> str:
    e = ENTITIES[key]
    x, y = e["x"], e["y"]
    return (
        f'<rect x="{x}" y="{y}" width="{ENTITY_W}" height="{ENTITY_H}" rx="8" ry="8" '
        f'fill="#f8fbff" stroke="#6d88c7" stroke-width="2"/>'
        f'<text x="{x + ENTITY_W/2}" y="{y + 43}" text-anchor="middle" '
        f'font-size="24" font-family="{FONT}" fill="#22324d">{html.escape(e["label"])}</text>'
    )


def attr_svg(entity_key: str, label: str, dx: int, dy: int) -> str:
    cx, cy = entity_center(entity_key)
    ax = cx + dx
    ay = cy + dy
    return (
        line((cx, cy), (ax, ay))
        + f'<ellipse cx="{ax}" cy="{ay}" rx="{ATTR_W/2}" ry="{ATTR_H/2}" fill="#ffffff" stroke="#6d88c7" stroke-width="2"/>'
        + f'<text x="{ax}" y="{ay + 8}" text-anchor="middle" font-size="22" font-family="{FONT}" fill="#22324d">{html.escape(label)}</text>'
    )


def relation_svg(label: str, left_key: str, right_key: str, left_card: str, right_card: str, rx: int, ry: int) -> str:
    lx, ly = entity_center(left_key)
    rx2, ry2 = entity_center(right_key)
    diamond = (
        f'<polygon points="{rx},{ry-46} {rx+78},{ry} {rx},{ry+46} {rx-78},{ry}" '
        f'fill="#ffca28" stroke="#d18d00" stroke-width="2"/>'
        f'<text x="{rx}" y="{ry+8}" text-anchor="middle" font-size="22" font-family="{FONT}" fill="#2f2a1f">{html.escape(label)}</text>'
    )
    left_line = line((lx, ly), (rx - 78, ry))
    right_line = line((rx + 78, ry), (rx2, ry2))
    left_text = f'<text x="{(lx + rx - 78)/2}" y="{(ly + ry)/2 - 10}" text-anchor="middle" font-size="20" font-family="{FONT}" fill="#22324d">{left_card}</text>'
    right_text = f'<text x="{(rx + 78 + rx2)/2}" y="{(ry + ry2)/2 - 10}" text-anchor="middle" font-size="20" font-family="{FONT}" fill="#22324d">{right_card}</text>'
    return left_line + right_line + diamond + left_text + right_text


def build_svg() -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="2200" height="1380" viewBox="0 0 2200 1380">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="1100" y="44" text-anchor="middle" font-size="30" font-family="Microsoft YaHei, SimSun, Arial" fill="#22324d">beauty_knowledge 概念 ER 图</text>',
        '<text x="1100" y="76" text-anchor="middle" font-size="16" font-family="Microsoft YaHei, SimSun, Arial" fill="#5a6478">采用实体-属性-联系表示法，根据 SQL 字段关系抽象绘制</text>',
    ]

    for key in ENTITIES:
        parts.append(entity_svg(key))
    for key, attrs in ATTRS.items():
        for label, dx, dy in attrs:
            parts.append(attr_svg(key, label, dx, dy))
    for rel in RELATIONSHIPS:
        parts.append(relation_svg(*rel))

    parts.append("</svg>")
    return "\n".join(parts)


def add_mx_cell(root: Element, cell_id: str, value: str, style: str, x: float, y: float, w: float, h: float, vertex: bool = True) -> None:
    cell = SubElement(
        root,
        "mxCell",
        {
            "id": cell_id,
            "value": value,
            "style": style,
            "parent": "1",
            "vertex": "1" if vertex else "0",
        },
    )
    SubElement(
        cell,
        "mxGeometry",
        {
            "x": str(x),
            "y": str(y),
            "width": str(w),
            "height": str(h),
            "as": "geometry",
        },
    )


def add_edge(root: Element, cell_id: str, source: str, target: str, value: str = "") -> None:
    cell = SubElement(
        root,
        "mxCell",
        {
            "id": cell_id,
            "value": value,
            "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#476aa8;strokeWidth=2;",
            "parent": "1",
            "source": source,
            "target": target,
            "edge": "1",
        },
    )
    SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})


def build_drawio() -> str:
    mxfile = Element("mxfile", {"host": "app.diagrams.net", "modified": "2026-04-16T14:40:00.000Z", "agent": "Codex", "version": "24.7.17"})
    diagram = SubElement(mxfile, "diagram", {"id": "beauty-knowledge-er-chen", "name": "ER图"})
    model = SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": "1600",
            "dy": "900",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": "2200",
            "pageHeight": "1380",
            "math": "0",
            "shadow": "0",
        },
    )
    root = SubElement(model, "root")
    SubElement(root, "mxCell", {"id": "0"})
    SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    entity_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8fbff;strokeColor=#6d88c7;strokeWidth=2;fontSize=18;fontColor=#22324d;"
    attr_style = "ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6d88c7;strokeWidth=2;fontSize=16;fontColor=#22324d;"
    rel_style = "rhombus;whiteSpace=wrap;html=1;fillColor=#ffca28;strokeColor=#d18d00;strokeWidth=2;fontSize=18;fontColor=#2f2a1f;"
    text_style = "text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=15;fontColor=#22324d;"

    ids = {}
    next_id = 2

    for key, entity in ENTITIES.items():
        cell_id = str(next_id)
        next_id += 1
        ids[f"entity:{key}"] = cell_id
        add_mx_cell(root, cell_id, entity["label"], entity_style, entity["x"], entity["y"], ENTITY_W, ENTITY_H)

    for key, attrs in ATTRS.items():
        cx, cy = entity_center(key)
        for label, dx, dy in attrs:
            ax = cx + dx - ATTR_W / 2
            ay = cy + dy - ATTR_H / 2
            attr_id = str(next_id)
            next_id += 1
            ids[f"attr:{key}:{label}"] = attr_id
            add_mx_cell(root, attr_id, label, attr_style, ax, ay, ATTR_W, ATTR_H)
            add_edge(root, str(next_id), ids[f"entity:{key}"], attr_id)
            next_id += 1

    for label, left_key, right_key, left_card, right_card, rx, ry in RELATIONSHIPS:
        rel_id = str(next_id)
        next_id += 1
        ids[f"rel:{label}:{left_key}:{right_key}"] = rel_id
        add_mx_cell(root, rel_id, label, rel_style, rx - 78, ry - 46, 156, 92)
        add_edge(root, str(next_id), ids[f"entity:{left_key}"], rel_id)
        next_id += 1
        add_edge(root, str(next_id), rel_id, ids[f"entity:{right_key}"])
        next_id += 1

        lx, ly = entity_center(left_key)
        rx2, ry2 = entity_center(right_key)
        left_tx = (lx + rx - 78) / 2 - 15
        left_ty = (ly + ry) / 2 - 28
        right_tx = (rx + 78 + rx2) / 2 - 15
        right_ty = (ry + ry2) / 2 - 28
        add_mx_cell(root, str(next_id), left_card, text_style, left_tx, left_ty, 30, 20)
        next_id += 1
        add_mx_cell(root, str(next_id), right_card, text_style, right_tx, right_ty, 30, 20)
        next_id += 1

    return tostring(mxfile, encoding="utf-8", xml_declaration=True).decode("utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SVG_PATH.write_text(build_svg(), encoding="utf-8")
    DRAWIO_PATH.write_text(build_drawio(), encoding="utf-8")
    subprocess.run(["node", str(RENDER_MJS), str(SVG_PATH), str(PNG_PATH)], check=True)
    print(DRAWIO_PATH)
    print(SVG_PATH)
    print(PNG_PATH)


if __name__ == "__main__":
    main()
