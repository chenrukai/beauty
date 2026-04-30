from __future__ import annotations

import html
import re
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(r"D:\beauty")
MD_PATH = ROOT / "毕业论文_正文提取版_按材料修订稿.md"
SOURCE_DOCX = ROOT / "毕业论文_完整草稿_按材料修订.docx"
OUTPUT_DOCX = ROOT / "毕业论文_完整草稿_按材料修订_补用例.docx"
ASSET_DIR = ROOT / "论文图表素材"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}

CHAPTER2 = """## 第二章 系统需求分析

### 2.1 业务场景分析

本系统主要面向普通用户与后台管理员两类角色。普通用户更关注知识获取效率与交互体验，希望能够通过推荐浏览、详情查看、关键词搜索和智能问答等方式快速获取所需内容；同时，在面对说明书、成分表、培训资料等非结构化文件时，还希望系统具备上传、解析和基于附件继续提问的能力。后台管理员则更关注平台知识资源的治理过程，需要完成知识录入、分类维护、文件处理、实体审核、图谱维护、公告管理、用户管理和统计分析等工作。

从业务流程角度看，系统并非仅承担静态内容展示功能，而是贯通了知识采集、知识加工、知识审核、知识组织和知识服务等多个环节。原始文件进入系统后，可以通过 OCR、语音转写、文本切分和实体抽取等处理流程逐步转化为结构化知识资源，再进一步支撑分类检索、图谱展示和问答服务。因此，该系统属于典型的垂直领域知识服务平台，其核心价值在于将分散信息转化为可管理、可检索、可问答、可分析的知识资产。

### 2.2 功能需求分析

根据业务场景，可将系统功能需求划分为用户端功能与管理端功能两部分。用户端主要包括首页推荐、知识搜索、知识详情查看、收藏管理、智能问答、会话历史管理、附件上传摘要以及基于附件继续追问等功能。其中，首页模块需要实现知识推荐和公告展示；知识模块需要支持列表检索与详情展示；问答模块需要完成问题输入、流式回答、来源呈现和上下文会话管理；收藏模块则用于提升用户对感兴趣内容的持续使用能力。

管理端功能主要包括数据概览、知识管理、分类管理、文件上传与处理、任务监控、实体确认、知识图谱、公告管理、用户管理和统计报表等。知识管理模块负责知识内容的录入、编辑、状态管理和检索；文件处理模块负责上传、预览、任务跟踪和失败重试；实体确认与知识图谱模块负责抽取结果审核、关系维护和图谱查询；统计报表模块用于展示平台运行中的热点内容、来源占比和用户活跃情况。各模块共同构成了系统从知识治理到知识服务的完整功能体系。

### 2.3 用例图与关键用例描述

根据《论文书写内容注意事项》中“第二章需包含每个用户的用例图及关键用例描述表”的要求，本文进一步从角色视角梳理系统功能边界。用例分析的目的在于明确不同角色与系统之间的交互关系，并为后续总体设计和详细设计提供角色职责依据。结合本系统的实际功能，可将主要角色划分为普通用户和后台管理员，两类角色的核心操作分别如图 2-2 与图 2-3 所示。

### 2.3.1 普通用户用例图分析

普通用户是系统知识服务能力的直接使用者，其主要目标是快速获取可信的美业知识内容，并在需要时借助系统的智能问答能力完成进一步查询。围绕这一目标，普通用户在系统中可执行首页浏览、知识检索、知识详情查看、收藏管理、智能问答、附件上传摘要以及基于附件继续追问等操作。其中，知识检索与知识详情查看构成基础知识访问路径，智能问答与附件追问则体现系统相较于传统内容展示平台的智能服务特征。

如图 2-2 所示，普通用户的核心活动既包括对知识内容的被动浏览，也包括围绕问题目标发起主动交互。用户在首页完成推荐浏览后，可以进入知识详情页面，也可以直接通过搜索或问答入口访问所需信息。当查询场景依赖外部资料时，用户还可以上传附件，系统完成摘要提取后继续支持围绕附件内容进行连续提问。上述用例共同构成了用户侧知识服务闭环。

图 2-2 普通用户用例图

### 2.3.2 后台管理员用例图分析

后台管理员承担平台治理与知识维护职责，其工作目标不在于直接消费知识内容，而在于保障平台数据质量、知识结构完整性以及服务过程的可控性。结合系统实现情况，管理员主要涉及数据概览查看、知识管理、分类管理、文件上传与处理、任务监控、实体确认、知识图谱维护、公告管理、用户管理和统计报表查看等操作。

如图 2-3 所示，管理员的操作链路贯穿知识治理全过程。管理员既可以直接录入或维护知识内容，也可以通过文件上传、任务监控和实体确认等环节参与非结构化资料向结构化知识的转化过程。在知识沉淀完成后，管理员还需要通过知识图谱与统计报表功能持续观察平台运行状态，并借助公告管理和用户管理模块维持系统正常运行。因此，管理员用例体现的是一种面向平台治理的复合型交互结构。

图 2-3 后台管理员用例图

### 2.3.3 关键用例描述表

在全部用例中，智能问答与文件处理及实体确认是最能体现本课题特色的两类关键用例。前者直接面向用户知识服务场景，后者则支撑知识治理链路中最核心的加工与审核过程。为便于后续模块设计，本文对这两类关键用例给出描述表。

表 2-1 智能问答用例描述表

| 项目 | 描述 |
| --- | --- |
| 用例名称 | 智能问答 |
| 参与角色 | 普通用户 |
| 前置条件 | 用户已完成登录，系统具备可检索的知识数据 |
| 触发条件 | 用户在问答页面输入问题并提交 |
| 基本流程 | 系统接收问题后执行关键词检索和向量召回；对候选证据进行融合排序；构建上下文并调用问答服务生成回答；以前端流式方式返回答案及来源信息 |
| 异常流程 | 当未检索到有效证据时，系统返回低置信度提示或引导用户调整问题；当服务异常时，提示稍后重试 |
| 后置条件 | 会话记录与消息内容被保存，可用于后续连续提问 |

表 2-2 文件处理与实体确认用例描述表

| 项目 | 描述 |
| --- | --- |
| 用例名称 | 文件处理与实体确认 |
| 参与角色 | 后台管理员 |
| 前置条件 | 管理员已登录系统，具备文件上传与知识治理权限 |
| 触发条件 | 管理员上传知识文件或处理待确认实体任务 |
| 基本流程 | 系统保存文件并创建处理任务；根据文件类型调用 OCR 或语音转写服务；对解析文本进行切分和实体抽取；管理员在实体确认页面审核抽取结果；审核通过的数据写入知识图谱与知识库 |
| 异常流程 | 文件格式不支持、任务执行失败或抽取结果不完整时，系统记录失败原因并支持重试或人工修正 |
| 后置条件 | 文件任务状态被更新，审核通过的数据进入后续检索与图谱服务链路 |

### 2.4 非功能需求分析

除功能需求外，系统还需要满足相应的非功能需求。在性能方面，系统应能够稳定支撑常见的分页查询、知识检索、会话加载和后台管理操作，并通过缓存和异步任务机制降低高频访问和耗时操作带来的压力。在安全性方面，系统需要通过身份认证和权限控制机制保证不同角色对接口和数据的访问边界，避免未授权操作对业务数据造成影响。

在可维护性方面，系统应保持前后端分离、模块职责清晰和接口边界明确，以便后续对知识管理、图谱服务和问答能力进行独立优化。在可扩展性方面，系统应支持知识类别扩展、实体类型扩展、模型服务替换以及基础设施组件的增减，从而满足后续业务持续演进的需要。在可用性方面，系统还应通过清晰的界面入口和稳定的处理流程，保证普通用户与管理员均能够顺利完成各自操作。

### 2.5 可行性分析

从技术可行性角度看，本系统采用的前端与后端技术栈较为成熟，具备良好的开发生态和文档支持。前端基于 Vue 3 构建页面交互，后端基于 Spring Boot 生态实现业务逻辑，结合 MySQL、Redis、RabbitMQ、MinIO、Milvus、OCR 和 Whisper 等组件，能够满足系统在知识存储、缓存、异步处理、对象存储、向量检索和文件智能解析方面的实际需求。因此，系统具备较好的技术实现基础。

从经济可行性角度看，系统主要依赖开源框架与本地容器化部署环境，开发与运行成本相对可控，适合毕业设计条件下完成。从操作可行性角度看，系统界面划分明确，功能入口清晰，普通用户与管理员均可以按照既定流程完成对应操作，具有较好的使用可行性。综上所述，本课题在技术、成本和实施方式等方面均具备较强的可行性。

### 2.6 本章小结

本章围绕系统面向的业务场景，从功能需求、角色用例、关键用例描述、非功能需求和可行性等方面进行了系统分析，进一步明确了普通用户与后台管理员的职责边界以及系统建设目标，为后续总体设计与详细实现提供了较为完整的需求依据。
"""

