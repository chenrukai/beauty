from __future__ import annotations

import math
import struct
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(r"D:\beauty")
SOURCE = ROOT / "毕业论文_最终稿_引文闭环重构版.docx"
OUTPUT = ROOT / "毕业论文_最终稿_规范达标版.docx"
PNG_DIR = ROOT / "submission_assets_ascii"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
PIC_NS = "http://schemas.openxmlformats.org/drawingml/2006/picture"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

NS = {"w": W_NS, "r": R_NS, "rel": REL_NS, "ct": CT_NS}

EMU_PER_INCH = 914400
MAX_WIDTH_EMU = int(6.1 * EMU_PER_INCH)

IMAGE_MAP = {
    "图 2-1 系统业务流程图": "fig_2_1_business_flow.png",
    "图 3-1 系统整体结构图": "fig_3_1_system_architecture.png",
    "图 3-2 系统 ER 图": "fig_3_2_er_diagram.png",
    "图 2-2 普通用户用例图": "fig_2_2_user_usecase.png",
    "图 2-3 后台管理员用例图": "fig_2_3_admin_usecase.png",
    "图 4-1 系统详细设计模块协作图": "fig_4_1_detail_collaboration.png",
    "图 4-2 用户端页面跳转关系图": "fig_4_2_frontend_navigation.png",
    "图 4-3 知识管理模块处理流程图": "fig_4_3_knowledge_manage_flow.png",
    "图 4-4 文件处理模块流程图": "fig_4_4_file_processing_flow.png",
    "图 4-5 知识图谱查询流程图": "fig_4_5_graph_query_flow.png",
    "图 4-6 智能问答模块流程图": "fig_4_6_qa_flow.png",
}


def w_tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def rel_tag(name: str) -> str:
    return f"{{{REL_NS}}}{name}"


def ct_tag(name: str) -> str:
    return f"{{{CT_NS}}}{name}"


def para_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS)).strip()


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG: {path}")
    width = struct.unpack(">I", data[16:20])[0]
    height = struct.unpack(">I", data[20:24])[0]
    return width, height


def scaled_emu(path: Path) -> tuple[int, int]:
    width_px, height_px = png_size(path)
    width_emu = min(int(width_px / 96 * EMU_PER_INCH), MAX_WIDTH_EMU)
    ratio = width_emu / max(width_px, 1)
    height_emu = int(height_px * ratio)
    return width_emu, height_emu


def make_drawing_paragraph(rid: str, image_name: str, width_emu: int, height_emu: int, docpr_id: int) -> ET.Element:
    xml = f"""
    <w:p xmlns:w="{W_NS}" xmlns:r="{R_NS}" xmlns:wp="{WP_NS}" xmlns:a="{A_NS}" xmlns:pic="{PIC_NS}">
      <w:pPr>
        <w:jc w:val="center"/>
        <w:spacing w:before="120" w:after="120" w:line="240" w:lineRule="auto"/>
      </w:pPr>
      <w:r>
        <w:drawing>
          <wp:inline distT="0" distB="0" distL="0" distR="0">
            <wp:extent cx="{width_emu}" cy="{height_emu}"/>
            <wp:effectExtent l="0" t="0" r="0" b="0"/>
            <wp:docPr id="{docpr_id}" name="{image_name}"/>
            <wp:cNvGraphicFramePr>
              <a:graphicFrameLocks noChangeAspect="1"/>
            </wp:cNvGraphicFramePr>
            <a:graphic>
              <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                <pic:pic>
                  <pic:nvPicPr>
                    <pic:cNvPr id="{docpr_id}" name="{image_name}"/>
                    <pic:cNvPicPr/>
                  </pic:nvPicPr>
                  <pic:blipFill>
                    <a:blip r:embed="{rid}"/>
                    <a:stretch><a:fillRect/></a:stretch>
                  </pic:blipFill>
                  <pic:spPr>
                    <a:xfrm>
                      <a:off x="0" y="0"/>
                      <a:ext cx="{width_emu}" cy="{height_emu}"/>
                    </a:xfrm>
                    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
                  </pic:spPr>
                </pic:pic>
              </a:graphicData>
            </a:graphic>
          </wp:inline>
        </w:drawing>
      </w:r>
    </w:p>
    """
    return ET.fromstring(xml)


def make_placeholder_paragraph(text: str) -> ET.Element:
    xml = f"""
    <w:p xmlns:w="{W_NS}">
      <w:pPr>
        <w:jc w:val="center"/>
        <w:spacing w:before="120" w:after="120" w:line="240" w:lineRule="auto"/>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:i/>
          <w:sz w:val="22"/>
          <w:szCs w:val="22"/>
        </w:rPr>
        <w:t>{text}</w:t>
      </w:r>
    </w:p>
    """
    return ET.fromstring(xml)


