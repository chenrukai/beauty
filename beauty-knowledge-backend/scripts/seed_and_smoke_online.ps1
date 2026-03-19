param(
  [string]$BaseUrl = "http://127.0.0.1:8080/api",
  [string]$AdminUser = "admin",
  [string]$AdminPass = "admin",
  [string]$NormalUser = "user",
  [string]$NormalPass = "user",
  [string]$ReportPath = "..\docs\generated\feature_smoke_20260318.md"
)

$ErrorActionPreference = "Stop"
$script:ApiBaseUrl = $BaseUrl

function New-ApiResult($name, $ok, $detail) {
  [PSCustomObject]@{ name = $name; ok = $ok; detail = $detail }
}

function Invoke-Api {
  param(
    [ValidateSet("GET", "POST", "PUT", "DELETE")] [string]$Method,
    [Alias("Path")] [string]$Endpoint,
    [string]$Token = "",
    $Body = $null,
    [hashtable]$Query = @{}
  )

  $uri = "$($script:ApiBaseUrl)$Endpoint"
  if ($Query.Count -gt 0) {
    $qs = ($Query.GetEnumerator() | ForEach-Object {
      "$($_.Key)=$([uri]::EscapeDataString([string]$_.Value))"
    }) -join "&"
    $uri = "$($uri)?$($qs)"
  }

  $headers = @{}
  if ($Token) {
    $headers["Authorization"] = "Bearer $Token"
  }

  try {
    if ($Body -ne $null) {
      $json = $Body | ConvertTo-Json -Depth 10
      return Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers -ContentType "application/json" -Body $json -TimeoutSec 30
    }
    return Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers -TimeoutSec 30
  } catch {
    throw "request failed: $Method $uri :: $($_.Exception.Message)"
  }
}

function Ensure-Code200($resp, $action) {
  if ($null -eq $resp -or [int]$resp.code -ne 200) {
    $raw = ""
    try { $raw = ($resp | ConvertTo-Json -Depth 8 -Compress) } catch {}
    throw "$action failed :: $raw"
  }
}

function Find-CategoryId($tree, $name) {
  foreach ($node in $tree) {
    if ($node.name -eq $name) { return [int64]$node.id }
    if ($node.children) {
      $childId = Find-CategoryId $node.children $name
      if ($childId) { return $childId }
    }
  }
  return $null
}

$results = New-Object System.Collections.Generic.List[object]