USER_USECASE_SPEC = """meta:
  title: "图2-2 普通用户用例图"
  source: "thesis"
  note: "黑白风格，供论文第二章插图使用"
diagram:
  type: usecase
  actor: "普通用户"
  usecases:
    - "首页浏览"
    - "知识检索"
    - "知识详情查看"
    - "收藏管理"
    - "智能问答"
    - "附件上传摘要"
    - "基于附件继续追问"
"""

ADMIN_USECASE_SPEC = """meta:
  title: "图2-3 后台管理员用例图"
  source: "thesis"
  note: "黑白风格，供论文第二章插图使用"
diagram:
  type: usecase
  actor: "后台管理员"
  usecases:
    - "数据概览"
    - "知识管理"
    - "分类管理"
    - "文件上传与处理"
    - "任务监控"
    - "实体确认"
    - "知识图谱"
    - "公告管理"
    - "用户管理"
    - "统计报表"
"""

USER_USECASE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="560" viewBox="0 0 1000 560">
  <rect width="1000" height="560" fill="#ffffff"/>
  <rect x="170" y="50" width="760" height="450" fill="none" stroke="#000000" stroke-width="2"/>
  <text x="550" y="85" font-size="26" text-anchor="middle" font-family="SimSun, serif">美业多媒体知识库系统</text>
  <line x1="120" y1="140" x2="120" y2="260" stroke="#000000" stroke-width="2"/>
  <circle cx="120" cy="110" r="24" fill="none" stroke="#000000" stroke-width="2"/>
  <line x1="120" y1="260" x2="95" y2="320" stroke="#000000" stroke-width="2"/>
  <line x1="120" y1="260" x2="145" y2="320" stroke="#000000" stroke-width="2"/>
  <line x1="95" y1="190" x2="145" y2="190" stroke="#000000" stroke-width="2"/>
  <text x="120" y="360" font-size="24" text-anchor="middle" font-family="SimSun, serif">普通用户</text>
  <ellipse cx="350" cy="150" rx="95" ry="32" fill="none" stroke="#000000" stroke-width="2"/>
  <ellipse cx="560" cy="150" rx="95" ry="32" fill="none" stroke="#000000" stroke-width="2"/>
  <ellipse cx="770" cy="150" rx="95" ry="32" fill="none" stroke="#000000" stroke-width="2"/>
  <ellipse cx="350" cy="270" rx="95" ry="32" fill="none" stroke="#000000" stroke-width="2"/>
  <ellipse cx="560" cy="270" rx="95" ry="32" fill="none" stroke="#000000" stroke-width="2"/>
  <ellipse cx="770" cy="270" rx="115" ry="32" fill="none" stroke="#000000" stroke-width="2"/>
  <ellipse cx="470" cy="390" rx="125" ry="32" fill="none" stroke="#000000" stroke-width="2"/>
  <text x="350" y="158" font-size="20" text-anchor="middle" font-family="SimSun, serif">首页浏览</text>
  <text x="560" y="158" font-size="20" text-anchor="middle" font-family="SimSun, serif">知识检索</text>
  <text x="770" y="158" font-size="20" text-anchor="middle" font-family="SimSun, serif">知识详情查看</text>
  <text x="350" y="278" font-size="20" text-anchor="middle" font-family="SimSun, serif">收藏管理</text>
  <text x="560" y="278" font-size="20" text-anchor="middle" font-family="SimSun, serif">智能问答</text>
  <text x="770" y="278" font-size="20" text-anchor="middle" font-family="SimSun, serif">附件上传摘要</text>
  <text x="470" y="398" font-size="20" text-anchor="middle" font-family="SimSun, serif">基于附件继续追问</text>
  <line x1="145" y1="170" x2="255" y2="150" stroke="#000000" stroke-width="1.8"/>
  <line x1="145" y1="180" x2="465" y2="150" stroke="#000000" stroke-width="1.8"/>
  <line x1="145" y1="190" x2="675" y2="150" stroke="#000000" stroke-width="1.8"/>
  <line x1="145" y1="205" x2="255" y2="270" stroke="#000000" stroke-width="1.8"/>
  <line x1="145" y1="215" x2="465" y2="270" stroke="#000000" stroke-width="1.8"/>
  <line x1="145" y1="225" x2="655" y2="270" stroke="#000000" stroke-width="1.8"/>
  <line x1="145" y1="235" x2="345" y2="390" stroke="#000000" stroke-width="1.8"/>