def make_caption_paragraph(text: str) -> ET.Element:
    xml = f"""
    <w:p xmlns:w="{W_NS}">
      <w:pPr>
        <w:jc w:val="center"/>
        <w:spacing w:before="60" w:after="120" w:line="240" w:lineRule="auto"/>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:t>{text}</w:t>
      </w:r>
    </w:p>
    """
    return ET.fromstring(xml)


def ensure_png_content_type(content_types_root: ET.Element) -> None:
    for node in content_types_root.findall("ct:Default", NS):
        if node.attrib.get("Extension") == "png":
            return
    ET.SubElement(
        content_types_root,
        ct_tag("Default"),
        {"Extension": "png", "ContentType": "image/png"},
    )


def main() -> None:
    with zipfile.ZipFile(SOURCE, "r") as zf:
        files = {name: zf.read(name) for name in zf.namelist()}

    document_root = ET.fromstring(files["word/document.xml"])
    rels_root = ET.fromstring(files["word/_rels/document.xml.rels"])
    content_types_root = ET.fromstring(files["[Content_Types].xml"])
    body = document_root.find("w:body", NS)
    if body is None:
        raise RuntimeError("Document body not found")

    ensure_png_content_type(content_types_root)

    rel_ids = []
    for rel in rels_root.findall("rel:Relationship", NS):
        rid = rel.attrib.get("Id", "")
        if rid.startswith("rId"):
            try:
                rel_ids.append(int(rid[3:]))
            except ValueError:
                pass
    next_rid_num = max(rel_ids, default=20) + 1
    docpr_id = 100

    caption_to_rel: dict[str, str] = {}
    for caption, image_file in IMAGE_MAP.items():
        img_path = PNG_DIR / image_file
        target = f"media/{image_file}"
        files[f"word/{target}"] = img_path.read_bytes()
        rid = f"rId{next_rid_num}"
        next_rid_num += 1
        ET.SubElement(
            rels_root,
            rel_tag("Relationship"),
            {
                "Id": rid,
                "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                "Target": target,
            },
        )
        caption_to_rel[caption] = rid

    new_children: list[ET.Element] = []
    inserted = set()
    placeholders_done = False
    auto_ch3_1_done = False
    auto_ch3_2_done = False

    for node in list(body):
        new_children.append(deepcopy(node))

        if node.tag == w_tag("p"):
            text = para_text(node)
            if text in IMAGE_MAP and text not in inserted:
                image_path = PNG_DIR / IMAGE_MAP[text]
                rid = caption_to_rel[text]
                width_emu, height_emu = scaled_emu(image_path)
                new_children.append(make_drawing_paragraph(rid, image_path.name, width_emu, height_emu, docpr_id))
                docpr_id += 1
                inserted.add(text)

            if (text.startswith("3.2") or "系统整体结构如图 3-1 所示" in text or "系统整体结构如图3-1所示" in text) and "图 3-1 系统整体结构图" not in inserted and not auto_ch3_1_done:
                caption = "图 3-1 系统整体结构图"
                image_path = PNG_DIR / IMAGE_MAP[caption]
                rid = caption_to_rel[caption]
                width_emu, height_emu = scaled_emu(image_path)
                new_children.append(make_caption_paragraph(caption))
                new_children.append(make_drawing_paragraph(rid, image_path.name, width_emu, height_emu, docpr_id))
                docpr_id += 1
                inserted.add(caption)
                auto_ch3_1_done = True

            if (text.startswith("3.3") or "系统主要实体及关系组织如图 3-2 所示" in text or "系统主要实体及关系组织如图3-2所示" in text) and "图 3-2 系统 ER 图" not in inserted and not auto_ch3_2_done:
                caption = "图 3-2 系统 ER 图"
                image_path = PNG_DIR / IMAGE_MAP[caption]
                rid = caption_to_rel[caption]
                width_emu, height_emu = scaled_emu(image_path)
                new_children.append(make_caption_paragraph(caption))
                new_children.append(make_drawing_paragraph(rid, image_path.name, width_emu, height_emu, docpr_id))
                docpr_id += 1
                inserted.add(caption)
                auto_ch3_2_done = True

            if text.startswith("5.3 性能测试与兼容性测试") and not placeholders_done:
                new_children.append(make_placeholder_paragraph("图 5-1 性能测试记录图（待补真实截图）"))
                new_children.append(make_placeholder_paragraph("图 5-2 兼容性测试结果图（待补真实截图）"))
                placeholders_done = True

    for node in list(body):
        body.remove(node)
    for node in new_children:
        body.append(node)

    files["word/document.xml"] = ET.tostring(document_root, encoding="utf-8", xml_declaration=True)
    files["word/_rels/document.xml.rels"] = ET.tostring(rels_root, encoding="utf-8", xml_declaration=True)
    files["[Content_Types].xml"] = ET.tostring(content_types_root, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)

    print(OUTPUT)


if __name__ == "__main__":
    main()
