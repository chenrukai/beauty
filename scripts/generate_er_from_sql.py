from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


ROOT = Path(r"D:\beauty")
SQL_PATH = Path(r"C:\Users\YLDN\Desktop\beauty_knowledge.sql")
OUT_DIR = ROOT / "final_assets" / "er_from_sql"
DRAWIO_SCRIPTS = Path(r"C:\Users\YLDN\.codex\skills\drawio\scripts")
DRAWIO_CLI = DRAWIO_SCRIPTS / "cli.js"
RENDER_MJS = DRAWIO_SCRIPTS / "_render_svg_to_png.mjs"


@dataclass
class Column:
    name: str
    comment: str = ""


@dataclass
class Table:
    name: str
    comment: str = ""
    columns: List[Column] = field(default_factory=list)
    pk: str = "id"


TABLE_LAYOUT = {
    "sys_user": (80, 80),
    "kb_category": (360, 80),
    "kb_knowledge": (660, 80),
    "kb_file": (980, 80),
    "kb_chunk": (1280, 80),
    "process_task": (1560, 80),
    "entity_extract_pending": (1840, 80),
    "chat_session": (80, 400),
    "chat_message": (380, 400),
    "chat_attachment": (680, 400),
    "favorite_record": (980, 400),
    "user_action_log": (1280, 400),
    "sys_notice": (1580, 400),
    "search_keyword_stat": (1840, 400),
    "beauty_product": (80, 760),
    "beauty_ingredient": (420, 760),
    "beauty_effect": (760, 760),
    "rel_product_ingredient": (80, 1080),
    "rel_product_effect": (480, 1080),
    "rel_ingredient_effect": (880, 1080),
    "kg_evidence": (1320, 1080),
}


DISPLAY_NAME = {
    "sys_user": "sys_user\n系统用户",
    "kb_category": "kb_category\n知识分类",
    "kb_knowledge": "kb_knowledge\n知识内容",
    "kb_file": "kb_file\n知识文件",
    "kb_chunk": "kb_chunk\n文本分块",
    "process_task": "process_task\n处理任务",
    "entity_extract_pending": "entity_extract_pending\n待确认实体",
    "chat_session": "chat_session\n会话",
    "chat_message": "chat_message\n消息",
    "chat_attachment": "chat_attachment\n会话附件",
    "favorite_record": "favorite_record\n收藏记录",
    "user_action_log": "user_action_log\n行为日志",
    "sys_notice": "sys_notice\n系统公告",
    "search_keyword_stat": "search_keyword_stat\n搜索词统计",
    "beauty_product": "beauty_product\n产品",
    "beauty_ingredient": "beauty_ingredient\n成分",
    "beauty_effect": "beauty_effect\n功效",
    "rel_product_ingredient": "rel_product_ingredient\n产品成分关系",
    "rel_product_effect": "rel_product_effect\n产品功效关系",
    "rel_ingredient_effect": "rel_ingredient_effect\n成分功效关系",
    "kg_evidence": "kg_evidence\n图谱证据",
}