</svg>
"""

ADMIN_USECASE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="620" viewBox="0 0 1120 620">
  <rect width="1120" height="620" fill="#ffffff"/>
  <rect x="190" y="45" width="860" height="520" fill="none" stroke="#000000" stroke-width="2"/>
  <text x="620" y="80" font-size="26" text-anchor="middle" font-family="SimSun, serif">美业多媒体知识库系统</text>
  <line x1="120" y1="160" x2="120" y2="290" stroke="#000000" stroke-width="2"/>
  <circle cx="120" cy="128" r="24" fill="none" stroke="#000000" stroke-width="2"/>
  <line x1="120" y1="290" x2="92" y2="350" stroke="#000000" stroke-width="2"/>
  <line x1="120" y1="290" x2="148" y2="350" stroke="#000000" stroke-width="2"/>
  <line x1="92" y1="210" x2="148" y2="210" stroke="#000000" stroke-width="2"/>
  <text x="120" y="390" font-size="24" text-anchor="middle" font-family="SimSun, serif">后台管理员</text>
  <g font-size="18" text-anchor="middle" font-family="SimSun, serif" fill="#000000" stroke="#000000" stroke-width="2">
    <ellipse cx="360" cy="140" rx="88" ry="28" fill="none"/><text x="360" y="146" stroke="none">数据概览</text>
    <ellipse cx="570" cy="140" rx="88" ry="28" fill="none"/><text x="570" y="146" stroke="none">知识管理</text>
    <ellipse cx="780" cy="140" rx="88" ry="28" fill="none"/><text x="780" y="146" stroke="none">分类管理</text>
    <ellipse cx="950" cy="140" rx="98" ry="28" fill="none"/><text x="950" y="146" stroke="none">文件上传与处理</text>
    <ellipse cx="360" cy="260" rx="88" ry="28" fill="none"/><text x="360" y="266" stroke="none">任务监控</text>
    <ellipse cx="570" cy="260" rx="88" ry="28" fill="none"/><text x="570" y="266" stroke="none">实体确认</text>
    <ellipse cx="780" cy="260" rx="88" ry="28" fill="none"/><text x="780" y="266" stroke="none">知识图谱</text>
    <ellipse cx="950" cy="260" rx="88" ry="28" fill="none"/><text x="950" y="266" stroke="none">公告管理</text>
    <ellipse cx="470" cy="380" rx="88" ry="28" fill="none"/><text x="470" y="386" stroke="none">用户管理</text>
    <ellipse cx="730" cy="380" rx="88" ry="28" fill="none"/><text x="730" y="386" stroke="none">统计报表</text>
  </g>
  <g stroke="#000000" stroke-width="1.6">
    <line x1="148" y1="190" x2="272" y2="140"/>
    <line x1="148" y1="200" x2="482" y2="140"/>
    <line x1="148" y1="210" x2="692" y2="140"/>
    <line x1="148" y1="220" x2="852" y2="140"/>
    <line x1="148" y1="230" x2="272" y2="260"/>
    <line x1="148" y1="240" x2="482" y2="260"/>
    <line x1="148" y1="250" x2="692" y2="260"/>
    <line x1="148" y1="260" x2="862" y2="260"/>
    <line x1="148" y1="270" x2="382" y2="380"/>
    <line x1="148" y1="280" x2="642" y2="380"/>
  </g>
</svg>
"""


