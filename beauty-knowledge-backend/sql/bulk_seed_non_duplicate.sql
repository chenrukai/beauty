-- ============================================================
-- 批量补数脚本（可重复执行，不重复插入）
-- 目标库: beauty_knowledge (MySQL 8.0+)
-- 用法:
--   USE beauty_knowledge;
--   SOURCE bulk_seed_non_duplicate.sql;
-- ============================================================

USE beauty_knowledge;

SET NAMES utf8mb4;

-- ------------------------------
-- 0) 确保有基础用户（admin/user）
-- ------------------------------
INSERT IGNORE INTO sys_user (id, username, password, nickname, phone, role, status)
VALUES
    (1, 'admin', '$2a$10$Xkzvqpccpw58aTSzFTliC./y3PIBlw31cd0EHgQl7lC4.g6A36cq2', '系统管理员', '13800000001', 'admin', 1),
    (2, 'user', '$2a$10$yxVRdh03A9RJt0hCXgmHceViy26jD1YObkOQ5Dkurxof9CbfkebqK', '普通用户', '13800000002', 'user', 1);

-- ------------------------------
-- 1) 批量普通用户（200）
-- username 唯一，重复执行自动忽略
-- ------------------------------
WITH RECURSIVE seq_user AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_user WHERE n < 200
)
INSERT IGNORE INTO sys_user (username, password, nickname, phone, role, status)
SELECT
    CONCAT('u_bulk_', LPAD(n, 4, '0')) AS username,
    '$2a$10$yxVRdh03A9RJt0hCXgmHceViy26jD1YObkOQ5Dkurxof9CbfkebqK' AS password,
    CONCAT('门店用户', LPAD(n, 4, '0')) AS nickname,
    CONCAT('139', LPAD(n, 8, '0')) AS phone,
    'user' AS role,
    1 AS status
FROM seq_user;

-- ------------------------------
-- 2) 分类补数（6 个一级 + 每个 10 个二级）
-- uk_parent_name 保障唯一
-- ------------------------------
WITH RECURSIVE seq_root AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_root WHERE n < 6
)
INSERT IGNORE INTO kb_category (name, parent_id, sort_order, status)
SELECT
    CONCAT('批量分类-根-', n) AS name,
    0 AS parent_id,
    n AS sort_order,
    1 AS status
FROM seq_root;

WITH RECURSIVE seq_child AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_child WHERE n < 10
)
INSERT IGNORE INTO kb_category (name, parent_id, sort_order, status)
SELECT
    CONCAT('批量分类-子-', r.id, '-', seq_child.n) AS name,
    r.id AS parent_id,
    seq_child.n AS sort_order,
    1 AS status
FROM kb_category r
CROSS JOIN seq_child
WHERE r.parent_id = 0
  AND r.name LIKE '批量分类-根-%';

-- ------------------------------
-- 3) 成分（300）+ 功效（120）+ 产品（500）
-- 唯一键保证不重复
-- ------------------------------
WITH RECURSIVE seq_ing AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_ing WHERE n < 300
)
INSERT IGNORE INTO beauty_ingredient (name, alias_name, category, safety_level, intro, status)
SELECT
    CONCAT('批量成分-', LPAD(n, 4, '0')) AS name,
    CONCAT('ING-', LPAD(n, 4, '0')) AS alias_name,
    ELT((n % 6) + 1, '保湿类', '修护类', '抗氧化类', '角质调理类', '舒缓类', '植物提取类') AS category,
    ELT((n % 3) + 1, 'A', 'B', 'C') AS safety_level,
    CONCAT('用于门店知识演示的批量成分数据，编号 ', n) AS intro,
    1 AS status
FROM seq_ing;

WITH RECURSIVE seq_eff AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_eff WHERE n < 120
)
INSERT IGNORE INTO beauty_effect (name, scene, intro, status)
SELECT
    CONCAT('批量功效-', LPAD(n, 4, '0')) AS name,
    ELT((n % 6) + 1, '日常护理', '敏感修护', '油痘管理', '抗老管理', '术后维养', '头皮护理') AS scene,
    CONCAT('用于演示检索与关系图谱的功效词条，编号 ', n) AS intro,
    1 AS status
FROM seq_eff;

