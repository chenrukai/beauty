from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(r"C:\Users\YLDN\Desktop\beauty")
OUT_DIR = ROOT / "docs" / "generated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PPTX_PATH = OUT_DIR / "AI美业知识台_毕业答辩PPT.pptx"
MD_PATH = OUT_DIR / "AI美业知识台_毕业答辩PPT_讲稿.md"


slides = [
    {
        "title": "AI美业知识台",
        "bullets": [
            "基于CMS架构的“美业多媒体知识库”构建与展示系统实现",
            "毕业设计答辩汇报",
            "专业：软件工程  班级：2022软件工程1班",
            "说明：封面中的姓名、学号、指导教师可按本人信息补充"
        ]
    },
    {
        "title": "选题背景与研究意义",
        "bullets": [
            "美业门店知识分散在产品手册、培训文档、护理SOP与经验口述中，难以统一沉淀",
            "传统CMS擅长内容管理，但缺少语义检索与智能问答能力",
            "大模型具备问答能力，但存在知识滞后与幻觉风险，需要结合私有知识库",
            "本课题希望建设一个可管理、可检索、可追溯、可问答的垂直领域知识平台"
        ]
    },
    {
        "title": "研究目标与核心问题",
        "bullets": [
            "实现一个面向美业场景的知识管理与智能问答系统原型",
            "打通“知识录入—文件处理—向量入库—智能问答—来源展示”的完整链路",
            "解决异构技术栈协同问题：Spring Boot业务系统 + 本地大模型/Ollama",
            "提升问答的专业性、可解释性与实际演示效果"
        ]
    },
    {
        "title": "系统总体方案",
        "bullets": [
            "前端：Vue 3 + Vite + Element Plus",
            "后端：Spring Boot 3 + Spring Security + JWT + MyBatis-Plus",
            "中间件：MySQL、Redis、RabbitMQ、MinIO、Milvus",
            "AI能力：Ollama 本地模型 + RAG 检索增强生成"
        ]
    },
    {
        "title": "系统功能设计",
        "bullets": [
            "管理员端：运营总览、公告管理、知识列表、分类树、文件上传、任务监控、实体确认、用户管理",
            "普通用户端：首页推荐、知识详情、收藏、智能问答、来源查看",
            "权限设计：管理员与普通用户分离，普通用户支持注册",
            "内容状态：草稿、发布、下线，支持相应的管理操作"
        ]
    },
    {
        "title": "关键业务流程",
        "bullets": [
            "知识入库流程：上传文件 -> 写入任务 -> RabbitMQ入队 -> 文本提取/分块 -> 向量化 -> 状态回写",
            "问答流程：用户提问 -> 混合检索 -> 组织上下文 -> 大模型生成 -> 返回回答与来源",
            "统计流程：浏览/搜索/收藏记录入库 -> 后台报表聚合 -> 热门内容与来源占比分析",
            "实体流程：自动抽取待确认 -> 管理员审核 -> 进入正式实体与关系表"
        ]
    },
    {
        "title": "数据库与知识建模",
        "bullets": [
            "系统围绕用户、知识、分类、文件、任务、聊天、实体和关系等核心对象设计数据表",
            "知识管理主表：kb_knowledge、kb_category、kb_file、kb_chunk、process_task",
            "问答与行为表：chat_session、chat_message、user_action_log、search_keyword_stat",
            "实体关系表：beauty_ingredient、beauty_effect、beauty_product 及关联关系表"
        ]
    },
    {
        "title": "系统实现与演示效果",
        "bullets": [
            "目前系统已完成主要页面和核心链路联调，支持中期检查及答辩演示",
            "管理员可创建知识、上传文档、查看任务状态、管理用户和公告",
            "普通用户可浏览推荐知识、查看详情、收藏内容并发起智能提问",
            "问答结果支持来源展示，提高回答可信度和演示说服力"
        ]
    },
    {
        "title": "项目特色、创新点与不足",
        "bullets": [
            "特色一：将CMS内容管理与RAG智能问答结合，面向美业垂直领域落地",
            "特色二：采用异步处理流水线，支持文件处理状态追踪与失败重试",
            "特色三：构建“成分—功效—产品”基础知识关系，支持后续图谱扩展",
            "当前不足：统计报表、知识图谱可视化、测试评估与论文正文仍需继续完善"
        ]
    },
    {
        "title": "后续计划与答辩总结",
        "bullets": [
            "继续优化管理端与用户端交互体验，补齐统计图表和状态流程细节",
            "完善系统测试、性能分析、问答效果评估与论文撰写",
            "整理部署说明、演示账号、演示数据与答辩材料",
            "总结：本课题已完成系统核心闭环，具备较好的工程实现价值与展示效果"
        ]
    },
]


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def make_text_runs(lines: list[str], font_size: int = 2200) -> str:
    parts = []
    for idx, line in enumerate(lines):
        bullet = ""
        if idx > 0:
            bullet = '<a:buChar char="•"/>'
        parts.append(
            f"""
            <a:p>
              <a:pPr lvl="0">{bullet}</a:pPr>
              <a:r>
                <a:rPr lang="zh-CN" sz="{font_size}" dirty="0"/>
                <a:t>{xml_escape(line)}</a:t>
              </a:r>
            </a:p>
            """
        )
    return "".join(parts)