EDGE_OVERRIDES = {
    ("kb_category", "kb_category"): ("1:N", "父子分类"),
    ("sys_user", "kb_knowledge"): ("1:N", "author_id"),
    ("kb_category", "kb_knowledge"): ("1:N", "category_id"),
    ("kb_knowledge", "kb_file"): ("1:N", "knowledge_id"),
    ("sys_user", "kb_file"): ("1:N", "uploaded_by"),
    ("kb_knowledge", "kb_chunk"): ("1:N", "knowledge_id"),
    ("kb_file", "kb_chunk"): ("1:N", "file_id"),
    ("kb_file", "process_task"): ("1:N", "file_id"),
    ("sys_user", "process_task"): ("1:N", "operator_id"),
    ("kb_file", "entity_extract_pending"): ("1:N", "file_id"),
    ("sys_user", "entity_extract_pending"): ("1:N", "reviewer_id"),
    ("sys_user", "chat_session"): ("1:N", "user_id"),
    ("chat_session", "chat_message"): ("1:N", "session_id"),
    ("chat_session", "chat_attachment"): ("1:N", "session_id"),
    ("sys_user", "chat_attachment"): ("1:N", "user_id"),
    ("sys_user", "favorite_record"): ("1:N", "user_id"),
    ("kb_knowledge", "favorite_record"): ("1:N", "knowledge_id"),
    ("sys_user", "user_action_log"): ("1:N", "user_id"),
    ("sys_user", "sys_notice"): ("1:N", "created_by"),
    ("beauty_product", "rel_product_ingredient"): ("1:N", "product_id"),
    ("beauty_ingredient", "rel_product_ingredient"): ("1:N", "ingredient_id"),
    ("beauty_product", "rel_product_effect"): ("1:N", "product_id"),
    ("beauty_effect", "rel_product_effect"): ("1:N", "effect_id"),
    ("beauty_ingredient", "rel_ingredient_effect"): ("1:N", "ingredient_id"),
    ("beauty_effect", "rel_ingredient_effect"): ("1:N", "effect_id"),
    ("kb_file", "kg_evidence"): ("1:N", "file_id"),
    ("kb_chunk", "kg_evidence"): ("1:N", "chunk_id"),
    ("sys_user", "kg_evidence"): ("1:N", "reviewer_id"),
}


FK_MAP = {
    "user_id": "sys_user",
    "author_id": "sys_user",
    "uploaded_by": "sys_user",
    "operator_id": "sys_user",
    "created_by": "sys_user",
    "reviewer_id": "sys_user",
    "category_id": "kb_category",
    "parent_id": "kb_category",
    "knowledge_id": "kb_knowledge",
    "file_id": "kb_file",
    "chunk_id": "kb_chunk",
    "session_id": "chat_session",
    "effect_id": "beauty_effect",
    "ingredient_id": "beauty_ingredient",
    "product_id": "beauty_product",
}


def parse_sql(sql_text: str) -> Dict[str, Table]:
    tables: Dict[str, Table] = {}
    block_re = re.compile(
        r"CREATE TABLE\s+`(?P<name>[^`]+)`\s*\((?P<body>.*?)\)\s*ENGINE.*?COMMENT\s*=\s*'(?P<comment>[^']*)'",
        re.S,
    )
    col_re = re.compile(r"^\s*`(?P<name>[^`]+)`.*?(?:COMMENT\s+'(?P<comment>[^']*)')?,?\s*$")
    pk_re = re.compile(r"PRIMARY KEY\s+\(`(?P<pk>[^`]+)`\)")
    for match in block_re.finditer(sql_text):
        table = Table(name=match.group("name"), comment=match.group("comment"))
        body = match.group("body")
        for line in body.splitlines():
            line = line.rstrip()
            if not line:
                continue
            pk_match = pk_re.search(line)
            if pk_match:
                table.pk = pk_match.group("pk")
                continue
            if line.lstrip().startswith(("PRIMARY KEY", "UNIQUE INDEX", "INDEX", "FULLTEXT INDEX")):
                continue
            col_match = col_re.match(line)
            if col_match:
                table.columns.append(Column(col_match.group("name"), col_match.group("comment") or ""))
        tables[table.name] = table
    return tables


def summarize_table(table: Table) -> str:
    priority = [
        table.pk,
        "name",
        "title",
        "username",
        "category_id",
        "knowledge_id",
        "file_id",
        "user_id",
        "status",
        "created_at",
    ]
    picked: List[str] = []
    by_name = {c.name: c for c in table.columns}
    for name in priority:
        if name in by_name and name not in picked:
            picked.append(name)
    for col in table.columns:
        if len(picked) >= 5:
            break
        if col.name not in picked and not col.name.endswith("_at"):
            picked.append(col.name)
    fields = []
    for name in picked[:5]:
        prefix = "PK " if name == table.pk else "FK " if name.endswith("_id") and name != table.pk else ""
        fields.append(f"{prefix}{name}")
    return DISPLAY_NAME.get(table.name, table.name) + "\n----------------\n" + "\n".join(fields)


