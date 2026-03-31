$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$frontendDir = Join-Path $repoRoot "beauty-knowledge-frontend"

Set-Location $frontendDir
npm run dev
