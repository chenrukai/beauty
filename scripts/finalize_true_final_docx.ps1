$ErrorActionPreference = 'Stop'

$root = 'D:\beauty'
$source = Join-Path $root '毕业论文_完整草稿_按材料修订_补图版.docx'
$output = Join-Path $root '毕业论文_最终稿_终版.docx'
$pngDir = Join-Path $root '论文图表素材\png_for_word'

$figureMap = [ordered]@{
  '图 2-1 系统业务流程图' = (Join-Path $pngDir 'fig_2_1_business_flow.png')
  '图 2-2 普通用户用例图' = (Join-Path $pngDir 'fig_2_2_user_usecase.png')
  '图 2-3 后台管理员用例图' = (Join-Path $pngDir 'fig_2_3_admin_usecase.png')
  '图 4-1 系统详细设计模块协作图' = (Join-Path $pngDir 'fig_4_1_detail_collaboration.png')
  '图 4-2 用户端页面跳转关系图' = (Join-Path $pngDir 'fig_4_2_frontend_navigation.png')
  '图 4-3 知识管理模块处理流程图' = (Join-Path $pngDir 'fig_4_3_knowledge_manage_flow.png')
  '图 4-4 文件处理模块流程图' = (Join-Path $pngDir 'fig_4_4_file_processing_flow.png')
  '图 4-5 知识图谱查询流程图' = (Join-Path $pngDir 'fig_4_5_graph_query_flow.png')
  '图 4-6 智能问答模块流程图' = (Join-Path $pngDir 'fig_4_6_qa_flow.png')
  '图 5-1 性能测试记录图' = (Join-Path $pngDir 'fig_5_1_performance_record.png')
  '图 5-2 兼容性测试结果图' = (Join-Path $pngDir 'fig_5_2_compatibility_result.png')
}

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

function Get-ParaText($para) {
  return ($para.Range.Text -replace '[\r\a]', '').Trim()
}

function Find-ParagraphIndex([object]$doc, [string]$target) {
  for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $text = Get-ParaText $doc.Paragraphs.Item($i)
    if ($text -eq $target) { return $i }
  }
  throw "Paragraph not found: $target"
}

function Insert-ParagraphsAfterMarker([object]$doc, [string]$marker, [string]$text) {
  $index = Find-ParagraphIndex $doc $marker
  $parts = ($text -split "(`r`n|`n){2,}") | Where-Object { $_.Trim() }
  $para = $doc.Paragraphs.Item($index)
  $sel = $word.Selection
  $sel.SetRange($para.Range.End, $para.Range.End)
  foreach ($part in $parts) {
    $sel.TypeParagraph()
    $sel.Style = $doc.Styles.Item('正文')
    $sel.ParagraphFormat.Alignment = 3
    $sel.ParagraphFormat.FirstLineIndent = $word.CentimetersToPoints(0.74)
    $sel.ParagraphFormat.LineSpacingRule = 4
    $sel.ParagraphFormat.LineSpacing = 28
    $sel.TypeText($part.Trim())
  }
}

function Ensure-FigureCaptionsAfterAnchor([object]$doc, [string]$anchorHeading, [string[]]$captions) {
  $missing = @()
  foreach ($caption in $captions) {
    try {
      [void](Find-ParagraphIndex $doc $caption)
    } catch {
      $missing += $caption
    }
  }
  if ($missing.Count -eq 0) { return }
  $index = Find-ParagraphIndex $doc $anchorHeading
  $para = $doc.Paragraphs.Item($index)
  $sel = $word.Selection
  $sel.SetRange($para.Range.End, $para.Range.End)
  foreach ($caption in $captions) {
    if ($missing -notcontains $caption) { continue }
    $sel.TypeParagraph()
    $sel.Style = $doc.Styles.Item('正文')
    $sel.ParagraphFormat.Alignment = 1
    $sel.Font.NameFarEast = '宋体'
    $sel.Font.Size = 14
    $sel.TypeText($caption)
  }
}

function Insert-BlockAfterAnchor([object]$doc, [string]$anchorHeading, [string[]]$captions, [string[]]$paragraphs) {
  $index = Find-ParagraphIndex $doc $anchorHeading
  $para = $doc.Paragraphs.Item($index)
  $sel = $word.Selection
  $sel.SetRange($para.Range.End, $para.Range.End)
  foreach ($caption in $captions) {
    $sel.TypeParagraph()
    $sel.Style = $doc.Styles.Item('正文')
    $sel.ParagraphFormat.Alignment = 1
    $sel.Font.NameFarEast = '宋体'
    $sel.Font.Size = 14
    $sel.TypeText($caption)
  }
  foreach ($paragraph in $paragraphs) {
    $sel.TypeParagraph()
    $sel.Style = $doc.Styles.Item('正文')
    $sel.ParagraphFormat.Alignment = 3
    $sel.ParagraphFormat.FirstLineIndent = $word.CentimetersToPoints(0.74)
    $sel.ParagraphFormat.LineSpacingRule = 4
    $sel.ParagraphFormat.LineSpacing = 28
    $sel.TypeText($paragraph)
  }
}

Copy-Item -LiteralPath $source -Destination $output -Force

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

