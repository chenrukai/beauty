$ErrorActionPreference = "Stop"

$taskName = "BeautyDevAutoStart"
$startupScript = "C:\Users\YLDN\Desktop\beauty\scripts\startup-dev.ps1"

if (-not (Test-Path $startupScript)) {
  throw "Missing startup script: $startupScript"
}

$action = "powershell.exe -ExecutionPolicy Bypass -File `"$startupScript`""
schtasks /Create /TN $taskName /SC ONLOGON /TR $action /F | Out-Null

Write-Host "Scheduled task created: $taskName"
