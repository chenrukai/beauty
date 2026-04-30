$ErrorActionPreference = 'Stop'

$manifestPath = 'D:\beauty\scripts\thesis_visual_fix_manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Encoding UTF8 -Raw | ConvertFrom-Json

$sourceDoc = $manifest.source_docx
$outputDoc = $manifest.output_docx
$finalCopyDoc = $manifest.final_copy_docx
$assetDir = $manifest.asset_dir

Copy-Item -LiteralPath $sourceDoc -Destination $outputDoc -Force

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

function ApplyRangeLook([object]$targetRange, [object]$sourceRange) {
  $targetRange.FormattedText = $sourceRange.FormattedText
}

function InsertStyledParagraphBeforeIndex([object]$doc, [int]$index, [string]$text, [object]$templateRange) {
  $range = $doc.Paragraphs.Item($index).Range
  $null = $range.InsertParagraphBefore()
  $para = $doc.Paragraphs.Item($index)
  ApplyRangeLook $para.Range $templateRange
  $para.Range.Text = $text + "`r"
  return $para
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
  $shape.Range.ParagraphFormat.LineSpacingRule = 1
  $shape.Range.ParagraphFormat.LineSpacing = 18
  $para.Range.Font.Size = 1
  $para.Range.Font.Color = 16777215
  $para.Range.ParagraphFormat.Alignment = 1
  return $shape
}

function InsertImageBlockAfterAnchor([object]$doc, [object]$word, [object]$item) {
  $anchorIndex = Find-ParagraphIndex $doc $item.anchor_text
  $anchorPara = $doc.Paragraphs.Item($anchorIndex)
  $bodyTemplate = $doc.Paragraphs.Item([Math]::Max(1, $anchorIndex - 1)).Range
  $captionTemplate = $anchorPara.Range
  $insertIndex = $anchorIndex + 1

  [void](InsertStyledParagraphBeforeIndex $doc $insertIndex $item.analysis_text $bodyTemplate)
  [void](InsertStyledParagraphBeforeIndex $doc $insertIndex $item.caption $captionTemplate)
  [void](InsertImageBeforeIndex $doc $word $insertIndex (Join-Path $assetDir $item.asset_name))
  [void](InsertStyledParagraphBeforeIndex $doc $insertIndex $item.intro_text $bodyTemplate)
}

function InsertReferenceBeforeAnchor([object]$doc, [string]$anchorText, [string]$referenceText) {
  $anchorIndex = Find-ParagraphIndex $doc $anchorText
  $templateRange = $doc.Paragraphs.Item($anchorIndex - 1).Range
  [void](InsertStyledParagraphBeforeIndex $doc $anchorIndex $referenceText $templateRange)
}

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

try {
  $doc = $word.Documents.Open($outputDoc)

  InsertReferenceBeforeAnchor $doc $manifest.reference_insert_before $manifest.reference_entry

  foreach ($item in $manifest.doc_items) {
    InsertImageBlockAfterAnchor $doc $word $item
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

Copy-Item -LiteralPath $outputDoc -Destination $finalCopyDoc -Force
Get-Item $outputDoc, $finalCopyDoc | Select-Object FullName,Length,LastWriteTime | Format-Table -AutoSize
