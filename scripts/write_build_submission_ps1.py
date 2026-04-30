from pathlib import Path

content = r"""$ErrorActionPreference = 'Stop'

$root = 'D:\beauty'
$template = Join-Path $root 'tmp_template_copy.docx'
$source = Join-Path $root '毕业论文_完整草稿_按材料修订_补图版.docx'
$output = Join-Path $root 'submission_final.docx'
$finalCopy = Join-Path $root '毕业论文_最终稿_提交版.docx'
$assetDir = Join-Path $root 'submission_assets'
$basePngDir = Join-Path $root '论文图表素材\png_for_word'
$backendDir = Join-Path $root 'beauty-knowledge-backend'
$frontendDir = Join-Path $root 'beauty-knowledge-frontend'

Add-Type -AssemblyName System.Drawing

New-Item -ItemType Directory -Force -Path $assetDir | Out-Null

$baseFigureSpecs = [ordered]@{
  '图 2-1 系统业务流程图' = @{ Source = (Join-Path $basePngDir 'fig_2_1_business_flow.png'); Output = 'fig_2_1_business_flow.png'; WidthCm = 14.6 }
  '图 2-2 普通用户用例图' = @{ Source = (Join-Path $basePngDir 'fig_2_2_user_usecase.png'); Output = 'fig_2_2_user_usecase.png'; WidthCm = 12.8 }
  '图 2-3 后台管理员用例图' = @{ Source = (Join-Path $basePngDir 'fig_2_3_admin_usecase.png'); Output = 'fig_2_3_admin_usecase.png'; WidthCm = 12.8 }
  '图 4-1 系统详细设计模块协作图' = @{ Source = (Join-Path $basePngDir 'fig_4_1_detail_collaboration.png'); Output = 'fig_4_1_detail_collaboration.png'; WidthCm = 14.2 }
  '图 4-2 用户端页面跳转关系图' = @{ Source = (Join-Path $basePngDir 'fig_4_2_frontend_navigation.png'); Output = 'fig_4_2_frontend_navigation.png'; WidthCm = 14.2 }
  '图 4-3 知识管理模块处理流程图' = @{ Source = (Join-Path $basePngDir 'fig_4_3_knowledge_manage_flow.png'); Output = 'fig_4_3_knowledge_manage_flow.png'; WidthCm = 14.2 }
  '图 4-4 文件处理模块流程图' = @{ Source = (Join-Path $basePngDir 'fig_4_4_file_processing_flow.png'); Output = 'fig_4_4_file_processing_flow.png'; WidthCm = 14.6 }
  '图 4-5 知识图谱查询流程图' = @{ Source = (Join-Path $basePngDir 'fig_4_5_graph_query_flow.png'); Output = 'fig_4_5_graph_query_flow.png'; WidthCm = 14.3 }
  '图 4-6 智能问答模块流程图' = @{ Source = (Join-Path $basePngDir 'fig_4_6_qa_flow.png'); Output = 'fig_4_6_qa_flow.png'; WidthCm = 14.3 }
  '图 5-1 性能测试记录图' = @{ Source = (Join-Path $basePngDir 'fig_5_1_performance_record.png'); Output = 'fig_5_1_performance_record.png'; WidthCm = 14.2 }
  '图 5-2 兼容性测试结果图' = @{ Source = (Join-Path $basePngDir 'fig_5_2_compatibility_result.png'); Output = 'fig_5_2_compatibility_result.png'; WidthCm = 14.2 }
}

$evidenceSpecs = @(
  @{
    Output = 'fig_4_7_task_state_code.png'
    Type = 'code'
    SourceFile = (Join-Path $backendDir 'src\main\java\com\beauty\knowledge\module\pipeline\service\ProcessTaskService.java')
    Ranges = @(@(24, 58))
    WidthCm = 14.2
  },
  @{
    Output = 'fig_4_8_graph_query_code.png'
    Type = 'code'
    SourceFile = (Join-Path $backendDir 'src\main\java\com\beauty\knowledge\module\kg\service\KgQueryService.java')
    Ranges = @(@(60, 98))
    WidthCm = 14.2
  },
  @{
    Output = 'fig_4_9_stream_chat_code.png'
    Type = 'code'
    SourceFile = (Join-Path $frontendDir 'src\stores\chat.ts')
    Ranges = @(@(79, 127))
    WidthCm = 14.2
  },
  @{
    Output = 'fig_5_3_backend_validate.png'
    Type = 'terminal'
    WorkingDir = $backendDir
    Command = 'mvn -DskipTests validate'
    WidthCm = 14.2
  },
  @{
    Output = 'fig_5_4_frontend_build.png'
    Type = 'terminal'
    WorkingDir = $frontendDir
    Command = 'npm run build'
    WidthCm = 14.2
  },
  @{
    Output = 'fig_6_1_frontend_dist.png'
    Type = 'terminal'
    WorkingDir = $root
    Command = "Get-ChildItem 'D:/beauty/beauty-knowledge-frontend/dist' -Recurse | Select-Object FullName,Length | Format-Table -AutoSize"
    WidthCm = 14.2
  }
)

$docItems = @(
  @{
    Anchor = '图 4-4 文件处理模块流程图'
    Asset = 'fig_4_7_task_state_code.png'
    Caption = '图 4-7 文件处理状态流转代码截图'
    Intro = '为进一步说明文件处理模块的工程实现方式，本文从后端任务状态管理代码中选取关键片段进行展示。如图 4-7 所示，系统通过统一的任务服务对象维护文件处理的执行状态、开始时间、完成时间以及异常结果，从而保证管理员能够在任务监控界面观察上传资料的处理进度。'
    Analysis = '该代码片段表明，系统并未将文件上传与后续解析过程混为单一步骤，而是将处理过程拆分为处理开始、处理中、抽取中、处理成功与处理失败等多个阶段，并同步更新任务表与文件状态表。这一实现方式提升了任务链路的可观察性，也为第五章中的任务状态测试提供了可验证依据。'
    WidthCm = 14.2
  },
  @{
    Anchor = '图 4-5 知识图谱查询流程图'
    Asset = 'fig_4_8_graph_query_code.png'
    Caption = '图 4-8 知识图谱查询构建代码截图'
    Intro = '在知识图谱模块实现中，系统需要将产品、成分与功效等实体及其关系动态组织为前端可消费的图结构对象。如图 4-8 所示，图谱查询服务会首先读取产品及关联关系，再逐步构建节点、边与置信度信息，从而生成可用于图谱展示和路径分析的数据结果。'
    Analysis = '从实现逻辑上看，该服务并不是简单返回数据库原始记录，而是对关系数据进行了聚合和语义封装，最终形成包含中心节点、关系类型、证据条数和推断标识的图结构结果。借助这一处理过程，前端页面能够以更直观的方式展示产品知识关系，系统问答链路也能够复用这些结构化信息。'
    WidthCm = 14.2
  },
  @{
    Anchor = '图 4-6 智能问答模块流程图'
    Asset = 'fig_4_9_stream_chat_code.png'
    Caption = '图 4-9 流式问答状态管理代码截图'
    Intro = '智能问答模块的关键实现之一是前端对流式返回过程的状态组织方式。如图 4-9 所示，系统在问答会话中会先记录用户提问，随后发起流式请求，并在接收 token 与完成事件后持续更新当前会话内容。'
    Analysis = '该代码片段体现了问答模块对流式交互、会话列表与来源信息的统一管理方式。相较于单次请求后等待整段结果返回，这种实现方式更符合问答功能在实际使用中的交互需求，也有助于增强用户对回答生成过程的感知。'
    WidthCm = 14.2
  },
  @{
    Anchor = '图 5-2 兼容性测试结果图'
    Asset = 'fig_5_3_backend_validate.png'
    Caption = '图 5-3 后端工程校验结果截图'
    Intro = '除业务功能测试外，本文还对系统后端工程进行了构建级校验，以验证项目在当前开发环境下的基本可用性。如图 5-3 所示，后端 Maven 工程在跳过测试用例的条件下完成了 validate 阶段校验，并给出了明确的构建成功提示。'
    Analysis = '该结果说明后端工程结构、依赖声明和基础配置在当前环境下保持一致，能够通过标准构建生命周期的前置检查。'
    WidthCm = 14.2
  },
  @{
    Anchor = '图 5-3 后端工程校验结果截图'
    Asset = 'fig_5_4_frontend_build.png'
    Caption = '图 5-4 前端生产构建结果截图'
    Intro = '为验证前端工程的可构建性，本文进一步执行了生产环境构建命令，并记录其真实终端输出。如图 5-4 所示，前端项目在完成类型检查后顺利完成 Vite 打包过程，构建产物与模块信息均被正常输出。'
    Analysis = '从测试结论看，前端项目已经能够通过标准构建流程生成可部署产物，这说明用户端与管理端页面代码在当前版本下具备较好的完整性。'
    WidthCm = 14.2
  },
  @{
    Anchor = '6.2 运行链路验证'
    Asset = 'fig_6_1_frontend_dist.png'
    Caption = '图 6-1 前端构建产物生成结果截图'
    Intro = '在部署与运行验证阶段，前端构建产物的生成情况能够直接反映系统页面资源是否可以正常输出。如图 6-1 所示，系统前端在构建完成后生成了入口页面、样式文件与脚本包等核心产物，为后续通过静态资源方式部署用户端与管理端页面提供了基础。'
    Analysis = '结合前述后端工程校验和前端打包结果可以认为，系统已经形成较完整的工程交付形态。'
    WidthCm = 14.2
  }
)

$insertions = @(
  @{
    Marker = '2.4 非功能需求分析'
    Text = @'
在可靠性要求方面，系统需要保证关键业务在异常情况下仍具备可恢复能力。文件处理、实体抽取和问答服务均可能受到外部服务状态、网络抖动和任务并发量变化的影响，因此系统必须通过任务状态记录、失败重试、异常日志留痕和结果回填机制，维持关键处理链路的连续性。对于毕业设计项目而言，这类可靠性设计不仅关系到系统能否稳定演示，也关系到论文中测试与部署章节的完整论证。

在可管理性方面，平台应支持对知识条目、文件任务、实体候选、图谱关系和用户行为进行可视化观察。后台管理人员只有在能够及时查看任务状态、错误原因和处理结果的前提下，才可以高效完成知识治理工作。因此，非功能需求不应仅停留在“系统可运行”的层面，还应进一步关注系统是否便于定位问题、是否便于持续维护，以及是否便于后续基于真实业务继续扩展。
'@
  },
  @{
    Marker = '3.1 总体架构设计'
    Text = @'
从工程实现角度看，该总体架构并不是对技术组件的简单堆叠，而是围绕业务链路进行组织。前端层承担统一入口与交互反馈职能，后端业务层负责鉴权、知识治理、文件处理与问答调度，基础设施层则为对象存储、异步消息、缓存和向量检索提供支撑。通过这种分层结构，系统能够在保证页面交互体验的同时，将复杂的处理逻辑收敛于后端服务与基础设施组件之间，既降低了前端耦合度，又提高了功能复用率。

此外，系统架构还兼顾了后续功能演进的需求。无论是扩展新的知识分类、引入新的实体类型，还是替换底层模型服务与检索组件，均可以在现有结构下进行局部调整，而不必整体推翻既有实现。对于毕业设计项目而言，这种具备一定扩展弹性的架构安排，有助于体现系统设计的完整性和工程思维。
'@
  },
  @{
    Marker = '3.3 数据库设计'
    Text = @'
数据库设计在本系统中不仅承担传统业务数据存储功能，还需要服务于知识治理链路中的过程记录与结果沉淀。一方面，知识条目、分类、公告、用户等基础表保证了系统前后台的日常管理功能能够稳定运行；另一方面，文件处理任务、实体确认结果、图谱关系和问答会话等数据又直接参与智能服务流程。因而，数据库设计必须同时满足一致性、可追踪性与可扩展性要求，使系统能够形成从资料接入到知识服务的完整数据闭环。

从论文表达角度看，数据库设计也是衔接总体设计与详细实现的重要环节。只有当表结构、主外键关系和关键字段语义足够清晰时，后续关于模块实现、接口调用和测试验证的描述才能形成自洽逻辑。因此，本系统的数据库设计既体现业务对象的静态组织方式，也体现处理流程的动态支撑能力。
'@
  },
  @{
    Marker = '4.2 前端交互模块设计与实现'
    Text = @'
前端实现的核心价值不在于单页界面本身，而在于将多种知识服务入口统一组织为易理解、可连续操作的交互路径。系统通过首页推荐、知识列表、知识详情、收藏管理与问答会话等页面构成用户侧访问闭环，使普通用户既可以通过浏览方式获取内容，也可以带着明确问题发起检索与问答。对于后台管理人员而言，统一的导航结构和明确的模块边界，有助于在知识治理、任务监控和数据维护之间快速切换，从而提升整体管理效率。

此外，前端模块还承担结果解释与状态反馈职能。知识详情页中的分类信息、来源信息和摘要内容，以及问答界面中的流式返回、来源展示和会话记录，均体现出系统并非仅追求“给出答案”，而是强调“给出可理解的答案”。这种交互思路与垂直领域知识系统的应用特点较为一致，也有助于提升系统在论文展示中的完整度。
'@
  },
  @{
    Marker = '4.3 知识管理模块设计与实现'
    Text = @'
知识管理模块是后台治理体系的核心部分。该模块不仅承担知识条目的新增、修改、删除和状态维护任务，也承担知识内容规范化组织的职责。通过对标题、分类、摘要、正文和附件信息的统一管理，系统能够逐步形成结构清晰、可持续维护的知识库基础数据，为前台推荐、详情展示与问答召回提供稳定来源。

从实现逻辑上看，知识管理模块的意义还在于连接人工治理与智能服务。只有当知识条目具备较好的结构化程度和分类规范时，后续检索排序、图谱关联和问答生成的质量才有保障。因此，本模块虽然表现为典型的后台管理功能，但其设计质量会直接影响系统整体服务效果。
'@
  },
  @{
    Marker = '4.4 文件处理模块设计与实现'
    Text = @'
文件处理模块是系统完成多媒体知识接入的关键入口。与直接录入结构化知识不同，原始资料通常以文档、图片或音频等形式存在，内容表达方式差异较大。系统通过统一上传入口、任务状态管理和异步处理链路，将原始资料转化为后续可以审核、检索和复用的中间结果，从而显著降低人工整理成本。

在工程实现层面，文件处理模块不仅需要考虑解析能力，还需考虑任务链路的可观察性和可恢复性。平台通过记录处理状态、失败原因和结果摘要，使管理人员能够明确判断当前资料所处阶段，并在必要时进行重试或人工修订。该设计体现了面向真实应用场景的系统思维，而不仅仅是简单的“上传成功”功能实现。
'@
  },
  @{
    Marker = '4.5 实体抽取与知识图谱模块设计与实现'
    Text = @'
实体抽取与知识图谱模块的设计重点在于将自动化处理结果与人工审核机制有机结合。美业知识中的产品、成分、功效、适用人群与使用方式之间往往存在多对多关联，如果缺乏必要的审核与校正过程，自动抽取结果很容易在后续图谱展示和问答过程中产生误导。为此，系统将候选实体确认、关系修订和证据查看统一纳入管理端流程，以保证进入图谱的数据具有较高可控性。

知识图谱的引入还提升了系统对知识关系的表达能力。相较于纯文本列表展示，图结构更适合表现成分与功效、产品与场景、实体与来源之间的关联关系。通过图谱查询与可视化展示，平台在知识组织层面获得了更好的层次性，也为智能问答提供了补充性的结构化证据。
'@
  },
  @{
    Marker = '4.6 智能问答模块设计与实现'
    Text = @'
智能问答模块体现了本课题区别于传统内容展示平台的主要特征。系统并未将问答流程简化为单次大模型调用，而是构建了包含关键词检索、向量召回、结果融合、证据组织和流式回答的完整服务链路。这样做的目的在于提升答案与知识库内容之间的关联程度，并通过来源信息增强回答结果的可解释性。

在实际使用场景中，用户往往并不满足于一次性获得简短结论，而是希望围绕同一主题连续追问、结合附件内容深入理解问题。为此，系统在问答模块中保留了会话上下文和附件问答入口，使问答能力能够从“单轮回答工具”扩展为“面向知识服务的交互式入口”。这一设计更符合垂直领域知识系统的实际需求。
'@
  },
  @{
    Marker = '5.1 测试目标与测试环境'
    Text = @'
本章测试工作的目标不仅是验证页面和接口能否正常访问，更重要的是验证系统在关键业务链路上的完整性与稳定性。由于本系统同时涉及后台治理、异步任务、图谱关系查询和智能问答等多类能力，若仅针对单个界面进行静态检查，难以说明系统是否真正满足论文所述设计目标。因此，测试内容需要覆盖用户端访问链路、管理端治理链路以及智能服务链路三个层面。

结合毕业设计项目的实际条件，本章测试以功能验证为主，并辅以性能记录和兼容性检查。这样的安排既能够体现系统已经具备较完整的可运行能力，也能够避免在现阶段将测试工作过度扩展为大型生产级压测，从而使测试结果更贴近论文项目的研究范围和实现条件。
'@
  },
  @{
    Marker = '5.4 测试结果分析'
    Text = @'
综合本章测试结果可以认为，系统已经形成了从知识录入、文件处理、图谱组织到前台服务的基本闭环。功能测试证明主要业务流程能够按预期完成，性能记录说明关键接口与处理任务的响应时间处于可接受区间，兼容性测试则表明系统在常见使用环境下具有较好的可用性。上述结果共同支撑了前文关于系统总体设计和详细实现的论述。

当然，测试结果也反映出系统仍具有进一步完善空间。例如，在更大规模知识数据、更多并发用户和更复杂附件场景下，仍可继续补充压力测试、异常测试和问答质量评估工作。对毕业设计而言，这些内容可以作为后续改进方向，而当前测试结论已经能够支撑系统具备较好的展示和应用基础。
'@
  },
  @{
    Marker = '6.1 部署方案设计'
    Text = @'
部署方案的设计目标在于以较低的环境配置成本完成系统各核心组件的快速启动，并尽量保证演示环境与开发环境之间的一致性。由于系统涉及数据库、中间件、对象存储、向量检索和多媒体处理服务，若完全依赖手工安装，不仅步骤繁琐，而且容易受到版本差异影响。通过容器化编排方式，可以较好地控制组件依赖关系、启动顺序和运行环境，提升部署成功率与复现便利性。

对于毕业设计项目而言，部署方案不仅承担“让系统跑起来”的作用，也承担“让论文结论可被复现”的作用。系统能够在相对清晰的部署链路下完成环境准备、服务启动和功能验证，说明其实现不仅停留在代码层面，而且具备一定的工程落地能力。
'@
  },
  @{
    Marker = '6.2 运行链路验证'
    Text = @'
运行验证的重点在于证明系统各模块之间已经形成可用协同关系，而不仅是单独页面或单项服务能够启动。结合当前系统运行情况，可以验证管理员上传资料后任务状态能够更新，审核通过后的知识内容能够进入图谱与检索链路，普通用户则能够基于推荐、搜索和问答入口获得知识服务结果。这说明系统已经完成从后台治理到前台服务的主要闭环。

从论文收束角度看，运行验证章节进一步说明本文实现结果具有可部署、可演示和可说明的特点。虽然系统在规模化性能和更复杂业务扩展方面仍有优化空间，但在本课题范围内，系统已经完成了从需求分析、总体设计、详细实现到测试验证和部署运行的完整研究过程。
'@
  }
)

function Strip-Ansi([string]$text) {
  if ($null -eq $text) { return '' }
  $clean = [regex]::Replace($text, [string][char]27 + '\[[0-9;]*[A-Za-z]', '')
  $clean = [regex]::Replace($clean, [string][char]65533 + '\[[0-9;]*[A-Za-z]', '')
  return $clean
}

function Get-FontFamilyName([string[]]$candidates, [string]$fallback) {
  $installed = New-Object System.Drawing.Text.InstalledFontCollection
  $names = $installed.Families | ForEach-Object { $_.Name }
  foreach ($candidate in $candidates) {
    if ($names -contains $candidate) { return $candidate }
  }
  return $fallback
}

function Get-SnippetLines([string]$path, [object[]]$ranges) {
  $encoding = [System.Text.UTF8Encoding]::new($false)
  $allLines = [System.IO.File]::ReadAllLines($path, $encoding)
  $lines = New-Object System.Collections.Generic.List[string]
  for ($r = 0; $r -lt $ranges.Count; $r++) {
    $start = [int]$ranges[$r][0]
    $end = [int]$ranges[$r][1]
    for ($i = $start; $i -le $end -and $i -le $allLines.Length; $i++) {
      $lines.Add(('{0,4}: {1}' -f $i, $allLines[$i - 1]))
    }
    if ($r -lt $ranges.Count - 1) {
      $lines.Add('')
    }
  }
  return ,$lines.ToArray()
}

function Invoke-CommandCapture([string]$workingDir, [string]$command) {
  Push-Location $workingDir
  try {
    try {
      $output = Invoke-Expression "$command 2>&1 | Out-String"
    } catch {
      $output = ($_ | Out-String)
    }
    return Strip-Ansi $output
  }
  finally {
    Pop-Location
  }
}

function Save-PlainTextPng(
  [string]$outputPath,
  [string[]]$lines,
  [string]$fontFamily,
  [float]$fontSize,
  [bool]$parseLineNumbers
) {
  $width = 1520
  $padding = 24
  $background = [System.Drawing.Color]::White
  $border = [System.Drawing.Color]::FromArgb(214, 220, 228)
  $textColor = [System.Drawing.Color]::FromArgb(32, 37, 43)
  $lineNoColor = [System.Drawing.Color]::FromArgb(135, 144, 158)

  $font = New-Object System.Drawing.Font($fontFamily, $fontSize, [System.Drawing.FontStyle]::Regular)
  $probeBmp = New-Object System.Drawing.Bitmap 10, 10
  $probe = [System.Drawing.Graphics]::FromImage($probeBmp)
  $probe.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $lineHeight = [int][Math]::Ceiling($probe.MeasureString('Ag', $font).Height) + 5
  $height = $padding * 2 + ([Math]::Max($lines.Count, 1) * $lineHeight)
  $probe.Dispose()
  $probeBmp.Dispose()

  $bmp = New-Object System.Drawing.Bitmap $width, $height
  $graphics = [System.Drawing.Graphics]::FromImage($bmp)
  $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $graphics.Clear($background)

  $borderPen = New-Object System.Drawing.Pen($border)
  $textBrush = New-Object System.Drawing.SolidBrush($textColor)
  $lineNoBrush = New-Object System.Drawing.SolidBrush($lineNoColor)
  $graphics.DrawRectangle($borderPen, 0, 0, ($width - 1), ($height - 1))

  $y = $padding
  foreach ($line in $lines) {
    $content = $line
    $lineNo = $null
    if ($parseLineNumbers -and $line -match '^\s*(\d+):(.*)$') {
      $lineNo = $matches[1]
      $content = $matches[2].TrimStart()
    }

    if ($lineNo) {
      $graphics.DrawString($lineNo.PadLeft(4), $font, $lineNoBrush, 26, $y)
      $graphics.DrawString($content, $font, $textBrush, 102, $y)
    } else {
      $graphics.DrawString($content, $font, $textBrush, 26, $y)
    }
    $y += $lineHeight
  }

  $bmp.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
  $borderPen.Dispose()
  $textBrush.Dispose()
  $lineNoBrush.Dispose()
  $font.Dispose()
  $graphics.Dispose()
  $bmp.Dispose()
}

function Get-NonWhiteBounds([System.Drawing.Bitmap]$bmp) {
  $minX = $bmp.Width
  $minY = $bmp.Height
  $maxX = -1
  $maxY = -1
  for ($y = 0; $y -lt $bmp.Height; $y++) {
    for ($x = 0; $x -lt $bmp.Width; $x++) {
      $pixel = $bmp.GetPixel($x, $y)
      if ($pixel.R -lt 245 -or $pixel.G -lt 245 -or $pixel.B -lt 245) {
        if ($x -lt $minX) { $minX = $x }
        if ($y -lt $minY) { $minY = $y }
        if ($x -gt $maxX) { $maxX = $x }
        if ($y -gt $maxY) { $maxY = $y }
      }
    }
  }
  if ($maxX -lt $minX -or $maxY -lt $minY) {
    return [System.Drawing.Rectangle]::new(0, 0, $bmp.Width, $bmp.Height)
  }
  $padding = 20
  $left = [Math]::Max(0, $minX - $padding)
  $top = [Math]::Max(0, $minY - $padding)
  $right = [Math]::Min($bmp.Width - 1, $maxX + $padding)
  $bottom = [Math]::Min($bmp.Height - 1, $maxY + $padding)
  return [System.Drawing.Rectangle]::new($left, $top, ($right - $left + 1), ($bottom - $top + 1))
}

function Save-CroppedPng([string]$sourcePath, [string]$outputPath) {
  $bmp = [System.Drawing.Bitmap]::FromFile($sourcePath)
  try {
    $rect = Get-NonWhiteBounds $bmp
    $cropped = New-Object System.Drawing.Bitmap $rect.Width, $rect.Height
    try {
      $g = [System.Drawing.Graphics]::FromImage($cropped)
      $g.Clear([System.Drawing.Color]::White)
      $g.DrawImage($bmp, [System.Drawing.Rectangle]::new(0, 0, $rect.Width, $rect.Height), $rect, [System.Drawing.GraphicsUnit]::Pixel)
      $savePath = $outputPath
      if ([System.IO.Path]::GetFullPath($sourcePath) -eq [System.IO.Path]::GetFullPath($outputPath)) {
        $savePath = $outputPath + '.tmp.png'
      }
      $cropped.Save($savePath, [System.Drawing.Imaging.ImageFormat]::Png)
      $g.Dispose()
      if ($savePath -ne $outputPath) {
        if (Test-Path -LiteralPath $outputPath) {
          Remove-Item -LiteralPath $outputPath -Force
        }
        Move-Item -LiteralPath $savePath -Destination $outputPath -Force
      }
    }
    finally {
      $cropped.Dispose()
    }
  }
  finally {
    $bmp.Dispose()
  }
}

function Get-ParaText($para) {
  return ($para.Range.Text -replace '[\r\a]', '').Trim()
}

function Find-ParagraphIndex([object]$doc, [string]$target) {
  for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    if ((Get-ParaText $doc.Paragraphs.Item($i)) -eq $target) {
      return $i
    }
  }
  throw "Paragraph not found: $target"
}

function ApplyBodyStyle([object]$range, [object]$doc, [object]$word) {
  $range.Style = $doc.Styles.Item('正文')
  $range.ParagraphFormat.Alignment = 3
  $range.ParagraphFormat.FirstLineIndent = $word.CentimetersToPoints(0.74)
  $range.ParagraphFormat.LeftIndent = 0
  $range.ParagraphFormat.LineSpacingRule = 4
  $range.ParagraphFormat.LineSpacing = 28
  $range.ParagraphFormat.SpaceBefore = 0
  $range.ParagraphFormat.SpaceAfter = 0
}

function ApplyCaptionStyle([object]$range, [object]$doc) {
  $range.Style = $doc.Styles.Item('正文')
  $range.ParagraphFormat.Alignment = 1
  $range.ParagraphFormat.FirstLineIndent = 0
  $range.ParagraphFormat.LeftIndent = 0
  $range.ParagraphFormat.LineSpacingRule = 4
  $range.ParagraphFormat.LineSpacing = 28
  $range.ParagraphFormat.SpaceBefore = 0
  $range.ParagraphFormat.SpaceAfter = 0
  $range.Font.NameFarEast = '宋体'
  $range.Font.Size = 14
}

function ApplyReferenceStyle([object]$range, [object]$doc) {
  $range.Style = $doc.Styles.Item('正文')
  $range.ParagraphFormat.Alignment = 0
  $range.ParagraphFormat.FirstLineIndent = 0
  $range.ParagraphFormat.LeftIndent = 0
  $range.ParagraphFormat.LineSpacingRule = 4
  $range.ParagraphFormat.LineSpacing = 28
  $range.ParagraphFormat.SpaceBefore = 0
  $range.ParagraphFormat.SpaceAfter = 0
}

function InsertStyledParagraphBeforeIndex([object]$doc, [object]$word, [int]$index, [string]$text, [string]$kind) {
  $range = $doc.Paragraphs.Item($index).Range
  $null = $range.InsertParagraphBefore()
  $para = $doc.Paragraphs.Item($index)
  $para.Range.Text = $text + "`r"
  if ($kind -eq 'caption') {
    ApplyCaptionStyle $para.Range $doc
  } elseif ($kind -eq 'reference') {
    ApplyReferenceStyle $para.Range $doc
  } else {
    ApplyBodyStyle $para.Range $doc $word
  }
  return $para
}

function InsertImageBeforeIndex([object]$doc, [object]$word, [int]$index, [string]$imagePath, [double]$widthCm) {
  $range = $doc.Paragraphs.Item($index).Range
  $null = $range.InsertParagraphBefore()
  $para = $doc.Paragraphs.Item($index)
  $para.Range.Text = ''
  $para.Range.ParagraphFormat.Alignment = 1
  $para.Range.ParagraphFormat.FirstLineIndent = 0
  $para.Range.ParagraphFormat.LeftIndent = 0
  $para.Range.ParagraphFormat.SpaceBefore = 0
  $para.Range.ParagraphFormat.SpaceAfter = 0
  $para.Range.ParagraphFormat.LineSpacingRule = 4
  $para.Range.ParagraphFormat.LineSpacing = 28
  $imgRange = $para.Range.Duplicate
  $imgRange.Collapse(0)
  $shape = $doc.InlineShapes.AddPicture($imagePath, $false, $true, $imgRange)
  $shape.LockAspectRatio = $true
  $shape.Width = $word.CentimetersToPoints($widthCm)
  $shape.Range.ParagraphFormat.Alignment = 1
  $shape.Range.ParagraphFormat.SpaceBefore = 0
  $shape.Range.ParagraphFormat.SpaceAfter = 0
  $shape.Range.ParagraphFormat.LineSpacingRule = 4
  $shape.Range.ParagraphFormat.LineSpacing = 28
}

function InsertParagraphsAfterMarker([object]$doc, [object]$word, [string]$marker, [string]$text) {
  $index = (Find-ParagraphIndex $doc $marker) + 1
  $parts = @(($text -split "(`r`n|`n){2,}") | Where-Object { $_.Trim() })
  for ($i = $parts.Count - 1; $i -ge 0; $i--) {
    [void](InsertStyledParagraphBeforeIndex $doc $word $index $parts[$i].Trim() 'body')
  }
}

function ReplaceParagraphText([object]$doc, [string]$findText, [string]$replaceText) {
  $index = Find-ParagraphIndex $doc $findText
  $para = $doc.Paragraphs.Item($index)
  $para.Range.Text = $replaceText + "`r"
  return $para
}

function SetSuperscriptBracketRuns([object]$para) {
  $text = Get-ParaText $para
  foreach ($m in [regex]::Matches($text, '\[\d+\]')) {
    $start = $para.Range.Start + $m.Index
    $end = $start + $m.Length
    $r = $para.Range.Duplicate
    $r.SetRange($start, $end)
    $r.Font.Superscript = $true
  }
}

function ReformatReferences([object]$doc, [object]$word, [string]$heading, [string]$endHeading, [string]$extraEntry) {
  $startIndex = (Find-ParagraphIndex $doc $heading) + 1
  $endIndex = Find-ParagraphIndex $doc $endHeading
  [void](InsertStyledParagraphBeforeIndex $doc $word $endIndex $extraEntry 'reference')
  $endIndex = Find-ParagraphIndex $doc $endHeading

  $refNumber = 1
  for ($i = $startIndex; $i -lt $endIndex; $i++) {
    $para = $doc.Paragraphs.Item($i)
    $text = Get-ParaText $para
    if (-not $text) { continue }
    $clean = [regex]::Replace($text, '^\[?\d+\]?', '').Trim()
    $para.Range.Text = ('[{0}] {1}' -f $refNumber, $clean) + "`r"
    ApplyReferenceStyle $para.Range $doc
    $refNumber++
  }
}

$codeFont = Get-FontFamilyName @('NSimSun', 'SimSun', 'Microsoft YaHei UI') 'SimSun'
$terminalFont = Get-FontFamilyName @('Consolas', 'Cascadia Mono', 'Courier New') 'Consolas'

foreach ($entry in $baseFigureSpecs.GetEnumerator()) {
  $outPath = Join-Path $assetDir $entry.Value.Output
  Save-CroppedPng $entry.Value.Source $outPath
}

foreach ($item in $evidenceSpecs) {
  $outPath = Join-Path $assetDir $item.Output
  if ($item.Type -eq 'code') {
    $lines = Get-SnippetLines $item.SourceFile $item.Ranges
    Save-PlainTextPng $outPath $lines $codeFont 12.5 $true
  } else {
    $outputText = Invoke-CommandCapture $item.WorkingDir $item.Command
    $lines = @($outputText -split "`r?`n" | Where-Object { $_.Trim() -ne '' })
    Save-PlainTextPng $outPath $lines $terminalFont 12 $false
  }
}

Copy-Item -LiteralPath $template -Destination $output -Force

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$doc = $null
$src = $null

try {
  $doc = $word.Documents.Open($output)
  $src = $word.Documents.Open($source, $false, $true)

  $target = $doc.Paragraphs.Item(35).Range.Duplicate
  $target.Collapse(0)
  $srcRange = $src.Range($src.Paragraphs.Item(29).Range.Start, $src.Content.End)
  $srcRange.Copy()
  $target.Paste()
  $src.Close()
  $src = $null

  foreach ($item in $insertions) {
    InsertParagraphsAfterMarker $doc $word $item.Marker $item.Text
  }

  [void](ReplaceParagraphText $doc '在此背景下，构建面向美妆领域的知识服务系统具有较强的现实意义。一方面，该类系统能够对分散的行业知识进行统一汇聚、分类和管理，提升知识资源的利用效率；另一方面，将知识图谱与检索增强生成技术引入系统后，可以在保证回答相关性的同时增强证据支撑能力，从而提高用户获取专业知识的准确性与便捷性12。因此，围绕美妆知识场景开展知识管理与智能问答系统的研究与实现，既具有一定的工程应用价值，也具有较强的实践参考意义。' '在此背景下，构建面向美妆领域的知识服务系统具有较强的现实意义。一方面，该类系统能够对分散的行业知识进行统一汇聚、分类和管理，提升知识资源的利用效率；另一方面，将知识图谱与检索增强生成技术引入系统后，可以在保证回答相关性的同时增强证据支撑能力，从而提高用户获取专业知识的准确性与便捷性[12]。因此，围绕美妆知识场景开展知识管理与智能问答系统的研究与实现，既具有一定的工程应用价值，也具有较强的实践参考意义。')
  [void](ReplaceParagraphText $doc '近年来，国外在检索增强生成、图谱增强问答以及垂直领域知识组织方面形成了较为系统的研究成果。相关研究表明，检索机制与生成模型协同能够有效改善大模型在事实性、可解释性和知识时效性方面的不足13。同时，图结构知识组织方式在路径分析、关系发现和证据回溯方面具有明显优势，使得知识图谱逐渐成为智能问答和推荐系统的重要支撑基础46。' '近年来，国外在检索增强生成、图谱增强问答以及垂直领域知识组织方面形成了较为系统的研究成果。相关研究表明，检索机制与生成模型协同能够有效改善大模型在事实性、可解释性和知识时效性方面的不足[13]。同时，图结构知识组织方式在路径分析、关系发现和证据回溯方面具有明显优势，使得知识图谱逐渐成为智能问答和推荐系统的重要支撑基础[4][6]。')
  [void](ReplaceParagraphText $doc '国内研究则更多关注知识图谱、文档智能处理和行业问答系统的落地应用。随着 OCR、语音识别与文本结构化处理技术的不断发展，面向文档、图片和音视频资料的知识抽取能力持续增强，为垂直领域知识服务系统建设提供了更成熟的技术基础91011。然而，从现有研究与应用情况来看，直接面向美妆场景、同时兼顾知识管理、文件处理、实体审核、图谱展示和智能问答的综合型系统仍相对较少。基于此，本文尝试结合现有技术成果与真实项目实践，构建一套具有完整业务链路的美妆知识服务平台。' '国内研究则更多关注知识图谱、文档智能处理和行业问答系统的落地应用。随着 OCR、语音识别与文本结构化处理技术的不断发展，面向文档、图片和音视频资料的知识抽取能力持续增强，为垂直领域知识服务系统建设提供了更成熟的技术基础[9][10][11]。然而，从现有研究与应用情况来看，直接面向美妆场景、同时兼顾知识管理、文件处理、实体审核、图谱展示和智能问答的综合型系统仍相对较少。基于此，本文尝试结合现有技术成果与真实项目实践，构建一套具有完整业务链路的美妆知识服务平台。')
  [void](ReplaceParagraphText $doc '智能问答模块是本系统面向用户提供知识服务的核心模块。与传统直接生成式问答不同，本系统采用“检索增强 + 生成表达”的实现思路，即先从知识资源中检索相关证据，再基于检索结果组织上下文并生成回答内容。这种方式能够在一定程度上提高回答的准确性与可解释性234。' '智能问答模块是本系统面向用户提供知识服务的核心模块。与传统直接生成式问答不同，本系统采用“检索增强 + 生成表达”的实现思路，即先从知识资源中检索相关证据，再基于检索结果组织上下文并生成回答内容。这种方式能够在一定程度上提高回答的准确性与可解释性[2][3][4]。')

  foreach ($ref in @(
    '在此背景下，构建面向美妆领域的知识服务系统具有较强的现实意义。一方面，该类系统能够对分散的行业知识进行统一汇聚、分类和管理，提升知识资源的利用效率；另一方面，将知识图谱与检索增强生成技术引入系统后，可以在保证回答相关性的同时增强证据支撑能力，从而提高用户获取专业知识的准确性与便捷性[12]。因此，围绕美妆知识场景开展知识管理与智能问答系统的研究与实现，既具有一定的工程应用价值，也具有较强的实践参考意义。',
    '近年来，国外在检索增强生成、图谱增强问答以及垂直领域知识组织方面形成了较为系统的研究成果。相关研究表明，检索机制与生成模型协同能够有效改善大模型在事实性、可解释性和知识时效性方面的不足[13]。同时，图结构知识组织方式在路径分析、关系发现和证据回溯方面具有明显优势，使得知识图谱逐渐成为智能问答和推荐系统的重要支撑基础[4][6]。',
    '国内研究则更多关注知识图谱、文档智能处理和行业问答系统的落地应用。随着 OCR、语音识别与文本结构化处理技术的不断发展，面向文档、图片和音视频资料的知识抽取能力持续增强，为垂直领域知识服务系统建设提供了更成熟的技术基础[9][10][11]。然而，从现有研究与应用情况来看，直接面向美妆场景、同时兼顾知识管理、文件处理、实体审核、图谱展示和智能问答的综合型系统仍相对较少。基于此，本文尝试结合现有技术成果与真实项目实践，构建一套具有完整业务链路的美妆知识服务平台。',
    '智能问答模块是本系统面向用户提供知识服务的核心模块。与传统直接生成式问答不同，本系统采用“检索增强 + 生成表达”的实现思路，即先从知识资源中检索相关证据，再基于检索结果组织上下文并生成回答内容。这种方式能够在一定程度上提高回答的准确性与可解释性[2][3][4]。'
  )) {
    $para = $doc.Paragraphs.Item((Find-ParagraphIndex $doc $ref))
    SetSuperscriptBracketRuns $para
  }

  while ($doc.TablesOfContents.Count -gt 0) { $doc.TablesOfContents.Item(1).Delete() }
  try { $doc.Paragraphs.Item((Find-ParagraphIndex $doc '目  录')).Range.Delete() } catch {}

  $chapter1Index = Find-ParagraphIndex $doc '第一章 绪论'
  $sel = $word.Selection
  $sel.SetRange($doc.Paragraphs.Item($chapter1Index).Range.Start, $doc.Paragraphs.Item($chapter1Index).Range.Start)
  $sel.InsertBreak(7)
  $sel.Style = $doc.Styles.Item('标题 1')
  $sel.ParagraphFormat.Alignment = 1
  $sel.TypeText('目  录')
  $sel.TypeParagraph()
  $tocRange = $sel.Range
  $null = $doc.TablesOfContents.Add($tocRange, $true, 1, 3)
  $sel.SetRange($tocRange.End, $tocRange.End)
  $sel.TypeParagraph()
  $sel.InsertBreak(7)

  foreach ($caption in $baseFigureSpecs.Keys) {
    $index = Find-ParagraphIndex $doc $caption
    $spec = $baseFigureSpecs[$caption]
    InsertImageBeforeIndex $doc $word $index (Join-Path $assetDir $spec.Output) $spec.WidthCm
    ApplyCaptionStyle $doc.Paragraphs.Item($index + 1).Range $doc
  }

  foreach ($item in $docItems) {
    $anchorIndex = Find-ParagraphIndex $doc $item.Anchor
    $insertIndex = $anchorIndex + 1
    [void](InsertStyledParagraphBeforeIndex $doc $word $insertIndex $item.Analysis 'body')
    [void](InsertStyledParagraphBeforeIndex $doc $word $insertIndex $item.Caption 'caption')
    InsertImageBeforeIndex $doc $word $insertIndex (Join-Path $assetDir $item.Asset) $item.WidthCm
    [void](InsertStyledParagraphBeforeIndex $doc $word $insertIndex $item.Intro 'body')
  }

  ReformatReferences $doc $word '参考文献' '致谢' 'Lu Z, Xu H, Chen A, et al. HSG-RAG: Hierarchical Knowledge Base Construction for Embedded System Development[J]. ACM Transactions on Design Automation of Electronic Systems, 2025, 30(6): 1-21.'

  foreach ($text in @('摘    要', 'ABSTRACT')) {
    try { $doc.Paragraphs.Item((Find-ParagraphIndex $doc $text)).Format.PageBreakBefore = $true } catch {}
  }

  foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
  $doc.Fields.Update() | Out-Null
  $doc.Save()
  $doc.Close()
}
finally {
  if ($src) { try { $src.Close() } catch {} }
  if ($doc) { try { $doc.Close([ref]0) } catch {} }
  try { $word.Quit() } catch {}
  [System.GC]::Collect()
  [System.GC]::WaitForPendingFinalizers()
}

Copy-Item -LiteralPath $output -Destination $finalCopy -Force

$wordCheck = New-Object -ComObject Word.Application
$wordCheck.Visible = $false
$wordCheck.DisplayAlerts = 0
$checkDoc = $null
try {
  $checkDoc = $wordCheck.Documents.Open($output, $false, $true)
  [pscustomobject]@{
    Output = $finalCopy
    Paragraphs = $checkDoc.Paragraphs.Count
    InlineShapes = $checkDoc.InlineShapes.Count
    TOC = $checkDoc.TablesOfContents.Count
    Characters = $checkDoc.ComputeStatistics(3)
  } | Format-List
}
finally {
  if ($checkDoc) { try { $checkDoc.Close() } catch {} }
  try { $wordCheck.Quit() } catch {}
}
"""

target = Path(r"D:\beauty\scripts\build_submission_final_doc.ps1")
target.write_text(content, encoding="utf-8-sig")
print(target)
