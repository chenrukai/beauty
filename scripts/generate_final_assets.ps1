$ErrorActionPreference = 'Stop'

$root = 'D:\beauty'
$outDir = Join-Path $root 'final_assets'
$pngDir = Join-Path $root '论文图表素材\png_for_word'
$submissionDir = Join-Path $root 'submission_assets'
$evidenceDir = Join-Path $root 'evidence_assets_fixed'
$backendDir = Join-Path $root 'beauty-knowledge-backend'
$frontendDir = Join-Path $root 'beauty-knowledge-frontend'

Add-Type -AssemblyName System.Drawing

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function Get-FontFamilyName([string[]]$candidates, [string]$fallback) {
  $installed = New-Object System.Drawing.Text.InstalledFontCollection
  $names = $installed.Families | ForEach-Object { $_.Name }
  foreach ($candidate in $candidates) {
    if ($names -contains $candidate) { return $candidate }
  }
  return $fallback
}

function Draw-RoundedBox($g, $pen, $brush, [float]$x, [float]$y, [float]$w, [float]$h, [string]$text, $font) {
  $rect = New-Object System.Drawing.RectangleF($x, $y, $w, $h)
  $radius = 26
  $path = New-Object System.Drawing.Drawing2D.GraphicsPath
  $path.AddArc($x, $y, $radius, $radius, 180, 90)
  $path.AddArc($x + $w - $radius, $y, $radius, $radius, 270, 90)
  $path.AddArc($x + $w - $radius, $y + $h - $radius, $radius, $radius, 0, 90)
  $path.AddArc($x, $y + $h - $radius, $radius, $radius, 90, 90)
  $path.CloseFigure()
  $g.FillPath($brush, $path)
  $g.DrawPath($pen, $path)
  $sf = New-Object System.Drawing.StringFormat
  $sf.Alignment = 'Center'
  $sf.LineAlignment = 'Center'
  $g.DrawString($text, $font, [System.Drawing.Brushes]::Black, $rect, $sf)
  $sf.Dispose()
  $path.Dispose()
}

function Draw-RectBox($g, $pen, $brush, [float]$x, [float]$y, [float]$w, [float]$h, [string]$text, $font) {
  $rect = New-Object System.Drawing.RectangleF($x, $y, $w, $h)
  $g.FillRectangle($brush, $rect)
  $g.DrawRectangle($pen, $x, $y, $w, $h)
  $sf = New-Object System.Drawing.StringFormat
  $sf.Alignment = 'Center'
  $sf.LineAlignment = 'Center'
  $g.DrawString($text, $font, [System.Drawing.Brushes]::Black, $rect, $sf)
  $sf.Dispose()
}

function Draw-Diamond($g, $pen, $brush, [float]$x, [float]$y, [float]$w, [float]$h, [string]$text, $font) {
  $pts = @(
    [System.Drawing.PointF]::new($x + $w / 2, $y),
    [System.Drawing.PointF]::new($x + $w, $y + $h / 2),
    [System.Drawing.PointF]::new($x + $w / 2, $y + $h),
    [System.Drawing.PointF]::new($x, $y + $h / 2)
  )
  $g.FillPolygon($brush, $pts)
  $g.DrawPolygon($pen, $pts)
  $rect = New-Object System.Drawing.RectangleF($x, $y, $w, $h)
  $sf = New-Object System.Drawing.StringFormat
  $sf.Alignment = 'Center'
  $sf.LineAlignment = 'Center'
  $g.DrawString($text, $font, [System.Drawing.Brushes]::Black, $rect, $sf)
  $sf.Dispose()
}

function Draw-Arrow($g, $pen, [float]$x1, [float]$y1, [float]$x2, [float]$y2) {
  $linePen = New-Object System.Drawing.Pen($pen.Color, $pen.Width)
  $cap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap(8, 10, $true)
  $linePen.CustomEndCap = $cap
  $g.DrawLine($linePen, $x1, $y1, $x2, $y2)
  $cap.Dispose()
  $linePen.Dispose()
}

function New-Canvas([int]$width = 1600, [int]$height = 900) {
  $bmp = New-Object System.Drawing.Bitmap($width, $height)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $g.Clear([System.Drawing.Color]::White)
  return @($bmp, $g)
}

function Save-Bitmap($bmp, $g, [string]$path) {
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose()
  $bmp.Dispose()
}

