$ErrorActionPreference = 'Stop'

$root = 'D:\beauty'
$source = Join-Path $root '毕业论文_最终稿_模板优先修复版.docx'
$output = Join-Path $root 'thesis_final_evidence.docx'
$assetDir = Join-Path $root 'evidence_assets'
$backendDir = Join-Path $root 'beauty-knowledge-backend'
$frontendDir = Join-Path $root 'beauty-knowledge-frontend'

Add-Type -AssemblyName System.Drawing

$codeBg = [System.Drawing.Color]::FromArgb(250, 250, 252)
$terminalBg = [System.Drawing.Color]::FromArgb(247, 249, 252)

New-Item -ItemType Directory -Force -Path $assetDir | Out-Null

function Strip-Ansi([string]$text) {
  if ($null -eq $text) { return '' }
  return ([regex]::Replace($text, "`e\[[0-9;]*[A-Za-z]", ''))
}

function Get-FileSnippet([string]$path, [int]$start, [int]$end) {
  $lines = Get-Content -LiteralPath $path
  $result = New-Object System.Collections.Generic.List[string]
  for ($i = $start; $i -le $end -and $i -le $lines.Count; $i++) {
    $result.Add(('{0,4}: {1}' -f $i, $lines[$i - 1]))
  }
  return ,$result.ToArray()
}

function New-TextScreenshot(
  [string]$outputPath,
  [string]$title,
  [string]$subtitle,
  [string[]]$lines,
  [System.Drawing.Color]$background
) {
  $width = 1560
  $padding = 42
  $titleFont = New-Object System.Drawing.Font('Microsoft YaHei UI', 22, [System.Drawing.FontStyle]::Bold)
  $subFont = New-Object System.Drawing.Font('Microsoft YaHei UI', 11)
  $codeFont = New-Object System.Drawing.Font('Consolas', 14)
  $probe = New-Object System.Drawing.Bitmap 10, 10
  $gProbe = [System.Drawing.Graphics]::FromImage($probe)
  $gProbe.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
  $lineHeight = [int][Math]::Ceiling($gProbe.MeasureString('Ag', $codeFont).Height) + 5
  $titleHeight = [int][Math]::Ceiling($gProbe.MeasureString($title, $titleFont).Height)
  $subHeight = [int][Math]::Ceiling($gProbe.MeasureString($subtitle, $subFont).Height)
  $bodyHeight = [Math]::Max(1, $lines.Count) * $lineHeight
  $height = $padding * 2 + $titleHeight + $subHeight + 24 + $bodyHeight + 18
  $gProbe.Dispose()
  $probe.Dispose()

  $bmp = New-Object System.Drawing.Bitmap $width, $height
  $graphics = [System.Drawing.Graphics]::FromImage($bmp)
  $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
  $graphics.Clear($background)

  $panelBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 255, 255))
  $shadowBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(16, 0, 0, 0))
  $titleBrush = [System.Drawing.Brushes]::Black
  $subBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(92, 99, 112))
  $codeBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(33, 37, 41))
  $lineNoBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(128, 137, 150))
  $borderPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(220, 228, 236))
  $dividerPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(232, 238, 244))

  $panelRect = New-Object System.Drawing.Rectangle 28, 28, ($width - 56), ($height - 56)
  $shadowRect = New-Object System.Drawing.Rectangle 34, 34, ($width - 56), ($height - 56)
  $graphics.FillRectangle($shadowBrush, $shadowRect)
  $graphics.FillRectangle($panelBrush, $panelRect)
  $graphics.DrawRectangle($borderPen, $panelRect)

  $graphics.DrawString($title, $titleFont, $titleBrush, 58, 52)
  $graphics.DrawString($subtitle, $subFont, $subBrush, 60, (58 + $titleHeight))
  $dividerY = 58 + $titleHeight + $subHeight + 18
  $graphics.DrawLine($dividerPen, 56, $dividerY, ($width - 56), $dividerY)

  $y = $dividerY + 18
  foreach ($line in $lines) {
    $lineNo = ''
    $content = $line
    if ($line -match '^\s*(\d+):(.*)$') {
      $lineNo = $matches[1]
      $content = $matches[2].TrimStart()
    }
    if ($lineNo) {
      $graphics.DrawString($lineNo.PadLeft(4), $codeFont, $lineNoBrush, 62, $y)
      $graphics.DrawString($content, $codeFont, $codeBrush, 132, $y)
    } else {
      $graphics.DrawString($content, $codeFont, $codeBrush, 62, $y)
    }
    $y += $lineHeight
  }

  $bmp.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)

  $borderPen.Dispose()
  $dividerPen.Dispose()
  $panelBrush.Dispose()
  $shadowBrush.Dispose()
  $subBrush.Dispose()
  $codeBrush.Dispose()
  $lineNoBrush.Dispose()
  $titleFont.Dispose()
  $subFont.Dispose()
  $codeFont.Dispose()
  $graphics.Dispose()
  $bmp.Dispose()
}

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