WITH RECURSIVE seq_prod AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_prod WHERE n < 500
)
INSERT IGNORE INTO beauty_product (name, brand, product_type, skin_type, intro, status)
SELECT
    CONCAT('批量产品-', LPAD(n, 5, '0')) AS name,
    CONCAT('示例品牌-', LPAD(((n - 1) % 25) + 1, 2, '0')) AS brand,
    ELT((n % 8) + 1, '洁面', '精华', '面霜', '乳液', '面膜', '防晒', '头皮护理', '修护霜') AS product_type,
    ELT((n % 5) + 1, '干性', '油性', '混合', '敏感', '中性') AS skin_type,
    CONCAT('用于系统压测与前台推荐卡展示，编号 ', n) AS intro,
    1 AS status
FROM seq_prod;

-- ------------------------------
-- 4) 成分-功效关系（1200）/ 产品-成分关系（3000）
-- 使用 INSERT IGNORE 防重复
-- ------------------------------
WITH RECURSIVE seq_ie AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_ie WHERE n < 1200
),
ing AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM beauty_ingredient
),
eff AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM beauty_effect
),
ingc AS (
    SELECT COUNT(*) AS c FROM ing
),
effc AS (
    SELECT COUNT(*) AS c FROM eff
)
INSERT IGNORE INTO rel_ingredient_effect (ingredient_id, effect_id, confidence, source)
SELECT
    i.id AS ingredient_id,
    e.id AS effect_id,
    ROUND(0.70 + (seq_ie.n % 25) * 0.01, 2) AS confidence,
    ELT((seq_ie.n % 2) + 1, 'dictionary', 'llm') AS source
FROM seq_ie
JOIN ingc ON ingc.c > 0
JOIN effc ON effc.c > 0
JOIN ing i ON i.rn = ((seq_ie.n - 1) % ingc.c) + 1
JOIN eff e ON e.rn = (((seq_ie.n - 1) * 3) % effc.c) + 1;

WITH RECURSIVE seq_pi AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_pi WHERE n < 3000
),
prod AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM beauty_product
),
ing2 AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM beauty_ingredient
),
prodc AS (
    SELECT COUNT(*) AS c FROM prod
),
ingc2 AS (
    SELECT COUNT(*) AS c FROM ing2
)
INSERT IGNORE INTO rel_product_ingredient (product_id, ingredient_id, concentration)
SELECT
    p.id AS product_id,
    i.id AS ingredient_id,
    ELT((seq_pi.n % 5) + 1, '0.1%-0.3%', '0.3%-1%', '1%-3%', '3%-5%', '5%-10%') AS concentration
FROM seq_pi
JOIN prodc ON prodc.c > 0
JOIN ingc2 ON ingc2.c > 0
JOIN prod p ON p.rn = ((seq_pi.n - 1) % prodc.c) + 1
JOIN ing2 i ON i.rn = (((seq_pi.n - 1) * 5) % ingc2.c) + 1;

-- ------------------------------
-- 5) 知识（2000）
-- 通过标题去重，避免重复执行产生重复内容
-- ------------------------------
WITH RECURSIVE seq_1000 AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_1000 WHERE n < 1000
),
seq_2000 AS (
    SELECT n FROM seq_1000
    UNION ALL
    SELECT n + 1000 FROM seq_1000
),
cat AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM kb_category
    WHERE status = 1
),
catc AS (
    SELECT COUNT(*) AS c FROM cat
),
author AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM sys_user
    WHERE status = 1
),
authorc AS (
    SELECT COUNT(*) AS c FROM author
)
INSERT INTO kb_knowledge (title, summary, content, category_id, type, cover_url, status, view_count, author_id)
SELECT
    CONCAT('批量知识-', LPAD(seq_2000.n, 5, '0')) AS title,
    CONCAT('用于系统演示和检索测试的批量知识摘要，编号 ', seq_2000.n) AS summary,
    CONCAT(
        '【批量知识正文】编号 ', seq_2000.n, '。先做肤质评估，再给护理路径：',
        '清洁-舒缓-修护-维稳。出现刺痛/泛红时，优先停用高刺激成分并降低频次。'
    ) AS content,
    c.id AS category_id,
    ELT((seq_2000.n % 3) + 1, 'TEXT', 'PDF', 'IMAGE') AS type,
    CONCAT('https://cdn.example.com/bulk/cover/', seq_2000.n, '.jpg') AS cover_url,
    1 AS status,
    (seq_2000.n * 13) % 3000 AS view_count,
    a.id AS author_id
FROM seq_2000
JOIN catc ON catc.c > 0
JOIN authorc ON authorc.c > 0
JOIN cat c ON c.rn = ((seq_2000.n - 1) % catc.c) + 1
JOIN author a ON a.rn = ((seq_2000.n - 1) % authorc.c) + 1
WHERE NOT EXISTS (
    SELECT 1
    FROM kb_knowledge k
    WHERE k.title = CONCAT('批量知识-', LPAD(seq_2000.n, 5, '0'))
);