function Make-Fig-2-1([string]$path) {
  $pair = New-Canvas 1600 860
  $bmp = $pair[0]; $g = $pair[1]
  $font = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 28)
  $titleFont = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 22)
  $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(120,90,40), 4)
  $arrowPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(90,90,90), 5)
  $boxBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(247,239,223))
  $greenBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(225,240,235))
  Draw-RoundedBox $g $pen $boxBrush 70 290 210 250 '用户提问' $font
  Draw-RoundedBox $g $pen $boxBrush 335 290 250 250 '混合检索' $font
  Draw-RoundedBox $g $pen $greenBrush 640 290 230 250 '证据整合' $font
  Draw-RoundedBox $g $pen $greenBrush 925 290 230 250 '流式回答' $font
  Draw-RoundedBox $g $pen $boxBrush 1210 290 210 250 '会话展示' $font
  Draw-Arrow $g $arrowPen 280 415 335 415
  Draw-Arrow $g $arrowPen 585 415 640 415
  Draw-Arrow $g $arrowPen 870 415 925 415
  Draw-Arrow $g $arrowPen 1155 415 1210 415
  $g.DrawString('关键词 + 向量召回', $titleFont, [System.Drawing.Brushes]::Black, 360, 160)
  $g.DrawString('证据构建上下文引导', $titleFont, [System.Drawing.Brushes]::Black, 705, 160)
  Save-Bitmap $bmp $g $path
  $font.Dispose(); $titleFont.Dispose(); $pen.Dispose(); $arrowPen.Dispose(); $boxBrush.Dispose(); $greenBrush.Dispose()
}

function Make-Fig-4-3([string]$path) {
  $pair = New-Canvas 1600 860
  $bmp = $pair[0]; $g = $pair[1]
  $font = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 27)
  $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 4)
  $arrowPen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 5)
  $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(250,250,250))
  Draw-RectBox $g $pen $brush 90 180 220 190 '知识录入' $font
  Draw-RectBox $g $pen $brush 370 180 260 190 '分类与标签绑定' $font
  Draw-RectBox $g $pen $brush 690 180 220 190 '摘要生成' $font
  Draw-RectBox $g $pen $brush 970 180 260 190 '状态维护与发布' $font
  Draw-RectBox $g $pen $brush 480 500 220 170 '分页检索' $font
  Draw-RectBox $g $pen $brush 820 500 220 170 '详情展示' $font
  Draw-Arrow $g $arrowPen 310 275 370 275
  Draw-Arrow $g $arrowPen 630 275 690 275
  Draw-Arrow $g $arrowPen 910 275 970 275
  Draw-Arrow $g $arrowPen 1100 370 930 500
  Draw-Arrow $g $arrowPen 800 370 610 500
  Draw-Arrow $g $arrowPen 700 585 820 585
  Save-Bitmap $bmp $g $path
  $font.Dispose(); $pen.Dispose(); $arrowPen.Dispose(); $brush.Dispose()
}

function Make-Fig-4-4([string]$path) {
  $pair = New-Canvas 1600 920
  $bmp = $pair[0]; $g = $pair[1]
  $font = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 25)
  $smallFont = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 22)
  $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 4)
  $arrowPen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 5)
  $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
  Draw-RectBox $g $pen $brush 70 350 170 150 '文件上传' $font
  Draw-RectBox $g $pen $brush 280 350 220 150 '对象存储与任务登记' $smallFont
  Draw-Diamond $g $pen $brush 550 315 220 220 '文件类型判断' $font
  Draw-RectBox $g $pen $brush 790 150 180 150 'OCR 解析' $font
  Draw-RectBox $g $pen $brush 790 560 180 150 'Whisper 转写' $smallFont
  Draw-RectBox $g $pen $brush 1040 350 180 150 '文本清洗' $font
  Draw-RectBox $g $pen $brush 1270 350 180 150 '初步切块' $font
  Draw-RectBox $g $pen $brush 1460 350 100 150 '进入抽取' $smallFont
  Draw-Arrow $g $arrowPen 240 425 280 425
  Draw-Arrow $g $arrowPen 500 425 550 425
  Draw-Arrow $g $arrowPen 770 370 790 225
  Draw-Arrow $g $arrowPen 770 480 790 635
  Draw-Arrow $g $arrowPen 970 225 1040 350
  Draw-Arrow $g $arrowPen 970 635 1040 500
  Draw-Arrow $g $arrowPen 1220 425 1270 425
  Draw-Arrow $g $arrowPen 1450 425 1460 425
  Save-Bitmap $bmp $g $path
  $font.Dispose(); $smallFont.Dispose(); $pen.Dispose(); $arrowPen.Dispose(); $brush.Dispose()
}

function Make-Fig-4-5([string]$path) {
  $pair = New-Canvas 1600 860
  $bmp = $pair[0]; $g = $pair[1]
  $font = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 27)
  $smallFont = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 24)
  $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 4)
  $arrowPen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 5)
  $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
  Draw-RectBox $g $pen $brush 70 330 220 170 '输入实体条件' $font
  Draw-RectBox $g $pen $brush 350 330 240 170 '查询图谱节点' $font
  Draw-RectBox $g $pen $brush 690 130 220 180 '邻居查询' $font
  Draw-RectBox $g $pen $brush 690 560 220 180 '路径查询' $font
  Draw-RectBox $g $pen $brush 1010 330 240 170 '证据文本回填' $smallFont
  Draw-RectBox $g $pen $brush 1320 330 220 170 '图谱结果展示' $font
  Draw-Arrow $g $arrowPen 290 415 350 415
  Draw-Arrow $g $arrowPen 590 340 690 220
  Draw-Arrow $g $arrowPen 590 490 690 650
  Draw-Arrow $g $arrowPen 910 220 1010 360
  Draw-Arrow $g $arrowPen 910 650 1010 470
  Draw-Arrow $g $arrowPen 1250 415 1320 415
  Save-Bitmap $bmp $g $path
  $font.Dispose(); $smallFont.Dispose(); $pen.Dispose(); $arrowPen.Dispose(); $brush.Dispose()
}