try {
  $doc = $word.Documents.Open($output)

  for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $para = $doc.Paragraphs.Item($i)
    $text = Get-ParaText $para
    if ($text -match '^第[一二三四五六七八九十]+章') {
      $para.Range.Style = $doc.Styles.Item('标题 1')
      $para.Range.ParagraphFormat.Alignment = 1
    } elseif ($text -in @('摘    要', '摘 要', 'ABSTRACT', '结论', '参考文献', '致谢', '目  录', '目录')) {
      $para.Range.Style = $doc.Styles.Item('标题 1')
      $para.Range.ParagraphFormat.Alignment = 1
    } elseif ($text -match '^\d+\.\d+\s') {
      $para.Range.Style = $doc.Styles.Item('标题 2')
      $para.Range.ParagraphFormat.Alignment = 0
    } elseif ($text -match '^\d+\.\d+\.\d+\s') {
      $para.Range.Style = $doc.Styles.Item('标题 3')
      $para.Range.ParagraphFormat.Alignment = 0
    }
  }

  Insert-BlockAfterAnchor $doc '2.1 业务场景分析' @('图 2-1 系统业务流程图') @(
    '如图 2-1 所示，系统业务流程围绕“资料接入—自动处理—人工确认—知识服务”四个阶段展开。首先，管理员从后台录入知识条目或上传原始资料，系统将资料统一纳入待处理队列；随后，平台根据文件类型选择文本解析、OCR 识别或语音转写等处理方式，并进一步完成文本切分、元数据整理和候选实体抽取；在自动处理完成后，管理员需对关键实体、关系及知识条目状态进行审核，以保证后续入库内容的准确性和可解释性；最终，经过整理后的知识资源进入前台推荐、检索、收藏、图谱查询和智能问答等服务链路。该流程不仅体现了系统从原始资料到知识服务的转化逻辑，也为后续章节关于详细设计和系统测试的描述提供了统一主线。'
  )
  Insert-BlockAfterAnchor $doc '5.3 性能测试与兼容性测试' @('图 5-1 性能测试记录图', '图 5-2 兼容性测试结果图') @(
    '在性能测试方面，本文重点关注知识检索、问答首段返回和文件处理任务状态更新等关键环节的响应情况。由于这些操作直接影响用户体验和系统演示效果，因此对其进行持续记录具有现实意义。结合当前演示环境的测试结果可以看出，普通查询与后台管理操作能够在较短时间内完成响应，而问答和文件处理等较复杂链路的耗时也保持在可接受范围内，说明系统在毕业设计场景下具备较好的运行稳定性。',
    '在兼容性测试方面，本文主要考察不同主流浏览器和常见终端环境下的页面布局、模块交互和会话流程是否保持一致。测试结果表明，用户端首页浏览、知识详情、搜索问答以及后台管理页中的列表筛选、任务监控和实体确认等核心功能在主流桌面浏览器下均能正常使用，移动端浏览器虽然在版式细节上存在一定压缩，但核心展示与交互流程保持可用，能够满足毕业设计演示需要。'
  )

  foreach ($item in $insertions) {
    Insert-ParagraphsAfterMarker $doc $item.Marker $item.Text
  }

  $chapter1Index = Find-ParagraphIndex $doc '第一章 绪论'
  $chapter1Para = $doc.Paragraphs.Item($chapter1Index)
  $sel = $word.Selection
  $sel.SetRange($chapter1Para.Range.Start, $chapter1Para.Range.Start)
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

  $captions = @()
  for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $text = Get-ParaText $doc.Paragraphs.Item($i)
    if ($figureMap.Contains($text)) {
      $captions += [pscustomobject]@{ Index = $i; Caption = $text; Path = $figureMap[$text] }
    }
  }

  $captions = $captions | Sort-Object Index -Descending
  foreach ($item in $captions) {
    if (-not (Test-Path -LiteralPath $item.Path)) { throw "Missing figure: $($item.Path)" }
    $captionPara = $doc.Paragraphs.Item($item.Index)
    $sel = $word.Selection
    $sel.SetRange($captionPara.Range.Start, $captionPara.Range.Start)
    $sel.TypeParagraph()
    $shape = $doc.InlineShapes.AddPicture($item.Path, $false, $true, $sel.Range)
    $shape.LockAspectRatio = $true
    $shape.Width = $word.CentimetersToPoints(13.5)
    $shape.Range.ParagraphFormat.Alignment = 1
    $shape.Range.ParagraphFormat.SpaceBefore = 0
    $shape.Range.ParagraphFormat.SpaceAfter = 0
    $captionPara.Range.ParagraphFormat.Alignment = 1
    $captionPara.Range.Font.NameFarEast = '宋体'
    $captionPara.Range.Font.Size = 14
  }

  for ($i = 1; $i -le $doc.TablesOfContents.Count; $i++) {
    $doc.TablesOfContents.Item($i).Update()
  }
  $doc.Fields.Update() | Out-Null

  $doc.Save()
  $doc.Close()
} finally {
  if ($word -ne $null) { $word.Quit() }
  [System.GC]::Collect()
  [System.GC]::WaitForPendingFinalizers()
}

Write-Output $output
