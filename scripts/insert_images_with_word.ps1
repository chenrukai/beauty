$ErrorActionPreference = 'Stop'

$source = 'D:\beauty\毕业论文_最终稿_引文闭环重构版.docx'
$output = 'D:\beauty\毕业论文_最终稿_规范达标版.docx'
$assetDir = 'D:\beauty\submission_assets_ascii'

Copy-Item -LiteralPath $source -Destination $output -Force

$map = [ordered]@{
  '图 2-1 系统业务流程图' = @{ File = 'fig_2_1_business_flow.png'; WidthCm = 13.6 }
  '图 2-2 普通用户用例图' = @{ File = 'fig_2_2_user_usecase.png'; WidthCm = 11.8 }
  '图 2-3 后台管理员用例图' = @{ File = 'fig_2_3_admin_usecase.png'; WidthCm = 11.8 }
  '图 3-1 系统整体结构图' = @{ File = 'fig_3_1_system_architecture.png'; WidthCm = 13.6 }
  '图 3-2 系统 ER 图' = @{ File = 'fig_3_2_er_diagram.png'; WidthCm = 13.2 }
  '图 4-1 系统详细设计模块协作图' = @{ File = 'fig_4_1_detail_collaboration.png'; WidthCm = 12.6 }
  '图 4-2 用户端页面跳转关系图' = @{ File = 'fig_4_2_frontend_navigation.png'; WidthCm = 12.6 }
  '图 4-3 知识管理模块处理流程图' = @{ File = 'fig_4_3_knowledge_manage_flow.png'; WidthCm = 13.6 }
  '图 4-4 文件处理模块流程图' = @{ File = 'fig_4_4_file_processing_flow.png'; WidthCm = 13.6 }
  '图 4-5 知识图谱查询流程图' = @{ File = 'fig_4_5_graph_query_flow.png'; WidthCm = 13.6 }
  '图 4-6 智能问答模块流程图' = @{ File = 'fig_4_6_qa_flow.png'; WidthCm = 13.6 }
  '图 5-1 性能测试记录图' = @{ File = 'fig_5_1_performance_record.png'; WidthCm = 12.6 }
  '图 5-2 兼容性测试结果图' = @{ File = 'fig_5_2_compatibility_result.png'; WidthCm = 12.6 }
}

$wdCollapseStart = 1
$wdAlignParagraphCenter = 1

function Normalize-Text([string]$text) {
  if ($null -eq $text) { return '' }
  return ($text -replace '[\r\n\a]', '').Trim()
}

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open($output)

try {
  for ($i = $doc.Paragraphs.Count; $i -ge 1; $i--) {
    $para = $doc.Paragraphs.Item($i)
    $text = Normalize-Text $para.Range.Text
    if (-not $map.Contains($text)) { continue }

    $spec = $map[$text]
    $imgPath = Join-Path $assetDir $spec.File
    if (-not (Test-Path -LiteralPath $imgPath)) { continue }

    $para.Range.ParagraphFormat.Alignment = $wdAlignParagraphCenter
    $para.Range.ParagraphFormat.FirstLineIndent = 0
    $para.Range.ParagraphFormat.CharacterUnitFirstLineIndent = 0
    $para.Range.ParagraphFormat.SpaceBefore = 6
    $para.Range.ParagraphFormat.SpaceAfter = 6

    $para.Range.InsertParagraphBefore() | Out-Null
    $imgPara = $doc.Paragraphs.Item($i)
    $imgPara.Range.ParagraphFormat.Alignment = $wdAlignParagraphCenter
    $imgPara.Range.ParagraphFormat.SpaceBefore = 6
    $imgPara.Range.ParagraphFormat.SpaceAfter = 6
    $imgPara.Range.ParagraphFormat.FirstLineIndent = 0
    $imgPara.Range.ParagraphFormat.CharacterUnitFirstLineIndent = 0

    $shape = $imgPara.Range.InlineShapes.AddPicture($imgPath, $false, $true)
    $shape.LockAspectRatio = -1
    $shape.Width = [double]$spec.WidthCm * 28.3465
  }

  foreach ($toc in $doc.TablesOfContents) {
    $toc.Update()
  }
  $doc.Repaginate()
  $doc.Save()
}
finally {
  $doc.Close()
  $word.Quit()
}

Write-Output $output
