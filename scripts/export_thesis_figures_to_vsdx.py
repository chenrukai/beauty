from __future__ import annotations

from pathlib import Path
from typing import Iterable

from vsdx import VisioFile, Shape


OUT = Path(r"D:\beauty\final_assets\thesis_copy_fix\thesis_selected_figures.vsdx")
MEDIA = Path(r"C:\Users\YLDN\AppData\Roaming\Python\Python312\site-packages\vsdx\media\media.vsdx")

BLACK = "0"
WHITE = "#ffffff"
PALE = "#fff6b0"


def clear_page(page) -> None:
    for shape in list(page.all_shapes):
        shape.remove()


def set_text(shape: Shape, text: str) -> Shape:
    shape.text = text
    return shape


def style_shape(shape: Shape, fill: str = WHITE, line: str = BLACK, text_color: str = BLACK, weight: str = "0.018") -> Shape:
    shape.fill_color = fill
    shape.line_color = line
    shape.text_color = text_color
    shape.line_weight = weight
    return shape


def rect(proto: Shape, page, x: float, y: float, w: float, h: float, text: str, fill: str = WHITE) -> Shape:
    s = proto.copy(page)
    s.x, s.y, s.width, s.height = x, y, w, h
    set_text(s, text)
    style_shape(s, fill=fill)
    return s


def circle(proto: Shape, page, x: float, y: float, d: float, text: str = "", fill: str = PALE) -> Shape:
    s = proto.copy(page)
    s.x, s.y, s.width, s.height = x, y, d, d
    set_text(s, text)
    style_shape(s, fill=fill)
    return s


def line(proto: Shape, page, x1: float, y1: float, x2: float, y2: float) -> Shape:
    s = proto.copy(page)
    s.begin_x, s.begin_y, s.end_x, s.end_y = x1, y1, x2, y2
    s.line_color = BLACK
    s.line_weight = "0.014"
    s.text = ""
    return s


def conn(proto: Shape, page, x1: float, y1: float, x2: float, y2: float, text: str = "") -> Shape:
    s = proto.copy(page)
    s.begin_x, s.begin_y, s.end_x, s.end_y = x1, y1, x2, y2
    s.line_color = BLACK
    s.line_weight = "0.014"
    if text:
        s.text = text
    else:
        s.text = ""
    return s


def diamond(rect_proto: Shape, page, x: float, y: float, w: float, h: float, text: str) -> Shape:
    s = rect(rect_proto, page, x, y, w, h, text)
    s.angle = "45 deg"
    return s


def actor(circle_proto: Shape, line_proto: Shape, page, x: float, y: float, label: str) -> None:
    head = circle(circle_proto, page, x, y + 0.55, 0.22, "", WHITE)
    line(line_proto, page, x, y + 0.1, x, y + 0.48)
    line(line_proto, page, x - 0.18, y + 0.32, x + 0.18, y + 0.32)
    line(line_proto, page, x, y + 0.1, x - 0.16, y - 0.18)
    line(line_proto, page, x, y + 0.1, x + 0.16, y - 0.18)
    label_shape = rect(circle_proto, page, x, y - 0.48, 0.95, 0.24, label, WHITE)
    label_shape.line_weight = "0"
    label_shape.line_color = WHITE


def add_page_title(rect_proto: Shape, page, title: str) -> None:
    t = rect(rect_proto, page, 4.1, 11.25, 4.6, 0.35, title, WHITE)
    t.line_weight = "0"
    t.line_color = WHITE


