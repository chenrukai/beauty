from __future__ import annotations

import html
import subprocess
from pathlib import Path

from generate_er_from_sql import OUT_DIR, RENDER_MJS


SVG_PATH = OUT_DIR / "beauty_knowledge_er_core.svg"
PNG_PATH = OUT_DIR / "beauty_knowledge_er_core.png"
TXT_PATH = OUT_DIR / "beauty_knowledge_er_core_notes.txt"

BOX_W = 240
BOX_H = 126
FONT_TITLE = 16
FONT_BODY = 13


NODES = {
    "sys_user": {"x": 40, "y": 40, "title": "sys_user / 系统用户", "fields": ["PK id", "username", "role", "status", "created_at"]},
    "kb_category": {"x": 360, "y": 40, "title": "kb_category / 知识分类", "fields": ["PK id", "name", "parent_id", "status", "sort_order"]},
    "kb_knowledge": {"x": 680, "y": 40, "title": "kb_knowledge / 知识内容", "fields": ["PK id", "title", "FK category_id", "FK author_id", "status"]},
    "kb_file": {"x": 1000, "y": 40, "title": "kb_file / 知识文件", "fields": ["PK id", "FK knowledge_id", "original_name", "process_status", "FK uploaded_by"]},
    "kb_chunk": {"x": 1320, "y": 40, "title": "kb_chunk / 文本分块", "fields": ["PK id", "FK knowledge_id", "FK file_id", "chunk_index", "vector_status"]},
    "process_task": {"x": 1640, "y": 40, "title": "process_task / 处理任务", "fields": ["PK id", "FK file_id", "task_type", "status", "FK operator_id"]},
    "chat_session": {"x": 40, "y": 320, "title": "chat_session / 会话", "fields": ["PK id", "FK user_id", "title", "status", "updated_at"]},
    "chat_message": {"x": 360, "y": 320, "title": "chat_message / 消息", "fields": ["PK id", "FK session_id", "role", "token_count", "created_at"]},
    "chat_attachment": {"x": 680, "y": 320, "title": "chat_attachment / 会话附件", "fields": ["PK id", "FK session_id", "FK user_id", "file_name", "minio_path"]},
    "favorite_record": {"x": 1000, "y": 320, "title": "favorite_record / 收藏记录", "fields": ["PK id", "FK user_id", "FK knowledge_id", "created_at"]},
    "entity_extract_pending": {"x": 1320, "y": 320, "title": "entity_extract_pending / 待确认实体", "fields": ["PK id", "FK file_id", "entity_type", "status", "FK reviewer_id"]},
    "kg_evidence": {"x": 1640, "y": 320, "title": "kg_evidence / 图谱证据", "fields": ["PK id", "relation_type", "FK file_id", "FK chunk_id", "FK reviewer_id"]},
    "beauty_product": {"x": 40, "y": 620, "title": "beauty_product / 产品", "fields": ["PK id", "name", "brand", "product_type", "status"]},
    "rel_product_ingredient": {"x": 360, "y": 620, "title": "rel_product_ingredient / 产品成分关系", "fields": ["PK id", "FK product_id", "FK ingredient_id", "confidence", "status"]},
    "beauty_ingredient": {"x": 680, "y": 620, "title": "beauty_ingredient / 成分", "fields": ["PK id", "name", "alias_name", "category", "status"]},
    "rel_ingredient_effect": {"x": 1000, "y": 620, "title": "rel_ingredient_effect / 成分功效关系", "fields": ["PK id", "FK ingredient_id", "FK effect_id", "confidence", "status"]},
    "beauty_effect": {"x": 1320, "y": 620, "title": "beauty_effect / 功效", "fields": ["PK id", "name", "scene", "status", "created_at"]},
    "rel_product_effect": {"x": 1640, "y": 620, "title": "rel_product_effect / 产品功效关系", "fields": ["PK id", "FK product_id", "FK effect_id", "confidence", "status"]},
}


EDGES = [
    ("kb_category", "kb_knowledge", "1:N category_id"),
    ("sys_user", "kb_knowledge", "1:N author_id"),
    ("kb_knowledge", "kb_file", "1:N knowledge_id"),
    ("sys_user", "kb_file", "1:N uploaded_by"),
    ("kb_file", "kb_chunk", "1:N file_id"),
    ("kb_knowledge", "kb_chunk", "1:N knowledge_id"),
    ("kb_file", "process_task", "1:N file_id"),
    ("kb_file", "entity_extract_pending", "1:N file_id"),
    ("sys_user", "chat_session", "1:N user_id"),
    ("chat_session", "chat_message", "1:N session_id"),
    ("chat_session", "chat_attachment", "1:N session_id"),
    ("sys_user", "chat_attachment", "1:N user_id"),
    ("sys_user", "favorite_record", "1:N user_id"),
    ("kb_knowledge", "favorite_record", "1:N knowledge_id"),
    ("kb_file", "kg_evidence", "1:N file_id"),
    ("kb_chunk", "kg_evidence", "1:N chunk_id"),
    ("beauty_product", "rel_product_ingredient", "1:N product_id"),
    ("beauty_ingredient", "rel_product_ingredient", "1:N ingredient_id"),
    ("beauty_ingredient", "rel_ingredient_effect", "1:N ingredient_id"),
    ("beauty_effect", "rel_ingredient_effect", "1:N effect_id"),
    ("beauty_product", "rel_product_effect", "1:N product_id"),
    ("beauty_effect", "rel_product_effect", "1:N effect_id"),
]


