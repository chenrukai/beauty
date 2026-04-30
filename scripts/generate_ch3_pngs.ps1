$ErrorActionPreference = 'Stop'

$root = 'D:\beauty'
$outDir = Join-Path $root '论文图表素材\png_for_word'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Add-Type -AssemblyName System.Drawing

function Get-FontFamilyName([string[]]$candidates, [string]$fallback) {
  $installed = New-Object System.Drawing.Text.InstalledFontCollection
  $names = $installed.Families | ForEach-Object { $_.Name }
  foreach ($candidate in $candidates) {
    if ($names -contains $candidate) { return $candidate }
  }
  return $fallback
}

function New-Canvas([int]$width = 1600, [int]$height = 920) {
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

function Draw-Arrow($g, $pen, [float]$x1, [float]$y1, [float]$x2, [float]$y2) {
  $linePen = New-Object System.Drawing.Pen($pen.Color, $pen.Width)
  $cap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap(8, 10, $true)
  $linePen.CustomEndCap = $cap
  $g.DrawLine($linePen, $x1, $y1, $x2, $y2)
  $cap.Dispose()
  $linePen.Dispose()
}

function Draw-Label($g, [string]$text, [float]$x, [float]$y, $font) {
  $g.DrawString($text, $font, [System.Drawing.Brushes]::Black, $x, $y)
}

function Make-Fig-3-1([string]$path) {
  $pair = New-Canvas 1700 980
  $bmp = $pair[0]; $g = $pair[1]
  $titleFont = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 24)
  $font = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 26)
  $small = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 22)
  $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 4)
  $arrowPen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 5)
  $userBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(248,248,248))
  $svcBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(238,245,240))

  Draw-Label $g 'Presentation Layer' 690 38 $titleFont
  Draw-RectBox $g $pen $userBrush 120 90 280 95 'User Client Vue 3' $font
  Draw-RectBox $g $pen $userBrush 470 90 280 95 'Admin Client Vue 3' $font
  Draw-RectBox $g $pen $userBrush 820 90 280 95 'Routing and State' $small
  Draw-RectBox $g $pen $userBrush 1170 90 280 95 'SSE Streaming' $small

  Draw-Label $g 'Business Layer' 735 250 $titleFont
  Draw-RectBox $g $pen $svcBrush 90 300 220 90 'Auth Service' $font
  Draw-RectBox $g $pen $svcBrush 350 300 220 90 'Knowledge Mgmt' $font
  Draw-RectBox $g $pen $svcBrush 610 300 220 90 'File Process' $font
  Draw-RectBox $g $pen $svcBrush 870 300 220 90 'Graph Service' $font
  Draw-RectBox $g $pen $svcBrush 1130 300 220 90 'QA Service' $font
  Draw-RectBox $g $pen $svcBrush 1390 300 220 90 'Statistics' $font

  Draw-Label $g 'Data and AI Layer' 720 515 $titleFont
  Draw-RectBox $g $pen $userBrush 95 570 180 85 'MySQL' $font
  Draw-RectBox $g $pen $userBrush 310 570 180 85 'Redis' $font
  Draw-RectBox $g $pen $userBrush 525 570 180 85 'RabbitMQ' $small
  Draw-RectBox $g $pen $userBrush 740 570 180 85 'MinIO' $font
  Draw-RectBox $g $pen $userBrush 955 570 180 85 'Milvus' $font
  Draw-RectBox $g $pen $userBrush 1170 570 180 85 'OCR Service' $small
  Draw-RectBox $g $pen $userBrush 1385 570 180 85 'Whisper ASR' $small

  Draw-Arrow $g $arrowPen 260 185 200 300
  Draw-Arrow $g $arrowPen 610 185 460 300
  Draw-Arrow $g $arrowPen 960 185 720 300
  Draw-Arrow $g $arrowPen 1310 185 1240 300
  Draw-Arrow $g $arrowPen 200 390 185 570
  Draw-Arrow $g $arrowPen 460 390 400 570
  Draw-Arrow $g $arrowPen 720 390 615 570
  Draw-Arrow $g $arrowPen 980 390 830 570
  Draw-Arrow $g $arrowPen 1240 390 1050 570
  Draw-Arrow $g $arrowPen 1500 390 1475 570

  Save-Bitmap $bmp $g $path
  $titleFont.Dispose(); $font.Dispose(); $small.Dispose(); $pen.Dispose(); $arrowPen.Dispose(); $userBrush.Dispose(); $svcBrush.Dispose()
}

function Make-Fig-3-2([string]$path) {
  $pair = New-Canvas 1700 980
  $bmp = $pair[0]; $g = $pair[1]
  $font = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 24)
  $small = New-Object System.Drawing.Font((Get-FontFamilyName @('Microsoft YaHei UI','SimSun') 'SimSun'), 18)
  $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 4)
  $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)

  Draw-RectBox $g $pen $brush 100 120 280 115 'category' $font
  Draw-Label $g 'id, name, sort, status' 125 195 $small

  Draw-RectBox $g $pen $brush 470 100 320 150 'knowledge' $font
  Draw-Label $g 'id, title, category_id' 505 175 $small
  Draw-Label $g 'content, status, summary' 505 205 $small

  Draw-RectBox $g $pen $brush 900 120 280 115 'file_info' $font
  Draw-Label $g 'id, file_name, file_type' 925 195 $small

  Draw-RectBox $g $pen $brush 1270 120 280 115 'file_task' $font
  Draw-Label $g 'id, file_id, task_status' 1295 195 $small

  Draw-RectBox $g $pen $brush 220 470 300 130 'graph_entity' $font
  Draw-Label $g 'id, entity_name, entity_type' 250 545 $small

  Draw-RectBox $g $pen $brush 650 470 320 130 'graph_relation' $font
  Draw-Label $g 'source_id, target_id, type' 695 545 $small

  Draw-RectBox $g $pen $brush 1090 470 260 130 'chat_session' $font
  Draw-Label $g 'id, user_id, title' 1120 545 $small

  Draw-RectBox $g $pen $brush 1370 470 240 130 'chat_message' $font
  Draw-Label $g 'session_id, role, content' 1385 545 $small

  Draw-Arrow $g $pen 380 175 470 175
  Draw-Arrow $g $pen 790 175 900 175
  Draw-Arrow $g $pen 1180 175 1270 175
  Draw-Arrow $g $pen 630 250 380 470
  Draw-Arrow $g $pen 700 250 800 470
  Draw-Arrow $g $pen 760 250 1180 470
  Draw-Arrow $g $pen 1350 535 1370 535

  Draw-Label $g 'category -> knowledge' 405 145 $small
  Draw-Label $g 'knowledge -> file' 820 145 $small
  Draw-Label $g 'file -> task' 1215 145 $small
  Draw-Label $g 'knowledge -> entity' 395 360 $small
  Draw-Label $g 'entity -> relation' 735 360 $small
  Draw-Label $g 'session -> message' 1250 445 $small

  Save-Bitmap $bmp $g $path
  $font.Dispose(); $small.Dispose(); $pen.Dispose(); $brush.Dispose()
}

Make-Fig-3-1 (Join-Path $outDir 'fig_3_1_system_architecture.png')
Make-Fig-3-2 (Join-Path $outDir 'fig_3_2_er_diagram.png')
Write-Output (Join-Path $outDir 'fig_3_1_system_architecture.png')
Write-Output (Join-Path $outDir 'fig_3_2_er_diagram.png')
