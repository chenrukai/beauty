from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import requests

ROOT = Path(r"D:\beauty")
MANIFEST_PATH = ROOT / "scripts" / "thesis_page_screenshot_manifest.json"
CLI = ROOT.parent / "nodejs" / "node_global" / "node_modules" / "playwright-cli" / "node_modules" / "@playwright" / "cli" / "playwright-cli.js"
FRONTEND_URL = "http://127.0.0.1:5173"
MOCK_ASSET_PATH = ROOT / "beauty-knowledge-frontend" / "public" / "thesis-mock-data.json"
VIEWPORT = (1600, 1200)

ADMIN_AUTH = {
    "token": "mock-admin-token",
    "userInfo": {"id": 1, "username": "admin", "nickname": "系统管理员", "role": "admin"},
}
USER_AUTH = {
    "token": "mock-user-token",
    "userInfo": {"id": 2, "username": "user", "nickname": "普通用户", "role": "user"},
}

MOCK = {
    "notices": [
        {"id": 1, "title": "五一活动知识专题已上线", "content": "新增敏感肌修护、夏季控油和彩妆卸除专题知识，用户端可直接搜索体验。", "status": 1, "isTop": 1, "publishTime": "2026-04-10 09:00:00", "expireTime": "2026-05-10 23:59:59"},
        {"id": 2, "title": "问答助手提示词库已更新", "content": "对成分解释、肤质分层护理和功效对比问答进行了增强。", "status": 1, "isTop": 0, "publishTime": "2026-04-08 14:20:00", "expireTime": "2026-05-08 23:59:59"},
        {"id": 3, "title": "知识抽取审核流程优化", "content": "后台新增候选筛选、批量确认与图谱证据回填入口。", "status": 0, "isTop": 0, "publishTime": "2026-04-05 10:00:00", "expireTime": "2026-04-25 23:59:59"},
    ],
    "categories": [
        {"id": 101, "name": "护肤基础", "parentId": 0, "sortOrder": 1, "status": 1, "children": [{"id": 102, "name": "敏感肌护理", "parentId": 101, "sortOrder": 1, "status": 1, "children": []}, {"id": 103, "name": "油皮控油", "parentId": 101, "sortOrder": 2, "status": 1, "children": []}]},
        {"id": 201, "name": "成分解析", "parentId": 0, "sortOrder": 2, "status": 1, "children": [{"id": 202, "name": "保湿修护", "parentId": 201, "sortOrder": 1, "status": 1, "children": []}, {"id": 203, "name": "功效成分", "parentId": 201, "sortOrder": 2, "status": 1, "children": []}]},
    ],
    "knowledge_records": [
        {"id": 1, "title": "神经酰胺屏障修护指南", "summary": "从屏障结构、适用肤质和搭配建议解释神经酰胺的修护价值。", "content": "神经酰胺适合用于屏障受损、干燥和轻度敏感状态的日常修护，可与胆固醇、脂肪酸协同提升角质层稳定性。", "status": 1, "viewCount": 268, "categoryId": 202, "updatedAt": "2026-04-12 15:20:00"},
        {"id": 2, "title": "烟酰胺与油皮提亮管理", "summary": "围绕控油、淡印和耐受建立循序渐进的使用方案。", "content": "烟酰胺可辅助控油与提亮，建议从低浓度起步，并配合保湿修护成分降低刺激风险。", "status": 1, "viewCount": 221, "categoryId": 203, "updatedAt": "2026-04-11 19:40:00"},
        {"id": 3, "title": "壬二酸痘印护理知识卡", "summary": "总结壬二酸在油痘肌、色沉和闭口中的常见使用策略。", "content": "壬二酸可用于痘印、闭口和油痘肌调理，夜间使用更利于与其他功能性成分错峰搭配。", "status": 1, "viewCount": 195, "categoryId": 103, "updatedAt": "2026-04-11 10:10:00"},
        {"id": 4, "title": "A醇夜间建立耐受方案", "summary": "通过低频起步和保湿辅助降低刺激风险。", "content": "A醇应采用低频率、低浓度起步，并注意避开破损皮肤以及与强酸同晚叠加。", "status": 0, "viewCount": 143, "categoryId": 203, "updatedAt": "2026-04-09 18:10:00"},
        {"id": 5, "title": "VC 与防晒协同思路", "summary": "从抗氧化和日间防护角度说明组合逻辑。", "content": "维生素C可作为白天抗氧化前置护理，与防晒协同减少自由基压力。", "status": 1, "viewCount": 176, "categoryId": 203, "updatedAt": "2026-04-08 16:30:00"},
    ],
    "favorites": [
        {"knowledgeId": 1, "title": "神经酰胺屏障修护指南", "type": "知识", "viewCount": 268},
        {"knowledgeId": 2, "title": "烟酰胺与油皮提亮管理", "type": "知识", "viewCount": 221},
        {"knowledgeId": 3, "title": "壬二酸痘印护理知识卡", "type": "知识", "viewCount": 195},
    ],
    "favorite_ids": [1, 2, 3],
    "sessions": [{"id": 301, "title": "敏感肌修护咨询", "updatedAt": "2026-04-13 10:18:00"}, {"id": 302, "title": "油皮夏季分层护理", "updatedAt": "2026-04-12 21:06:00"}],
    "session_messages": {
        "301": [{"role": "user", "content": "神经酰胺适合敏感肌吗？"}, {"role": "assistant", "content": "适合。神经酰胺主要帮助修护角质层屏障，适用于干燥、屏障受损和轻度敏感状态，建议搭配保湿修护类产品循序使用。", "sources": [{"chunkId": 501, "fileId": 801, "fileName": "神经酰胺修护专题.pdf", "pageNo": 3, "content": "神经酰胺可协同胆固醇和脂肪酸提升角质层脂质完整性。"}]}],
        "302": [{"role": "user", "content": "油皮夏天怎么分层护肤？"}, {"role": "assistant", "content": "建议采用轻薄保湿 + 定向控油 + 白天防晒的结构，避免一次叠加过多厚重产品。", "sources": [{"chunkId": 502, "fileId": 803, "fileName": "烟酰胺控油讲解.docx", "pageNo": 2, "content": "油皮夏季护理应关注轻薄保湿、耐受建立和白天防晒。"}]}],
    },
    "tasks": [
        {"id": 601, "fileId": 801, "fileName": "神经酰胺修护专题.pdf", "knowledgeTitle": "神经酰胺屏障修护指南", "taskType": "KNOWLEDGE_PROCESS", "status": "SUCCESS", "stageCode": "CONFIRMED", "stageText": "确认完成", "progress": 100, "resultMsg": "实体抽取 12 条，关系确认 8 条", "failureReason": "", "updatedAt": "2026-04-12 15:08:00", "startedAt": "2026-04-12 15:01:00", "finishedAt": "2026-04-12 15:08:00", "canRetry": False, "canReExtract": True, "canConfirm": False},
        {"id": 602, "fileId": 803, "fileName": "烟酰胺控油讲解.docx", "knowledgeTitle": "烟酰胺与油皮提亮管理", "taskType": "KNOWLEDGE_PROCESS", "status": "RUNNING", "stageCode": "PENDING_CONFIRM", "stageText": "待人工确认", "progress": 82, "resultMsg": "已完成候选抽取，待审核 5 条", "failureReason": "", "updatedAt": "2026-04-11 19:28:00", "startedAt": "2026-04-11 19:20:00", "finishedAt": "", "canRetry": False, "canReExtract": False, "canConfirm": True},
        {"id": 603, "fileId": 804, "fileName": "痘印护理门店话术.txt", "knowledgeTitle": "壬二酸痘印护理知识卡", "taskType": "KNOWLEDGE_PROCESS", "status": "FAIL", "stageCode": "PARSE_FAILED", "stageText": "解析失败", "progress": 36, "resultMsg": "部分文本编码异常，建议重新上传 UTF-8 文件", "failureReason": "文件源格式不规范", "updatedAt": "2026-04-11 09:46:00", "startedAt": "2026-04-11 09:40:00", "finishedAt": "2026-04-11 09:46:00", "canRetry": True, "canReExtract": False, "canConfirm": False},
    ],
    "overview": {"knowledgeTotal": 126, "knowledgeTodayAdded": 8, "entityPending": 5, "taskFailed": 1},
    "hot_contents": [{"id": 1, "title": "神经酰胺屏障修护指南", "type": "知识", "viewCount": 268, "updatedAt": "2026-04-12 15:20:00"}, {"id": 2, "title": "烟酰胺与油皮提亮管理", "type": "知识", "viewCount": 221, "updatedAt": "2026-04-11 19:40:00"}, {"id": 3, "title": "VC 与防晒协同思路", "type": "知识", "viewCount": 176, "updatedAt": "2026-04-08 16:30:00"}],
    "hot_keywords": [{"id": 1, "keyword": "神经酰胺", "searchCount": 49}, {"id": 2, "keyword": "烟酰胺", "searchCount": 42}, {"id": 3, "keyword": "控油", "searchCount": 37}, {"id": 4, "keyword": "敏感肌", "searchCount": 31}],
    "source_ratio": [{"source": "recommend", "count": 68}, {"source": "search", "count": 94}, {"source": "favorite", "count": 27}],
    "report": {
        "active": {"activeUsers": 46, "actionCount": 312, "avgActionsPerUser": 6.78},
        "browseTrend": [{"label": "周一", "cnt": 31}, {"label": "周二", "cnt": 48}, {"label": "周三", "cnt": 52}, {"label": "周四", "cnt": 61}, {"label": "周五", "cnt": 74}, {"label": "周六", "cnt": 66}, {"label": "周日", "cnt": 57}],
        "sourceRatio": [{"source": "recommend", "count": 126}, {"source": "search", "count": 181}, {"source": "favorite", "count": 58}],
        "hotKnowledge": [{"title": "神经酰胺屏障修护指南", "browseCount": 268}, {"title": "烟酰胺与油皮提亮管理", "browseCount": 221}, {"title": "壬二酸痘印护理知识卡", "browseCount": 195}],
        "hotKeywords": [{"keyword": "神经酰胺", "searchCount": 49}, {"keyword": "控油", "searchCount": 37}, {"keyword": "痘印", "searchCount": 29}],
    },
    "pending_list": [
        {"id": 701, "candidateType": "entity", "entityType": "ingredient", "entityName": "神经酰胺 NP", "confidence": 0.96, "extractMethod": "RULE", "sourceText": "来源文件：神经酰胺修护专题.pdf，第 3 页", "status": "PENDING", "payloadJson": {}},
        {"id": 702, "candidateType": "relation", "entityType": "relation", "entityName": "产品与成分关系", "confidence": 0.91, "extractMethod": "RULE", "sourceText": "来源文件：烟酰胺控油讲解.docx，第 2 页", "status": "PENDING", "payloadJson": {"predicate": "PRODUCT_CONTAINS_INGREDIENT", "subjectName": "清透修护乳", "objectName": "烟酰胺"}},
        {"id": 703, "candidateType": "relation", "entityType": "relation", "entityName": "成分与功效关系", "confidence": 0.88, "extractMethod": "MODEL", "sourceText": "来源文件：痘印护理门店话术.txt，第 1 页", "status": "CONFIRMED", "payloadJson": {"predicate": "INGREDIENT_HAS_EFFECT", "subjectName": "壬二酸", "objectName": "淡化痘印"}},
    ],
    "kg_config": {"minSegmentLength": 18, "productIngredientConfidence": 0.82, "ingredientEffectConfidence": 0.78, "productEffectConfidence": 0.8},
    "products": [{"id": 901, "name": "清透修护乳"}, {"id": 902, "name": "控油平衡精华"}, {"id": 903, "name": "舒缓保湿霜"}],
    "ingredients": [{"id": 911, "name": "神经酰胺"}, {"id": 912, "name": "烟酰胺"}, {"id": 913, "name": "壬二酸"}],
    "effects": [{"id": 921, "name": "修护屏障"}, {"id": 922, "name": "提亮肤色"}, {"id": 923, "name": "淡化痘印"}],
    "graph": {
        "centerKey": "PRODUCT:901",
        "nodes": [{"nodeKey": "PRODUCT:901", "type": "PRODUCT", "name": "清透修护乳"}, {"nodeKey": "INGREDIENT:911", "type": "INGREDIENT", "name": "神经酰胺"}, {"nodeKey": "INGREDIENT:912", "type": "INGREDIENT", "name": "烟酰胺"}, {"nodeKey": "EFFECT:921", "type": "EFFECT", "name": "修护屏障"}, {"nodeKey": "EFFECT:922", "type": "EFFECT", "name": "提亮肤色"}],
        "edges": [{"subjectKey": "PRODUCT:901", "objectKey": "INGREDIENT:911", "predicate": "PRODUCT_CONTAINS_INGREDIENT", "confidence": 0.95, "evidenceCount": 2}, {"subjectKey": "PRODUCT:901", "objectKey": "INGREDIENT:912", "predicate": "PRODUCT_CONTAINS_INGREDIENT", "confidence": 0.9, "evidenceCount": 1}, {"subjectKey": "INGREDIENT:911", "objectKey": "EFFECT:921", "predicate": "INGREDIENT_HAS_EFFECT", "confidence": 0.93, "evidenceCount": 2}],
    },
    "path_result": {"found": True, "hopCount": 2, "nodes": [{"nodeKey": "PRODUCT:901", "name": "清透修护乳"}, {"nodeKey": "INGREDIENT:911", "name": "神经酰胺"}, {"nodeKey": "EFFECT:921", "name": "修护屏障"}], "edges": [{"subjectKey": "PRODUCT:901", "objectKey": "INGREDIENT:911", "predicate": "PRODUCT_CONTAINS_INGREDIENT"}, {"subjectKey": "INGREDIENT:911", "objectKey": "EFFECT:921", "predicate": "INGREDIENT_HAS_EFFECT"}]},
    "evidence": [{"id": 1001, "fileId": 801, "chunkId": 501, "pageNo": 3, "extractor": "RULE", "confidence": 0.95, "sourceText": "清透修护乳添加神经酰胺，以提升角质层脂质结构稳定性。", "createdAt": "2026-04-12 15:06:00"}],
    "users": [{"id": 1, "username": "admin", "nickname": "系统管理员", "role": "admin", "status": 1, "createdAt": "2026-03-01 09:00:00"}, {"id": 2, "username": "user", "nickname": "演示用户", "role": "user", "status": 1, "createdAt": "2026-03-02 10:30:00"}, {"id": 3, "username": "ops_demo", "nickname": "运营值班", "role": "admin", "status": 1, "createdAt": "2026-03-10 15:12:00"}, {"id": 4, "username": "guest_train", "nickname": "培训顾问", "role": "user", "status": 0, "createdAt": "2026-03-18 13:45:00"}],
}


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    cmd = ["node", str(CLI), *args]
    return subprocess.run(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="ignore", capture_output=True, check=True)