def center_right(node_id: str) -> tuple[int, int]:
    node = NODES[node_id]
    return node["x"] + BOX_W, node["y"] + BOX_H // 2


def center_left(node_id: str) -> tuple[int, int]:
    node = NODES[node_id]
    return node["x"], node["y"] + BOX_H // 2


def center_bottom(node_id: str) -> tuple[int, int]:
    node = NODES[node_id]
    return node["x"] + BOX_W // 2, node["y"] + BOX_H


def center_top(node_id: str) -> tuple[int, int]:
    node = NODES[node_id]
    return node["x"] + BOX_W // 2, node["y"]


def edge_path(src: str, dst: str) -> tuple[str, tuple[int, int]]:
    sx, sy = center_right(src)
    dx, dy = center_left(dst)
    if NODES[src]["y"] == NODES[dst]["y"]:
        mx = (sx + dx) // 2
        return f"M {sx} {sy} L {mx} {sy} L {mx} {dy} L {dx} {dy}", (mx, sy - 8)
    sx, sy = center_bottom(src)
    dx, dy = center_top(dst)
    my = (sy + dy) // 2
    return f"M {sx} {sy} L {sx} {my} L {dx} {my} L {dx} {dy}", (sx + 8, my - 8)


def table_svg(node_id: str, node: dict) -> str:
    x, y = node["x"], node["y"]
    fields = node["fields"]
    lines = []
    lines.append(f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="10" ry="10" fill="#ffffff" stroke="#111111" stroke-width="1.6"/>')
    lines.append(f'<line x1="{x}" y1="{y + 34}" x2="{x + BOX_W}" y2="{y + 34}" stroke="#111111" stroke-width="1.2"/>')
    lines.append(
        f'<text x="{x + BOX_W/2}" y="{y + 22}" text-anchor="middle" font-size="{FONT_TITLE}" font-family="Microsoft YaHei, SimSun, Arial" fill="#111111">{html.escape(node["title"])}</text>'
    )
    for idx, field in enumerate(fields):
        ty = y + 56 + idx * 14
        lines.append(
            f'<text x="{x + 14}" y="{ty}" font-size="{FONT_BODY}" font-family="Microsoft YaHei, SimSun, Arial" fill="#111111">{html.escape(field)}</text>'
        )
    return "\n".join(lines)


def build_svg() -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="860" viewBox="0 0 1920 860">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#111111"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="960" y="30" text-anchor="middle" font-size="22" font-family="Microsoft YaHei, SimSun, Arial" fill="#111111">beauty_knowledge 核心业务 ER 图</text>',
        '<text x="960" y="54" text-anchor="middle" font-size="12" font-family="Microsoft YaHei, SimSun, Arial" fill="#444444">根据 beauty_knowledge.sql 主键与 *_id 字段关系推断绘制</text>',
    ]

    parts.append('<rect x="20" y="18" width="1880" height="270" fill="none" stroke="#999999" stroke-dasharray="5 4"/>')
    parts.append('<text x="32" y="36" font-size="14" font-family="Microsoft YaHei, SimSun, Arial" fill="#111111">知识内容域</text>')
    parts.append('<rect x="20" y="298" width="1880" height="270" fill="none" stroke="#999999" stroke-dasharray="5 4"/>')
    parts.append('<text x="32" y="316" font-size="14" font-family="Microsoft YaHei, SimSun, Arial" fill="#111111">会话与审核域</text>')
    parts.append('<rect x="20" y="598" width="1880" height="230" fill="none" stroke="#999999" stroke-dasharray="5 4"/>')
    parts.append('<text x="32" y="616" font-size="14" font-family="Microsoft YaHei, SimSun, Arial" fill="#111111">产品图谱域</text>')

    for node_id, node in NODES.items():
        parts.append(table_svg(node_id, node))

    for src, dst, label in EDGES:
        path, (lx, ly) = edge_path(src, dst)
        parts.append(f'<path d="{path}" fill="none" stroke="#111111" stroke-width="1.4" marker-end="url(#arrow)"/>')
        parts.append(
            f'<rect x="{lx - 4}" y="{ly - 12}" width="{max(88, len(label) * 7)}" height="16" fill="#ffffff"/>'
        )
        parts.append(
            f'<text x="{lx}" y="{ly}" font-size="12" font-family="Microsoft YaHei, SimSun, Arial" fill="#111111">{html.escape(label)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    svg = build_svg()
    SVG_PATH.write_text(svg, encoding="utf-8")
    subprocess.run(["node", str(RENDER_MJS), str(SVG_PATH), str(PNG_PATH)], check=True)
    TXT_PATH.write_text(
        "该图聚焦核心业务表：用户、知识、文件、会话、收藏、处理任务、待确认实体、图谱证据、产品/成分/功效及其关系表。\n"
        "未纳入主图的统计/日志类表：sys_notice、search_keyword_stat、user_action_log。\n"
        "关系根据 SQL 中 *_id 字段推断，原 SQL 未显式声明 FOREIGN KEY 约束。\n",
        encoding="utf-8",
    )
    print(SVG_PATH)
    print(PNG_PATH)
    print(TXT_PATH)


if __name__ == "__main__":
    main()
