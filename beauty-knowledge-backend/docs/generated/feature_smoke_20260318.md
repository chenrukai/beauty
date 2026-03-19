# Feature Smoke Report

- Generated at: 2026-03-18 20:12:54
- Base URL: http://127.0.0.1:8080/api
- Passed: 10
- Failed: 1

## Details
- [PASS] auth login: admin/user login passed
- [PASS] category tree: evidence categories ready
- [PASS] knowledge seed: evidence knowledge inserted
- [PASS] notice module: notice create/list passed
- [PASS] entity module: ingredient/effect seed passed
- [PASS] relation module: ingredient-effect relation bind passed
- [FAIL] user action logs: record browse failed :: {"code":500,"message":"æå¡å¨å\u0085é¨éè¯¯","timestamp":1773835974228}
- [PASS] favorite flow: add/list/remove passed
- [PASS] knowledge lifecycle: draft->publish->offline->delete passed
- [PASS] dashboard/report: overview + report + source ratio passed
- [PASS] admin modules: task/entity/user endpoints passed

## Dashboard Snapshot
- knowledgeTotal: 13
- knowledgePublished: 13
- knowledgeTodayAdded: 12
- taskPending: 0
- entityPending: 0
- sourceRatio: recommend:0, search:4, favorite:0, other:18