-- ------------------------------
-- 6) 为批量知识补文件（每知识 1 个文件）
-- file_hash 唯一，knowledge_id 已有文件则跳过
-- ------------------------------
INSERT INTO kb_file (knowledge_id, original_name, file_type, file_size, minio_path, file_hash, version, process_status, uploaded_by)
SELECT
    k.id AS knowledge_id,
    CONCAT('bulk_', k.id, '.', IF(k.type = 'IMAGE', 'png', 'pdf')) AS original_name,
    IF(k.type = 'IMAGE', 'image', 'pdf') AS file_type,
    150000 + (k.id % 1000) * 123 AS file_size,
    CONCAT('bulk/', DATE_FORMAT(NOW(), '%Y/%m/'), k.id, '.', IF(k.type = 'IMAGE', 'png', 'pdf')) AS minio_path,
    SHA2(CONCAT('bulk-file-', k.id), 256) AS file_hash,
    1 AS version,
    'SUCCESS' AS process_status,
    COALESCE((SELECT id FROM sys_user WHERE role = 'admin' AND status = 1 ORDER BY id LIMIT 1), 1) AS uploaded_by
FROM kb_knowledge k
WHERE k.title LIKE '批量知识-%'
  AND NOT EXISTS (
      SELECT 1
      FROM kb_file f
      WHERE f.knowledge_id = k.id
  );

-- ------------------------------
-- 7) 任务（每文件 1 条）
-- ------------------------------
INSERT INTO process_task (file_id, task_type, status, progress, result_msg, retry_count, max_retry, started_at, finished_at)
SELECT
    f.id AS file_id,
    'KNOWLEDGE_PROCESS' AS task_type,
    'SUCCESS' AS status,
    100 AS progress,
    '批量任务处理成功' AS result_msg,
    0 AS retry_count,
    3 AS max_retry,
    DATE_SUB(NOW(), INTERVAL (f.id % 20) DAY) AS started_at,
    DATE_SUB(NOW(), INTERVAL (f.id % 20) DAY) + INTERVAL 3 MINUTE AS finished_at
FROM kb_file f
JOIN kb_knowledge k ON k.id = f.knowledge_id
WHERE k.title LIKE '批量知识-%'
  AND NOT EXISTS (
      SELECT 1
      FROM process_task t
      WHERE t.file_id = f.id
  );

-- ------------------------------
-- 8) 分块（每文件 4 块）
-- ------------------------------
WITH RECURSIVE seq_chunk AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_chunk WHERE n < 4
)
INSERT INTO kb_chunk (knowledge_id, file_id, chunk_index, page_no, content, char_count, vector_status)
SELECT
    f.knowledge_id,
    f.id AS file_id,
    seq_chunk.n AS chunk_index,
    seq_chunk.n AS page_no,
    CONCAT(
        '批量分块内容：知识ID=', f.knowledge_id,
        ' 文件ID=', f.id,
        ' 分块=', seq_chunk.n,
        '。包含场景评估、成分搭配、风险提示和回访建议。'
    ) AS content,
    90 + seq_chunk.n * 15 AS char_count,
    1 AS vector_status
FROM kb_file f
JOIN kb_knowledge k ON k.id = f.knowledge_id
CROSS JOIN seq_chunk
WHERE k.title LIKE '批量知识-%'
  AND NOT EXISTS (
      SELECT 1
      FROM kb_chunk c
      WHERE c.file_id = f.id
        AND c.chunk_index = seq_chunk.n
  );

-- ------------------------------
-- 9) 会话（500）+ 消息（每会话 4 条）
-- ------------------------------
WITH RECURSIVE seq_s AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_s WHERE n < 500
),
u AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM sys_user
    WHERE role = 'user' AND status = 1
),
uc AS (
    SELECT COUNT(*) AS c FROM u
)
INSERT INTO chat_session (user_id, title, status, created_at, updated_at)
SELECT
    u.id AS user_id,
    CONCAT('批量会话-', LPAD(seq_s.n, 4, '0')) AS title,
    1 AS status,
    DATE_SUB(NOW(), INTERVAL seq_s.n DAY) AS created_at,
    DATE_SUB(NOW(), INTERVAL seq_s.n DAY) + INTERVAL 20 MINUTE AS updated_at
FROM seq_s
JOIN uc ON uc.c > 0
JOIN u ON u.rn = ((seq_s.n - 1) % uc.c) + 1
WHERE NOT EXISTS (
    SELECT 1
    FROM chat_session s
    WHERE s.title = CONCAT('批量会话-', LPAD(seq_s.n, 4, '0'))
);

