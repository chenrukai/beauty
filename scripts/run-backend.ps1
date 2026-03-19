$ErrorActionPreference = "Stop"

$repoRoot = "C:\Users\YLDN\Desktop\beauty"
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

Set-Location $backendDir
mvn -DskipTests spring-boot:run