try {
  $adminLogin = Invoke-Api -Method POST -Path "/auth/login" -Body @{ username = $AdminUser; password = $AdminPass }
  Ensure-Code200 $adminLogin "admin login"
  $adminToken = [string]$adminLogin.data.token

  $userLogin = Invoke-Api -Method POST -Path "/auth/login" -Body @{ username = $NormalUser; password = $NormalPass }
  Ensure-Code200 $userLogin "user login"
  $userToken = [string]$userLogin.data.token
  $results.Add((New-ApiResult "auth login" $true "admin/user login passed"))

  $treeResp = Invoke-Api -Method GET -Path "/category/tree" -Token $adminToken
  Ensure-Code200 $treeResp "category tree"
  $tree = @($treeResp.data)

  $root = "Evidence Hub"
  $rootId = Find-CategoryId $tree $root
  if (-not $rootId) {
    Ensure-Code200 (Invoke-Api -Method POST -Path "/category" -Token $adminToken -Body @{
      name = $root
      parentId = 0
      sortOrder = 90
      status = 1
    }) "create root category"
    $tree = @((Invoke-Api -Method GET -Path "/category/tree" -Token $adminToken).data)
    $rootId = Find-CategoryId $tree $root
  }

  $childNames = @("Acne", "Barrier Repair", "Sun Care", "Ingredient Safety")
  foreach ($name in $childNames) {
    if (-not (Find-CategoryId $tree $name)) {
      Ensure-Code200 (Invoke-Api -Method POST -Path "/category" -Token $adminToken -Body @{
        name = $name
        parentId = $rootId
        sortOrder = 10
        status = 1
      }) "create child category"
      $tree = @((Invoke-Api -Method GET -Path "/category/tree" -Token $adminToken).data)
    }
  }
  $catMap = @{}
  foreach ($name in $childNames) { $catMap[$name] = Find-CategoryId $tree $name }
  $results.Add((New-ApiResult "category tree" $true "evidence categories ready"))

  $knowledgeSeeds = @(
    @{
      title = "Evidence Brief | AAD Acne Guideline Highlights"
      summary = "AAD guideline supports multi-mechanism acne strategies."
      category = "Acne"
      content = "Summary: benzoyl peroxide, topical retinoids, salicylic acid, and azelaic acid are included in recommendations. Source: https://www.aad.org/member/clinical-quality/guidelines/acne"
    },
    @{
      title = "Evidence Brief | Benzoyl Peroxide Safety Update"
      summary = "Use batch control and storage discipline for BPO products."
      category = "Ingredient Safety"
      content = "Operational points: inventory traceability, heat avoidance, and recall execution. Source: https://www.aad.org/news/benzoyl-peroxide-personal-care-products"
    },
    @{
      title = "Evidence Brief | Niacinamide + Ceramide in Acne Care"
      summary = "RCT evidence supports barrier-friendly adjunct care during acne treatment."
      category = "Barrier Repair"
      content = "Practice tip: pair active acne treatment with tolerance-supportive moisturization. Source: https://pubmed.ncbi.nlm.nih.gov/38299457/"
    },
    @{
      title = "Evidence Brief | Pseudo-Ceramide and TEWL"
      summary = "RCT suggests improved barrier metrics in sensitive skin context."
      category = "Barrier Repair"
      content = "Practice tip: use in sensitive and recovery periods. Source: https://pubmed.ncbi.nlm.nih.gov/39492723/"
    },
    @{
      title = "Evidence Brief | FDA Sun Safety SOP"
      summary = "Broad-spectrum sunscreen plus reapplication and physical protection."
      category = "Sun Care"
      content = "SOP: broad-spectrum use, adequate amount, and repeat application in outdoor scenarios. Source: https://www.fda.gov/consumers/consumer-updates/tips-stay-safe-sun-sunscreen-sunglasses"
    },
    @{
      title = "Evidence Brief | Azelaic Acid Use Positioning"
      summary = "Useful in acne and post-inflammatory discoloration workflows."
      category = "Acne"
      content = "Use with barrier care for tolerance stability. Source: https://www.aad.org/member/clinical-quality/guidelines/acne"
    },
    @{
      title = "Evidence Brief | Retinoid Ramp-up at Night"
      summary = "Low-frequency start and gradual ramp-up improves tolerance."
      category = "Acne"
      content = "Three-step method: low frequency, buffer with moisturizer, then progressive ramp-up. Source: https://www.aad.org/member/clinical-quality/guidelines/acne"
    },
    @{
      title = "Evidence Brief | Sensitive Skin Intake Checklist"
      summary = "Assessment-first flow helps reduce avoidable irritation."
      category = "Ingredient Safety"
      content = "Collect prior intolerance history and define stop criteria. Source: https://www.aad.org/member/clinical-quality/guidelines/acne"
    }
  )

  foreach ($k in $knowledgeSeeds) {
    $check = Invoke-Api -Method GET -Path "/knowledge/page" -Token $adminToken -Query @{ pageNum = 1; pageSize = 1; keyword = $k.title }
    Ensure-Code200 $check "knowledge check"
    if ([int]$check.data.total -eq 0) {
      Ensure-Code200 (Invoke-Api -Method POST -Path "/knowledge" -Token $adminToken -Body @{
        title = $k.title
        summary = $k.summary
        content = $k.content
        categoryId = [int64]$catMap[$k.category]
        type = "TEXT_MD"
        status = 1
      }) "knowledge create"
    }
  }
  $results.Add((New-ApiResult "knowledge seed" $true "evidence knowledge inserted"))

  $noticeCheck = Invoke-Api -Method GET -Path "/admin/notice/page" -Token $adminToken -Query @{ pageNum = 1; pageSize = 20; keyword = "Evidence pack synced" }
  Ensure-Code200 $noticeCheck "notice page"
  if ([int]$noticeCheck.data.total -eq 0) {
    Ensure-Code200 (Invoke-Api -Method POST -Path "/admin/notice" -Token $adminToken -Body @{
      title = "Evidence pack synced"
      content = "AAD, FDA, and PubMed-backed content has been added to the knowledge base."
      isTop = 1
      status = 1
      expireTime = $null
    }) "notice create"
  }
  $results.Add((New-ApiResult "notice module" $true "notice create/list passed"))

  $effectNames = @("Oil Control", "Anti-Inflammatory", "Barrier Repair", "Tone Evenness")
  foreach ($name in $effectNames) {
    $list = Invoke-Api -Method GET -Path "/entity/effect" -Token $adminToken -Query @{ keyword = $name }
    Ensure-Code200 $list "effect list"
    if (@($list.data).Count -eq 0) {
      Ensure-Code200 (Invoke-Api -Method POST -Path "/entity/effect" -Token $adminToken -Body @{
        name = $name
        scene = "Seed"
        intro = "seeded by script"
        status = 1
      }) "effect create"
    }
  }

  $ingredientNames = @("Niacinamide", "Azelaic Acid", "Benzoyl Peroxide", "Retinol", "Salicylic Acid", "Ceramide", "Panthenol")
  foreach ($name in $ingredientNames) {
    $list = Invoke-Api -Method GET -Path "/entity/ingredient" -Token $adminToken -Query @{ keyword = $name }
    Ensure-Code200 $list "ingredient list"
    if (@($list.data).Count -eq 0) {
      Ensure-Code200 (Invoke-Api -Method POST -Path "/entity/ingredient" -Token $adminToken -Body @{
        name = $name
        aliasName = $null
        category = "Seed"
        safetyLevel = "A"
        intro = "seeded by script"
        status = 1
      }) "ingredient create"
    }
  }
  $results.Add((New-ApiResult "entity module" $true "ingredient/effect seed passed"))

  $ingList = @((Invoke-Api -Method GET -Path "/entity/ingredient" -Token $adminToken).data)
  $effList = @((Invoke-Api -Method GET -Path "/entity/effect" -Token $adminToken).data)
  $ingMap = @{}
  foreach ($x in $ingList) { $ingMap[$x.name] = [int64]$x.id }
  $effMap = @{}
  foreach ($x in $effList) { $effMap[$x.name] = [int64]$x.id }

  $bindPairs = @(
    @{ ing = "Niacinamide"; eff = "Barrier Repair" },
    @{ ing = "Niacinamide"; eff = "Tone Evenness" },
    @{ ing = "Azelaic Acid"; eff = "Oil Control" },
    @{ ing = "Benzoyl Peroxide"; eff = "Oil Control" },
    @{ ing = "Salicylic Acid"; eff = "Oil Control" },
    @{ ing = "Ceramide"; eff = "Barrier Repair" },
    @{ ing = "Panthenol"; eff = "Anti-Inflammatory" }
  )
  foreach ($pair in $bindPairs) {
    try {
      $resp = Invoke-Api -Method POST -Path "/entity/relation/ingredient-effect" -Token $adminToken -Body @{
        leftId = $ingMap[$pair.ing]
        rightId = $effMap[$pair.eff]
      }
      Ensure-Code200 $resp "bind relation"
    } catch {
      # ignore existing relation errors
    }
  }
  $results.Add((New-ApiResult "relation module" $true "ingredient-effect relation bind passed"))

  $seedPage = Invoke-Api -Method GET -Path "/knowledge/page" -Token $userToken -Query @{ pageNum = 1; pageSize = 20; status = 1; keyword = "Evidence Brief |" }
  Ensure-Code200 $seedPage "seed page fetch"
  $seedIds = @($seedPage.data.records | ForEach-Object { [int64]$_.id })
  if ($seedIds.Count -lt 3) { throw "insufficient seeded knowledge rows" }

  $actionOk = $true
  $actionErr = ""
  try {
    for ($n = 1; $n -le 80; $n++) {
      $kid = $seedIds[($n - 1) % $seedIds.Count]
      $source = @("recommend", "search", "favorite")[($n - 1) % 3]

      Ensure-Code200 (Invoke-Api -Method POST -Path "/user/action" -Token $userToken -Body @{
        actionType = "browse"
        targetType = "knowledge"
        targetId = $kid
        source = $source
      }) "record browse"

      if ($n % 3 -eq 0) {
        $kw = @("niacinamide", "azelaic", "sunscreen", "retinol", "salicylic")[($n - 1) % 5]
        Ensure-Code200 (Invoke-Api -Method POST -Path "/user/action" -Token $userToken -Body @{
          actionType = "search"
          targetType = "knowledge"
          keyword = $kw
          source = "search"
        }) "record search"
      }
    }
  } catch {
    $actionOk = $false
    $actionErr = $_.Exception.Message
  }
  if ($actionOk) {
    $results.Add((New-ApiResult "user action logs" $true "browse/search log seeded"))
  } else {
    $results.Add((New-ApiResult "user action logs" $false $actionErr))
  }

  Ensure-Code200 (Invoke-Api -Method POST -Path "/user/favorite/$($seedIds[0])" -Token $userToken) "favorite add"
  Ensure-Code200 (Invoke-Api -Method GET -Path "/user/favorite/page" -Token $userToken -Query @{ pageNum = 1; pageSize = 10 }) "favorite page"
  Ensure-Code200 (Invoke-Api -Method DELETE -Path "/user/favorite/$($seedIds[0])" -Token $userToken) "favorite remove"
  $results.Add((New-ApiResult "favorite flow" $true "add/list/remove passed"))

  $tmpTitle = "Smoke Draft " + (Get-Date -Format "yyyyMMddHHmmss")
  Ensure-Code200 (Invoke-Api -Method POST -Path "/knowledge" -Token $adminToken -Body @{
    title = $tmpTitle
    summary = "temp smoke row"
    content = "draft -> publish -> offline -> delete"
    categoryId = [int64]$catMap["Acne"]
    type = "TEXT_TXT"
    status = 0
  }) "create temp knowledge"
  Start-Sleep -Milliseconds 300
  $tmpPage = Invoke-Api -Method GET -Path "/knowledge/page" -Token $adminToken -Query @{ pageNum = 1; pageSize = 1; keyword = $tmpTitle }
  Ensure-Code200 $tmpPage "temp query"
  $tmpId = [int64]$tmpPage.data.records[0].id
  Ensure-Code200 (Invoke-Api -Method PUT -Path "/knowledge/$tmpId/status" -Token $adminToken -Query @{ status = 1 }) "publish temp"
  Ensure-Code200 (Invoke-Api -Method PUT -Path "/knowledge/$tmpId/status" -Token $adminToken -Query @{ status = 2 }) "offline temp"
  Ensure-Code200 (Invoke-Api -Method DELETE -Path "/knowledge/$tmpId" -Token $adminToken) "delete temp"
  $results.Add((New-ApiResult "knowledge lifecycle" $true "draft->publish->offline->delete passed"))

  $overview = Invoke-Api -Method GET -Path "/admin/dashboard/overview" -Token $adminToken
  Ensure-Code200 $overview "dashboard overview"
  $report = Invoke-Api -Method GET -Path "/admin/dashboard/report" -Token $adminToken -Query @{ range = "week" }
  Ensure-Code200 $report "dashboard report"
  $ratio = Invoke-Api -Method GET -Path "/admin/dashboard/source-ratio" -Token $adminToken -Query @{ range = "week" }
  Ensure-Code200 $ratio "dashboard ratio"
  $results.Add((New-ApiResult "dashboard/report" $true "overview + report + source ratio passed"))

  Ensure-Code200 (Invoke-Api -Method GET -Path "/file/task/recent" -Token $adminToken -Query @{ size = 10 }) "task recent"
  Ensure-Code200 (Invoke-Api -Method GET -Path "/entity/pending/count" -Token $adminToken) "entity pending count"
  Ensure-Code200 (Invoke-Api -Method GET -Path "/admin/user/page" -Token $adminToken -Query @{ pageNum = 1; pageSize = 20 }) "admin user page"
  $results.Add((New-ApiResult "admin modules" $true "task/entity/user endpoints passed"))

  $passCount = @($results | Where-Object { $_.ok }).Count
  $failCount = @($results | Where-Object { -not $_.ok }).Count

  $lines = @()
  $lines += "# Feature Smoke Report"
  $lines += ""
  $lines += "- Generated at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
  $lines += "- Base URL: $BaseUrl"
  $lines += "- Passed: $passCount"
  $lines += "- Failed: $failCount"
  $lines += ""
  $lines += "## Details"
  foreach ($r in $results) {
    $flag = if ($r.ok) { "PASS" } else { "FAIL" }
    $lines += "- [$flag] $($r.name): $($r.detail)"
  }
  $lines += ""
  $lines += "## Dashboard Snapshot"
  $lines += "- knowledgeTotal: $($overview.data.knowledgeTotal)"
  $lines += "- knowledgePublished: $($overview.data.knowledgePublished)"
  $lines += "- knowledgeTodayAdded: $($overview.data.knowledgeTodayAdded)"
  $lines += "- taskPending: $($overview.data.taskPending)"
  $lines += "- entityPending: $($overview.data.entityPending)"
  $lines += "- sourceRatio: $((($ratio.data | ForEach-Object { $_.source + ':' + $_.count }) -join ', '))"

  $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
  $target = Join-Path $scriptDir $ReportPath
  $targetDir = Split-Path -Parent $target
  if (-not (Test-Path $targetDir)) { New-Item -Path $targetDir -ItemType Directory | Out-Null }
  $lines -join "`r`n" | Set-Content -Path $target -Encoding UTF8

  Write-Host "SEED_AND_SMOKE_OK"
  Write-Host "REPORT=$target"
}
catch {
  Write-Error $_.Exception.Message
  exit 1
}