def slide_xml(title: str, bullets: list[str]) -> str:
    title_text = make_text_runs([title], font_size=2800)
    body_text = make_text_runs(bullets, font_size=2000)
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
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="2" name="Title 1"/>
          <p:cNvSpPr/>
          <p:nvPr>
            <p:ph type="title"/>
          </p:nvPr>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="457200" y="274320"/>
            <a:ext cx="8229600" cy="914400"/>
          </a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          {title_text}
        </p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="3" name="Content Placeholder 2"/>
          <p:cNvSpPr/>
          <p:nvPr>
            <p:ph idx="1"/>
          </p:nvPr>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="685800" y="1463040"/>
            <a:ext cx="7772400" cy="4114800"/>
          </a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"/>
          <a:lstStyle/>
          {body_text}
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr>
    <a:masterClrMapping/>
  </p:clrMapOvr>
</p:sld>
"""


def slide_rel_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
                Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"
                Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>
"""


def build_pptx() -> None:
    timestamp = datetime.now(timezone(timedelta(hours=8))).isoformat()
    slide_entries = []
    slide_rel_entries = []
    presentation_rels = []
    slide_id_entries = []
    for idx, slide in enumerate(slides, start=1):
        slide_entries.append((f"ppt/slides/slide{idx}.xml", slide_xml(slide["title"], slide["bullets"])))
        slide_rel_entries.append((f"ppt/slides/_rels/slide{idx}.xml.rels", slide_rel_xml()))
        presentation_rels.append(
            f'<Relationship Id="rId{idx+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{idx}.xml"/>'
        )
        slide_id_entries.append(f'<p:sldId id="{255 + idx}" r:id="rId{idx+1}"/>')

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
  {''.join(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, len(slides)+1))}
</Types>
"""

    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""

    app_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Office PowerPoint</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
  <Slides>10</Slides>
  <Notes>0</Notes>
  <HiddenSlides>0</HiddenSlides>
  <MMClips>0</MMClips>
  <ScaleCrop>false</ScaleCrop>
  <HeadingPairs>
    <vt:vector size="2" baseType="variant">
      <vt:variant><vt:lpstr>主题</vt:lpstr></vt:variant>
      <vt:variant><vt:i4>1</vt:i4></vt:variant>
    </vt:vector>
  </HeadingPairs>
  <TitlesOfParts>
    <vt:vector size="1" baseType="lpstr">
      <vt:lpstr>AI美业知识台_毕业答辩PPT</vt:lpstr>
    </vt:vector>
  </TitlesOfParts>
  <Company></Company>
  <LinksUpToDate>false</LinksUpToDate>
  <SharedDoc>false</SharedDoc>
  <HyperlinksChanged>false</HyperlinksChanged>
  <AppVersion>16.0000</AppVersion>
</Properties>
"""

    core_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>AI美业知识台 毕业答辩PPT</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>
</cp:coreProperties>
"""

    presentation_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                saveSubsetFonts="1" autoCompressPictures="0">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId1"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
    {''.join(slide_id_entries)}
  </p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>
"""

    presentation_rels_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  {''.join(presentation_rels)}
  <Relationship Id="rId{len(slides)+2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>
  <Relationship Id="rId{len(slides)+3}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>
  <Relationship Id="rId{len(slides)+4}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="tableStyles.xml"/>