def w_tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def para_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def esc(text: str) -> str:
    return html.escape(text.strip())


def render_runs(text: str, size: int = 24, superscript_refs: bool = False) -> str:
    if not superscript_refs:
        return (
            f"<w:r><w:rPr><w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
            f"<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>"
        )
    pattern = re.compile(r"\[(\d+)\]")
    parts: list[str] = []
    last = 0
    for match in pattern.finditer(text):
        normal = text[last:match.start()]
        if normal:
            parts.append(
                f"<w:r><w:rPr><w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
                f"<w:t xml:space=\"preserve\">{esc(normal)}</w:t></w:r>"
            )
        parts.append(
            "<w:r><w:rPr><w:vertAlign w:val=\"superscript\"/><w:sz w:val=\"18\"/>"
            "<w:szCs w:val=\"18\"/></w:rPr>"
            f"<w:t>{match.group(1)}</w:t></w:r>"
        )
        last = match.end()
    tail = text[last:]
    if tail:
        parts.append(
            f"<w:r><w:rPr><w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
            f"<w:t xml:space=\"preserve\">{esc(tail)}</w:t></w:r>"
        )
    return "".join(parts)


def p_body(text: str, indent: bool = True, superscript_refs: bool = False) -> str:
    ind = "<w:ind w:firstLineChars=\"200\"/>" if indent else ""
    return (
        "<w:p><w:pPr><w:jc w:val=\"both\"/><w:spacing w:line=\"400\" w:lineRule=\"exact\"/>"
        f"{ind}</w:pPr>{render_runs(text, 24, superscript_refs)}</w:p>"
    )


