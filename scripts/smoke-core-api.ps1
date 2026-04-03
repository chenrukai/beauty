param(
    [string]$BaseUrl = "http://127.0.0.1:8080/api",
    [string]$Token = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step([string]$Text) {
    Write-Host ""
    Write-Host "==> $Text" -ForegroundColor Cyan
}

function Invoke-ApiGet([string]$Path) {
    $uri = "$BaseUrl$Path"
    $headers = @{}
    if ($Token) {
        $headers["Authorization"] = "Bearer $Token"
    }
    return Invoke-RestMethod -Uri $uri -Method Get -Headers $headers -TimeoutSec 25
}

function Assert-Success([object]$Resp, [string]$Name) {
    if ($null -eq $Resp) {
        throw "$Name: empty response"
    }
    $code = [int]($Resp.code)
    if ($code -ne 200) {
        $msg = [string]($Resp.message)
        if (-not $msg) { $msg = "unknown error" }
        throw "$Name: code=$code, message=$msg"
    }
    Write-Host "$Name: OK" -ForegroundColor Green
}

Write-Host "Smoke check baseUrl: $BaseUrl"
if (-not $Token) {
    Write-Host "No token passed. Public endpoints only may work; auth endpoints may fail." -ForegroundColor Yellow
}

try {
    Write-Step "Health-like check: notice list"
    $notice = Invoke-ApiGet "/notice/list?size=1"
    Assert-Success $notice "GET /notice/list"

    Write-Step "Knowledge page"
    $knowledge = Invoke-ApiGet "/knowledge/page?pageNum=1&pageSize=3"
    Assert-Success $knowledge "GET /knowledge/page"

    Write-Step "Chat session list (requires login)"
    $chatSession = Invoke-ApiGet "/chat/session"
    Assert-Success $chatSession "GET /chat/session"

    Write-Step "Task recent (requires permission)"
    $taskRecent = Invoke-ApiGet "/file/task/recent?size=3"
    Assert-Success $taskRecent "GET /file/task/recent"

    Write-Host ""
    Write-Host "Smoke check finished: PASS" -ForegroundColor Green
    exit 0
}
catch {
    Write-Host ""
    Write-Host "Smoke check finished: FAIL" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