def infer_edges(tables: Dict[str, Table]) -> List[dict]:
    edges = []
    seen = set()
    for table in tables.values():
        for col in table.columns:
            target = FK_MAP.get(col.name)
            if not target or target not in tables:
                continue
            key = (target, table.name, col.name)
            if key in seen:
                continue
            seen.add(key)
            rel_label, field_label = EDGE_OVERRIDES.get((target, table.name), ("1:N", col.name))
            edge_type = "optional" if col.name in {"reviewer_id", "created_by", "operator_id"} else "primary"
            if table.name in {"kg_evidence", "user_action_log"}:
                edge_type = "data"
            edges.append(
                {
                    "from": target,
                    "to": table.name,
                    "type": edge_type,
                    "label": f"{rel_label} {field_label}",
                }
            )
    return edges


def build_spec(tables: Dict[str, Table]) -> dict:
    nodes = []
    for name, table in tables.items():
        x, y = TABLE_LAYOUT.get(name, (80, 80))
        nodes.append(
            {
                "id": name,
                "label": summarize_table(table),
                "type": "service" if not name.endswith("_stat") else "document",
                "size": "xl",
                "position": {"x": x, "y": y},
                "style": {
                    "fillColor": "#FFFFFF",
                    "strokeColor": "#111111",
                    "fontColor": "#111111",
                },
            }
        )

    modules = [
        {"id": "m_content", "label": "知识内容域", "position": {"x": 40, "y": 40}, "size": {"width": 1880, "height": 300}},
        {"id": "m_chat", "label": "会话与运营域", "position": {"x": 40, "y": 360}, "size": {"width": 1880, "height": 280}},
        {"id": "m_graph", "label": "产品图谱域", "position": {"x": 40, "y": 720}, "size": {"width": 1880, "height": 520}},
    ]

    return {
        "meta": {
            "profile": "academic-paper",
            "theme": "academic",
            "source": "generated",
            "layout": "hierarchical",
            "canvas": "2100x1350",
            "routing": "orthogonal",
            "title": "beauty_knowledge 数据库 ER 图",
            "description": "基于 beauty_knowledge.sql 中表结构和 *_id 字段推断的实体关系图",
            "legend": "矩形为数据表；连线标签表示主外键推断的一对多关系；虚线表示弱依赖或日志/证据类关联。",
        },
        "nodes": nodes,
        "edges": infer_edges(tables),
        "modules": modules,
    }


def ensure_renderer() -> None:
    if RENDER_MJS.exists():
        return
    RENDER_MJS.write_text(
        """import fs from 'node:fs';\nimport { Resvg } from '@resvg/resvg-js';\nconst [,, src, dst] = process.argv;\nconst svg = fs.readFileSync(src, 'utf8');\nconst resvg = new Resvg(svg, { background: 'white', fitTo: { mode: 'original' } });\nconst png = resvg.render();\nfs.writeFileSync(dst, png.asPng());\n""",
        encoding="utf-8",
    )


def run(cmd: List[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd or ROOT, check=True)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sql_text = SQL_PATH.read_text(encoding="utf-8", errors="ignore")
    tables = parse_sql(sql_text)
    spec = build_spec(tables)

    yaml_path = OUT_DIR / "beauty_knowledge_er.yaml"
    drawio_path = OUT_DIR / "beauty_knowledge_er.drawio"
    svg_path = OUT_DIR / "beauty_knowledge_er.svg"
    png_path = OUT_DIR / "beauty_knowledge_er.png"
    arch_path = OUT_DIR / "beauty_knowledge_er.arch.json"

    import yaml  # type: ignore

    yaml_path.write_text(yaml.safe_dump(spec, allow_unicode=True, sort_keys=False), encoding="utf-8")
    arch_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")

    run(["node", str(DRAWIO_CLI), str(yaml_path), str(drawio_path), "--validate", "--write-sidecars"])
    run(["node", str(DRAWIO_CLI), str(yaml_path), str(svg_path), "--validate", "--write-sidecars"])

    ensure_renderer()
    run(["node", str(RENDER_MJS), str(svg_path), str(png_path)])

    print(drawio_path)
    print(svg_path)
    print(png_path)


if __name__ == "__main__":
    main()
