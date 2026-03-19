from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(r"C:\Users\YLDN\Desktop\beauty")
OUT_DIR = ROOT / "docs" / "generated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PPTX_PATH = OUT_DIR / "beauty-defense-refined.pptx"
MD_PATH = OUT_DIR / "beauty-defense-refined-notes.md"

SLIDES = [
    {
        "title": "AI美业知识台",
        "subtitle": "基于CMS架构的“美业多媒体知识库”构建与展示系统实现",
        "bullets": [
            "项目定位：面向美业门店培训、知识沉淀与智能问答的垂直知识平台",
            "答辩重点：为什么做、怎么做、做成了什么、还有哪些提升空间"
        ],
        "highlight_title": "答辩建议",
        "highlight_body": "封面页口播控制在 15 秒内，先报题目，再说明系统定位与汇报结构。"
    },
    {
        "title": "研究背景与目标",
        "subtitle": "从行业痛点出发，构建可管理、可检索、可追溯的知识系统",
        "bullets": [
            "美业知识分散在产品手册、培训文档、护理SOP与经验口述中，难以形成统一资产",
            "传统CMS偏重内容录入与展示，缺少语义检索与专业问答能力",
            "大模型具备生成能力，但需要私有知识库约束，避免知识滞后与幻觉",
            "本课题目标是打通“知识管理 + 异步处理 + RAG问答 + 来源展示”的完整闭环"
        ],
        "highlight_title": "一句话概括",
        "highlight_body": "这不是单纯的聊天系统，而是一个围绕美业知识资产构建的专业辅助平台。"
    },
    {
        "title": "系统角色与业务场景",
        "subtitle": "围绕管理员维护知识、普通用户使用知识两条主线展开",
        "bullets": [
            "管理员端：公告管理、知识列表、分类树、文件上传、任务监控、实体确认、用户管理",
            "普通用户端：首页推荐、知识详情、我的收藏、智能问答、来源查看",
            "典型场景一：门店培训人员上传护理资料，系统自动处理并纳入知识库",
            "典型场景二：门店员工查询成分、护理问题或产品信息，快速获得有来源的回答"
        ],
        "highlight_title": "业务价值",
        "highlight_body": "实现从“知识录入”到“知识消费”的完整使用路径，更贴近真实应用而非单点演示。"
    },
    {
        "title": "总体架构与技术选型",
        "subtitle": "前后端分离 + 模块化单体 + 本地大模型 / RAG",
        "bullets": [
            "前端：Vue 3 + Vite + Element Plus，负责管理员与普通用户两套界面",
            "后端：Spring Boot 3 + Spring Security + JWT + MyBatis-Plus，负责核心业务逻辑与权限控制",
            "中间件：MySQL、Redis、RabbitMQ、MinIO、Milvus，分别承担结构化存储、缓存、异步队列、文件存储与向量检索",
            "AI能力：本地 Ollama 模型接入，配合混合检索实现 RAG 智能问答"
        ],
        "highlight_title": "架构特点",
        "highlight_body": "兼顾工程可实现性与系统完整度，既能演示，又具备一定扩展基础。"
    },
    {
        "title": "核心业务流程",
        "subtitle": "知识入库链路与问答链路共同构成系统核心闭环",
        "bullets": [
            "知识入库：文件上传 -> MinIO存储 -> RabbitMQ入队 -> 文本提取/分块 -> 向量化 -> 状态回写",
            "任务处理：管理员可在任务监控中查看处理状态，对失败任务进行重试",
            "智能问答：用户提问 -> 混合检索（BM25 + 向量）-> 上下文组装 -> 大模型生成回答",
            "结果展示：问答内容与来源同时返回，提升回答的专业性与可解释性"
        ],
        "highlight_title": "核心亮点",
        "highlight_body": "系统不是“只会答”，而是“能基于知识库回答，并给出依据”。"
    },
    {
        "title": "系统实现效果",
        "subtitle": "管理员端与普通用户端均已形成可演示页面与主流程",
        "bullets": [
            "管理员端已实现知识新增、状态管理、文件上传、任务监控、公告管理、实体确认与用户管理",
            "普通用户端已实现首页推荐、知识详情、收藏分页、问答助手与来源跳转",
            "登录后支持按角色分流：管理员进入后台，普通用户进入首页",
            "当前版本已能够支撑中期检查与毕业答辩中的系统操作演示"
        ],
        "highlight_title": "建议展示顺序",
        "highlight_body": "登录 -> 管理员新增知识/上传文件 -> 查看任务 -> 切换普通用户 -> 浏览推荐 -> 发起提问。"
    },
    {
        "title": "项目特色与阶段成果",
        "subtitle": "围绕垂直知识管理、异步处理和问答可信性做了重点建设",
        "bullets": [
            "特色一：将 CMS 内容管理与 RAG 问答结合，聚焦美业垂直场景而非通用问答",
            "特色二：采用异步任务链路，支持状态跟踪、失败重试和处理结果回写",
            "特色三：围绕“成分—功效—产品”建立基础结构化关系，为后续知识图谱扩展做准备",
            "阶段成果：系统主流程已打通，前后端页面已完成主要联调，并补充了中文业务数据"
        ],
        "highlight_title": "当前完成度",
        "highlight_body": "已从“方案设计”进入“系统完善与答辩收尾”阶段，核心闭环已经形成。"
    },
    {
        "title": "不足、优化方向与总结",
        "subtitle": "诚实说明边界，同时体现项目后续可扩展性",
        "bullets": [
            "当前不足：统计报表仍可继续丰富，知识图谱可视化和更系统的测试评估尚未完全完成",
            "交互层面：管理端和用户端视觉表现还有继续打磨空间",
            "后续方向：完善测试与性能分析、补充论文正文、整理最终答辩材料与部署说明",
            "总结：本项目已完成知识管理、异步处理、RAG问答与前后端联动的主要实现，具备较好的工程展示价值"
        ],
        "highlight_title": "结尾表述",
        "highlight_body": "课题已完成核心目标，后续重点是细节打磨、测试评估与论文完善。"
    },
]


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def para(text: str, size: int, bullet: bool = False) -> str:
    bullet_xml = '<a:buChar char="•"/>' if bullet else ""
    return f"""
    <a:p>
      <a:pPr lvl="0" marL="342900" indent="-171450">{bullet_xml}</a:pPr>
      <a:r>
        <a:rPr lang="zh-CN" sz="{size}" dirty="0"/>
        <a:t>{esc(text)}</a:t>
      </a:r>
    </a:p>
    """


