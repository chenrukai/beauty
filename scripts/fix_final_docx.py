from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(r"D:\beauty")
SOURCE_DOC = next(p for p in ROOT.glob("*.docx") if p.stat().st_size == 843879)
OUTPUT_DOC = ROOT / "毕业论文_最终稿_定稿版.docx"

SUBMISSION_ASSETS = ROOT / "submission_assets"
EVIDENCE_ASSETS = ROOT / "evidence_assets_fixed"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"w": W, "a": A, "r": R, "pr": PR}

ET.register_namespace("w", W)
ET.register_namespace("a", A)
ET.register_namespace("r", R)

BASE_REPLACEMENTS = {
    "图 2-1 系统业务流程图": SUBMISSION_ASSETS / "fig_2_1_business_flow.png",
    "图 2-2 普通用户用例图": SUBMISSION_ASSETS / "fig_2_2_user_usecase.png",
    "图 2-3 后台管理员用例图": SUBMISSION_ASSETS / "fig_2_3_admin_usecase.png",
    "图 4-1 系统详细设计模块协作图": SUBMISSION_ASSETS / "fig_4_1_detail_collaboration.png",
    "图 4-2 用户端页面跳转关系图": SUBMISSION_ASSETS / "fig_4_2_frontend_navigation.png",
    "图 4-3 知识管理模块处理流程图": SUBMISSION_ASSETS / "fig_4_3_knowledge_manage_flow.png",
    "图 4-4 文件处理模块流程图": SUBMISSION_ASSETS / "fig_4_4_file_processing_flow.png",
    "图 4-5 知识图谱查询流程图": SUBMISSION_ASSETS / "fig_4_5_graph_query_flow.png",
    "图 4-6 智能问答模块流程图": SUBMISSION_ASSETS / "fig_4_6_qa_flow.png",
    "图 5-1 性能测试记录图": SUBMISSION_ASSETS / "fig_5_1_performance_record.png",
    "图 5-2 兼容性测试结果图": SUBMISSION_ASSETS / "fig_5_2_compatibility_result.png",
}

EVIDENCE_REPLACEMENTS = {
    "图 4-7 文件处理状态流转代码截图": EVIDENCE_ASSETS / "fig_4_7_task_state_code.png",
    "图 4-8 知识图谱查询构建代码截图": EVIDENCE_ASSETS / "fig_4_8_graph_query_code.png",
    "图 4-9 流式问答状态管理代码截图": EVIDENCE_ASSETS / "fig_4_9_stream_chat_code.png",
    "图 5-3 后端工程校验结果截图": SUBMISSION_ASSETS / "fig_5_3_backend_validate.png",
    "图 5-4 前端生产构建结果截图": SUBMISSION_ASSETS / "fig_5_4_frontend_build.png",
    "图 6-1 前端构建产物生成结果截图": SUBMISSION_ASSETS / "fig_6_1_frontend_dist.png",
}

REFS = [
    "Zhao S, Wang Y, Liu C, et al. Retrieval-Augmented Generation for AI-Generated Content: A Survey[J/OL]. Data Intelligence, 2026.",
    "Edge D, Trinh H, Cheng N, et al. From Local to Global: A Graph RAG Approach to Query-Focused Summarization[EB/OL]. Microsoft Research, 2024.",
    "Asai A, Wu Z, Wang Y, et al. Self-RAG: Learning to Retrieve, Generate and Critique through Self-Reflection[EB/OL]. ICLR, 2024.",
    "He X, Tian Y, Xiong W, et al. G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering[EB/OL]. arXiv, 2024.",
    "Zhang Y, Yu Y, Huang X. Scholarly Recommendation Systems: A Literature Survey[J]. International Journal on Digital Libraries, 2023.",
    "Bellini E, Nuzzolese A G, Gentile A L. Knowledge Graphs in Recommendation Scenarios: A Systematic Review[J]. Data Intelligence, 2024.",
    "Niu W, Wang X, Liu Y. Learning Resource Recommendation Based on Knowledge Graph and Collaborative Filtering[J]. Applied Sciences, 2023.",
    "Leng J, Chen Y, Zhao Y, et al. A Knowledge Graph Based Personalized Recommendation System for Dementia Care[J]. JMIR Medical Informatics, 2023.",
    "Radford A, Kim J W, Xu T, et al. Robust Speech Recognition via Large-Scale Weak Supervision[C]. ICML 2023.",
    "刘成林, 王衡, 李晓宇, 等. 文档智能分析与识别前沿: 回顾与展望[J]. 中国图象图形学报, 2023, 28(10): 3047-3076.",
    "王建林, 马会芳. 基于知识图谱的档案领域问答系统研究与应用[J]. 软件工程与应用, 2024, 13(2): 223-232.",
    "纪雷, 马松雷, 张崇富. 知识图谱嵌入的安全性问题分析[J]. 软件工程与应用, 2023, 12(6): 1133-1143.",
    "Lu Z, Xu H, Chen A, et al. HSG-RAG: Hierarchical Knowledge Base Construction for Embedded System Development[J]. ACM Transactions on Design Automation of Electronic Systems, 2025, 30(6): 1-21.",
]


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def para_text(p: ET.Element) -> str:
    return "".join(t.text or "" for t in p.findall(".//w:t", NS)).strip()