def build_dfd(page, p_rect: Shape, p_circle: Shape, p_conn: Shape) -> None:
    add_page_title(p_rect, page, "图 3-2 系统数据流图")
    rect(p_rect, page, 0.95, 9.6, 1.2, 0.55, "普通用户")
    rect(p_rect, page, 7.2, 9.6, 1.2, 0.55, "管理员")
    circle(p_circle, page, 2.3, 8.2, 1.25, "认证")
    circle(p_circle, page, 4.1, 8.2, 1.25, "知识检索")
    circle(p_circle, page, 5.8, 8.2, 1.25, "文件处理")
    circle(p_circle, page, 7.1, 6.4, 1.25, "实体审核")
    circle(p_circle, page, 4.4, 6.1, 1.3, "智能问答")
    rect(p_rect, page, 2.25, 4.0, 1.55, 0.75, "业务数据库")
    rect(p_rect, page, 4.45, 4.0, 1.55, 0.75, "对象存储")
    rect(p_rect, page, 6.7, 4.0, 1.55, 0.75, "向量库")

    for a, b in [
        ((1.55, 9.6), (2.0, 8.8)),
        ((7.8, 9.6), (7.55, 7.0)),
        ((2.95, 8.2), (3.45, 8.2)),
        ((4.75, 8.2), (5.15, 8.2)),
        ((5.95, 7.7), (6.55, 6.85)),
        ((5.0, 6.15), (6.1, 6.8)),
        ((4.1, 7.55), (4.45, 6.75)),
        ((2.95, 7.5), (2.95, 4.75)),
        ((5.8, 7.5), (5.2, 4.75)),
        ((7.1, 5.75), (7.1, 4.75)),
        ((3.0, 4.75), (4.05, 5.55)),
        ((5.2, 4.75), (4.75, 5.45)),
        ((7.0, 4.75), (5.1, 5.4)),
    ]:
        conn(p_conn, page, a[0], a[1], b[0], b[1])


def build_architecture(page, p_rect: Shape, p_conn: Shape) -> None:
    add_page_title(p_rect, page, "图 4-1 系统整体结构图")
    rect(p_rect, page, 0.75, 9.6, 0.9, 1.0, "访问层")
    rect(p_rect, page, 1.95, 9.95, 1.4, 0.45, "用户端 Vue3")
    rect(p_rect, page, 3.85, 9.95, 1.4, 0.45, "管理端 Vue3")
    rect(p_rect, page, 0.75, 8.0, 1.05, 1.25, "接口/应用层")
    for x, text in [(2.2, "认证授权"), (3.55, "知识管理"), (4.9, "文件处理"), (6.25, "图谱服务"), (7.5, "问答服务")]:
        rect(p_rect, page, x, 8.55, 1.05, 0.42, text)
    rect(p_rect, page, 0.75, 5.9, 1.05, 1.45, "业务服务层")
    for x, text in [(2.15, "Spring Boot"), (3.5, "统计分析"), (4.85, "任务调度"), (6.2, "实体确认"), (7.55, "公告/用户管理")]:
        rect(p_rect, page, x, 6.6, 1.08, 0.42, text)
    rect(p_rect, page, 0.75, 4.0, 1.15, 1.15, "数据与 AI\n支撑层")
    for x, text in [(2.0, "MySQL"), (3.15, "Redis"), (4.3, "RabbitMQ"), (5.45, "MinIO"), (6.6, "Milvus"), (7.75, "OCR/Whisper")]:
        rect(p_rect, page, x, 4.45, 0.95, 0.4, text)
    for x in [2.65, 4.55]:
        conn(p_conn, page, x, 9.95, x, 9.0)
    for x in [2.75, 4.1, 5.45, 6.8, 8.0]:
        conn(p_conn, page, x, 8.55, x, 7.05)
    for x in [2.55, 3.9, 5.25, 6.6, 7.95]:
        conn(p_conn, page, x, 6.6, x, 4.9)


