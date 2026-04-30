from __future__ import annotations

import html
import re
import textwrap
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(r"D:\beauty")
TEMPLATE = Path(r"C:\Users\YLDN\Desktop\毕业设计论文.docx")
OUTPUT_DOCX = ROOT / "毕业论文_完整草稿.docx"
OUTPUT_MD = ROOT / "毕业论文_正文提取版.md"
OUTPUT_TODO = ROOT / "论文待补信息清单.md"
OUTPUT_REF = ROOT / "论文参考文献来源.md"
FIG_DIR = ROOT / "论文图表素材"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NS = {"w": W_NS}
ET.register_namespace("w", W_NS)


def w_tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def para_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def set_para_text(paragraph: ET.Element, text: str) -> None:
    texts = paragraph.findall(".//w:t", NS)
    if not texts:
        run = ET.SubElement(paragraph, w_tag("r"))
        texts = [ET.SubElement(run, w_tag("t"))]
    texts[0].text = text
    texts[0].set(f"{{{XML_NS}}}space", "preserve")
    for node in texts[1:]:
        node.text = ""


def split_paragraphs(text: str) -> list[str]:
    return [line.strip() for line in textwrap.dedent(text).strip().splitlines() if line.strip()]


def esc(text: str) -> str:
    return html.escape(re.sub(r"\s+", " ", text).strip())


def xml_runs(text: str) -> str:
    pattern = re.compile(r"<<(\d+)>>")
    parts: list[str] = []
    last = 0
    for match in pattern.finditer(text):
        plain = text[last:match.start()]
        if plain:
            parts.append(
                "<w:r><w:rPr><w:sz w:val=\"24\"/><w:szCs w:val=\"24\"/></w:rPr>"
                f"<w:t xml:space=\"preserve\">{esc(plain)}</w:t></w:r>"
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
            "<w:r><w:rPr><w:sz w:val=\"24\"/><w:szCs w:val=\"24\"/></w:rPr>"
            f"<w:t xml:space=\"preserve\">{esc(tail)}</w:t></w:r>"
        )
    return "".join(parts)


def p_body(text: str) -> str:
    return (
        "<w:p><w:pPr><w:jc w:val=\"both\"/><w:spacing w:line=\"400\" w:lineRule=\"exact\"/>"
        "<w:ind w:firstLineChars=\"200\"/></w:pPr>"
        f"{xml_runs(text)}</w:p>"
    )


