from __future__ import annotations

import re
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(r"D:\beauty")
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}

TITLE = '基于 CMS 架构的“美业多媒体知识库”构建与展示系统实现'
COLLEGE = "计算机工程学院/大数据学院"
CLASS_NAME = "2022 软件工程 4 班"
STUDENT = "陈汝楷"
STUDENT_ID = "202210098069"
TEACHER = "梁来养"
SUBMIT_DATE = "2026 年 5 月 22 日"


def w_tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def get_target_docx() -> Path:
    candidates = [p for p in ROOT.glob("*.docx") if not p.name.startswith("~$") and "tmp_template" not in p.name.lower()]
    if not candidates:
        raise FileNotFoundError("未找到目标论文 docx")
    return max(candidates, key=lambda p: p.stat().st_size)


def get_markdown() -> Path:
    candidates = [p for p in ROOT.glob("*.md") if "提取版" in p.name]
    if not candidates:
        raise FileNotFoundError("未找到正文提取版 markdown")
    return candidates[0]


def para_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def set_first_text(paragraph: ET.Element, text: str) -> None:
    texts = paragraph.findall(".//w:t", NS)
    if not texts:
        run = ET.SubElement(paragraph, w_tag("r"))
        texts = [ET.SubElement(run, w_tag("t"))]
    texts[0].text = text
    for node in texts[1:]:
        node.text = ""


def fill_cover_and_frontmatter(docx_path: Path) -> None:
    with zipfile.ZipFile(docx_path, "r") as zf:
        files = {name: zf.read(name) for name in zf.namelist()}

    root = ET.fromstring(files["word/document.xml"])
    body = root.find("w:body", NS)
    if body is None:
        raise RuntimeError("document.xml 缺少 body")

    non_empty = []
    for p in body.findall("w:p", NS):
        text = para_text(p).strip()
        if text:
            non_empty.append((p, text))

    for p, text in non_empty[:40]:
        if "基于CMS架构" in text or "【待填写论文题目】" in text:
            set_first_text(p, TITLE)
        elif text.startswith("学院") or "【待填写学院】" in text:
            set_first_text(p, f"学院  {COLLEGE}")
        elif text.startswith("专业班级") or "【待填写专业班级】" in text:
            set_first_text(p, f"专业班级  {CLASS_NAME}")
        elif text.startswith("学生姓名") or "【待填写姓名】" in text:
            set_first_text(p, f"学生姓名  {STUDENT}")
        elif text.startswith("学生学号") or "【待填写学号】" in text:
            set_first_text(p, f"学生学号  {STUDENT_ID}")
        elif text.startswith("指导教师") or "【待填写指导教师姓名及职称】" in text:
            set_first_text(p, f"指导教师  {TEACHER}")
        elif text.startswith("提交日期"):
            set_first_text(p, f"提交日期  {SUBMIT_DATE}")
        elif "美妆知识问答与知识图谱管理系统的设计与实现" in text:
            set_first_text(p, TITLE)

    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    for header_name, data in list(files.items()):
        if not header_name.startswith("word/header") or not header_name.endswith(".xml"):
            continue
        text = data.decode("utf-8", errors="ignore")
        text = text.replace("【待填写论文题目】", TITLE)
        text = text.replace("美妆知识问答与知识图谱管理系统的设计与实现", TITLE)
        files[header_name] = text.encode("utf-8")

    target_path = docx_path
    try:
        with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, data in files.items():
                zf.writestr(name, data)
    except PermissionError:
        target_path = docx_path.with_name(docx_path.stem + "_已填信息" + docx_path.suffix)
        with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, data in files.items():
                zf.writestr(name, data)
    return target_path


def fill_markdown(md_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    replacements = {
        "# 美妆知识问答与知识图谱管理系统的设计与实现": f"# {TITLE}",
        "学院： 【待填写学院】": f"学院： {COLLEGE}",
        "专业班级： 【待填写专业班级】": f"专业班级： {CLASS_NAME}",
        "学生姓名： 【待填写姓名】": f"学生姓名： {STUDENT}",
        "学生学号： 【待填写学号】": f"学生学号： {STUDENT_ID}",
        "指导教师： 【待填写指导教师姓名及职称】": f"指导教师： {TEACHER}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    if "提交日期：" not in text:
        text = re.sub(
            r"(指导教师： .+\n)",
            r"\1- 提交日期： " + SUBMIT_DATE + "\n",
            text,
            count=1,
        )
    md_path.write_text(text, encoding="utf-8")


def main() -> None:
    docx_path = get_target_docx()
    md_path = get_markdown()
    output_docx = fill_cover_and_frontmatter(docx_path)
    fill_markdown(md_path)
    print(output_docx)
    print(md_path)


if __name__ == "__main__":
    main()