def build_module_tree(page, p_rect: Shape, p_conn: Shape) -> None:
    add_page_title(p_rect, page, "图 4-2 系统功能模块设计图")
    root = rect(p_rect, page, 4.15, 10.4, 2.8, 0.5, "美业多媒体知识服务系统")
    level1 = [
        (0.95, 8.8, "用户端模块"),
        (2.15, 8.8, "管理端模块"),
        (3.35, 8.8, "知识治理模块"),
        (4.55, 8.8, "文件处理模块"),
        (5.75, 8.8, "实体确认模块"),
        (6.95, 8.8, "问答服务模块"),
    ]
    for x, y, text in level1:
        rect(p_rect, page, x, y, 1.0, 0.42, text)
        conn(p_conn, page, 4.15, 10.15, x, y + 0.21)
    rect(p_rect, page, 3.0, 6.8, 1.1, 0.42, "统计分析模块")
    rect(p_rect, page, 5.2, 6.8, 1.1, 0.42, "基础设施模块")
    conn(p_conn, page, 4.15, 10.15, 3.0, 7.0)
    conn(p_conn, page, 4.15, 10.15, 5.2, 7.0)
    leaves = [
        (0.75, 7.7, "首页浏览"), (1.15, 7.1, "知识检索"), (1.55, 6.5, "收藏管理"),
        (1.95, 7.7, "概览看板"), (2.35, 7.1, "用户管理"), (2.75, 6.5, "公告管理"),
        (3.15, 7.7, "知识管理"), (3.55, 7.1, "分类管理"), (3.95, 6.5, "知识详情"),
        (4.35, 7.7, "文件上传"), (4.75, 7.1, "任务监控"), (5.15, 6.5, "处理追踪"),
        (5.55, 7.7, "候选确认"), (5.95, 7.1, "图谱维护"), (6.35, 6.5, "关系修订"),
        (6.75, 7.7, "智能问答"), (7.15, 7.1, "附件问答"), (7.55, 6.5, "会话管理"),
    ]
    for x, y, text in leaves:
        rect(p_rect, page, x, y, 0.7, 0.28, text)


def build_er(page, p_rect: Shape, p_circle: Shape, p_conn: Shape) -> None:
    add_page_title(p_rect, page, "图 4-3 系统 ER 图")
    ents = {
        "分类": (1.3, 8.8), "知识": (3.0, 8.8), "文件": (4.7, 8.8), "任务": (6.4, 8.8),
        "图谱实体": (2.3, 6.2), "图谱关系": (4.7, 6.2), "会话": (6.5, 6.2), "消息": (7.9, 6.2),
    }
    for name, (x, y) in ents.items():
        rect(p_rect, page, x, y, 1.0, 0.42, name)
    # relationship diamonds approximated by rotated rectangles
    belong = diamond(p_rect, page, 2.15, 8.8, 0.38, 0.38, "归属")
    attach = diamond(p_rect, page, 3.85, 8.8, 0.38, 0.38, "关联")
    gen = diamond(p_rect, page, 5.55, 8.8, 0.38, 0.38, "生成")
    extract = diamond(p_rect, page, 3.55, 7.2, 0.48, 0.48, "抽取")
    include = diamond(p_rect, page, 7.2, 6.2, 0.42, 0.42, "包含")
    for a, b in [
        ((1.8, 8.8), (1.96, 8.8)), ((2.34, 8.8), (2.5, 8.8)),
        ((3.5, 8.8), (3.66, 8.8)), ((4.04, 8.8), (4.2, 8.8)),
        ((5.2, 8.8), (5.36, 8.8)), ((5.74, 8.8), (5.9, 8.8)),
        ((3.0, 8.55), (3.55, 7.45)), ((4.7, 8.55), (3.8, 7.45)),
        ((2.8, 6.2), (3.3, 7.0)), ((5.2, 6.2), (3.8, 7.0)),
        ((7.0, 6.2), (7.0, 6.2)), ((7.4, 6.2), (7.5, 6.2)),
    ]:
        conn(p_conn, page, a[0], a[1], b[0], b[1])
    attrs = [
        (0.75, 9.6, "category_id"), (1.85, 9.6, "name"),
        (2.45, 9.6, "knowledge_id"), (3.55, 9.6, "title"),
        (4.15, 9.6, "file_id"), (5.25, 9.6, "file_name"),
        (5.95, 9.6, "task_id"), (7.0, 9.6, "status"),
        (1.6, 5.2, "entity_id"), (2.95, 5.2, "entity_name"),
        (4.1, 5.2, "relation_id"), (5.35, 5.2, "relation_type"),
        (6.2, 5.2, "session_id"), (7.1, 5.2, "user_id"),
        (7.8, 5.2, "message_id"), (8.55, 5.2, "role"),
    ]
    for x, y, text in attrs:
        circle(p_circle, page, x, y, 0.55, text, WHITE)


