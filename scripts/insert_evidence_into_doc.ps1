$ErrorActionPreference = 'Stop'

$docPath = 'D:\beauty\thesis_final_evidence.docx'
$assetDir = 'D:\beauty\evidence_assets'

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

function ApplyBodyStyle([object]$doc, [object]$word, [object]$range) {
  $range.Style = $doc.Styles.Item('正文')
  $range.ParagraphFormat.Alignment = 3
  $range.ParagraphFormat.FirstLineIndent = $word.CentimetersToPoints(0.74)
  $range.ParagraphFormat.LineSpacingRule = 4
  $range.ParagraphFormat.LineSpacing = 28
  $range.ParagraphFormat.SpaceBefore = 0
  $range.ParagraphFormat.SpaceAfter = 0
}

function ApplyCaptionStyle([object]$doc, [object]$range) {
  $range.Style = $doc.Styles.Item('正文')
  $range.ParagraphFormat.Alignment = 1
  $range.ParagraphFormat.FirstLineIndent = 0
  $range.ParagraphFormat.LineSpacingRule = 4
  $range.ParagraphFormat.LineSpacing = 28
  $range.ParagraphFormat.SpaceBefore = 0
  $range.ParagraphFormat.SpaceAfter = 0
  $range.Font.NameFarEast = '宋体'
  $range.Font.Size = 14
}

function InsertParagraphBeforeIndex([object]$doc, [object]$word, [int]$index, [string]$text, [string]$kind) {
  $range = $doc.Paragraphs.Item($index).Range
  $null = $range.InsertParagraphBefore()
  $para = $doc.Paragraphs.Item($index)
  $para.Range.Text = $text + "`r"
  if ($kind -eq 'caption') {
    ApplyCaptionStyle $doc $para.Range
  } else {
    ApplyBodyStyle $doc $word $para.Range
  }
}

function InsertImageBeforeIndex([object]$doc, [object]$word, [int]$index, [string]$imagePath, [double]$widthCm = 13.5) {
  $range = $doc.Paragraphs.Item($index).Range
  $null = $range.InsertParagraphBefore()
  $para = $doc.Paragraphs.Item($index)
  $imgRange = $para.Range.Duplicate
  $imgRange.Text = ''
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

function InsertImageBlockAfterAnchor(
  [object]$doc,
  [object]$word,
  [string]$anchor,
  [string]$introText,
  [string]$imagePath,
  [string]$caption,
  [string]$analysisText,
  [double]$widthCm = 13.5
) {
  $index = (Find-ParagraphIndex $doc $anchor) + 1
  InsertParagraphBeforeIndex $doc $word $index $analysisText 'body'
  InsertParagraphBeforeIndex $doc $word $index $caption 'caption'
  InsertImageBeforeIndex $doc $word $index $imagePath $widthCm
  InsertParagraphBeforeIndex $doc $word $index $introText 'body'
}

$blocks = @(
  @{
    Anchor = '图 4-4 文件处理模块流程图'
    Intro = 'Figure 4-7 shows the process task status flow code.'
    Image = (Join-Path $assetDir 'fig_4_7_process_task_code.png')
    Caption = '图 4-7 文件处理状态流转代码截图'
    Analysis = 'This code reflects staged task management for file processing.'
  },
  @{
    Anchor = '图 4-5 知识图谱查询流程图'
    Intro = 'Figure 4-8 shows the graph query construction code.'
    Image = (Join-Path $assetDir 'fig_4_8_graph_query_code.png')
    Caption = '图 4-8 知识图谱查询构建代码截图'
    Analysis = 'This code shows how nodes and edges are aggregated.'
  },
  @{
    Anchor = '图 4-6 智能问答模块流程图'
    Intro = 'Figure 4-9 shows the streaming chat interface code.'
    Image = (Join-Path $assetDir 'fig_4_9_chat_stream_code.png')
    Caption = '图 4-9 智能问答流式接口代码截图'
    Analysis = 'This code demonstrates unified handling of chat and attachments.'
  },
  @{
    Anchor = '图 5-2 兼容性测试结果图'
    Intro = 'Figure 5-3 shows the backend validation result.'
    Image = (Join-Path $assetDir 'fig_5_3_backend_validate_terminal.png')
    Caption = '图 5-3 后端工程校验结果截图'
    Analysis = 'The result indicates the backend project passes base validation.'
  },
  @{
    Anchor = '图 5-3 后端工程校验结果截图'
    Intro = 'Figure 5-4 shows the frontend production build result.'
    Image = (Join-Path $assetDir 'fig_5_4_frontend_build_terminal.png')
    Caption = '图 5-4 前端生产构建结果截图'
    Analysis = 'The result indicates the frontend can generate deployable assets.'
  },
  @{
    Anchor = '6.2 运行链路验证'
    Intro = 'Figure 6-1 shows the frontend build output listing.'
    Image = (Join-Path $assetDir 'fig_6_1_dist_output_terminal.png')
    Caption = '图 6-1 前端构建产物生成结果截图'
    Analysis = 'The listing serves as extra evidence for deployment verification.'
  }
)

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

try {
  $doc = $word.Documents.Open($docPath)
  foreach ($block in $blocks) {
    InsertImageBlockAfterAnchor $doc $word $block.Anchor $block.Intro $block.Image $block.Caption $block.Analysis
  }
  for ($i = 1; $i -le $doc.TablesOfContents.Count; $i++) {
    $doc.TablesOfContents.Item($i).Update()
  }
  $doc.Save()
  $doc.Close()
}
finally {
  if ($doc) { try { $doc.Close([ref]0) } catch {} }
  try { $word.Quit() } catch {}
}

'DONE'
