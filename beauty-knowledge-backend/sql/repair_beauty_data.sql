-- Beauty Knowledge DB repair + beauty data refresh
-- Execute on MySQL 8.0+:  USE beauty_knowledge; SOURCE repair_beauty_data.sql;

USE beauty_knowledge;

-- 1) Repair legacy schema differences
CREATE TABLE IF NOT EXISTS process_task
(
    id          BIGINT      NOT NULL AUTO_INCREMENT,
    file_id     BIGINT      NOT NULL,
    task_type   VARCHAR(32) NOT NULL DEFAULT 'KNOWLEDGE_PROCESS',
    status      VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    progress    INT         NOT NULL DEFAULT 0,
    result_msg  VARCHAR(500)         DEFAULT NULL,
    retry_count INT         NOT NULL DEFAULT 0,
    max_retry   INT         NOT NULL DEFAULT 3,
    started_at  DATETIME             DEFAULT NULL,
    finished_at DATETIME             DEFAULT NULL,
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_file (file_id),
    KEY idx_status (status)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS entity_extract_pending
(
    id             BIGINT       NOT NULL AUTO_INCREMENT,
    file_id        BIGINT       NOT NULL,
    entity_type    VARCHAR(20)  NOT NULL,
    entity_name    VARCHAR(120) NOT NULL,
    source_text    VARCHAR(500)          DEFAULT NULL,
    extract_method VARCHAR(20)  NOT NULL DEFAULT 'dictionary',
    status         VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_file_status (file_id, status),
    KEY idx_entity_type (entity_type)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

SET @has_sort_order := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'kb_category'
      AND COLUMN_NAME = 'sort_order'
);
SET @sql_sort_order := IF(@has_sort_order = 0,
    'ALTER TABLE kb_category ADD COLUMN sort_order INT NOT NULL DEFAULT 0 AFTER parent_id',
    'SELECT 1');
PREPARE stmt FROM @sql_sort_order;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2) Refresh beauty category data (tree)
DELETE FROM kb_category;
INSERT INTO kb_category (id, name, parent_id, sort_order, status)
VALUES
    (1,  '护肤理论',   0, 1, 1),
    (2,  '产品资料',   0, 2, 1),
    (3,  '门店流程',   0, 3, 1),
    (4,  '问题处理',   0, 4, 1),
    (11, '皮肤结构基础', 1, 1, 1),
    (12, '屏障与修护',   1, 2, 1),
    (13, '敏感肌管理',   1, 3, 1),
    (21, '洁面与卸妆',   2, 1, 1),
    (22, '精华与功效',   2, 2, 1),
    (23, '面膜与护理',   2, 3, 1),
    (31, '接待标准话术', 3, 1, 1),
    (32, '项目操作SOP',  3, 2, 1),
    (33, '售后回访',     3, 3, 1),
    (41, '不良反应处理', 4, 1, 1),
    (42, '客诉应对',     4, 2, 1),
    (43, '禁忌与风险提示', 4, 3, 1);

-- 3) Replace domain entities with beauty records
DELETE FROM rel_product_ingredient;
DELETE FROM rel_ingredient_effect;
DELETE FROM beauty_product;
DELETE FROM beauty_effect;
DELETE FROM beauty_ingredient;

INSERT INTO beauty_effect (name, scene, intro, status)
VALUES
    ('补水保湿', '日常护理', '提升角质层含水量，缓解干燥紧绷', 1),
    ('修护屏障', '敏感修护', '改善泛红刺痛，增强皮肤屏障', 1),
    ('控油平衡', '油皮护理', '减少多余油脂分泌，改善油光', 1),
    ('舒缓镇静', '敏感护理', '降低刺激感和不适感', 1),
    ('提亮肤色', '暗沉改善', '改善肤色不均和暗沉', 1),
    ('淡化细纹', '抗老护理', '改善干纹细纹外观', 1),
    ('祛痘调理', '痘肌护理', '减少粉刺痘痘发生', 1),
    ('术后维稳', '项目护理', '配合术后恢复周期', 1);

INSERT INTO beauty_ingredient (name, alias_name, category, safety_level, intro, status)
VALUES
    ('烟酰胺', NULL, '维生素类', 'A', '提亮与屏障修护成分', 1),
    ('透明质酸钠', '玻尿酸', '保湿类', 'A', '高效补水保湿成分', 1),
    ('泛醇', '维生素B5', '修护类', 'A', '舒缓并修护屏障', 1),
    ('神经酰胺NP', NULL, '脂质类', 'A', '强化皮肤脂质结构', 1),
    ('积雪草提取物', NULL, '植物提取', 'A', '舒缓敏感泛红', 1),
    ('水杨酸', 'BHA', '酸类', 'B', '角质调理和毛孔管理', 1),
    ('壬二酸衍生物', NULL, '功效类', 'B', '痘肌调理与匀净肤色', 1),
    ('传明酸', NULL, '功效类', 'A', '色沉管理', 1),
    ('视黄醇', 'A醇', '抗老类', 'B', '促进更新与淡纹', 1),
    ('多肽复合物', NULL, '抗老类', 'A', '紧致弹润支持', 1);