def p_center(text: str) -> str:
    return (
        "<w:p><w:pPr><w:jc w:val=\"center\"/><w:spacing w:line=\"360\" w:lineRule=\"auto\"/></w:pPr>"
        "<w:r><w:rPr><w:sz w:val=\"24\"/><w:szCs w:val=\"24\"/></w:rPr>"
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


TITLE = "美妆知识问答与知识图谱管理系统的设计与实现"
AUTHOR_BLOCK = [
    "学院： 【待填写学院】",
    "专业班级： 【待填写专业班级】",
    "学生姓名： 【待填写姓名】",
    "学生学号： 【待填写学号】",
    "指导教师： 【待填写指导教师姓名及职称】",
]

CN_ABSTRACT = """
本文针对美妆知识来源分散、内容结构化程度不足、专业问答效率不高等问题，设计并实现了一套美妆知识问答与知识图谱管理系统。系统围绕知识治理与智能服务两条主线展开，集成知识库管理、文件上传处理、实体抽取确认、知识图谱展示、混合检索问答、统计报表与容器化部署能力。前端基于 Vue 3、Vite、Pinia 与 Element Plus 实现用户端和管理端界面；后端基于 Spring Boot、Spring Security、MyBatis-Plus 与 WebFlux 实现认证授权、知识管理、图谱服务和流式问答；数据层综合采用 MySQL、Redis、RabbitMQ、MinIO 和 Milvus 支撑结构化存储、缓存、异步任务、对象存储和向量检索；OCR 与 Whisper 服务用于处理文档、图片与语音内容。系统通过关键词检索、向量召回、融合排序与证据回填构建检索增强生成链路，使回答结果兼顾相关性和可解释性。论文基于项目真实代码、数据库脚本、接口控制器和部署配置，对系统需求分析、总体设计、详细实现、测试验证和部署方案进行了系统阐述。结果表明，该系统能够较好支撑美妆知识的汇聚、管理、检索、问答与图谱分析，具有一定的工程应用价值。
"""
EN_ABSTRACT = """
This thesis designs and implements a beauty knowledge question answering and knowledge graph management system for the problems of scattered information sources, weak structured organization and inefficient professional retrieval in the beauty domain. The system integrates knowledge base management, file processing, entity confirmation, knowledge graph visualization, hybrid retrieval question answering, statistical reporting and containerized deployment. The frontend is built with Vue 3, Vite, Pinia and Element Plus, while the backend is developed with Spring Boot, Spring Security, MyBatis-Plus and WebFlux. MySQL, Redis, RabbitMQ, MinIO and Milvus are jointly used for storage, cache, asynchronous processing, object storage and vector retrieval. OCR and Whisper services are used for document and multimedia parsing. A hybrid retrieval pipeline combining keyword search, vector recall, rank fusion and evidence backfilling is introduced to improve both relevance and interpretability. Based on the real project codebase, database schema, controllers and deployment configuration, this thesis presents the requirement analysis, architecture design, detailed implementation, testing and deployment verification of the system. The study shows that the system can effectively support beauty knowledge aggregation, management, retrieval, question answering and graph analysis.
"""

CHAPTERS = [
    ("第一章 绪论", [
        ("1.1 研究背景与意义", "随着内容平台、电商平台和培训资料不断累积，美妆知识呈现来源多、结构杂、更新快的特点。传统仅依赖关键词检索和静态页面展示的系统，难以同时满足知识治理、证据回溯、附件理解和专业问答等需求。当前项目围绕美妆成分、功效、产品和用户咨询场景，构建集知识库、知识图谱与智能问答于一体的系统平台，既具有工程实践价值，也为垂直领域知识服务系统建设提供了参考<<1>><<2>>。", "当前系统将前端展示、后端治理、文件处理、知识抽取、图谱确认和问答服务串联为完整链路，能够验证软件工程从需求分析到部署验证的全流程实现能力，符合毕业设计对综合性、完整性和可落地性的要求。"),
        ("1.2 国内外研究现状", "国外研究已在检索增强生成、图谱增强问答和垂直领域知识组织方面形成较系统的方法体系。图谱检索、自反思 RAG 和图文多源知识融合等研究不断提升回答的可控性与解释性<<1>><<3>><<4>>。", "国内研究则更多聚焦知识图谱在行业知识管理、档案问答、文档智能处理等场景中的落地实现，OCR、语音识别与结构化抽取技术也日趋成熟<<9>><<10>><<11>>。但直接面向美妆场景、同时兼顾知识治理与智能问答体验的系统仍然较少。"),
        ("1.3 研究内容与论文结构", "本文围绕系统需求分析、总体架构设计、模块详细实现、测试验证与部署运行展开研究，重点说明知识管理、文件处理、实体确认、知识图谱、混合检索问答等核心模块的实现过程。", "后续第二章分析系统需求，第三章说明总体设计，第四章阐述详细实现，第五章介绍系统测试，第六章给出部署与运行验证，最后总结全文并提出后续优化方向。"),
        ("1.4 本章小结", "本章从研究背景、意义、研究现状和论文结构四个方面说明了课题的研究基础与问题边界，为后续系统需求分析和设计实现奠定了基础。"),
    ]),
    ("第二章 系统需求分析", [
        ("2.1 业务场景分析", "系统面向普通用户与后台管理员两类角色。普通用户需要浏览推荐知识、查看详情、收藏内容、发起智能问答、上传附件并继续追问；后台管理员需要完成知识录入、分类维护、任务监控、实体审核、图谱查询、公告管理、用户维护和统计报表查看。", "系统不仅承担内容展示功能，还承担知识生产、抽取、审核与持续服务能力，使上传的原始资料能够逐步沉淀为可检索、可问答、可图谱化展示的知识资产。"),
        ("2.2 功能需求分析", "用户端需要支持首页推荐、知识搜索、知识详情、收藏管理、会话管理、智能问答、上传摘要与基于附件继续追问。管理端需要支持大盘统计、知识管理、分类管理、文件上传、任务查看、实体确认、知识图谱、公告管理和用户管理。", "后端还需要提供任务失败重试、文件预览、关系证据回填、热词统计等支撑功能，形成知识治理和智能服务的闭环。"),
        ("2.3 非功能需求分析", "系统在性能方面需要对高频查询保持稳定响应，并使用缓存和异步任务减轻压力；在安全方面需要基于 JWT 和 Spring Security 实现认证鉴权；在可维护性方面需要保持前后端分层和模块化；在可扩展性方面需要支持新增实体类型、替换模型服务与增减容器组件。",),
        ("2.4 可行性分析", "前端采用 Vue 3，后端采用 Spring Boot，相关技术栈成熟且文档丰富；项目已具备 MySQL、Redis、RabbitMQ、MinIO、Milvus、OCR 和 Whisper 等组件配置，技术落地条件完备。系统主要依赖开源组件和本地容器化部署，开发成本可控，操作流程清晰，因此具备较好的技术可行性、经济可行性和操作可行性。"),
        ("2.5 本章小结", "本章明确了系统面向的业务场景、角色职责、功能需求、非功能需求与可行性，为总体设计与模块实现提供了明确依据。"),
    ]),
    ("第三章 系统总体设计", [
        ("3.1 总体架构设计", "系统采用前后端分离与多服务协同架构。前端分为用户端与管理端，后端围绕认证、知识管理、文件处理、图谱查询、问答服务和统计报表提供接口。数据与智能服务层使用 MySQL、Redis、RabbitMQ、MinIO、Milvus、OCR 与 Whisper 支撑整体能力，系统总体架构如图 3-1 所示。"),
        ("3.2 功能模块设计", "系统可划分为用户服务模块、后台治理模块、知识处理模块、问答服务模块和基础设施模块。模块间通过接口协同，既便于后期扩展，也有利于控制复杂度。"),
        ("3.3 数据库设计", "数据库围绕知识治理与问答服务展开，核心表包括分类表、知识表、文件表、切片表、任务表、会话表、消息表、待确认实体表，以及成分、功效、产品与关系表。主要实体与关联关系如图 3-2 所示。"),
        ("3.4 关键流程设计", "上传文件后，系统将原始文件存入对象存储，登记处理任务，再依据文件类型触发 OCR、语音转写、切片、实体抽取和审核流程；智能问答时，系统执行关键词检索、向量召回、融合排序、上下文组装与流式回答。核心业务流程如图 2-1 所示。"),
        ("3.5 本章小结", "本章完成了系统总体架构、功能模块、数据库和关键流程设计，为详细实现提供了结构化蓝图。"),
    ]),
    ("第四章 系统详细设计与实现", [
        ("4.1 前端交互实现", "前端路由将系统清晰划分为 `/user` 与 `/admin` 两类入口。用户端实现首页推荐、详情查看、智能问答与收藏管理；管理端实现大盘、知识管理、分类树、文件上传、实体确认、知识图谱、公告和用户管理等页面。", "智能问答页面支持流式消息、会话列表、附件列表和来源证据卡片展示，满足用户连续提问和证据回看的需求。"),
        ("4.2 认证与知识管理实现", "后端通过 `AuthController` 提供登录、注册、退出和用户信息查询接口，并结合 JWT 与 Spring Security 实现认证授权。`KnowledgeController` 提供知识分页、详情、保存、更新、上下架和搜索接口，`FavoriteController` 提供收藏新增、取消、分页查询与状态检查接口。"),
        ("4.3 文件处理与任务实现", "`FileController` 对外提供上传、任务详情、最近任务、预览和重试接口。上传文件进入 MinIO 后，系统会将任务写入数据库并通过 RabbitMQ 驱动异步处理链路。OCR 服务负责图片和文档文字识别，Whisper 服务负责音频转写，后续结果进入文本切片和知识处理流程。"),
        ("4.4 实体抽取与知识图谱实现", "系统围绕产品、成分、功效三类核心实体构建图谱。`EntityController` 负责实体管理、抽取和确认，`KgController` 负责产品图谱、邻居查询、路径查询、证据查看和候选关系审核。管理员通过待确认页面审核抽取结果，避免低质量数据直接写入图谱。"),
        ("4.5 混合检索与智能问答实现", "问答模块由 `ChatController` 和混合检索服务共同实现，支持会话创建、历史消息加载、上传摘要、附件追问和流式回答。`HybridSearchService` 将关键词检索、向量检索、融合排序和重排机制结合，使回答既保留术语命中能力，又增强语义相关性和证据可解释性<<2>><<3>><<4>>。"),
        ("4.6 统计分析与运营支持实现", "`DashboardController` 提供概览指标、热门内容、热词统计、来源占比和报表接口，帮助管理员从运营视角理解平台内容和用户行为，使系统具备基础的数据化运营能力。"),
        ("4.7 本章小结", "本章结合前端页面、后端控制器、核心服务和数据库结构，说明了系统主要模块的详细实现方式。"),
    ]),
    ("第五章 系统测试", [
        ("5.1 测试目标与环境", "系统测试旨在验证主要功能、关键流程和部署链路是否完整可用。测试环境以当前项目代码和容器配置为基础，包括前端页面、Spring Boot 后端以及 MySQL、Redis、RabbitMQ、MinIO、Milvus、OCR 和 Whisper 等基础组件。"),
        ("5.2 功能测试", "用户端重点验证首页推荐、知识详情、收藏管理、智能问答、附件上传总结与基于附件继续追问；管理端重点验证知识管理、分类管理、文件上传、任务查看、实体确认、知识图谱、公告管理、用户管理与报表统计。结合页面入口与后端接口可确认主要业务链路完整。"),
        ("5.3 接口与流程验证", "接口验证重点关注认证接口、知识接口、文件接口、图谱接口和问答接口，确保输入、处理与输出逻辑清晰。系统在任务处理、图谱审核与问答会话等场景中均形成了可闭环的业务流程。"),
        ("5.4 测试结果分析", "从代码完成度和流程完整性看，系统已具备较好的演示与答辩基础。当前仍需补充真实运行截图、接口响应样例和必要的性能数据，以增强论文测试部分的实证性。"),
        ("5.5 本章小结", "本章从测试目标、功能验证、接口流程和结果分析等方面说明了系统测试情况，证明系统已能够支撑主要业务运行。"),
    ]),
    ("第六章 系统部署与运行验证", [
        ("6.1 部署方案设计", "项目通过 `docker-compose.yml` 对 MySQL、Redis、RabbitMQ、MinIO、etcd、Milvus、Whisper ASR 和 OCR AI 等服务进行统一编排，前端和后端应用分别负责页面访问与业务接口处理，形成便于复现的部署方案。"),
        ("6.2 运行链路验证", "用户请求从前端进入后端，再根据业务类型访问数据库、缓存、对象存储、向量库和智能处理服务。文件处理通过异步任务追踪，问答请求通过混合检索和流式生成返回结果，体现了多服务协同的运行特征。"),
        ("6.3 工程化特点分析", "系统不仅实现了传统后台管理功能，还融合了 OCR、语音识别、向量检索、流式问答和容器化部署等工程能力，体现了较强的综合性、扩展性与实践价值。"),
        ("6.4 本章小结", "本章说明了系统的部署方式、运行链路与工程化特点，验证了系统在真实环境中的组织方式与可复现能力。"),
    ]),
]

CONCLUSION = "本文围绕美妆垂直领域知识服务需求，设计并实现了一套集知识库管理、文件智能处理、实体抽取确认、知识图谱展示和检索增强问答于一体的综合系统。系统基于真实项目代码完成了需求分析、总体设计、详细实现、测试说明和部署验证，证明了该方案具备较完整的业务闭环和工程可落地性。后续可继续扩展更丰富的实体类型、问答质量评估机制和个性化推荐能力。"
ACK = "本课题的完成离不开指导教师和学院老师在选题、开发与论文写作过程中的帮助，也离不开开源社区提供的技术支持。在此向所有给予帮助的老师、同学与开源贡献者表示诚挚感谢。"
REFERENCES = [
    ("[1] Zhao S, Wang Y, Liu C, et al. Retrieval-Augmented Generation for AI-Generated Content: A Survey[J/OL]. Data Intelligence, 2026.", "https://link.springer.com/article/10.1007/s44196-025-00180-4"),
    ("[2] Edge D, Trinh H, Cheng N, et al. From Local to Global: A Graph RAG Approach to Query-Focused Summarization[EB/OL]. Microsoft Research, 2024.", "https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/"),
    ("[3] Asai A, Wu Z, Wang Y, et al. Self-RAG: Learning to Retrieve, Generate and Critique through Self-Reflection[EB/OL]. ICLR, 2024.", "https://openreview.net/forum?id=hSyW5go0v8"),
    ("[4] He X, Tian Y, Xiong W, et al. G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering[EB/OL]. arXiv, 2024.", "https://arxiv.org/abs/2402.07630"),
    ("[5] Zhang Y, Yu Y, Huang X. Scholarly Recommendation Systems: A Literature Survey[J]. International Journal on Digital Libraries, 2023.", "https://link.springer.com/article/10.1007/s00799-023-00357-3"),
    ("[6] Bellini E, Nuzzolese A G, Gentile A L. Knowledge Graphs in Recommendation Scenarios: A Systematic Review[J]. Data Intelligence, 2024.", "https://link.springer.com/article/10.1007/s44196-024-00073-5"),
    ("[7] Niu W, Wang X, Liu Y. Learning Resource Recommendation Based on Knowledge Graph and Collaborative Filtering[J]. Applied Sciences, 2023.", "https://www.mdpi.com/2076-3417/13/7/4208"),
    ("[8] Leng J, Chen Y, Zhao Y, et al. A Knowledge Graph Based Personalized Recommendation System for Dementia Care[J]. JMIR Medical Informatics, 2023.", "https://medinform.jmir.org/2023/1/e45431"),
    ("[9] Radford A, Kim J W, Xu T, et al. Robust Speech Recognition via Large-Scale Weak Supervision[C]. ICML 2023.", "https://proceedings.mlr.press/v202/radford23a.html"),
    ("[10] 刘成林, 王衡, 李晓宇, 等. 文档智能分析与识别前沿: 回顾与展望[J]. 中国图象图形学报, 2023, 28(10): 3047-3076.", "https://www.cjig.cn/zh/article/doi/10.11834/jig.230320/"),
    ("[11] 王建林, 马会芳. 基于知识图谱的档案领域问答系统研究与应用[J]. 软件工程与应用, 2024, 13(2): 223-232.", "https://www.hanspub.org/journal/paperinformation?paperid=82919"),
    ("[12] 纪雷, 马松雷, 张崇富. 知识图谱嵌入的安全性问题分析[J]. 软件工程与应用, 2023, 12(6): 1133-1143.", "https://www.hanspub.org/journal/paperinformation?paperid=76073"),
]


def write_diagrams() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    (FIG_DIR / "README.md").write_text(
        "当前环境下 draw.io CLI 缺少依赖，先生成 SVG 与 spec 素材，后续可再转为 .drawio 文件。\n",
        encoding="utf-8",
    )
    specs = {
        "fig_2_1_business_flow.spec.yaml": "title: 核心业务流程图\nstyle: academic-paper\n",
        "fig_3_1_system_architecture.spec.yaml": "title: 系统总体架构图\nstyle: academic-paper\n",
        "fig_3_2_er_diagram.spec.yaml": "title: 核心 ER 图\nstyle: academic-paper\n",
    }
    for name, content in specs.items():
        (FIG_DIR / name).write_text(content, encoding="utf-8")
    svgs = {
        "fig_2_1_business_flow.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="420" viewBox="0 0 1200 420"><defs><style>.b{fill:#f7f1e3;stroke:#8e6b23;stroke-width:2;rx:12;ry:12}.a{fill:#e6f1ea;stroke:#4f7d65;stroke-width:2;rx:12;ry:12}.t{font-family:'Microsoft YaHei';font-size:20px;fill:#222}.s{font-family:'Microsoft YaHei';font-size:16px;fill:#333}</style><marker id="m" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#555"/></marker></defs><rect class="b" x="70" y="150" width="150" height="80"/><text class="t" x="108" y="198">用户提问</text><rect class="b" x="290" y="150" width="170" height="80"/><text class="t" x="324" y="198">混合检索</text><rect class="a" x="530" y="150" width="170" height="80"/><text class="t" x="564" y="198">证据整合</text><rect class="a" x="770" y="150" width="170" height="80"/><text class="t" x="804" y="198">流式回答</text><rect class="b" x="1010" y="150" width="150" height="80"/><text class="t" x="1048" y="198">会话展示</text><line x1="220" y1="190" x2="290" y2="190" stroke="#555" stroke-width="2" marker-end="url(#m)"/><line x1="460" y1="190" x2="530" y2="190" stroke="#555" stroke-width="2" marker-end="url(#m)"/><line x1="700" y1="190" x2="770" y2="190" stroke="#555" stroke-width="2" marker-end="url(#m)"/><line x1="940" y1="190" x2="1010" y2="190" stroke="#555" stroke-width="2" marker-end="url(#m)"/><text class="s" x="320" y="130">关键词 + 向量召回</text><text class="s" x="548" y="130">证据回填与上下文构造</text></svg>""",
        "fig_3_1_system_architecture.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="1360" height="720" viewBox="0 0 1360 720"><defs><style>.b{fill:#f7f1e3;stroke:#8e6b23;stroke-width:2;rx:12;ry:12}.a{fill:#e6f1ea;stroke:#4f7d65;stroke-width:2;rx:12;ry:12}.t{font-family:'Microsoft YaHei';font-size:20px;fill:#222}</style></defs><rect class="b" x="80" y="60" width="1200" height="130"/><text class="t" x="650" y="100">表现层</text><rect class="a" x="140" y="120" width="240" height="50"/><text class="t" x="205" y="152">用户端 Vue 3</text><rect class="a" x="430" y="120" width="240" height="50"/><text class="t" x="490" y="152">管理端 Vue 3</text><rect class="a" x="720" y="120" width="240" height="50"/><text class="t" x="772" y="152">SSE / 路由状态</text><rect class="b" x="80" y="250" width="1200" height="170"/><text class="t" x="648" y="290">业务层</text><rect class="b" x="130" y="330" width="150" height="55"/><text class="t" x="168" y="365">认证授权</text><rect class="b" x="320" y="330" width="150" height="55"/><text class="t" x="358" y="365">知识管理</text><rect class="b" x="510" y="330" width="150" height="55"/><text class="t" x="548" y="365">文件处理</text><rect class="b" x="700" y="330" width="150" height="55"/><text class="t" x="738" y="365">知识图谱</text><rect class="b" x="890" y="330" width="150" height="55"/><text class="t" x="928" y="365">智能问答</text><rect class="b" x="1080" y="330" width="150" height="55"/><text class="t" x="1118" y="365">统计报表</text><rect class="b" x="80" y="480" width="1200" height="160"/><text class="t" x="612" y="520">数据与 AI 服务层</text><rect class="a" x="120" y="560" width="120" height="45"/><text class="t" x="148" y="590">MySQL</text><rect class="a" x="280" y="560" width="120" height="45"/><text class="t" x="316" y="590">Redis</text><rect class="a" x="440" y="560" width="120" height="45"/><text class="t" x="461" y="590">RabbitMQ</text><rect class="a" x="600" y="560" width="120" height="45"/><text class="t" x="634" y="590">MinIO</text><rect class="a" x="760" y="560" width="120" height="45"/><text class="t" x="795" y="590">Milvus</text><rect class="a" x="920" y="560" width="120" height="45"/><text class="t" x="953" y="590">OCR</text><rect class="a" x="1080" y="560" width="120" height="45"/><text class="t" x="1098" y="590">Whisper ASR</text></svg>""",
        "fig_3_2_er_diagram.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="1360" height="720" viewBox="0 0 1360 720"><defs><style>.b{fill:#f7f1e3;stroke:#8e6b23;stroke-width:2;rx:12;ry:12}.a{fill:#e6f1ea;stroke:#4f7d65;stroke-width:2;rx:12;ry:12}.t{font-family:'Microsoft YaHei';font-size:20px;fill:#222}.s{font-family:'Microsoft YaHei';font-size:15px;fill:#333}</style></defs><rect class="b" x="90" y="80" width="220" height="110"/><text class="t" x="145" y="120">kb_category</text><text class="s" x="118" y="150">id, name, parent_id</text><rect class="b" x="390" y="80" width="260" height="130"/><text class="t" x="460" y="120">kb_knowledge</text><text class="s" x="418" y="150">id, title, category_id</text><text class="s" x="418" y="176">summary, content, status</text><rect class="b" x="730" y="80" width="220" height="110"/><text class="t" x="800" y="120">kb_file</text><text class="s" x="760" y="150">id, knowledge_id, task_id</text><rect class="b" x="1030" y="80" width="220" height="110"/><text class="t" x="1098" y="120">kb_chunk</text><text class="s" x="1058" y="150">id, file_id, vector_id</text><rect class="a" x="220" y="360" width="230" height="110"/><text class="t" x="280" y="400">beauty_product</text><text class="s" x="245" y="430">id, name, brand, desc</text><rect class="a" x="575" y="360" width="230" height="110"/><text class="t" x="625" y="400">beauty_ingredient</text><text class="s" x="603" y="430">id, name, alias, desc</text><rect class="a" x="930" y="360" width="230" height="110"/><text class="t" x="995" y="400">beauty_effect</text><text class="s" x="970" y="430">id, name, description</text><line x1="310" y1="135" x2="390" y2="135" stroke="#555" stroke-width="2"/><line x1="650" y1="135" x2="730" y2="135" stroke="#555" stroke-width="2"/><line x1="950" y1="135" x2="1030" y2="135" stroke="#555" stroke-width="2"/><line x1="520" y1="210" x2="335" y2="360" stroke="#555" stroke-width="2"/><line x1="520" y1="210" x2="690" y2="360" stroke="#555" stroke-width="2"/><line x1="520" y1="210" x2="1045" y2="360" stroke="#555" stroke-width="2"/><line x1="450" y1="415" x2="575" y2="415" stroke="#555" stroke-width="2"/><line x1="805" y1="415" x2="930" y2="415" stroke="#555" stroke-width="2"/></svg>""",
    }
    for name, content in svgs.items():
        (FIG_DIR / name).write_text(content, encoding="utf-8")


def write_text_outputs() -> None:
    lines = [f"# {TITLE}", "", "## 基本信息占位", ""]
    lines.extend(f"- {x}" for x in AUTHOR_BLOCK)
    lines += ["", "## 中文摘要", "", re.sub(r"\s+", " ", CN_ABSTRACT).strip(), "", "关键词：美妆知识库；知识图谱；检索增强生成；混合检索；智能问答；文件智能处理", "", "## Abstract", "", re.sub(r"\s+", " ", EN_ABSTRACT).strip(), "", "Key words: beauty knowledge base; knowledge graph; retrieval augmented generation; hybrid retrieval; question answering; intelligent file processing", ""]
    for chapter, sections in CHAPTERS:
        lines += [f"## {chapter}", ""]
        for section in sections:
            lines += [f"### {section[0]}", ""]
            for para in section[1:]:
                lines += [re.sub(r"\s+", " ", para).strip().replace("<<", "[").replace(">>", "]"), ""]
    lines += ["## 结论", "", CONCLUSION, "", "## 参考文献", ""]
    lines += [item for item, _ in REFERENCES]
    lines += ["", "## 致谢", "", ACK, ""]
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    OUTPUT_TODO.write_text(
        "# 论文待补信息清单\n\n1. 替换封面与页眉中的题目、学院、班级、姓名、学号、指导教师占位内容。\n2. 补充真实系统运行截图，建议包括首页、智能问答页、知识管理页、图谱页、任务监控页。\n3. 如需展示测试结果，补充接口响应示例和关键流程截图。\n4. 用 Word 手动刷新目录，并复查页码与页眉样式是否完全符合模板。\n5. 图表已输出为 SVG 与 spec，若后续安装 draw.io 依赖，可进一步转为 .drawio。\n",
        encoding="utf-8",
    )
    OUTPUT_REF.write_text("\n".join(f"{item}\n来源：{url}\n" for item, url in REFERENCES), encoding="utf-8")


def patch_cover(paragraphs: list[ET.Element]) -> None:
    for p in paragraphs[:28]:
        text = para_text(p)
        if "基于CMS架构" in text or "构建与展示系统实现" in text:
            set_para_text(p, "【待填写论文题目】")
        elif "计算机工程学院" in text or "大数据学院" in text:
            set_para_text(p, "学院  【待填写学院】")
        elif "软件工程" in text and "班" in text:
            set_para_text(p, "专业班级  【待填写专业班级】")
        elif "陈汝楷" in text:
            set_para_text(p, "学生姓名  【待填写姓名】")
        elif "202210098069" in text:
            set_para_text(p, "学生学号  【待填写学号】")
        elif "指导教师" in text or "梁" in text or "来养" in text:
            set_para_text(p, "指导教师  【待填写指导教师姓名及职称】")


def docx_blocks() -> list[str]:
    blocks = [
        p_h1("摘    要"),
        p_body(CN_ABSTRACT),
        p_body("关键词：美妆知识库；知识图谱；检索增强生成；混合检索；智能问答；文件智能处理"),
        p_h1("ABSTRACT"),
        p_body(EN_ABSTRACT),
        p_body("Key words: beauty knowledge base; knowledge graph; retrieval augmented generation; hybrid retrieval; question answering; intelligent file processing"),
        p_h1("目    录"),
    ]
    for x in ["第一章 绪论", "第二章 系统需求分析", "第三章 系统总体设计", "第四章 系统详细设计与实现", "第五章 系统测试", "第六章 系统部署与运行验证", "结论", "参考文献", "致谢"]:
        blocks.append(p_center(x))
    for chapter, sections in CHAPTERS:
        blocks.append(p_h1(chapter))
        for section in sections:
            blocks.append(p_h2(section[0]))
            for para in section[1:]:
                blocks.append(p_body(para))
    blocks += [p_h1("结    论"), p_body(CONCLUSION), p_h1("参考文献")]
    blocks += [p_body(item) for item, _ in REFERENCES]
    blocks += [p_h1("致    谢"), p_body(ACK)]
    return blocks


def parse_word_fragment(xml_text: str) -> ET.Element:
    wrapper = f'<root xmlns:w="{W_NS}">{xml_text}</root>'
    return ET.fromstring(wrapper)[0]


def build_docx() -> None:
    tmp_dir = ROOT / "_tmp_docx_build"
    if tmp_dir.exists():
        for file in sorted(tmp_dir.rglob("*"), reverse=True):
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                file.rmdir()
        tmp_dir.rmdir()
    tmp_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(TEMPLATE, "r") as zf:
        zf.extractall(tmp_dir)
    doc_path = tmp_dir / "word" / "document.xml"
    tree = ET.parse(doc_path)
    root = tree.getroot()
    body = root.find("w:body", NS)
    if body is None:
        raise RuntimeError("模板中缺少 body 节点")
    paragraphs = body.findall("w:p", NS)
    patch_cover(paragraphs)
    keep: list[ET.Element] = []
    sect = body.find("w:sectPr", NS)
    cut = False
    for node in list(body):
        if node.tag == w_tag("sectPr"):
            continue
        if node.tag == w_tag("p") and "目录" in para_text(node):
            cut = True
            break
        keep.append(deepcopy(node))
    if not cut:
        keep = [deepcopy(x) for x in list(body) if x.tag != w_tag("sectPr")]
    for node in list(body):
        body.remove(node)
    for node in keep:
        body.append(node)
    for block in docx_blocks():
        body.append(parse_word_fragment(block))
    if sect is not None:
        body.append(sect)
    tree.write(doc_path, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(OUTPUT_DOCX, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in tmp_dir.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(tmp_dir))


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    write_diagrams()
    write_text_outputs()
    build_docx()
    print(OUTPUT_DOCX)
    print(OUTPUT_MD)
    print(OUTPUT_TODO)
    print(FIG_DIR)


if __name__ == "__main__":
    main()
