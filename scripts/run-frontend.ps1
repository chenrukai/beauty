$ErrorActionPreference = "Stop"

$repoRoot = "C:\Users\YLDN\Desktop\beauty"
$frontendDir = Join-Path $repoRoot "beauty-knowledge-frontend"

Set-Location $frontendDir
npm run dev
