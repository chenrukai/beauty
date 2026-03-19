$ErrorActionPreference = "Stop"

$repoRoot = "C:\Users\YLDN\Desktop\beauty"
$backendDir = Join-Path $repoRoot "beauty-knowledge-backend"
$envFile = Join-Path $backendDir ".env"
$dockerDesktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
$taskName = "BeautyDevAutoStart"

function Write-Step($msg) {
  Write-Host ("[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $msg)
}

function Ensure-DotEnv {
  if (Test-Path $envFile) {
    Write-Step ".env already exists"
    return
  }

  Write-Step "Creating default .env for local dev"
  @"
MYSQL_ROOT_PASSWORD=beauty_mysql_2026
MYSQL_DATABASE=beauty_knowledge
MYSQL_PORT=3306
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=beauty_knowledge
DB_USER=root
DB_PASSWORD=beauty_mysql_2026

RABBITMQ_USER=beauty
RABBITMQ_PASSWORD=beauty_rabbit_2026
RABBITMQ_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672
RABBIT_HOST=127.0.0.1
RABBIT_PORT=5672
RABBIT_USER=beauty
RABBIT_PASSWORD=beauty_rabbit_2026

MINIO_ROOT_USER=beauty
MINIO_ROOT_PASSWORD=beauty_minio_2026
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_ENDPOINT=http://127.0.0.1:9000
MINIO_ACCESS_KEY=beauty
MINIO_SECRET_KEY=beauty_minio_2026

REDIS_PORT=6379
MILVUS_PORT=19530

BEAUTY_JWT_SECRET=beauty_jwt_secret_2026_please_change_me
DISABLE_DEFAULT_SEED_USERS=true
DB_AUTO_CREATE_CHAT_TABLES=false
BOOTSTRAP_ADMIN_ENABLED=false
BOOTSTRAP_ADMIN_USERNAME=
BOOTSTRAP_ADMIN_PASSWORD=
"@ | Set-Content -Path $envFile -Encoding UTF8
}

function Wait-DockerReady {
  $maxAttempts = 36
  for ($i = 1; $i -le $maxAttempts; $i++) {
    docker version | Out-Null
    if ($LASTEXITCODE -eq 0) { return $true }
    Start-Sleep -Seconds 5
  }
  return $false
}

function Wait-PortReady([int]$port, [int]$maxAttempts = 24) {
  for ($i = 1; $i -le $maxAttempts; $i++) {
    $ok = (Test-NetConnection -ComputerName "127.0.0.1" -Port $port -WarningAction SilentlyContinue).TcpTestSucceeded
    if ($ok) { return $true }
    Start-Sleep -Seconds 3
  }
  return $false
}

Ensure-DotEnv

Write-Step "Checking Docker daemon"
docker version | Out-Null
if ($LASTEXITCODE -ne 0) {
  if (Test-Path $dockerDesktop) {
    Write-Step "Starting Docker Desktop"
    Start-Process -FilePath $dockerDesktop
  } else {
    throw "Docker Desktop not found: $dockerDesktop"
  }
}

if (-not (Wait-DockerReady)) {
  throw "Docker daemon did not become ready in time"
}

Write-Step "Starting infrastructure containers"
Set-Location $backendDir
docker compose --env-file .env up -d mysql redis rabbitmq minio etcd milvus

if (-not (Wait-PortReady -port 5672)) {
  Write-Warning "RabbitMQ port 5672 is still unavailable"
}

Write-Step "Launching backend window"
Start-Process powershell.exe -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-File", (Join-Path $repoRoot "scripts\run-backend.ps1")
)

Write-Step "Launching frontend window"
Start-Process powershell.exe -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-File", (Join-Path $repoRoot "scripts\run-frontend.ps1")
)

Write-Step "Startup completed"