def build_flow(page, p_rect: Shape, p_circle: Shape, p_conn: Shape, title: str, spec: dict) -> None:
    add_page_title(p_rect, page, title)
    cx = 4.15
    start = circle(p_circle, page, cx, 10.55, 0.62, "开始", WHITE)
    prev_y = 10.2
    first_x, first_y, first_w, first_h, first_text = spec["main"][0]
    for idx, (x, y, w, h, text) in enumerate(spec["main"]):
        rect(p_rect, page, x, y, w, h, text)
        if idx == 0:
            conn(p_conn, page, cx, 10.24, x, y + h / 2)
        else:
            px, py, pw, ph, _ = spec["main"][idx - 1]
            conn(p_conn, page, px, py - ph / 2, x, y + h / 2)
    for (sx, sy, ex, ey) in spec.get("extra_conns", []):
        conn(p_conn, page, sx, sy, ex, ey)
    for x, y, w, h, text in spec.get("side", []):
        rect(p_rect, page, x, y, w, h, text)
    for x, y, w, h, text in spec.get("decisions", []):
        diamond(p_rect, page, x, y, w, h, text)
    end_y = spec["end_y"]
    circle(p_circle, page, cx, end_y, 0.62, "结束", WHITE)


def main() -> None:
    with VisioFile(str(MEDIA)) as vis:
        proto_page = vis.pages[0]
        rect_proto = proto_page.find_shape_by_text("RECTANGLE")
        circle_proto = proto_page.find_shape_by_text("CIRCLE")
        conn_proto = proto_page.find_shape_by_text("STRAIGHT_CONNECTOR")
        clear_page(proto_page)
        proto_page.name = "图3-2_系统数据流图"
        build_dfd(proto_page, rect_proto, circle_proto, conn_proto)

        p = vis.add_page("图4-1_系统整体结构图")
        build_architecture(p, rect_proto, conn_proto)
        p = vis.add_page("图4-2_系统功能模块设计图")
        build_module_tree(p, rect_proto, conn_proto)
        p = vis.add_page("图4-3_系统ER图")
        build_er(p, rect_proto, circle_proto, conn_proto)

        flow_specs = [
            ("图5-3_知识管理流程图", "图 5-3 知识管理模块处理流程图", {
                "main": [(4.15, 9.6, 1.9, 0.45, "进入知识管理页面"), (4.15, 8.8, 2.2, 0.52, "录入标题/分类/摘要/正文"),
                         (4.15, 7.9, 1.6, 0.36, "保存知识内容"), (4.15, 6.95, 1.9, 0.45, "写入知识表/文件表"), (4.15, 6.15, 1.8, 0.4, "用户检索并查看详情")],
                "decisions": [(4.15, 8.3, 0.55, 0.55, "信息是否完整"), (4.15, 7.35, 0.55, 0.55, "是否包含附件")],
                "side": [(1.3, 7.9, 1.45, 0.45, "补充或修改知识信息"), (7.0, 6.95, 1.55, 0.45, "上传并关联附件")],
                "extra_conns": [(3.85, 8.3, 2.0, 8.3), (2.0, 8.3, 2.0, 7.9), (2.0, 7.9, 2.75, 7.9),
                                (4.45, 7.35, 7.0, 7.35), (7.0, 7.35, 7.0, 6.95), (6.22, 6.95, 5.1, 6.95)],
                "end_y": 5.45,
            }),
            ("图5-4_文件处理流程图", "图 5-4 文件处理模块流程图", {
                "main": [(4.15, 9.65, 1.6, 0.42, "上传原始文件"), (4.15, 8.85, 2.15, 0.5, "写入对象存储/任务记录"),
                         (4.15, 7.9, 2.0, 0.48, "执行 OCR 或 Whisper"), (4.15, 7.1, 1.55, 0.4, "文本清洗与切片"),
                         (4.15, 6.35, 1.45, 0.4, "生成候选实体"), (4.15, 5.4, 1.95, 0.45, "保存文本结果并入治理链路")],
                "decisions": [(4.15, 8.3, 0.55, 0.55, "类型可识别"), (4.15, 5.85, 0.55, 0.55, "处理是否成功")],
                "side": [(1.25, 7.9, 1.55, 0.45, "失败记录/人工重试"), (7.0, 5.4, 1.55, 0.45, "更新失败状态/重试")],
                "extra_conns": [(3.85, 8.3, 1.95, 8.3), (1.95, 8.3, 1.95, 7.9), (1.95, 7.9, 2.8, 7.9),
                                (4.45, 5.85, 7.0, 5.85), (7.0, 5.85, 7.0, 5.4), (6.22, 5.4, 5.12, 5.4)],
                "end_y": 4.7,
            }),
            ("图5-5_知识图谱流程图", "图 5-5 知识图谱查询流程图", {
                "main": [(4.15, 9.65, 2.0, 0.42, "进入实体审核/图谱查询"), (4.15, 8.85, 2.0, 0.5, "生成候选实体与关系"),
                         (4.15, 7.9, 1.9, 0.45, "写入图谱实体与关系"), (4.15, 7.1, 1.95, 0.42, "发起邻居/路径/证据查询"),
                         (4.15, 5.75, 2.0, 0.45, "返回图谱结果及证据文本")],
                "decisions": [(4.15, 8.3, 0.55, 0.55, "审核是否通过"), (4.15, 6.45, 0.55, 0.55, "是否命中结果")],
                "side": [(1.2, 7.9, 1.65, 0.45, "修订/驳回/补充候选结果"), (7.0, 5.75, 1.7, 0.45, "调整查询条件后重试")],
                "extra_conns": [(3.85, 8.3, 1.95, 8.3), (1.95, 8.3, 1.95, 7.9), (1.95, 7.9, 2.85, 7.9),
                                (4.15, 6.89, 4.15, 6.7), (4.45, 6.45, 7.0, 6.45), (7.0, 6.45, 7.0, 5.75), (6.15, 5.75, 5.15, 5.75)],
                "end_y": 5.0,
            }),
            ("图5-6_智能问答流程图", "图 5-6 智能问答模块流程图", {
                "main": [(4.15, 9.65, 1.9, 0.42, "输入问题或上传附件"), (4.15, 8.9, 1.5, 0.4, "问题预处理"),
                         (4.15, 8.1, 2.2, 0.5, "关键词检索与向量召回"), (4.15, 7.1, 1.4, 0.38, "融合排序"),
                         (4.15, 6.35, 1.6, 0.38, "构建问答上下文"), (4.15, 5.6, 1.6, 0.38, "生成流式回答")],
                "decisions": [(4.15, 7.55, 0.55, 0.55, "证据是否充足"), (4.15, 4.95, 0.6, 0.6, "是否继续追问")],
                "side": [(6.95, 7.1, 1.75, 0.45, "扩展检索范围/附件摘要"), (1.2, 5.1, 1.8, 0.5, "保留会话上下文并返回输入")],
                "extra_conns": [(4.45, 7.55, 6.95, 7.55), (6.95, 7.55, 6.95, 7.1), (6.08, 7.1, 4.95, 7.1),
                                (3.85, 4.95, 1.95, 4.95), (1.95, 4.95, 1.95, 5.1), (3.0, 5.1, 3.55, 9.65)],
                "end_y": 4.3,
            }),
        ]
        for page_name, title, spec in flow_specs:
            p = vis.add_page(page_name)
            build_flow(p, rect_proto, circle_proto, conn_proto, title, spec)

        vis.save_vsdx(str(OUT))
    print(OUT)


if __name__ == "__main__":
    main()