INSERT INTO beauty_product (name, brand, product_type, skin_type, intro, status)
VALUES
    ('舒缓保湿修护精华', '美研LAB', '精华', '干敏肌', '针对泛红、干燥、刺痛的日常修护精华', 1),
    ('净肤控油平衡精华', '美研LAB', '精华', '油痘肌', '帮助控油、细致毛孔、减少痘痘反复', 1),
    ('清透温和洁面乳', '净颜Pro', '洁面', '全肤质', '温和清洁不拔干，适合早晚使用', 1),
    ('屏障修护面霜', '美研LAB', '面霜', '干敏肌', '补脂修护，提升皮肤舒适度', 1),
    ('焕亮淡纹晚霜', '时光研', '面霜', '中性/混合', '夜间提亮并改善细纹粗糙', 1),
    ('玻尿酸保湿面膜', '水漾', '面膜', '全肤质', '密集补水，适合换季和空调环境', 1);

INSERT INTO rel_ingredient_effect (ingredient_id, effect_id, confidence, source)
SELECT i.id, e.id, 0.90, 'seed'
FROM beauty_ingredient i
JOIN beauty_effect e
  ON (i.name = '透明质酸钠' AND e.name IN ('补水保湿', '舒缓镇静'))
  OR (i.name = '神经酰胺NP' AND e.name IN ('修护屏障', '舒缓镇静'))
  OR (i.name = '烟酰胺' AND e.name IN ('提亮肤色', '控油平衡'))
  OR (i.name = '水杨酸' AND e.name IN ('控油平衡', '祛痘调理'))
  OR (i.name = '视黄醇' AND e.name IN ('淡化细纹', '提亮肤色'))
  OR (i.name = '多肽复合物' AND e.name IN ('淡化细纹', '修护屏障'));

INSERT INTO rel_product_ingredient (product_id, ingredient_id, concentration)
SELECT p.id, i.id, '0.1%-2%'
FROM beauty_product p
JOIN beauty_ingredient i
  ON (p.name = '舒缓保湿修护精华' AND i.name IN ('泛醇', '神经酰胺NP', '积雪草提取物'))
  OR (p.name = '净肤控油平衡精华' AND i.name IN ('水杨酸', '烟酰胺', '壬二酸衍生物'))
  OR (p.name = '屏障修护面霜' AND i.name IN ('神经酰胺NP', '泛醇'))
  OR (p.name = '焕亮淡纹晚霜' AND i.name IN ('视黄醇', '多肽复合物', '烟酰胺'))
  OR (p.name = '玻尿酸保湿面膜' AND i.name IN ('透明质酸钠', '泛醇'));

-- 4) Force kb_knowledge to beauty-themed content
UPDATE kb_knowledge
SET
    category_id = CASE MOD(id, 4)
        WHEN 0 THEN 11
        WHEN 1 THEN 22
        WHEN 2 THEN 32
        ELSE 41
    END,
    type = 'TEXT',
    status = 1,
    title = CONCAT(
        CASE MOD(id, 6)
            WHEN 0 THEN '敏感肌舒缓方案'
            WHEN 1 THEN '油痘肌控油与清洁流程'
            WHEN 2 THEN '门店面诊沟通与需求确认'
            WHEN 3 THEN '屏障受损修护步骤'
            WHEN 4 THEN '术后维稳与禁忌提示'
            ELSE '提亮淡纹护理建议'
        END,
        ' #', id
    ),
    summary = '围绕成分-功效-产品的美业知识条目，用于门店培训和客户科普。',
    content = CONCAT(
        '【门店场景】用于顾客面诊、项目推荐和售后回访。', CHAR(10),
        '【核心成分】烟酰胺 / 透明质酸钠 / 神经酰胺 / 泛醇。', CHAR(10),
        '【功效目标】补水保湿、屏障修护、控油平衡、舒缓镇静。', CHAR(10),
        '【话术建议】避免夸大疗效，先评估肤质与禁忌。', CHAR(10),
        '【版本】beauty-seed-v1'
    ),
    view_count = 100 + MOD(id * 73, 3800);

-- 5) Seed pending entities and task monitor examples
DELETE FROM entity_extract_pending;
INSERT INTO entity_extract_pending (file_id, entity_type, entity_name, source_text, extract_method, status)
VALUES
    (1, 'ingredient', '烟酰胺', '该产品富含烟酰胺和泛醇，适合暗沉与屏障受损肌肤。', 'dictionary', 'PENDING'),
    (1, 'ingredient', '泛醇', '该产品富含烟酰胺和泛醇，适合暗沉与屏障受损肌肤。', 'dictionary', 'PENDING'),
    (2, 'effect', '控油平衡', '建议油痘肌选择含水杨酸与壬二酸衍生物的精华。', 'dictionary', 'PENDING'),
    (2, 'ingredient', '水杨酸', '建议油痘肌选择含水杨酸与壬二酸衍生物的精华。', 'dictionary', 'PENDING'),
    (3, 'product', '屏障修护面霜', '修护期优先使用神经酰胺面霜，减少高刺激成分。', 'llm', 'PENDING');

DELETE FROM process_task;
INSERT INTO process_task (file_id, task_type, status, progress, result_msg, retry_count, max_retry, started_at, finished_at)
VALUES
    (1, 'KNOWLEDGE_PROCESS', 'SUCCESS', 100, '向量化完成', 0, 3, NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 110 MINUTE),
    (2, 'KNOWLEDGE_PROCESS', 'RUNNING', 65, '正在抽取实体', 0, 3, NOW() - INTERVAL 20 MINUTE, NULL),
    (3, 'KNOWLEDGE_PROCESS', 'PENDING', 0, '等待消费者', 0, 3, NULL, NULL),
    (4, 'KNOWLEDGE_PROCESS', 'FAILED', 40, '文档解析失败，待重试', 1, 3, NOW() - INTERVAL 50 MINUTE, NOW() - INTERVAL 45 MINUTE);

