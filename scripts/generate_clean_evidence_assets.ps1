$ErrorActionPreference = 'Stop'

$manifestPath = 'D:\beauty\scripts\thesis_visual_fix_manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Encoding UTF8 -Raw | ConvertFrom-Json
$assetDir = $manifest.asset_dir

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

New-Item -ItemType Directory -Force -Path $assetDir | Out-Null

function Get-FontFamilyName([string[]]$candidates, [string]$fallback) {
  $installed = New-Object System.Drawing.Text.InstalledFontCollection
  $names = $installed.Families | ForEach-Object { $_.Name }
  foreach ($candidate in $candidates) {
    if ($names -contains $candidate) { return $candidate }
  }
  return $fallback
}

function Strip-Ansi([string]$text) {
  if ($null -eq $text) { return '' }
  $clean = [regex]::Replace($text, [string][char]27 + '\[[0-9;]*[A-Za-z]', '')
  $clean = [regex]::Replace($clean, [string][char]65533 + '\[[0-9;]*[A-Za-z]', '')
  return $clean
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
    $output = Invoke-Expression "$command 2>&1 | Out-String"
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
  $width = 1540
  $padding = 34
  $background = [System.Drawing.Color]::White
  $border = [System.Drawing.Color]::FromArgb(214, 220, 228)
  $textColor = [System.Drawing.Color]::FromArgb(32, 37, 43)
  $lineNoColor = [System.Drawing.Color]::FromArgb(135, 144, 158)

  $font = New-Object System.Drawing.Font($fontFamily, $fontSize, [System.Drawing.FontStyle]::Regular)
  $probeBmp = New-Object System.Drawing.Bitmap 10, 10
  $probe = [System.Drawing.Graphics]::FromImage($probeBmp)
  $probe.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $lineHeight = [int][Math]::Ceiling($probe.MeasureString('Ag', $font).Height) + 6
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
      $graphics.DrawString($lineNo.PadLeft(4), $font, $lineNoBrush, 34, $y)
      $graphics.DrawString($content, $font, $textBrush, 118, $y)
    } else {
      $graphics.DrawString($content, $font, $textBrush, 34, $y)
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

$codeFont = Get-FontFamilyName @('NSimSun', 'SimSun', 'Microsoft YaHei UI') 'SimSun'
$terminalFont = Get-FontFamilyName @('Consolas', 'Cascadia Mono', 'Courier New') 'Consolas'

foreach ($item in $manifest.code_screenshots) {
  $lines = Get-SnippetLines $item.source_file $item.ranges
  Save-PlainTextPng (Join-Path $assetDir $item.output_name) $lines $codeFont 12.5 $true
}

foreach ($item in $manifest.terminal_screenshots) {
  $output = Invoke-CommandCapture $item.working_dir $item.command
  $lines = @($output -split "`r?`n" | Where-Object { $_ -ne '' })
  Save-PlainTextPng (Join-Path $assetDir $item.output_name) $lines $terminalFont 12 $false
}

Get-ChildItem $assetDir -Filter '*.png' | Select-Object Name,Length | Format-Table -AutoSize