WITH RECURSIVE seq_msg AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_msg WHERE n < 4
)
INSERT INTO chat_message (session_id, role, content, token_count, sources, created_at)
SELECT
    s.id AS session_id,
    IF(seq_msg.n % 2 = 1, 'user', 'assistant') AS role,
    IF(
        seq_msg.n % 2 = 1,
        CONCAT('用户提问：批量会话 ', s.id, ' 的问题 ', seq_msg.n),
        CONCAT('助手回答：批量会话 ', s.id, ' 的建议 ', seq_msg.n)
    ) AS content,
    80 + seq_msg.n * 12 AS token_count,
    IF(
        seq_msg.n % 2 = 0,
        JSON_ARRAY(JSON_OBJECT('level', 'B', 'source', CONCAT('bulk_ref_', s.id, '_', seq_msg.n))),
        NULL
    ) AS sources,
    s.created_at + INTERVAL seq_msg.n MINUTE AS created_at
FROM chat_session s
CROSS JOIN seq_msg
WHERE s.title LIKE '批量会话-%'
  AND NOT EXISTS (
      SELECT 1
      FROM chat_message m
      WHERE m.session_id = s.id
        AND m.role = IF(seq_msg.n % 2 = 1, 'user', 'assistant')
        AND m.content = IF(
            seq_msg.n % 2 = 1,
            CONCAT('用户提问：批量会话 ', s.id, ' 的问题 ', seq_msg.n),
            CONCAT('助手回答：批量会话 ', s.id, ' 的建议 ', seq_msg.n)
        )
  );

-- ------------------------------
-- 10) 待确认实体（2000）
-- ------------------------------
WITH RECURSIVE seq_1000b AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq_1000b WHERE n < 1000
),
seq_2000b AS (
    SELECT n FROM seq_1000b
    UNION ALL
    SELECT n + 1000 FROM seq_1000b
),
f AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM kb_file
),
fc AS (
    SELECT COUNT(*) AS c FROM f
)
INSERT INTO entity_extract_pending (file_id, entity_type, entity_name, source_text, extract_method, status)
SELECT
    f.id AS file_id,
    ELT((seq_2000b.n % 3) + 1, 'ingredient', 'effect', 'product') AS entity_type,
    CONCAT('批量候选实体-', LPAD(seq_2000b.n, 5, '0')) AS entity_name,
    CONCAT('批量抽取来源片段，编号 ', seq_2000b.n) AS source_text,
    ELT((seq_2000b.n % 2) + 1, 'dictionary', 'llm') AS extract_method,
    ELT((seq_2000b.n % 5) + 1, 'PENDING', 'PENDING', 'CONFIRMED', 'PENDING', 'REJECTED') AS status
FROM seq_2000b
JOIN fc ON fc.c > 0
JOIN f ON f.rn = ((seq_2000b.n - 1) % fc.c) + 1
WHERE NOT EXISTS (
    SELECT 1
    FROM entity_extract_pending p
    WHERE p.entity_name = CONCAT('批量候选实体-', LPAD(seq_2000b.n, 5, '0'))
);

-- ------------------------------
-- 11) 补数统计
-- ------------------------------
SELECT 'sys_user' AS table_name, COUNT(*) AS total FROM sys_user
UNION ALL
SELECT 'kb_category', COUNT(*) FROM kb_category
UNION ALL
SELECT 'kb_knowledge', COUNT(*) FROM kb_knowledge
UNION ALL
SELECT 'kb_file', COUNT(*) FROM kb_file
UNION ALL
SELECT 'kb_chunk', COUNT(*) FROM kb_chunk
UNION ALL
SELECT 'process_task', COUNT(*) FROM process_task
UNION ALL
SELECT 'chat_session', COUNT(*) FROM chat_session
UNION ALL
SELECT 'chat_message', COUNT(*) FROM chat_message
UNION ALL
SELECT 'beauty_ingredient', COUNT(*) FROM beauty_ingredient
UNION ALL
SELECT 'beauty_effect', COUNT(*) FROM beauty_effect
UNION ALL
SELECT 'beauty_product', COUNT(*) FROM beauty_product
UNION ALL
SELECT 'rel_ingredient_effect', COUNT(*) FROM rel_ingredient_effect
UNION ALL
SELECT 'rel_product_ingredient', COUNT(*) FROM rel_product_ingredient
UNION ALL
SELECT 'entity_extract_pending', COUNT(*) FROM entity_extract_pending;