def find_paragraph_index(paras, target: str) -> int:
    for i, p in enumerate(paras):
        if para_text(p) == target:
            return i
    raise ValueError(target)


def clear_runs(p: ET.Element) -> None:
    for child in list(p):
        if child.tag != qn(W, "pPr"):
            p.remove(child)


def ensure_rpr(run: ET.Element) -> ET.Element:
    rpr = run.find("w:rPr", NS)
    if rpr is None:
        rpr = ET.Element(qn(W, "rPr"))
        run.insert(0, rpr)
    return rpr


def append_run(p: ET.Element, text: str, superscript: bool = False) -> None:
    if not text:
        return
    r = ET.SubElement(p, qn(W, "r"))
    rpr = ET.SubElement(r, qn(W, "rPr"))
    if superscript:
        va = ET.SubElement(rpr, qn(W, "vertAlign"))
        va.set(qn(W, "val"), "superscript")
    t = ET.SubElement(r, qn(W, "t"))
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text


def set_paragraph_with_citations(p: ET.Element, text: str) -> None:
    clear_runs(p)
    pos = 0
    import re
    for m in re.finditer(r"\[\d+\]", text):
        append_run(p, text[pos:m.start()], False)
        append_run(p, m.group(0), True)
        pos = m.end()
    append_run(p, text[pos:], False)


def set_paragraph_plain(p: ET.Element, text: str) -> None:
    clear_runs(p)
    append_run(p, text, False)


def delete_paragraph(p: ET.Element, body: ET.Element) -> None:
    body.remove(p)


def nearest_caption(paras, idx: int) -> str | None:
    current = para_text(paras[idx])
    if current.startswith("图 "):
        return current
    candidates = []
    for delta in (-2, -1, 1, 2, 3):
        j = idx + delta
        if 0 <= j < len(paras):
            text = para_text(paras[j])
            if text.startswith("图 "):
                candidates.append((abs(delta), text))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def split_image_caption_paragraphs(body: ET.Element) -> None:
    paras = body.findall("w:p", NS)
    for p in list(paras):
        if not p.findall(".//a:blip", NS):
            continue
        text = para_text(p)
        if not text.startswith("图 "):
            continue
        new_p = deepcopy(p)
        clear_runs(p)
        set_paragraph_plain(new_p, text)
        body.insert(list(body).index(p) + 1, new_p)