def p_center(text: str, size: int = 24, bold: bool = False) -> str:
    bold_xml = "<w:b/>" if bold else ""
    return (
        "<w:p><w:pPr><w:jc w:val=\"center\"/><w:spacing w:line=\"360\" w:lineRule=\"auto\"/></w:pPr>"
        f"<w:r><w:rPr>{bold_xml}<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
        f"<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r></w:p>"
    )


def p_h1(text: str) -> str:
    return (
        "<w:p><w:pPr><w:pageBreakBefore/><w:jc w:val=\"center\"/></w:pPr>"
        "<w:r><w:rPr><w:b/><w:sz w:val=\"32\"/><w:szCs w:val=\"32\"/></w:rPr>"
        f"<w:t>{esc(text)}</w:t></w:r></w:p>"
    )


def p_h2(text: str) -> str:
    return (
        "<w:p><w:pPr><w:jc w:val=\"left\"/></w:pPr>"
        "<w:r><w:rPr><w:b/><w:sz w:val=\"28\"/><w:szCs w:val=\"28\"/></w:rPr>"
        f"<w:t>{esc(text)}</w:t></w:r></w:p>"
    )


def parse_fragment(xml_text: str) -> ET.Element:
    wrapper = f'<root xmlns:w="{W_NS}">{xml_text}</root>'
    return ET.fromstring(wrapper)[0]