def shape_text(x: int, y: int, cx: int, cy: int, paragraphs: str, shape_id: int, name: str) -> str:
    return f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="{name}"/>
        <p:cNvSpPr/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm>
          <a:off x="{x}" y="{y}"/>
          <a:ext cx="{cx}" cy="{cy}"/>
        </a:xfrm>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" lIns="91440" tIns="45720" rIns="91440" bIns="45720"/>
        <a:lstStyle/>
        {paragraphs}
      </p:txBody>
    </p:sp>
    """


def rect(x: int, y: int, cx: int, cy: int, shape_id: int, name: str, fill: str, line: str | None = None) -> str:
    line_xml = f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>' if line else '<a:ln><a:noFill/></a:ln>'
    return f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="{name}"/>
        <p:cNvSpPr/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm>
          <a:off x="{x}" y="{y}"/>
          <a:ext cx="{cx}" cy="{cy}"/>
        </a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>
        {line_xml}
      </p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
    </p:sp>
    """


def slide_xml(slide: dict, idx: int) -> str:
    title_paras = para(slide["title"], 2800)
    subtitle_paras = para(slide["subtitle"], 1700)
    bullet_paras = "".join(para(item, 1900, bullet=True) for item in slide["bullets"])
    hi_title = para(slide["highlight_title"], 1800)
    hi_body = para(slide["highlight_body"], 1600)
    footer = para(f"AI美业知识台 | 毕业答辩汇报 | 第 {idx} 页", 1200)

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      {rect(0, 0, 12192000, 6858000, 2, "Background", "FFFDF8")}
      {rect(0, 0, 12192000, 685800, 3, "TopBar", "0F766E")}
      {rect(0, 6202680, 12192000, 655320, 4, "FooterBar", "143D38")}
      {rect(457200, 1066800, 7620000, 3924300, 5, "MainCard", "FFFFFF", "D8E7E3")}
      {rect(8382000, 1066800, 2895600, 3924300, 6, "SideCard", "F0F8F6", "B7D8D2")}
      {shape_text(640080, 182880, 7315200, 411480, title_paras, 7, "Title")}
      {shape_text(640080, 655320, 7620000, 274320, subtitle_paras, 8, "Subtitle")}
      {shape_text(640080, 1244600, 7200000, 3500000, bullet_paras, 9, "Bullets")}
      {shape_text(8560000, 1260000, 2500000, 500000, hi_title, 10, "HighlightTitle")}
      {shape_text(8560000, 1750000, 2400000, 2500000, hi_body, 11, "HighlightBody")}
      {shape_text(457200, 6290000, 3200000, 180000, footer, 12, "FooterText")}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>
"""


def slide_rel() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>
"""


def write_pptx() -> None:
    timestamp = datetime.now(timezone(timedelta(hours=8))).isoformat()
    slide_entries = []
    slide_rels = []
    slide_ids = []
    presentation_rels = []
    for i, slide in enumerate(SLIDES, start=1):
        slide_entries.append((f"ppt/slides/slide{i}.xml", slide_xml(slide, i)))
        slide_rels.append((f"ppt/slides/_rels/slide{i}.xml.rels", slide_rel()))
        slide_ids.append(f'<p:sldId id="{255+i}" r:id="rId{i+1}"/>')
        presentation_rels.append(
            f'<Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        )

    content_types = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>
  <Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>
  <Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {''.join(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, len(SLIDES)+1))}
