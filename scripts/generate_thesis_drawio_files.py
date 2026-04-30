from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(r"D:\beauty")
OUT_DIR = ROOT / "final_assets" / "thesis_copy_fix" / "drawio"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DRAWIO_SCRIPTS = Path(r"C:\Users\YLDN\.codex\skills\drawio\scripts")
CLI = DRAWIO_SCRIPTS / "cli.js"


SPECS: dict[str, str] = {
    "图3-2-系统数据流图": """meta:
  profile: academic-paper
  theme: academic
  source: generated
  layout: horizontal
  routing: orthogonal
  title: "图 3-2 系统数据流图"
  description: "普通用户、管理员、处理过程与核心数据存储之间的数据流。"
  legend: "矩形为外部实体或数据存储；菱形流程节点为处理过程；虚线表示数据存储交互。"

nodes:
  - id: user
    label: 普通用户
    type: user
    position: { x: 80, y: 160 }
  - id: admin
    label: 管理员
    type: user
    position: { x: 920, y: 160 }
  - id: auth
    label: 用户信息管理/认证
    type: process
    position: { x: 240, y: 160 }
  - id: search
    label: 知识检索
    type: process
    position: { x: 420, y: 160 }
  - id: file
    label: 文件处理
    type: process
    position: { x: 600, y: 160 }
  - id: entity
    label: 实体审核
    type: process
    position: { x: 780, y: 160 }
  - id: qa
    label: 智能问答
    type: process
    position: { x: 510, y: 360 }
  - id: db
    label: 业务数据库
    type: database
    position: { x: 260, y: 540 }
  - id: store
    label: 对象存储
    type: database
    position: { x: 510, y: 540 }
  - id: vector
    label: 向量库
    type: database
    position: { x: 760, y: 540 }

edges:
  - from: user
    to: auth
    type: primary
    label: 登录信息
  - from: auth
    to: search
    type: primary
    label: 身份信息
  - from: user
    to: search
    type: primary
    label: 检索条件
  - from: user
    to: file
    type: primary
    label: 上传文件
  - from: file
    to: entity
    type: primary
    label: 候选实体
  - from: admin
    to: entity
    type: primary
    label: 审核指令
  - from: user
    to: qa
    type: primary
    label: 问答请求
  - from: qa
    to: user
    type: primary
    label: 问答结果
  - from: auth
    to: db
    type: data
    label: 用户/权限数据
  - from: search
    to: db
    type: data
    label: 知识信息
  - from: file
    to: store
    type: data
    label: 原始文件
  - from: entity
    to: db
    type: data
    label: 审核回写
  - from: qa
    to: store
    type: data
    label: 附件内容
  - from: qa
    to: vector
    type: data
    label: 向量检索结果
""",
    "图4-1-系统整体结构图": """meta:
  profile: academic-paper
  theme: academic
  source: generated
  layout: hierarchical
  routing: orthogonal
  title: "图 4-1 系统整体结构图"
  description: "访问层、接口层、业务服务层和数据与AI支撑层的总体结构。"
  legend: "容器表示分层；圆角矩形为服务组件；圆柱为存储组件。"

modules:
  - id: access
    label: 访问层
  - id: app
    label: 接口/应用层
  - id: biz
    label: 业务服务层
  - id: data
    label: 数据与AI支撑层

nodes:
  - id: userui
    label: 用户端 Vue3
    type: service
    module: access
    position: { x: 130, y: 120 }
  - id: adminui
    label: 管理端 Vue3
    type: service
    module: access
    position: { x: 320, y: 120 }
  - id: auth
    label: 认证授权
    type: service
    module: app
    position: { x: 80, y: 290 }
  - id: know
    label: 知识管理
    type: service
    module: app
    position: { x: 250, y: 290 }
  - id: file
    label: 文件处理
    type: service
    module: app
    position: { x: 420, y: 290 }
  - id: graph
    label: 图谱服务
    type: service
    module: app
    position: { x: 590, y: 290 }
  - id: qa
    label: 问答服务
    type: service
    module: app
    position: { x: 760, y: 290 }
  - id: boot
    label: Spring Boot / WebFlux
    type: service
    module: biz
    position: { x: 310, y: 460 }
  - id: report
    label: 统计分析
    type: service
    module: biz
    position: { x: 120, y: 580 }
  - id: task
    label: 任务调度
    type: service
    module: biz
    position: { x: 310, y: 580 }
  - id: entity
    label: 实体确认
    type: service
    module: biz
    position: { x: 500, y: 580 }
  - id: sys
    label: 公告/用户管理
    type: service
    module: biz
    position: { x: 690, y: 580 }
  - id: mysql
    label: MySQL
    type: database
    module: data
    position: { x: 90, y: 780 }
  - id: redis
    label: Redis
    type: database
    module: data
    position: { x: 250, y: 780 }
  - id: mq
    label: RabbitMQ
    type: database
    module: data
    position: { x: 410, y: 780 }
  - id: minio
    label: MinIO
    type: database
    module: data
    position: { x: 570, y: 780 }
  - id: milvus
    label: Milvus
    type: database
    module: data
    position: { x: 730, y: 780 }
  - id: ocr
    label: OCR / Whisper ASR
    type: database
    module: data
    position: { x: 890, y: 780 }

edges:
  - from: userui
    to: auth
    type: primary
  - from: adminui
    to: know
    type: primary
  - from: adminui
    to: file
    type: primary
  - from: userui
    to: qa
    type: primary
  - from: auth
    to: boot
    type: primary
  - from: know
    to: boot
    type: primary
  - from: file
    to: boot
    type: primary
  - from: graph
    to: boot
    type: primary
  - from: qa
    to: boot
    type: primary
  - from: boot
    to: report
    type: primary
  - from: boot
    to: task
    type: primary
  - from: boot
    to: entity
    type: primary
  - from: boot
    to: sys
    type: primary
  - from: report
    to: mysql
    type: data
  - from: task
    to: redis
    type: data
  - from: task
    to: mq
    type: data
  - from: entity
    to: minio
    type: data
  - from: qa
    to: milvus
    type: data
  - from: file
    to: ocr
    type: data
""",
    "图4-2-系统功能模块设计图": """meta:
  profile: academic-paper
  theme: academic
  source: generated
  layout: vertical
  routing: orthogonal
  title: "图 4-2 系统功能模块设计图"
  description: "美业多媒体知识服务系统的模块树。"
  legend: "顶层为系统根节点；下层为一级与二级功能模块。"

nodes:
  - id: root
    label: 美业多媒体知识服务系统
    type: service
    position: { x: 460, y: 80 }
  - id: u
    label: 用户端模块
    type: service
    position: { x: 80, y: 240 }
  - id: a
    label: 管理端模块
    type: service
    position: { x: 220, y: 240 }
  - id: k
    label: 知识治理模块
    type: service
    position: { x: 360, y: 240 }
  - id: f
    label: 文件处理模块
    type: service
    position: { x: 500, y: 240 }
  - id: e
    label: 实体确认模块
    type: service
    position: { x: 640, y: 240 }
  - id: q
    label: 问答服务模块
    type: service
    position: { x: 780, y: 240 }
  - id: s
    label: 统计分析模块
    type: service
    position: { x: 300, y: 440 }
  - id: i
    label: 基础设施模块
    type: service
    position: { x: 560, y: 440 }
  - id: u1
    label: 首页浏览
    type: service
    position: { x: 40, y: 380 }
  - id: u2
    label: 知识检索
    type: service
    position: { x: 100, y: 520 }
  - id: u3
    label: 收藏管理
    type: service
    position: { x: 160, y: 660 }
  - id: a1
    label: 概览看板
    type: service
    position: { x: 220, y: 380 }
  - id: a2
    label: 用户管理
    type: service
    position: { x: 220, y: 520 }
  - id: a3
    label: 公告管理
    type: service
    position: { x: 220, y: 660 }
  - id: k1
    label: 知识管理
    type: service
    position: { x: 360, y: 380 }
  - id: k2
    label: 分类管理
    type: service
    position: { x: 360, y: 520 }
  - id: k3
    label: 知识详情
    type: service
    position: { x: 360, y: 660 }
  - id: f1
    label: 文件上传
    type: service
    position: { x: 500, y: 380 }
  - id: f2
    label: 任务监控
    type: service
    position: { x: 500, y: 520 }
  - id: f3
    label: 处理追踪
    type: service
    position: { x: 500, y: 660 }
  - id: e1
    label: 候选确认
    type: service
    position: { x: 640, y: 380 }
  - id: e2
    label: 图谱维护
    type: service
    position: { x: 640, y: 520 }
  - id: e3
    label: 关系修订
    type: service
    position: { x: 640, y: 660 }
  - id: q1
    label: 智能问答
    type: service
    position: { x: 780, y: 380 }
  - id: q2
    label: 附件问答
    type: service
    position: { x: 780, y: 520 }
  - id: q3
    label: 会话管理
    type: service
    position: { x: 780, y: 660 }
  - id: s1
    label: 报表分析
    type: service
    position: { x: 300, y: 580 }
  - id: i1
    label: MySQL/Redis
    type: service
    position: { x: 560, y: 580 }
  - id: i2
    label: MinIO/Milvus
    type: service
    position: { x: 560, y: 700 }
  - id: i3
    label: RabbitMQ/OCR/ASR
    type: service
    position: { x: 560, y: 820 }

edges:
  - { from: root, to: u, type: primary }
  - { from: root, to: a, type: primary }
  - { from: root, to: k, type: primary }
  - { from: root, to: f, type: primary }
  - { from: root, to: e, type: primary }
  - { from: root, to: q, type: primary }
  - { from: root, to: s, type: primary }
  - { from: root, to: i, type: primary }
  - { from: u, to: u1, type: primary }
  - { from: u, to: u2, type: primary }
  - { from: u, to: u3, type: primary }
  - { from: a, to: a1, type: primary }
  - { from: a, to: a2, type: primary }
  - { from: a, to: a3, type: primary }
  - { from: k, to: k1, type: primary }
  - { from: k, to: k2, type: primary }
  - { from: k, to: k3, type: primary }
  - { from: f, to: f1, type: primary }
  - { from: f, to: f2, type: primary }
  - { from: f, to: f3, type: primary }
  - { from: e, to: e1, type: primary }
  - { from: e, to: e2, type: primary }
  - { from: e, to: e3, type: primary }
  - { from: q, to: q1, type: primary }
  - { from: q, to: q2, type: primary }
  - { from: q, to: q3, type: primary }
  - { from: s, to: s1, type: primary }
  - { from: i, to: i1, type: primary }
  - { from: i, to: i2, type: primary }
  - { from: i, to: i3, type: primary }
""",
    "图4-3-系统ER图": """meta:
  profile: academic-paper
  theme: academic
  source: generated
  layout: hierarchical
  routing: orthogonal
  title: "图 4-3 系统 ER 图"
  description: "分类、知识、文件、任务、图谱和会话消息的实体关系。"
  legend: "矩形为实体；菱形为联系；椭圆为属性。"

nodes:
  - id: cat
    label: 分类
    type: service
    position: { x: 80, y: 160 }
  - id: kn
    label: 知识
    type: service
    position: { x: 280, y: 160 }
  - id: file
    label: 文件
    type: service
    position: { x: 500, y: 160 }
  - id: task
    label: 任务
    type: service
    position: { x: 720, y: 160 }
  - id: ent
    label: 图谱实体
    type: service
    position: { x: 230, y: 520 }
  - id: rel
    label: 图谱关系
    type: service
    position: { x: 500, y: 520 }
  - id: session
    label: 会话
    type: service
    position: { x: 760, y: 520 }
  - id: msg
    label: 消息
    type: service
    position: { x: 950, y: 520 }
  - id: r1
    label: 归属
    type: decision
    position: { x: 180, y: 160 }
  - id: r2
    label: 关联
    type: decision
    position: { x: 390, y: 160 }
  - id: r3
    label: 生成
    type: decision
    position: { x: 610, y: 160 }
  - id: r4
    label: 抽取
    type: decision
    position: { x: 360, y: 350 }
  - id: r5
    label: 包含
    type: decision
    position: { x: 860, y: 520 }
  - id: catid
    label: category_id
    type: user
    position: { x: 40, y: 40 }
  - id: catname
    label: name
    type: user
    position: { x: 140, y: 40 }
  - id: kid
    label: knowledge_id
    type: user
    position: { x: 240, y: 40 }
  - id: ktitle
    label: title
    type: user
    position: { x: 340, y: 40 }
  - id: fid
    label: file_id
    type: user
    position: { x: 460, y: 40 }
  - id: fname
    label: file_name
    type: user
    position: { x: 560, y: 40 }
  - id: tid
    label: task_id
    type: user
    position: { x: 680, y: 40 }
  - id: tstatus
    label: status
    type: user
    position: { x: 780, y: 40 }
  - id: eid
    label: entity_id
    type: user
    position: { x: 150, y: 760 }
  - id: ename
    label: entity_name
    type: user
    position: { x: 300, y: 760 }
  - id: rid
    label: relation_id
    type: user
    position: { x: 430, y: 760 }
  - id: rtype
    label: relation_type
    type: user
    position: { x: 570, y: 760 }
  - id: sid
    label: session_id
    type: user
    position: { x: 710, y: 760 }
  - id: uid
    label: user_id
    type: user
    position: { x: 820, y: 760 }
  - id: mid
    label: message_id
    type: user
    position: { x: 930, y: 760 }
  - id: role
    label: role
    type: user
    position: { x: 1040, y: 760 }

edges:
  - { from: cat, to: r1, type: primary, label: "1" }
  - { from: r1, to: kn, type: primary, label: "N" }
  - { from: kn, to: r2, type: primary, label: "1" }
  - { from: r2, to: file, type: primary, label: "N" }
  - { from: file, to: r3, type: primary, label: "1" }
  - { from: r3, to: task, type: primary, label: "N" }
  - { from: kn, to: r4, type: primary, label: "1" }
  - { from: r4, to: ent, type: primary, label: "N" }
  - { from: rel, to: ent, type: primary, label: "源/目标" }
  - { from: session, to: r5, type: primary, label: "1" }
  - { from: r5, to: msg, type: primary, label: "N" }
  - { from: cat, to: catid, type: optional }
  - { from: cat, to: catname, type: optional }
  - { from: kn, to: kid, type: optional }
  - { from: kn, to: ktitle, type: optional }
  - { from: file, to: fid, type: optional }
  - { from: file, to: fname, type: optional }
  - { from: task, to: tid, type: optional }
  - { from: task, to: tstatus, type: optional }
  - { from: ent, to: eid, type: optional }
  - { from: ent, to: ename, type: optional }
  - { from: rel, to: rid, type: optional }
  - { from: rel, to: rtype, type: optional }
  - { from: session, to: sid, type: optional }
  - { from: session, to: uid, type: optional }
  - { from: msg, to: mid, type: optional }
  - { from: msg, to: role, type: optional }
""",
    "图5-3-知识管理流程图": """meta:
  profile: academic-paper
  theme: academic
  source: generated
  layout: vertical
  routing: orthogonal
  title: "图 5-3 知识管理模块处理流程图"
  description: "知识录入、校验、附件关联与展示流程。"
  legend: "椭圆为开始/结束；矩形为处理步骤；菱形为判断。"

nodes:
  - { id: start, label: 开始, type: terminal, position: { x: 420, y: 60 } }
  - { id: enter, label: 进入知识管理页面, type: process, position: { x: 420, y: 160 } }
  - { id: form, label: 录入标题、分类、摘要、正文, type: process, position: { x: 420, y: 280 } }
  - { id: complete, label: 信息是否完整？, type: decision, position: { x: 420, y: 400 } }
  - { id: revise, label: 补充或修改知识信息, type: process, position: { x: 140, y: 520 } }
  - { id: save, label: 保存知识内容, type: process, position: { x: 420, y: 520 } }
  - { id: attach, label: 是否包含附件？, type: decision, position: { x: 420, y: 660 } }
  - { id: upload, label: 上传并关联附件\\n登记文件信息, type: process, position: { x: 740, y: 800 } }
  - { id: write, label: 写入知识表/文件表\\n并更新索引, type: process, position: { x: 420, y: 800 } }
  - { id: view, label: 用户检索并查看详情, type: process, position: { x: 420, y: 940 } }
  - { id: end, label: 结束, type: terminal, position: { x: 420, y: 1060 } }

edges:
  - { from: start, to: enter, type: primary }
  - { from: enter, to: form, type: primary }
  - { from: form, to: complete, type: primary }
  - { from: complete, to: revise, type: primary, label: 否 }
  - { from: revise, to: save, type: primary }
  - { from: complete, to: save, type: primary, label: 是 }
  - { from: save, to: attach, type: primary }
  - { from: attach, to: write, type: primary, label: 否 }
  - { from: attach, to: upload, type: primary, label: 是 }
  - { from: upload, to: write, type: primary }
  - { from: write, to: view, type: primary }
  - { from: view, to: end, type: primary }
""",
    "图5-4-文件处理流程图": """meta:
  profile: academic-paper
  theme: academic
  source: generated
  layout: vertical
  routing: orthogonal
  title: "图 5-4 文件处理模块流程图"
  description: "文件上传、类型识别、解析、切片与入库流程。"
  legend: "椭圆为开始/结束；矩形为处理步骤；菱形为判断。"

nodes:
  - { id: start, label: 开始, type: terminal, position: { x: 420, y: 60 } }
  - { id: upload, label: 上传原始文件, type: process, position: { x: 420, y: 160 } }
  - { id: store, label: 写入对象存储\\n并登记文件/任务记录, type: process, position: { x: 420, y: 280 } }
  - { id: typecheck, label: 文件类型是否可识别？, type: decision, position: { x: 420, y: 410 } }
  - { id: fail1, label: 记录失败原因\\n等待人工重试, type: process, position: { x: 140, y: 560 } }
  - { id: parse, label: 按类型执行 OCR\\n或 Whisper 转写, type: process, position: { x: 420, y: 560 } }
  - { id: clean, label: 文本清洗与切片, type: process, position: { x: 420, y: 700 } }
  - { id: entity, label: 生成候选实体, type: process, position: { x: 420, y: 820 } }
  - { id: ok, label: 处理是否成功？, type: decision, position: { x: 420, y: 940 } }
  - { id: fail2, label: 更新失败状态\\n支持再次重试, type: process, position: { x: 740, y: 1080 } }
  - { id: write, label: 保存文本结果\\n进入后续治理链路, type: process, position: { x: 420, y: 1080 } }
  - { id: end, label: 结束, type: terminal, position: { x: 420, y: 1200 } }

edges:
  - { from: start, to: upload, type: primary }
  - { from: upload, to: store, type: primary }
  - { from: store, to: typecheck, type: primary }
  - { from: typecheck, to: fail1, type: primary, label: 否 }
  - { from: typecheck, to: parse, type: primary, label: 是 }
  - { from: parse, to: clean, type: primary }
  - { from: clean, to: entity, type: primary }
  - { from: entity, to: ok, type: primary }
  - { from: ok, to: write, type: primary, label: 是 }
  - { from: ok, to: fail2, type: primary, label: 否 }
  - { from: write, to: end, type: primary }
""",
    "图5-5-知识图谱流程图": """meta:
  profile: academic-paper
  theme: academic
  source: generated
  layout: vertical
  routing: orthogonal
  title: "图 5-5 知识图谱查询流程图"
  description: "实体关系抽取、审核、写入图谱与查询返回流程。"
  legend: "椭圆为开始/结束；矩形为处理步骤；菱形为判断。"

nodes:
  - { id: start, label: 开始, type: terminal, position: { x: 420, y: 60 } }
  - { id: enter, label: 进入实体审核/图谱查询, type: process, position: { x: 420, y: 160 } }
  - { id: candidate, label: 生成候选实体与候选关系, type: process, position: { x: 420, y: 280 } }
  - { id: review, label: 审核是否通过？, type: decision, position: { x: 420, y: 410 } }
  - { id: revise, label: 修订/驳回/补充候选结果, type: process, position: { x: 140, y: 560 } }
  - { id: write, label: 写入图谱实体与关系数据, type: process, position: { x: 420, y: 560 } }
  - { id: query, label: 发起邻居/路径/证据查询, type: process, position: { x: 420, y: 700 } }
  - { id: hit, label: 是否命中图谱结果？, type: decision, position: { x: 420, y: 840 } }
  - { id: retry, label: 调整查询条件\\n重新发起查询, type: process, position: { x: 740, y: 980 } }
  - { id: show, label: 返回图谱结果\\n及证据文本, type: process, position: { x: 420, y: 980 } }
  - { id: end, label: 结束, type: terminal, position: { x: 420, y: 1100 } }

edges:
  - { from: start, to: enter, type: primary }
  - { from: enter, to: candidate, type: primary }
  - { from: candidate, to: review, type: primary }
  - { from: review, to: revise, type: primary, label: 否 }
  - { from: review, to: write, type: primary, label: 是 }
  - { from: write, to: query, type: primary }
  - { from: query, to: hit, type: primary }
  - { from: hit, to: show, type: primary, label: 是 }
  - { from: hit, to: retry, type: primary, label: 否 }
  - { from: retry, to: query, type: primary }
  - { from: show, to: end, type: primary }
""",
    "图5-6-智能问答流程图": """meta:
  profile: academic-paper
  theme: academic
  source: generated
  layout: vertical
  routing: orthogonal
  title: "图 5-6 智能问答流程图"
  description: "问题输入、检索召回、融合排序、上下文构建与继续追问流程。"
  legend: "椭圆为开始/结束；矩形为处理步骤；菱形为判断。"

nodes:
  - { id: start, label: 开始, type: terminal, position: { x: 420, y: 60 } }
  - { id: input, label: 输入问题或上传附件, type: process, position: { x: 420, y: 160 } }
  - { id: prep, label: 问题预处理, type: process, position: { x: 420, y: 280 } }
  - { id: recall, label: 关键词检索\\n与向量召回, type: process, position: { x: 420, y: 400 } }
  - { id: enough, label: 证据是否充足？, type: decision, position: { x: 420, y: 540 } }
  - { id: expand, label: 扩展检索范围\\n或生成附件摘要, type: process, position: { x: 740, y: 680 } }
  - { id: rank, label: 融合排序, type: process, position: { x: 420, y: 680 } }
  - { id: ctx, label: 构建问答上下文, type: process, position: { x: 420, y: 820 } }
  - { id: answer, label: 生成流式回答, type: process, position: { x: 420, y: 940 } }
  - { id: again, label: 用户是否继续追问？, type: decision, position: { x: 420, y: 1080 } }
  - { id: keep, label: 保留会话上下文\\n返回问题输入, type: process, position: { x: 140, y: 1220 } }
  - { id: end, label: 结束, type: terminal, position: { x: 420, y: 1220 } }

edges:
  - { from: start, to: input, type: primary }
  - { from: input, to: prep, type: primary }
  - { from: prep, to: recall, type: primary }
  - { from: recall, to: enough, type: primary }
  - { from: enough, to: rank, type: primary, label: 是 }
  - { from: enough, to: expand, type: primary, label: 否 }
  - { from: expand, to: rank, type: primary }
  - { from: rank, to: ctx, type: primary }
  - { from: ctx, to: answer, type: primary }
  - { from: answer, to: again, type: primary }
  - { from: again, to: keep, type: primary, label: 是 }
  - { from: keep, to: input, type: primary }
  - { from: again, to: end, type: primary, label: 否 }
""",
}


def write_specs() -> list[Path]:
    paths: list[Path] = []
    for name, content in SPECS.items():
        path = OUT_DIR / f"{name}.yaml"
        path.write_text(content, encoding="utf-8")
        paths.append(path)
    return paths


def generate_drawio(spec_paths: list[Path]) -> None:
    for spec in spec_paths:
        out = spec.with_suffix(".drawio")
        cmd = [
            "node",
            str(CLI),
            str(spec),
            str(out),
            "--validate",
            "--write-sidecars",
        ]
        subprocess.run(cmd, cwd=str(DRAWIO_SCRIPTS), check=True)


def main() -> None:
    specs = write_specs()
    generate_drawio(specs)
    for spec in specs:
        print(spec.with_suffix(".drawio"))


if __name__ == "__main__":
    main()