</Relationships>
"""

    pres_props_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentationPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                  xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>
"""

    view_props_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:viewPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
          xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:normalViewPr/>
  <p:slideViewPr/>
  <p:notesTextViewPr/>
  <p:gridSpacing cx="72008" cy="72008"/>
</p:viewPr>
"""

    table_styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>
"""

    slide_master_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld name="Office Theme">
    <p:bg>
      <p:bgRef idx="1001">
        <a:schemeClr val="bg1"/>
      </p:bgRef>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="1" r:id="rId1"/>
  </p:sldLayoutIdLst>
  <p:txStyles>
    <p:titleStyle/>
    <p:bodyStyle/>
    <p:otherStyle/>
  </p:txStyles>
</p:sldMaster>
"""

    slide_master_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>
"""

    slide_layout_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             type="titleAndContent" preserve="1">
  <p:cSld name="Title and Content">
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="Title Placeholder 1"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>
        <p:spPr/>
        <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="3" name="Content Placeholder 2"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph idx="1"/></p:nvPr></p:nvSpPr>
        <p:spPr/>
        <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>
"""

    slide_layout_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>
"""

    theme_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
  <a:themeElements>
    <a:clrScheme name="Office">
      <a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>
      <a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1F3B4D"/></a:dk2>
      <a:lt2><a:srgbClr val="F5F5F5"/></a:lt2>
      <a:accent1><a:srgbClr val="0F766E"/></a:accent1>
      <a:accent2><a:srgbClr val="2F80ED"/></a:accent2>
      <a:accent3><a:srgbClr val="F2994A"/></a:accent3>
      <a:accent4><a:srgbClr val="27AE60"/></a:accent4>
      <a:accent5><a:srgbClr val="9B51E0"/></a:accent5>
      <a:accent6><a:srgbClr val="EB5757"/></a:accent6>
      <a:hlink><a:srgbClr val="0563C1"/></a:hlink>
      <a:folHlink><a:srgbClr val="954F72"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Office">
      <a:majorFont><a:latin typeface="Aptos Display"/><a:ea typeface="等线"/><a:cs typeface=""/></a:majorFont>
      <a:minorFont><a:latin typeface="Aptos"/><a:ea typeface="等线"/><a:cs typeface=""/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Office">
      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
      <a:lnStyleLst><a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
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
        zf.writestr("ppt/presProps.xml", pres_props_xml)
        zf.writestr("ppt/viewProps.xml", view_props_xml)
        zf.writestr("ppt/tableStyles.xml", table_styles_xml)
        zf.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml)
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels_xml)
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml)
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels_xml)
        zf.writestr("ppt/theme/theme1.xml", theme_xml)
        for path, content in slide_entries:
            zf.writestr(path, content)
        for path, content in slide_rel_entries:
            zf.writestr(path, content)


def build_markdown() -> None:
    parts = ["# AI美业知识台 毕业答辩PPT讲稿", ""]
    for idx, slide in enumerate(slides, start=1):
        parts.append(f"## 第{idx}页：{slide['title']}")
        parts.extend([f"- {item}" for item in slide["bullets"]])
        parts.append("")
        parts.append("讲述建议：")
        if idx == 1:
            parts.append("- 用 10~15 秒说明课题名称、项目定位和汇报结构。")
        elif idx == 2:
            parts.append("- 强调美业知识碎片化、培训依赖经验、资料检索困难这几个痛点。")
        elif idx == 3:
            parts.append("- 说明系统目标不是泛化聊天，而是基于私有知识库做可追溯问答。")
        elif idx == 4:
            parts.append("- 从前端、后端、中间件和AI能力四层快速概括整体方案。")
        elif idx == 5:
            parts.append("- 建议配合系统截图讲，突出管理员端和普通用户端两个视角。")
        elif idx == 6:
            parts.append("- 这一页适合配流程图，突出异步处理和RAG问答闭环。")
        elif idx == 7:
            parts.append("- 说明你做了结构化设计，不只是简单做页面。")
        elif idx == 8:
            parts.append("- 这里重点讲“现在已经能演示什么”。")
        elif idx == 9:
            parts.append("- 先讲亮点，再诚实说明目前还没做完的部分，会显得更稳。")
        else:
            parts.append("- 结尾收束到“系统核心闭环已完成，后续重点是优化、测试和论文完善”。")
        parts.append("")
    MD_PATH.write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    build_pptx()
    build_markdown()
    print(PPTX_PATH)
    print(MD_PATH)
