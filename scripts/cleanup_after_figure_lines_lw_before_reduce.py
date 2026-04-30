from __future__ import annotations

from pathlib import Path

import docx


DOC_PATH = Path(r"D:\beauty\lw_before_reduce.docx")


REMOVE_TEXTS = {
    "图 3-2 采用外部实体、处理过程、数据存储和数据流四类元素，重点说明登录鉴权、知识检索、文件处理、实体审核与智能问答之间的衔接关系。",
    "图 3-3 展示了普通用户从内容浏览到问题驱动交互的主要使用路径。",
    "图 3-4 展示了管理员贯穿知识治理全过程的核心操作链路。",
    "该结构图重点说明访问层、接口层、业务服务层以及数据与 AI 支撑层之间的分层关系和协同方式。",
    "该图重点对应用户端、管理端、知识治理、文件处理、实体确认、问答服务和基础设施等主要模块。",
    "该图重点描述分类、知识、文件、任务、会话消息以及图谱相关实体之间的主要联系。",
    "图 4-4 用于描述资料接入、任务处理、候选抽取、人工审核和结果沉淀之间的处理顺序。",
    "与知识入库流程对应，图 4-5 进一步说明问答模块如何把已沉淀知识重新组织为可交互的回答能力。",
    "该协作图用于概括前端页面、后端接口、数据存储和智能服务之间的总体配合关系。",
    "该图重点对应首页推荐、知识详情、收藏管理和智能问答等主要页面之间的跳转关系。",
    "该流程重点对应知识保存、分类组织、检索展示以及与附件、切片信息的关联处理。",
    "该流程图重点反映对象存储、任务创建、OCR 或转写服务调用以及结果回写等关键步骤。",
    "该图重点对应候选审核、关系查询、路径分析和证据查看等关键环节。",
    "该流程图重点对应问题输入、关键词检索、向量召回、证据融合、上下文构建和流式输出等步骤。",
    "在实现效果上，该模块不仅强化了用户与知识资源之间的交互方式，也提高了平台的综合服务能力。尤其是在附件问答场景下，系统可以围绕上传材料进行持续对话，使文件内容不再只是静态附件，而是能够转化为可被追问和解释的知识载体。这种设计更符合垂直领域知识服务系统对实用性和交互性的要求。",
}


def remove_paragraph(paragraph) -> None:
    element = paragraph._element
    element.getparent().remove(element)


def main() -> None:
    doc = docx.Document(str(DOC_PATH))
    for para in list(doc.paragraphs):
        text = para.text.strip()
        if text in REMOVE_TEXTS:
            remove_paragraph(para)
    doc.save(str(DOC_PATH))
    print(DOC_PATH)


if __name__ == "__main__":
    main()
