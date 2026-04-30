from copy import deepcopy
from pathlib import Path
import re

from docx import Document


DOC_PATH = Path(r"D:\beauty\lw.docx")
BACKUP_PATH = Path(r"D:\beauty\lw_before_restructure_from_user_request.docx")


def insert_copies_before(target_para, source_paras):
    for src in source_paras:
        target_para._p.addprevious(deepcopy(src._p))


def move_block_before(target_para, source_paras):
    for para in source_paras:
        target_para._p.addprevious(para._p)


def delete_paragraph(paragraph):
    p = paragraph._element
    parent = p.getparent()
    if parent is not None:
        parent.remove(p)
    paragraph._p = paragraph._element = None


def replace_text_global(text: str) -> str:
    # chapter titles
    text = text.replace("第三章 系统需求与分析", "第二章 系统需求分析")
    text = text.replace("第四章 系统总体设计", "第三章 系统总体设计")
    text = text.replace("第五章 系统详细设计与实现", "第四章 系统详细设计与实现")
    text = text.replace("第六章 系统测试", "第五章 系统测试")

    # common structure sentence
    text = text.replace(
        "全文结构安排如下：第一章为绪论，主要阐述研究背景、研究意义、国内外研究现状及论文结构；第二章介绍系统相关技术与理论基础；第三章分析系统需求与数据流；第四章介绍系统总体设计与关键流程；第五章详细说明系统各模块的设计实现、运行界面与关键代码；第六章对系统测试情况进行分析；第七章介绍系统部署与运行验证；最后对全文进行总结，并给出后续改进方向。",
        "全文结构安排如下：第一章为绪论，主要阐述研究背景、研究意义、国内外研究现状、技术路线及论文结构；第二章分析系统需求与数据流；第三章介绍系统总体设计与关键流程；第四章详细说明系统各模块的设计实现、运行界面与关键代码；第五章对系统测试情况进行分析，并补充部署与运行验证内容；最后对全文进行总结，并给出后续改进方向。"
    )

    # paragraph heading renumbering
    text = re.sub(r"^3\.(\d+(?:\.\d+)*)", lambda m: "2." + m.group(1), text)
    text = re.sub(r"^4\.(\d+(?:\.\d+)*)", lambda m: "3." + m.group(1), text)
    text = re.sub(r"^5\.(\d+(?:\.\d+)*)", lambda m: "4." + m.group(1), text)
    text = re.sub(r"^6\.1\b", "5.1", text)
    text = re.sub(r"^6\.2\b", "5.2", text)
    text = re.sub(r"^6\.3\b", "5.3", text)
    text = re.sub(r"^6\.4\b", "5.4", text)
    text = re.sub(r"^6\.5\b", "5.5", text)
    text = re.sub(r"^6\.6\b", "5.7", text)
    text = re.sub(r"^7\.1\b", "5.6", text)
    text = re.sub(r"^7\.2\b", "5.6.1", text)
    text = re.sub(r"^7\.3\b", "5.6.2", text)

    # figure/table numbering by chapter shift, using placeholders to avoid cascading
    swaps = [
        ("图 3-", "__FIG3__"), ("图3-", "__FIG3N__"),
        ("表 3-", "__TAB3__"), ("表3-", "__TAB3N__"),
        ("图 4-", "__FIG4__"), ("图4-", "__FIG4N__"),
        ("表 4-", "__TAB4__"), ("表4-", "__TAB4N__"),
        ("图 5-", "__FIG5__"), ("图5-", "__FIG5N__"),
        ("表 5-", "__TAB5__"), ("表5-", "__TAB5N__"),
        ("图 6-", "__FIG6__"), ("图6-", "__FIG6N__"),
        ("表 6-", "__TAB6__"), ("表6-", "__TAB6N__"),
    ]
    for old, token in swaps:
        text = text.replace(old, token)
    final_map = {
        "__FIG3__": "图 2-", "__FIG3N__": "图2-",
        "__TAB3__": "表 2-", "__TAB3N__": "表2-",
        "__FIG4__": "图 3-", "__FIG4N__": "图3-",
        "__TAB4__": "表 3-", "__TAB4N__": "表3-",
        "__FIG5__": "图 4-", "__FIG5N__": "图4-",
        "__TAB5__": "表 4-", "__TAB5N__": "表4-",
        "__FIG6__": "图 5-", "__FIG6N__": "图5-",
        "__TAB6__": "表 5-", "__TAB6N__": "表5-",
    }
    for token, new in final_map.items():
        text = text.replace(token, new)
    return text


def main():
    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_bytes(DOC_PATH.read_bytes())

    doc = Document(str(DOC_PATH))
    paras = doc.paragraphs

    # Insert technology content into retained chapters
    insert_copies_before(paras[67], paras[71:73])   # into chapter 1 before summary
    insert_copies_before(paras[117], paras[74:76])  # into overall design
    insert_copies_before(paras[149], paras[77:79])  # into database design
    insert_copies_before(paras[214], paras[80:82])  # into intelligent QA section

    # Merge chapter 7 summary into chapter 6 summary text before deletion
    paras[318].text = paras[318].text.rstrip("。") + "。此外，" + paras[334].text

    # Move deployment/testing content before the test chapter summary
    move_block_before(paras[317], paras[320:333])   # 7.1 to 7.3 content

    # Remove old standalone chapter 2 and chapter 7 shell paragraphs
    for para in reversed(paras[69:84]):
        delete_paragraph(para)

    doc = Document(str(DOC_PATH)) if False else doc
    paras = doc.paragraphs
    # Delete old chapter 7 heading + summary heading + summary text by text match after move
    for para in list(doc.paragraphs):
        if para.text.strip() in {
            "第七章 系统部署与运行验证",
            "7.4 本章小结",
            "本章围绕系统部署方案、运行链路与工程化组织方式进行了分析，说明了系统在当前环境中的服务编排关系、关键组件协同方式和运行验证结果，进一步证明了本文提出的系统方案在工程实现层具有较好的可部署性与可运行性。",
        }:
            delete_paragraph(para)

    # Global renumbering and wording update
    for para in doc.paragraphs:
        text = para.text
        if not text:
            continue
        new = replace_text_global(text)
        if new != text:
            para.text = new

    doc.save(str(DOC_PATH))


if __name__ == "__main__":
    main()
