$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backendDir = Join-Path $repoRoot "beauty-knowledge-backend"
$envFile = Join-Path $backendDir ".env"

if (-not (Test-Path $envFile)) {
  throw "Missing .env file: $envFile"
}

Get-Content $envFile | ForEach-Object {
  $line = $_.Trim()
  if (-not $line -or $line.StartsWith("#")) { return }
  $parts = $line -split "=", 2
  if ($parts.Length -ne 2) { return }
  $key = $parts[0].Trim()
  $value = $parts[1].Trim()
  [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
}

[System.Environment]::SetEnvironmentVariable("SPRING_PROFILES_ACTIVE", "dev", "Process")

# Stable local defaults for AI OCR and media transcribe service.
$pythonAiBaseUrl = [System.Environment]::GetEnvironmentVariable("PYTHON_AI_BASE_URL", "Process")
if ([string]::IsNullOrWhiteSpace($pythonAiBaseUrl)) {
  $pythonAiBaseUrl = "http://127.0.0.1:8001"
  [System.Environment]::SetEnvironmentVariable("PYTHON_AI_BASE_URL", $pythonAiBaseUrl, "Process")
}

$pythonTranscribeBaseUrl = [System.Environment]::GetEnvironmentVariable("PYTHON_TRANSCRIBE_BASE_URL", "Process")
if ([string]::IsNullOrWhiteSpace($pythonTranscribeBaseUrl)) {
  $pythonTranscribeBaseUrl = $pythonAiBaseUrl
  [System.Environment]::SetEnvironmentVariable("PYTHON_TRANSCRIBE_BASE_URL", $pythonTranscribeBaseUrl, "Process")
}

Write-Host "Using PYTHON_AI_BASE_URL=$pythonAiBaseUrl"
Write-Host "Using PYTHON_TRANSCRIBE_BASE_URL=$pythonTranscribeBaseUrl"

Set-Location $backendDir
mvn -DskipTests spring-boot:run