function ApplyBodyStyle([object]$range) {
  $range.Style = $doc.Styles.Item('正文')
  $range.ParagraphFormat.Alignment = 3
  $range.ParagraphFormat.FirstLineIndent = $word.CentimetersToPoints(0.74)
  $range.ParagraphFormat.LineSpacingRule = 4
  $range.ParagraphFormat.LineSpacing = 28
  $range.ParagraphFormat.SpaceBefore = 0
  $range.ParagraphFormat.SpaceAfter = 0
}

function ApplyCaptionStyle([object]$range) {
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

function InsertParagraphBeforeIndex([int]$index, [string]$text, [string]$kind) {
  $range = $doc.Paragraphs.Item($index).Range
  $null = $range.InsertParagraphBefore()
  $para = $doc.Paragraphs.Item($index)
  $para.Range.Text = $text + "`r"
  if ($kind -eq 'caption') {
    ApplyCaptionStyle $para.Range
  } else {
    ApplyBodyStyle $para.Range
  }
}

function InsertImageBeforeIndex([int]$index, [string]$imagePath, [double]$widthCm = 13.5) {
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
  [string]$anchor,
  [string]$introText,
  [string]$imagePath,
  [string]$caption,
  [string]$analysisText,
  [double]$widthCm = 13.5
) {
  $index = (Find-ParagraphIndex $doc $anchor) + 1
  InsertParagraphBeforeIndex $index $analysisText 'body'
  InsertParagraphBeforeIndex $index $caption 'caption'
  InsertImageBeforeIndex $index $imagePath $widthCm
  InsertParagraphBeforeIndex $index $introText 'body'
}

$chatController = Join-Path $backendDir 'src\main\java\com\beauty\knowledge\module\rag\controller\ChatController.java'
$taskService = Join-Path $backendDir 'src\main\java\com\beauty\knowledge\module\pipeline\service\ProcessTaskService.java'
$graphService = Join-Path $backendDir 'src\main\java\com\beauty\knowledge\module\kg\service\KgQueryService.java'

Push-Location $backendDir
try {
  $backendValidateOutput = (& mvn -DskipTests validate 2>&1 | Out-String)
}
finally {
  Pop-Location
}

Push-Location $frontendDir
try {
  $frontendBuildOutput = (& npm run build 2>&1 | Out-String)
}
finally {
  Pop-Location
}
$distOutput = (& Get-ChildItem (Join-Path $frontendDir 'dist') -Recurse | Select-Object FullName,Length | Format-Table -AutoSize | Out-String)

$assets = @(
  @{
    Path = (Join-Path $assetDir 'fig_4_7_process_task_code.png')
    Title = 'Figure 4-7 Process Task Code'
    Subtitle = 'Source: ProcessTaskService.java lines 22-77'
    Lines = (Get-FileSnippet $taskService 22 77)
    Bg = $codeBg
  },
  @{
    Path = (Join-Path $assetDir 'fig_4_8_graph_query_code.png')
    Title = 'Figure 4-8 Graph Query Code'
    Subtitle = 'Source: KgQueryService.java lines 52-120'
    Lines = (Get-FileSnippet $graphService 52 120)
    Bg = $codeBg
  },
  @{
    Path = (Join-Path $assetDir 'fig_4_9_chat_stream_code.png')
    Title = 'Figure 4-9 Chat Stream Code'
    Subtitle = 'Source: ChatController.java lines 47-123'
    Lines = (Get-FileSnippet $chatController 47 123)
    Bg = $codeBg
  },
  @{
    Path = (Join-Path $assetDir 'fig_5_3_backend_validate_terminal.png')
    Title = 'Figure 5-3 Backend Validate Result'
    Subtitle = 'Source: mvn -DskipTests validate'
    Lines = @((Strip-Ansi $backendValidateOutput) -split "`r?`n" | Where-Object { $_ -ne '' })
    Bg = $terminalBg
  },
  @{
    Path = (Join-Path $assetDir 'fig_5_4_frontend_build_terminal.png')
    Title = 'Figure 5-4 Frontend Build Result'
    Subtitle = 'Source: npm run build'
    Lines = @((Strip-Ansi $frontendBuildOutput) -split "`r?`n" | Where-Object { $_ -ne '' })
    Bg = $terminalBg
  },
  @{
    Path = (Join-Path $assetDir 'fig_6_1_dist_output_terminal.png')
    Title = 'Figure 6-1 Build Output Listing'
    Subtitle = 'Source: frontend dist directory'
    Lines = @((Strip-Ansi $distOutput) -split "`r?`n" | Where-Object { $_ -ne '' })
    Bg = $terminalBg
  }
)

foreach ($asset in $assets) {
  New-TextScreenshot -outputPath $asset.Path -title $asset.Title -subtitle $asset.Subtitle -lines $asset.Lines -background $asset.Bg
}

$intro447 = 'Figure 4-7 shows the process task status flow code.'
$analysis447 = 'This code reflects staged task management for file processing.'
$intro448 = 'Figure 4-8 shows the graph query construction code.'
$analysis448 = 'This code shows how nodes and edges are aggregated.'
$intro449 = 'Figure 4-9 shows the streaming chat interface code.'
$analysis449 = 'This code demonstrates unified handling of chat and attachments.'
$intro53 = 'Figure 5-3 shows the backend validation result.'
$analysis53 = 'The result indicates the backend project passes base validation.'
$intro54 = 'Figure 5-4 shows the frontend production build result.'
$analysis54 = 'The result indicates the frontend can generate deployable assets.'
$intro61 = 'Figure 6-1 shows the frontend build output listing.'
$analysis61 = 'The listing serves as extra evidence for deployment verification.'

Copy-Item -LiteralPath $source -Destination $output -Force

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

try {
  $doc = $word.Documents.Open($output)

  InsertImageBlockAfterAnchor `
    '图 4-4 文件处理模块流程图' `
    $intro447 `
    (Join-Path $assetDir 'fig_4_7_process_task_code.png') `
    '图 4-7 文件处理状态流转代码截图' `
    $analysis447

  InsertImageBlockAfterAnchor `
    '图 4-5 知识图谱查询流程图' `
    $intro448 `
    (Join-Path $assetDir 'fig_4_8_graph_query_code.png') `
    '图 4-8 知识图谱查询构建代码截图' `
    $analysis448

  InsertImageBlockAfterAnchor `
    '图 4-6 智能问答模块流程图' `
    $intro449 `
    (Join-Path $assetDir 'fig_4_9_chat_stream_code.png') `
    '图 4-9 智能问答流式接口代码截图' `
    $analysis449

  InsertImageBlockAfterAnchor `
    '图 5-2 兼容性测试结果图' `
    $intro53 `
    (Join-Path $assetDir 'fig_5_3_backend_validate_terminal.png') `
    '图 5-3 后端工程校验结果截图' `
    $analysis53

  InsertImageBlockAfterAnchor `
    '图 5-3 后端工程校验结果截图' `
    $intro54 `
    (Join-Path $assetDir 'fig_5_4_frontend_build_terminal.png') `
    '图 5-4 前端生产构建结果截图' `
    $analysis54

  InsertImageBlockAfterAnchor `
    '6.2 运行链路验证' `
    $intro61 `
    (Join-Path $assetDir 'fig_6_1_dist_output_terminal.png') `
    '图 6-1 前端构建产物生成结果截图' `
    $analysis61

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

$summary = [pscustomobject]@{
  Output = $output
  AssetDir = $assetDir
  AssetCount = (Get-ChildItem $assetDir -Filter '*.png').Count
}
$summary | ConvertTo-Json -Compress