def wait_http(url: str, timeout: int = 120) -> None:
    end = time.time() + timeout
    while time.time() < end:
        try:
            if requests.get(url, timeout=5).ok:
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError(f"Timed out waiting for {url}")


def ensure_mock_asset() -> None:
    MOCK_ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    MOCK_ASSET_PATH.write_text(json.dumps(MOCK, ensure_ascii=False, indent=2), encoding="utf-8")


def session_name(role: str, route: str) -> str:
    slug = route.strip("/").replace("/", "_").replace("-", "_") or "root"
    return f"{role}_{slug}"


def page_config(route: str) -> tuple[str, str]:
    if route == "/login":
        return "", ""
    if route == "/user/home":
        return """
if (path === '/notice/list') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.notices.filter(it => it.status === 1).slice(0, 3)) });
if (path === '/knowledge/page') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok({ total: mock.knowledge_records.length, pageNum: 1, pageSize: 6, records: mock.knowledge_records.filter(it => Number(it.status) === 1) }) });
if (/^\\/user\\/favorite\\/check\\/\\d+$/.test(path)) return route.fulfill({ status: 200, headers: jsonHeaders, body: ok({ favorited: mock.favorite_ids.includes(Number(path.split('/').pop() || 0)) }) });
if (path === '/user/action') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(true) });
""", ""
    if route == "/user/chat":
        return """
if (path === '/chat/session') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.sessions) });
if (/^\\/chat\\/session\\/\\d+\\/messages$/.test(path)) return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.session_messages[path.split('/')[3]] || []) });
if (/^\\/chat\\/session\\/\\d+\\/attachments$/.test(path)) return route.fulfill({ status: 200, headers: jsonHeaders, body: ok([]) });
""", """
const firstSession = page.locator('.session').first();
if (await firstSession.count()) {
  await firstSession.click();
  await page.waitForTimeout(1200);
}
"""
    if route == "/user/favorites":
        return """
if (path === '/user/favorite/page') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok({ total: mock.favorites.length, pageNum: 1, pageSize: 8, records: mock.favorites }) });
""", ""
    if route == "/admin/overview":
        return """
if (path === '/admin/dashboard/overview') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.overview) });
if (path === '/admin/dashboard/hot-content') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.hot_contents) });
if (path === '/admin/dashboard/hot-keywords') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.hot_keywords) });
if (path === '/admin/dashboard/source-ratio') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.source_ratio) });
if (path === '/file/task/recent') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.tasks) });
""", ""
    if route == "/admin/report":
        return """
if (path === '/admin/dashboard/report') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.report) });
""", ""
    if route == "/admin/knowledge/list":
        return """
if (path === '/category/tree') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.categories) });
if (path === '/knowledge/page') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok({ total: mock.knowledge_records.length, pageNum: 1, pageSize: 20, records: mock.knowledge_records }) });
""", ""
    if route == "/admin/knowledge/upload":
        return """
if (path === '/category/tree') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.categories) });
if (path === '/knowledge/page') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok({ total: mock.knowledge_records.length, pageNum: 1, pageSize: 100, records: mock.knowledge_records }) });
if (path === '/file/capability/transcribe') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok({ available: true, message: '本地演示环境已启用多媒体转写能力' }) });
""", ""
    if route == "/admin/category/tree":
        return """
if (path === '/category/tree') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.categories) });
""", ""
    if route == "/admin/entity/confirm":
        return """
if (path === '/kg/pending') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.pending_list) });
if (path === '/kg/config/extraction') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.kg_config) });
""", ""
    if route == "/admin/entity/graph":
        return """
if (path === '/entity/product') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.products) });
if (path === '/entity/ingredient') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.ingredients) });
if (path === '/entity/effect') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.effects) });
if (/^\\/kg\\/product\\/\\d+\\/graph$/.test(path)) return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.graph) });
if (path === '/kg/path') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.path_result) });
if (path === '/kg/evidence') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.evidence) });
""", """
const selectWrappers = page.locator('.el-select .el-input__wrapper');
if (await selectWrappers.count() >= 4) {
  await selectWrappers.nth(0).click();
  await page.locator('.el-select-dropdown__item').first().click();
  await page.waitForTimeout(500);
  await page.getByRole('button', { name: '加载图谱' }).click();
  await page.waitForTimeout(800);
  await selectWrappers.nth(1).click();
  await page.locator('.el-select-dropdown__item').first().click();
  await page.waitForTimeout(400);
  await selectWrappers.nth(3).click();
  await page.locator('.el-select-dropdown__item').last().click();
  await page.waitForTimeout(400);
  await page.getByRole('button', { name: '查询路径' }).click();
  await page.waitForTimeout(1000);
  const evidenceButton = page.getByRole('button', { name: '查看证据' }).first();
  if (await evidenceButton.count()) {
    await evidenceButton.click();
    await page.waitForTimeout(800);
  }
}
"""
    if route == "/admin/task/monitor":
        return """
if (path === '/file/task/recent') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.tasks) });
if (/^\\/file\\/task\\/\\d+$/.test(path)) return route.fulfill({ status: 200, headers: jsonHeaders, body: ok(mock.tasks.find(it => String(it.id) === String(path.split('/').pop())) || mock.tasks[0]) });
""", """
const viewButton = page.getByRole('button', { name: '查看' }).first();
if (await viewButton.count()) {
  await viewButton.click();
  await page.waitForTimeout(1200);
}
"""
    if route == "/admin/user/manage":
        return """
if (path === '/admin/user/page') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok({ total: mock.users.length, pageNum: 1, pageSize: 10, records: mock.users }) });
""", ""
    if route == "/admin/system/notice":
        return """
if (path === '/admin/notice/page') return route.fulfill({ status: 200, headers: jsonHeaders, body: ok({ total: mock.notices.length, pageNum: 1, pageSize: 10, records: mock.notices }) });
""", ""
    raise ValueError(f"Unsupported route: {route}")