function Make-Fig-4-6([string]$path) {
  $pair = New-Canvas 1600 860
  $bmp = $pair[0]; $g = $pair[1]
  $font = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 27)
  $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 4)
  $arrowPen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 5)
  $boxBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(247,247,247))
  Draw-RectBox $g $pen $boxBrush 70 330 200 170 '用户提问' $font
  Draw-RectBox $g $pen $boxBrush 330 330 220 170 '关键词检索' $font
  Draw-RectBox $g $pen $boxBrush 610 330 220 170 '向量召回' $font
  Draw-RectBox $g $pen $boxBrush 890 330 220 170 '结果融合' $font
  Draw-RectBox $g $pen $boxBrush 1170 330 200 170 '上下文构建' $font
  Draw-RectBox $g $pen $boxBrush 1410 330 120 170 '流式回答' $font
  Draw-Arrow $g $arrowPen 270 415 330 415
  Draw-Arrow $g $arrowPen 550 415 610 415
  Draw-Arrow $g $arrowPen 830 415 890 415
  Draw-Arrow $g $arrowPen 1110 415 1170 415
  Draw-Arrow $g $arrowPen 1370 415 1410 415
  Save-Bitmap $bmp $g $path
  $font.Dispose(); $pen.Dispose(); $arrowPen.Dispose(); $boxBrush.Dispose()
}

function Save-PlainTextPng(
  [string]$outputPath,
  [string[]]$lines,
  [string]$fontFamily,
  [float]$fontSize,
  [bool]$parseLineNumbers
) {
  $width = 1420
  $padding = 28
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
      $graphics.DrawString($lineNo.PadLeft(4), $font, $lineNoBrush, 28, $y)
      $graphics.DrawString($content, $font, $textBrush, 108, $y)
    } else {
      $graphics.DrawString($content, $font, $textBrush, 28, $y)
    }
    $y += $lineHeight
  }

  $bmp.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
  $borderPen.Dispose(); $textBrush.Dispose(); $lineNoBrush.Dispose(); $font.Dispose(); $graphics.Dispose(); $bmp.Dispose()
}

function Get-SnippetLines([string]$path, [int]$start, [int]$end) {
  $encoding = [System.Text.UTF8Encoding]::new($false)
  $allLines = [System.IO.File]::ReadAllLines($path, $encoding)
  $lines = New-Object System.Collections.Generic.List[string]
  for ($i = $start; $i -le $end -and $i -le $allLines.Length; $i++) {
    $lines.Add(('{0,4}: {1}' -f $i, $allLines[$i - 1]))
  }
  return ,$lines.ToArray()
}

Make-Fig-2-1 (Join-Path $outDir 'fig_2_1_business_flow.png')
Make-Fig-4-3 (Join-Path $outDir 'fig_4_3_knowledge_manage_flow.png')
Make-Fig-4-4 (Join-Path $outDir 'fig_4_4_file_processing_flow.png')
Make-Fig-4-5 (Join-Path $outDir 'fig_4_5_graph_query_flow.png')
Make-Fig-4-6 (Join-Path $outDir 'fig_4_6_qa_flow.png')

foreach ($name in @(
  'fig_2_2_user_usecase.png',
  'fig_2_3_admin_usecase.png',
  'fig_4_1_detail_collaboration.png',
  'fig_4_2_frontend_navigation.png',
  'fig_5_1_performance_record.png',
  'fig_5_2_compatibility_result.png',
  'fig_5_3_backend_validate.png',
  'fig_5_4_frontend_build.png',
  'fig_6_1_frontend_dist.png'
)) {
  $src = if (Test-Path (Join-Path $submissionDir $name)) { Join-Path $submissionDir $name } else { Join-Path $evidenceDir $name }
  if (Test-Path $src) {
    Copy-Item -LiteralPath $src -Destination (Join-Path $outDir $name) -Force
  }
}

$codeFont = Get-FontFamilyName @('NSimSun', 'SimSun', 'Microsoft YaHei UI') 'SimSun'
Save-PlainTextPng (Join-Path $outDir 'fig_4_7_task_state_code.png') (Get-SnippetLines (Join-Path $backendDir 'src\main\java\com\beauty\knowledge\module\pipeline\service\ProcessTaskService.java') 24 47) $codeFont 14 $true
Save-PlainTextPng (Join-Path $outDir 'fig_4_8_graph_query_code.png') (Get-SnippetLines (Join-Path $backendDir 'src\main\java\com\beauty\knowledge\module\kg\service\KgQueryService.java') 60 90) $codeFont 14 $true
Save-PlainTextPng (Join-Path $outDir 'fig_4_9_stream_chat_code.png') (Get-SnippetLines (Join-Path $frontendDir 'src\stores\chat.ts') 79 115) $codeFont 14 $true

Get-ChildItem $outDir -Filter *.png | Sort-Object Name | Select-Object Name,Length | Format-Table -AutoSize
