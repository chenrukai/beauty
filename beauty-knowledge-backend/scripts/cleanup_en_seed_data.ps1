param(
  [string]$BaseUrl = "http://127.0.0.1:8080/api",
  [string]$AdminUser = "admin",
  [string]$AdminPass = "admin"
)

$ErrorActionPreference = "Stop"

function Api {
  param(
    [ValidateSet("GET", "POST", "PUT", "DELETE")] [string]$Method,
    [string]$Endpoint,
    [string]$Token = "",
    $Body = $null,
    [hashtable]$Query = @{}
  )
  $uri = "$($BaseUrl)$Endpoint"
  if ($Query.Count -gt 0) {
    $qs = ($Query.GetEnumerator() | ForEach-Object { "$($_.Key)=$([uri]::EscapeDataString([string]$_.Value))" }) -join "&"
    $uri = "$($uri)?$($qs)"
  }
  $headers = @{}
  if ($Token) { $headers["Authorization"] = "Bearer $Token" }
  if ($Body -ne $null) {
    $json = $Body | ConvertTo-Json -Depth 8
    return Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers -ContentType "application/json" -Body $json -TimeoutSec 30
  }
  return Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers -TimeoutSec 30
}

function Ok($resp, $name) {
  if ($null -eq $resp -or [int]$resp.code -ne 200) { throw "failed: $name" }
}

function FindNodeByName($nodes, $name) {
  foreach ($n in $nodes) {
    if ($n.name -eq $name) { return $n }
    if ($n.children) {
      $x = FindNodeByName $n.children $name
      if ($x) { return $x }
    }
  }
  return $null
}

$login = Api -Method POST -Endpoint "/auth/login" -Body @{ username = $AdminUser; password = $AdminPass }
Ok $login "admin login"
$token = [string]$login.data.token

# 1) delete English knowledge rows inserted by seed script
$page = Api -Method GET -Endpoint "/knowledge/page" -Token $token -Query @{ pageNum = 1; pageSize = 50; keyword = "Evidence Brief |" }
Ok $page "query english knowledge"
foreach ($row in @($page.data.records)) {
  try { Ok (Api -Method DELETE -Endpoint "/knowledge/$($row.id)" -Token $token) "delete english knowledge" } catch {}
}

# 2) disable English notice row
$notices = Api -Method GET -Endpoint "/admin/notice/page" -Token $token -Query @{ pageNum = 1; pageSize = 30 }
Ok $notices "query notices"
foreach ($n in @($notices.data.records)) {
  if ($n.title -eq "Evidence pack synced") {
    try {
      Ok (Api -Method PUT -Endpoint "/admin/notice/$($n.id)" -Token $token -Body @{
        title = "System Notice"
        content = "English seed data cleaned"
        status = 0
        isTop = 0
        expireTime = $null
      }) "disable english notice"
    } catch {}
  }
}

# 3) remove English ingredient/effect relations and entities
$ingResp = Api -Method GET -Endpoint "/entity/ingredient" -Token $token
Ok $ingResp "ingredient list"
$effResp = Api -Method GET -Endpoint "/entity/effect" -Token $token
Ok $effResp "effect list"
$relResp = Api -Method GET -Endpoint "/entity/relation/ingredient-effect" -Token $token
Ok $relResp "relation list"

$enIng = @($ingResp.data | Where-Object { $_.name -match '^(Niacinamide|Azelaic Acid|Benzoyl Peroxide|Retinol|Salicylic Acid|Ceramide|Panthenol)$' })
$enEff = @($effResp.data | Where-Object { $_.name -match '^(Oil Control|Barrier Repair|Tone Evenness|Anti-Inflammatory)$' })
$enIngIds = @($enIng | ForEach-Object { [int64]$_.id })
$enEffIds = @($enEff | ForEach-Object { [int64]$_.id })

foreach ($r in @($relResp.data)) {
  if ($enIngIds -contains [int64]$r.ingredientId -or $enEffIds -contains [int64]$r.effectId) {
    try {
      Ok (Api -Method DELETE -Endpoint "/entity/relation/ingredient-effect" -Token $token -Query @{
        ingredientId = [int64]$r.ingredientId
        effectId = [int64]$r.effectId
      }) "delete relation"
    } catch {}
  }
}

foreach ($x in $enIng) {
  try { Ok (Api -Method DELETE -Endpoint "/entity/ingredient/$($x.id)" -Token $token) "delete ingredient" } catch {}
}
foreach ($x in $enEff) {
  try { Ok (Api -Method DELETE -Endpoint "/entity/effect/$($x.id)" -Token $token) "delete effect" } catch {}
}

# 4) disable English category branch
$treeResp = Api -Method GET -Endpoint "/category/tree" -Token $token
Ok $treeResp "category tree"
$tree = @($treeResp.data)
$enRoot = FindNodeByName $tree "Evidence Hub"
if ($enRoot) {
  foreach ($child in @($enRoot.children)) {
    try {
      Ok (Api -Method PUT -Endpoint "/category/$($child.id)" -Token $token -Body @{
        name = $child.name
        parentId = [int64]$child.parentId
        sortOrder = [int]$child.sortOrder
        status = 0
      }) "disable child category"
    } catch {}
  }
  try {
    Ok (Api -Method PUT -Endpoint "/category/$($enRoot.id)" -Token $token -Body @{
      name = $enRoot.name
      parentId = [int64]$enRoot.parentId
      sortOrder = [int]$enRoot.sortOrder
      status = 0
    }) "disable root category"
  } catch {}
}

Write-Host "CLEANUP_EN_SEED_DONE"