def make_script(route: str, role: str, image_path: str) -> str:
    handlers, after_load = page_config(route)
    auth = {"guest": None, "admin": ADMIN_AUTH, "user": USER_AUTH}[role]
    auth_json = json.dumps(auth, ensure_ascii=True)
    page_url = f"{FRONTEND_URL}{route}"
    image_path = image_path.replace("\\", "/")
    return f"""
async page => {{
  const auth = {auth_json};
  const jsonHeaders = {{
    'access-control-allow-origin': '*',
    'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'access-control-allow-headers': 'Authorization,Content-Type',
    'content-type': 'application/json; charset=utf-8'
  }};
  const ok = (data) => JSON.stringify({{ code: 200, message: 'success', data }});

  await page.setViewportSize({{ width: {VIEWPORT[0]}, height: {VIEWPORT[1]} }});
  await page.goto('{FRONTEND_URL}/login', {{ waitUntil: 'domcontentloaded' }});
  const mock = await page.evaluate(async () => (await (await fetch('/thesis-mock-data.json')).json()));

  await page.route('**://127.0.0.1:8080/api/**', async (route) => {{
    const request = route.request();
    const rawUrl = request.url();
    const path = rawUrl.split('?')[0].replace('http://127.0.0.1:8080/api', '');
    if (request.method().toUpperCase() === 'OPTIONS') {{
      return route.fulfill({{ status: 204, headers: jsonHeaders, body: '' }});
    }}
{handlers}
    if (path === '/auth/info') return route.fulfill({{ status: 200, headers: jsonHeaders, body: ok(auth ? auth.userInfo : null) }});
    if (path === '/auth/logout') return route.fulfill({{ status: 200, headers: jsonHeaders, body: ok(true) }});
    return route.fulfill({{ status: 200, headers: jsonHeaders, body: ok(true) }});
  }});

  await page.addInitScript((payload) => {{
    if (payload) {{
      localStorage.setItem('bk_token', payload.token || '');
      localStorage.setItem('bk_user', JSON.stringify(payload.userInfo || null));
    }} else {{
      localStorage.removeItem('bk_token');
      localStorage.removeItem('bk_user');
    }}
  }}, auth);

  await page.goto('{page_url}', {{ waitUntil: 'domcontentloaded' }});
  await page.waitForTimeout(1600);
{after_load}
  await page.screenshot({{ path: '{image_path}', fullPage: true }});
}}
""".strip()


def capture_item(item: dict) -> None:
    out_path = Path(item["image_path"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    session = session_name(item["role"], item["route"])
    try:
        run_cli("--session", session, "open", f"{FRONTEND_URL}/login")
        run_cli("--session", session, "resize", str(VIEWPORT[0]), str(VIEWPORT[1]))
        run_cli("--session", session, "run-code", make_script(item["route"], item["role"], str(out_path)))
    finally:
        try:
            run_cli("session-stop", session)
        except subprocess.CalledProcessError:
            pass


def main() -> None:
    wait_http(f"{FRONTEND_URL}/login", timeout=120)
    ensure_mock_asset()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for item in manifest:
        capture_item(item)


if __name__ == "__main__":
    main()
