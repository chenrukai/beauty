USE beauty_knowledge;

SET @exists := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'sys_user' AND COLUMN_NAME = 'last_login_at'
);
SET @sql := IF(@exists = 0, 'ALTER TABLE sys_user ADD COLUMN last_login_at DATETIME NULL AFTER updated_at', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exists := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'sys_user' AND COLUMN_NAME = 'last_login_ip'
);
SET @sql := IF(@exists = 0, 'ALTER TABLE sys_user ADD COLUMN last_login_ip VARCHAR(64) NULL AFTER last_login_at', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exists := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'kb_category' AND COLUMN_NAME = 'sort_order'
);
SET @sql := IF(@exists = 0, 'ALTER TABLE kb_category ADD COLUMN sort_order INT NOT NULL DEFAULT 0 AFTER parent_id', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exists := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'kb_knowledge' AND COLUMN_NAME = 'publish_at'
);
SET @sql := IF(@exists = 0, 'ALTER TABLE kb_knowledge ADD COLUMN publish_at DATETIME NULL AFTER status', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exists := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'kb_knowledge' AND COLUMN_NAME = 'offline_at'
);
SET @sql := IF(@exists = 0, 'ALTER TABLE kb_knowledge ADD COLUMN offline_at DATETIME NULL AFTER publish_at', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exists := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'kb_knowledge' AND COLUMN_NAME = 'is_deleted'
);
SET @sql := IF(@exists = 0, 'ALTER TABLE kb_knowledge ADD COLUMN is_deleted TINYINT NOT NULL DEFAULT 0 AFTER offline_at', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exists := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'kb_file' AND COLUMN_NAME = 'is_deleted'
);
SET @sql := IF(@exists = 0, 'ALTER TABLE kb_file ADD COLUMN is_deleted TINYINT NOT NULL DEFAULT 0 AFTER process_status', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exists := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'kb_file' AND COLUMN_NAME = 'parse_cost_ms'
);
SET @sql := IF(@exists = 0, 'ALTER TABLE kb_file ADD COLUMN parse_cost_ms BIGINT NOT NULL DEFAULT 0 AFTER is_deleted', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

CREATE TABLE IF NOT EXISTS kb_chunk (
    id BIGINT NOT NULL AUTO_INCREMENT,
    knowledge_id BIGINT NOT NULL,
    file_id BIGINT NOT NULL,
    chunk_index INT NOT NULL,
    page_no INT NOT NULL DEFAULT 1,
    content TEXT NOT NULL,
    char_count INT NOT NULL DEFAULT 0,
    vector_status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_file_chunk (file_id, chunk_index),
    KEY idx_knowledge (knowledge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS process_task (
    id BIGINT NOT NULL AUTO_INCREMENT,
    file_id BIGINT NOT NULL,
    task_type VARCHAR(32) NOT NULL DEFAULT 'KNOWLEDGE_PROCESS',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    progress INT NOT NULL DEFAULT 0,
    result_msg VARCHAR(500) DEFAULT NULL,
    retry_count INT NOT NULL DEFAULT 0,
    max_retry INT NOT NULL DEFAULT 3,
    operator_id BIGINT DEFAULT NULL,
    cost_ms BIGINT NOT NULL DEFAULT 0,
    started_at DATETIME DEFAULT NULL,
    finished_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_file (file_id),
    KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS favorite_record (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    knowledge_id BIGINT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_knowledge (user_id, knowledge_id),
    KEY idx_user_time (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sys_notice (
    id BIGINT NOT NULL AUTO_INCREMENT,
    title VARCHAR(120) NOT NULL,
    content TEXT NOT NULL,
    is_top TINYINT NOT NULL DEFAULT 0,
    status TINYINT NOT NULL DEFAULT 1,
    publish_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expire_time DATETIME DEFAULT NULL,
    created_by BIGINT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_notice_status_time (status, publish_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_action_log (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    action_type VARCHAR(32) NOT NULL,
    target_type VARCHAR(32) DEFAULT NULL,
    target_id BIGINT DEFAULT NULL,
    keyword VARCHAR(128) DEFAULT NULL,
    extra JSON DEFAULT NULL,
    ip VARCHAR(64) DEFAULT NULL,
    user_agent VARCHAR(255) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_user_time (user_id, created_at),
    KEY idx_action_time (action_type, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS search_keyword_stat (
    id BIGINT NOT NULL AUTO_INCREMENT,
    stat_date DATE NOT NULL,
    keyword VARCHAR(128) NOT NULL,
    search_count INT NOT NULL DEFAULT 0,
    user_count INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_date_keyword (stat_date, keyword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS beauty_ingredient (
    id BIGINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    alias_name VARCHAR(100) DEFAULT NULL,
    category VARCHAR(50) DEFAULT NULL,
    safety_level VARCHAR(20) DEFAULT NULL,
    intro VARCHAR(500) DEFAULT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_ingredient_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS beauty_effect (
    id BIGINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    scene VARCHAR(100) DEFAULT NULL,
    intro VARCHAR(500) DEFAULT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_effect_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS beauty_product (
    id BIGINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    brand VARCHAR(100) DEFAULT NULL,
    product_type VARCHAR(50) DEFAULT NULL,
    skin_type VARCHAR(100) DEFAULT NULL,
    intro VARCHAR(500) DEFAULT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_product_name_brand (name, brand)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rel_product_ingredient (
    id BIGINT NOT NULL AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    ingredient_id BIGINT NOT NULL,
    concentration VARCHAR(64) DEFAULT NULL,
    confidence DECIMAL(5,4) NOT NULL DEFAULT 0.8000,
    source VARCHAR(100) NOT NULL DEFAULT 'manual',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    evidence_count INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_product_ingredient (product_id, ingredient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rel_ingredient_effect (
    id BIGINT NOT NULL AUTO_INCREMENT,
    ingredient_id BIGINT NOT NULL,
    effect_id BIGINT NOT NULL,
    confidence DECIMAL(5,4) NOT NULL DEFAULT 0.8000,
    source VARCHAR(100) NOT NULL DEFAULT 'manual',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    evidence_count INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_ingredient_effect (ingredient_id, effect_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS entity_extract_pending (
    id BIGINT NOT NULL AUTO_INCREMENT,
    file_id BIGINT NOT NULL,
    entity_type VARCHAR(20) NOT NULL,
    entity_name VARCHAR(120) NOT NULL,
    source_text VARCHAR(500) DEFAULT NULL,
    extract_method VARCHAR(20) NOT NULL DEFAULT 'dictionary',
    candidate_type VARCHAR(20) NOT NULL DEFAULT 'entity',
    payload_json JSON DEFAULT NULL,
    confidence DECIMAL(5,4) NOT NULL DEFAULT 0.7000,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    reviewer_id BIGINT DEFAULT NULL,
    reviewed_at DATETIME DEFAULT NULL,
    review_comment VARCHAR(255) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_file_status (file_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO sys_notice (title, content, is_top, status, publish_time, created_by)
SELECT 'Runtime evidence seeded', 'Runtime data for thesis screenshots has been prepared.', 1, 1, NOW(), 1
WHERE NOT EXISTS (SELECT 1 FROM sys_notice WHERE title = 'Runtime evidence seeded');

INSERT INTO beauty_ingredient (name, alias_name, category, safety_level, intro, status)
VALUES
    ('Niacinamide', NULL, 'vitamin', 'A', 'Used for tone and barrier support', 1),
    ('Hyaluronic Acid', 'HA', 'hydration', 'A', 'Used for hydration support', 1),
    ('Salicylic Acid', 'BHA', 'acid', 'B', 'Used for pore and acne care', 1),
    ('Ceramide', NULL, 'lipid', 'A', 'Used for barrier repair', 1)
ON DUPLICATE KEY UPDATE intro = VALUES(intro), status = VALUES(status);

INSERT INTO beauty_effect (name, scene, intro, status)
VALUES
    ('Hydration', 'daily care', 'Used for dry skin support', 1),
    ('Oil Control', 'acne care', 'Used for oil and acne management', 1),
    ('Barrier Repair', 'sensitive care', 'Used for barrier recovery', 1),
    ('Brightening', 'tone care', 'Used for tone improvement', 1)
ON DUPLICATE KEY UPDATE intro = VALUES(intro), status = VALUES(status);

INSERT INTO beauty_product (name, brand, product_type, skin_type, intro, status)
VALUES
    ('Calm Hydration Serum', 'Beauty Lab', 'serum', 'dry-sensitive', 'Supports hydration and soothing care', 1),
    ('Clear Balance Serum', 'Beauty Lab', 'serum', 'oily-acne', 'Supports oil control and acne care', 1),
    ('Barrier Repair Cream', 'Beauty Lab', 'cream', 'sensitive', 'Supports barrier recovery', 1)
ON DUPLICATE KEY UPDATE intro = VALUES(intro), status = VALUES(status);

INSERT INTO rel_product_ingredient (product_id, ingredient_id, concentration, confidence, source, status, evidence_count)
SELECT p.id, i.id, '核心成分', 0.8600, 'seed', 'ACTIVE', 1
FROM beauty_product p
JOIN beauty_ingredient i
WHERE (p.name = 'Calm Hydration Serum' AND i.name IN ('Hyaluronic Acid', 'Ceramide'))
   OR (p.name = 'Clear Balance Serum' AND i.name IN ('Niacinamide', 'Salicylic Acid'))
   OR (p.name = 'Barrier Repair Cream' AND i.name IN ('Ceramide', 'Niacinamide'))
ON DUPLICATE KEY UPDATE confidence = VALUES(confidence), evidence_count = VALUES(evidence_count);

INSERT INTO rel_ingredient_effect (ingredient_id, effect_id, confidence, source, status, evidence_count)
SELECT i.id, e.id, 0.8800, 'seed', 'ACTIVE', 1
FROM beauty_ingredient i
JOIN beauty_effect e
WHERE (i.name = 'Hyaluronic Acid' AND e.name = 'Hydration')
   OR (i.name = 'Salicylic Acid' AND e.name = 'Oil Control')
   OR (i.name = 'Ceramide' AND e.name = 'Barrier Repair')
   OR (i.name = 'Niacinamide' AND e.name = 'Brightening')
ON DUPLICATE KEY UPDATE confidence = VALUES(confidence), evidence_count = VALUES(evidence_count);

INSERT INTO entity_extract_pending (file_id, entity_type, entity_name, source_text, extract_method, candidate_type, confidence, status)
SELECT 1, 'ingredient', 'Niacinamide', 'Product note mentions niacinamide for tone and barrier support.', 'dictionary', 'entity', 0.9100, 'PENDING'
WHERE NOT EXISTS (SELECT 1 FROM entity_extract_pending WHERE entity_name = 'Niacinamide');

INSERT INTO process_task (file_id, task_type, status, progress, result_msg, retry_count, max_retry, operator_id, cost_ms, started_at, finished_at)
SELECT 1, 'KNOWLEDGE_PROCESS', 'SUCCESS', 100, 'File parsed and stored successfully', 0, 3, 1, 4200, NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 115 MINUTE
WHERE NOT EXISTS (SELECT 1 FROM process_task WHERE file_id = 1 AND status = 'SUCCESS');

INSERT INTO process_task (file_id, task_type, status, progress, result_msg, retry_count, max_retry, operator_id, cost_ms, started_at, finished_at)
SELECT 2, 'KNOWLEDGE_PROCESS', 'RUNNING', 65, 'Extracting entities and relations', 0, 3, 1, 2600, NOW() - INTERVAL 25 MINUTE, NULL
WHERE NOT EXISTS (SELECT 1 FROM process_task WHERE file_id = 2 AND status = 'RUNNING');

INSERT INTO process_task (file_id, task_type, status, progress, result_msg, retry_count, max_retry, operator_id, cost_ms, started_at, finished_at)
SELECT 3, 'KNOWLEDGE_PROCESS', 'FAILED', 40, 'OCR failed and is waiting for retry', 1, 3, 1, 1800, NOW() - INTERVAL 50 MINUTE, NOW() - INTERVAL 46 MINUTE
WHERE NOT EXISTS (SELECT 1 FROM process_task WHERE file_id = 3 AND status = 'FAILED');

INSERT INTO favorite_record (user_id, knowledge_id)
SELECT u.id, k.id
FROM sys_user u
JOIN kb_knowledge k
WHERE u.username = 'user'
ORDER BY k.id
LIMIT 1
ON DUPLICATE KEY UPDATE knowledge_id = VALUES(knowledge_id);

INSERT INTO user_action_log (user_id, action_type, target_type, target_id, keyword, extra, ip, user_agent, created_at)
SELECT u.id, 'browse', 'knowledge', k.id, NULL, JSON_OBJECT('source', 'recommend'), '127.0.0.1', 'seed-script', NOW() - INTERVAL 1 DAY
FROM sys_user u
JOIN kb_knowledge k
WHERE u.username = 'user'
ORDER BY k.id DESC
LIMIT 1;

INSERT INTO user_action_log (user_id, action_type, target_type, target_id, keyword, extra, ip, user_agent, created_at)
SELECT u.id, 'search', 'knowledge', k.id, 'niacinamide', JSON_OBJECT('source', 'search'), '127.0.0.1', 'seed-script', NOW() - INTERVAL 5 HOUR
FROM sys_user u
JOIN kb_knowledge k
WHERE u.username = 'user'
ORDER BY k.id DESC
LIMIT 1;

INSERT INTO search_keyword_stat (stat_date, keyword, search_count, user_count)
VALUES
    (CURDATE(), 'niacinamide', 18, 1),
    (CURDATE(), 'salicylic acid', 12, 1),
    (CURDATE(), 'barrier repair', 15, 1)
ON DUPLICATE KEY UPDATE search_count = VALUES(search_count), user_count = VALUES(user_count);