def fix_document_xml(doc_bytes: bytes) -> bytes:
    root = ET.fromstring(doc_bytes)
    body = root.find("w:body", NS)
    paras = body.findall("w:p", NS)

    for p in paras:
        text = para_text(p)
        if text == "在此背景下，构建面向美妆领域的知识服务系统具有较强的现实意义。一方面，该类系统能够对分散的行业知识进行统一汇聚、分类和管理，提升知识资源的利用效率；另一方面，将知识图谱与检索增强生成技术引入系统后，可以在保证回答相关性的同时增强证据支撑能力，从而提高用户获取专业知识的准确性与便捷性12。因此，围绕美妆知识场景开展知识管理与智能问答系统的研究与实现，既具有一定的工程应用价值，也具有较强的实践参考意义。":
            set_paragraph_with_citations(p, text.replace("便捷性12。", "便捷性[12]。"))
        elif text == "近年来，国外在检索增强生成、图谱增强问答以及垂直领域知识组织方面形成了较为系统的研究成果。相关研究表明，检索机制与生成模型协同能够有效改善大模型在事实性、可解释性和知识时效性方面的不足13。同时，图结构知识组织方式在路径分析、关系发现和证据回溯方面具有明显优势，使得知识图谱逐渐成为智能问答和推荐系统的重要支撑基础46。":
            set_paragraph_with_citations(p, text.replace("不足13。", "不足[13]。").replace("支撑基础46。", "支撑基础[4][6]。"))
        elif text == "国内研究则更多关注知识图谱、文档智能处理和行业问答系统的落地应用。随着 OCR、语音识别与文本结构化处理技术的不断发展，面向文档、图片和音视频资料的知识抽取能力持续增强，为垂直领域知识服务系统建设提供了更成熟的技术基础91011。然而，从现有研究与应用情况来看，直接面向美妆场景、同时兼顾知识管理、文件处理、实体审核、图谱展示和智能问答的综合型系统仍相对较少。基于此，本文尝试结合现有技术成果与真实项目实践，构建一套具有完整业务链路的美妆知识服务平台。":
            set_paragraph_with_citations(p, text.replace("技术基础91011。", "技术基础[9][10][11]。"))
        elif text == "智能问答模块是本系统面向用户提供知识服务的核心模块。与传统直接生成式问答不同，本系统采用“检索增强 + 生成表达”的实现思路，即先从知识资源中检索相关证据，再基于检索结果组织上下文并生成回答内容。这种方式能够在一定程度上提高回答的准确性与可解释性234。":
            set_paragraph_with_citations(p, text.replace("可解释性234。", "可解释性[2][3][4]。"))

    # Remove stray bibliography line from TOC area.
    paras = body.findall("w:p", NS)
    ref_heading_idx = find_paragraph_index(paras, "参考文献")
    for i, p in enumerate(list(paras)):
        t = para_text(p)
        if i < ref_heading_idx and "HSG-RAG: Hierarchical Knowledge Base Construction for Embedded System Development" in t:
            delete_paragraph(p, body)

    split_image_caption_paragraphs(body)

    paras = body.findall("w:p", NS)
    ref_idx = find_paragraph_index(paras, "参考文献")
    ack_idx = find_paragraph_index(paras, "致谢")
    ref_paras = paras[ref_idx + 1:ack_idx]
    template_ref = ref_paras[0]

    for p in ref_paras:
        delete_paragraph(p, body)

    insert_pos = list(body).index(paras[ref_idx]) + 1
    for i, ref in enumerate(REFS, 1):
        new_p = deepcopy(template_ref)
        set_paragraph_plain(new_p, f"[{i}] {ref}")
        body.insert(insert_pos, new_p)
        insert_pos += 1

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def image_mapping(doc_bytes: bytes, rel_bytes: bytes) -> dict[str, Path]:
    root = ET.fromstring(doc_bytes)
    rel_root = ET.fromstring(rel_bytes)
    rels = {r.attrib["Id"]: r.attrib["Target"].replace("../", "") for r in rel_root}
    paras = root.findall(".//w:body/w:p", NS)
    media_map: dict[str, Path] = {}
    for idx, p in enumerate(paras):
        blips = p.findall(".//a:blip", NS)
        if not blips:
            continue
        rid = blips[0].attrib.get(f"{{{R}}}embed")
        target = rels.get(rid, "")
        if not target.startswith("media/"):
            continue
        caption = nearest_caption(paras, idx)
        replacement = BASE_REPLACEMENTS.get(caption) or EVIDENCE_REPLACEMENTS.get(caption)
        if replacement:
            media_map[f"word/{target}"] = replacement
    return media_map


def build():
    with ZipFile(SOURCE_DOC, "r") as zin:
        doc_xml = zin.read("word/document.xml")
        rel_xml = zin.read("word/_rels/document.xml.rels")
        replacements = image_mapping(doc_xml, rel_xml)
        fixed_doc = fix_document_xml(doc_xml)

        temp_doc = ROOT / "_tmp_submission_fixed.docx"
        with ZipFile(temp_doc, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    data = fixed_doc
                elif item.filename in replacements:
                    data = replacements[item.filename].read_bytes()
                zout.writestr(item, data)
        shutil.copyfile(temp_doc, OUTPUT_DOC)
        temp_doc.unlink(missing_ok=True)

    print(OUTPUT_DOC)
    print(f"replaced_images={len(replacements)}")


if __name__ == "__main__":
    build()