def build_table(table_lines: list[str]) -> ET.Element:
    rows = []
    for idx, line in enumerate(table_lines):
        parts = [cell.strip() for cell in line.strip("|").split("|")]
        if idx == 1 and all(set(cell) <= {"-", " "} for cell in parts):
            continue
        rows.append(parts)

    col_count = max(len(r) for r in rows)
    grid = "".join('<w:gridCol w:w="1800"/>' for _ in range(col_count))
    tr_xml = []
    for r_idx, row in enumerate(rows):
        cells = []
        for cell in row:
            content = p_center(cell, size=22, bold=True) if r_idx == 0 else p_body(cell, indent=False)
            cells.append(
                "<w:tc><w:tcPr><w:tcW w:w=\"1800\" w:type=\"dxa\"/></w:tcPr>"
                f"{content}</w:tc>"
            )
        tr_xml.append("<w:tr>" + "".join(cells) + "</w:tr>")

    tbl_xml = (
        "<w:tbl><w:tblPr>"
        "<w:tblW w:w=\"0\" w:type=\"auto\"/>"
        "<w:tblBorders>"
        "<w:top w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:left w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:right w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "</w:tblBorders></w:tblPr>"
        f"<w:tblGrid>{grid}</w:tblGrid>{''.join(tr_xml)}</w:tbl>"
    )
    return parse_fragment(tbl_xml)


def markdown_to_blocks(text: str) -> list[ET.Element]:
    lines = text.splitlines()
    blocks: list[ET.Element] = []
    i = 0
    in_body = False

    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue

        if stripped.startswith("## 中文摘要"):
            in_body = True
            blocks.append(parse_fragment(p_h1("摘    要")))
            i += 1
            continue

        if not in_body:
            i += 1
            continue

        if stripped.startswith("## Abstract"):
            blocks.append(parse_fragment(p_h1("ABSTRACT")))
            i += 1
            continue

        if stripped.startswith("## "):
            blocks.append(parse_fragment(p_h1(stripped[3:].strip())))
            i += 1
            continue

        if stripped.startswith("### "):
            blocks.append(parse_fragment(p_h2(stripped[4:].strip())))
            i += 1
            continue

        if stripped.startswith("关键词：") or stripped.startswith("Key words:"):
            blocks.append(parse_fragment(p_body(stripped, indent=False)))
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            blocks.append(build_table(table_lines))
            continue

        blocks.append(parse_fragment(p_body(stripped, superscript_refs=True)))
        i += 1

    return blocks


def update_markdown() -> None:
    text = MD_PATH.read_text(encoding="utf-8")
    updated = re.sub(
        r"## 第二章 系统需求分析.*?## 第三章 系统总体设计",
        CHAPTER2 + "\n\n## 第三章 系统总体设计",
        text,
        flags=re.S,
    )
    MD_PATH.write_text(updated, encoding="utf-8")


def write_assets() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    (ASSET_DIR / "fig_2_2_user_usecase.spec.yaml").write_text(USER_USECASE_SPEC, encoding="utf-8")
    (ASSET_DIR / "fig_2_2_user_usecase.svg").write_text(USER_USECASE_SVG, encoding="utf-8")
    (ASSET_DIR / "fig_2_3_admin_usecase.spec.yaml").write_text(ADMIN_USECASE_SPEC, encoding="utf-8")
    (ASSET_DIR / "fig_2_3_admin_usecase.svg").write_text(ADMIN_USECASE_SVG, encoding="utf-8")


def rebuild_docx() -> None:
    md_text = MD_PATH.read_text(encoding="utf-8")
    blocks = markdown_to_blocks(md_text)

    with zipfile.ZipFile(SOURCE_DOCX, "r") as zf:
        files = {name: zf.read(name) for name in zf.namelist()}

    root = ET.fromstring(files["word/document.xml"])
    body = root.find("w:body", NS)
    if body is None:
        raise RuntimeError("源文档缺少 body 节点")

    keep_nodes: list[ET.Element] = []
    sect = body.find("w:sectPr", NS)
    for node in list(body):
        if node.tag == w_tag("sectPr"):
            continue
        text = para_text(node).replace(" ", "")
        if node.tag == w_tag("p") and "摘要" in text:
            break
        keep_nodes.append(deepcopy(node))

    for node in list(body):
        body.remove(node)
    for node in keep_nodes:
        body.append(node)
    for block in blocks:
        body.append(block)
    if sect is not None:
        body.append(sect)

    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(OUTPUT_DOCX, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)


def main() -> None:
    update_markdown()
    write_assets()
    rebuild_docx()
    print(MD_PATH)
    print(OUTPUT_DOCX)


if __name__ == "__main__":
    main()
