$ErrorActionPreference = 'Stop'

$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$assetDir = 'D:\beauty\论文图表素材'
$outputDir = 'D:\beauty\论文图表素材\png_for_word'
$tmpDir = 'D:\beauty\tmp_png_export'
$edgeProfile = 'D:\beauty\tmp_edge_profile'

$targets = @(
  'fig_2_2_user_usecase',
  'fig_2_3_admin_usecase',
  'fig_4_1_detail_collaboration',
  'fig_4_2_frontend_navigation',
  'fig_4_3_knowledge_manage_flow',
  'fig_4_4_file_processing_flow',
  'fig_4_5_graph_query_flow',
  'fig_4_6_qa_flow'
)

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null
New-Item -ItemType Directory -Force -Path $edgeProfile | Out-Null

foreach ($name in $targets) {
  $svgPath = Join-Path $assetDir ($name + '.svg')
  $tmpPng = Join-Path $tmpDir ($name + '.png')
  $finalPng = Join-Path $outputDir ($name + '.png')
  $urlPath = ($svgPath -replace '\\','/')
  $url = 'file:///' + [System.Uri]::EscapeUriString($urlPath)

  & $edge --headless --disable-gpu "--user-data-dir=$edgeProfile" "--screenshot=$tmpPng" --window-size=1600,1200 $url | Out-Null
  Copy-Item -Force $tmpPng $finalPng
  Write-Output $finalPng
}