</Types>
"""

    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""

    app_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Office PowerPoint</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
  <Slides>{len(SLIDES)}</Slides>
  <Notes>0</Notes>
  <HiddenSlides>0</HiddenSlides>
  <MMClips>0</MMClips>
  <ScaleCrop>false</ScaleCrop>
  <HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>主题</vt:lpstr></vt:variant><vt:variant><vt:i4>1</vt:i4></vt:variant></vt:vector></HeadingPairs>
  <TitlesOfParts><vt:vector size="1" baseType="lpstr"><vt:lpstr>beauty-defense-refined</vt:lpstr></vt:vector></TitlesOfParts>
  <AppVersion>16.0000</AppVersion>
</Properties>
"""

    core_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:dcmitype="http://purl.org/dc/dcmitype/"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>AI美业知识台 毕业答辩PPT 精修版</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>
</cp:coreProperties>
"""

    presentation_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>{''.join(slide_ids)}</p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>
"""

    presentation_rels_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  {''.join(presentation_rels)}
  <Relationship Id="rId{len(SLIDES)+2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>
  <Relationship Id="rId{len(SLIDES)+3}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>
  <Relationship Id="rId{len(SLIDES)+4}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="tableStyles.xml"/>
</Relationships>
"""

    pres_props = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentationPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                  xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>
"""

    view_props = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:viewPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
          xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:normalViewPr/>
  <p:slideViewPr/>
  <p:notesTextViewPr/>
  <p:gridSpacing cx="72008" cy="72008"/>
</p:viewPr>
"""

    table_styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>
"""

    slide_master = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld name="Refined Theme"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>
"""

    slide_master_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>
"""

    slide_layout = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>
"""

    slide_layout_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>
"""

    theme = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Beauty Defense Theme">
  <a:themeElements>
    <a:clrScheme name="Beauty">
      <a:dk1><a:srgbClr val="102A28"/></a:dk1>
      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1F3B4D"/></a:dk2>
      <a:lt2><a:srgbClr val="F8F3EA"/></a:lt2>
      <a:accent1><a:srgbClr val="0F766E"/></a:accent1>
      <a:accent2><a:srgbClr val="2F80ED"/></a:accent2>
      <a:accent3><a:srgbClr val="F2994A"/></a:accent3>
      <a:accent4><a:srgbClr val="27AE60"/></a:accent4>
      <a:accent5><a:srgbClr val="5B8C85"/></a:accent5>
      <a:accent6><a:srgbClr val="EB5757"/></a:accent6>
      <a:hlink><a:srgbClr val="0563C1"/></a:hlink>
      <a:folHlink><a:srgbClr val="954F72"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="BeautyFonts">
      <a:majorFont><a:latin typeface="Aptos Display"/><a:ea typeface="微软雅黑"/><a:cs typeface=""/></a:majorFont>
      <a:minorFont><a:latin typeface="Aptos"/><a:ea typeface="微软雅黑"/><a:cs typeface=""/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="BeautyFmt">
      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
      <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
      <a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
  <a:objectDefaults/>
  <a:extraClrSchemeLst/>
</a:theme>
"""

    with ZipFile(PPTX_PATH, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("docProps/app.xml", app_xml)
        zf.writestr("docProps/core.xml", core_xml)
        zf.writestr("ppt/presentation.xml", presentation_xml)
        zf.writestr("ppt/_rels/presentation.xml.rels", presentation_rels_xml)
        zf.writestr("ppt/presProps.xml", pres_props)
        zf.writestr("ppt/viewProps.xml", view_props)
        zf.writestr("ppt/tableStyles.xml", table_styles)
        zf.writestr("ppt/slideMasters/slideMaster1.xml", slide_master)
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels)
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout)
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels)
        zf.writestr("ppt/theme/theme1.xml", theme)
        for path, content in slide_entries:
            zf.writestr(path, content)
        for path, content in slide_rels:
            zf.writestr(path, content)


def write_notes() -> None:
    lines = ["# AI美业知识台 毕业答辩PPT 精修版讲稿", ""]
    for i, slide in enumerate(SLIDES, start=1):
        lines.append(f"## 第{i}页：{slide['title']}")
        lines.append(f"- 副标题：{slide['subtitle']}")
        for item in slide["bullets"]:
            lines.append(f"- {item}")
        lines.append(f"- 强调点：{slide['highlight_title']}：{slide['highlight_body']}")
        lines.append("")
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    write_pptx()
    write_notes()
    print(PPTX_PATH)
    print(MD_PATH)
