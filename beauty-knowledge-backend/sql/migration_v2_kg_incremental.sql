-- Incremental schema for knowledge-graph workflow (MySQL compatibility mode).
-- This script avoids `ADD COLUMN IF NOT EXISTS` / `CREATE INDEX IF NOT EXISTS`
-- so it can run on older MySQL 8.0 builds.

CREATE TABLE IF NOT EXISTS kg_evidence
(
    id            BIGINT        NOT NULL AUTO_INCREMENT,
    relation_type VARCHAR(64)   NOT NULL COMMENT 'ENTITY / PRODUCT_CONTAINS_INGREDIENT / INGREDIENT_HAS_EFFECT',
    subject_type  VARCHAR(32)            DEFAULT NULL,
    subject_id    BIGINT                 DEFAULT NULL,
    object_type   VARCHAR(32)            DEFAULT NULL,
    object_id     BIGINT                 DEFAULT NULL,
    file_id       BIGINT                 DEFAULT NULL,
    chunk_id      BIGINT                 DEFAULT NULL,
    page_no       INT                    DEFAULT NULL,
    source_text   VARCHAR(1000)          DEFAULT NULL,
    extractor     VARCHAR(32)   NOT NULL DEFAULT 'rule',
    confidence    DECIMAL(5, 4) NOT NULL DEFAULT 0.7000,
    reviewer_id   BIGINT                 DEFAULT NULL,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_relation (relation_type, subject_id, object_id),
    KEY idx_file (file_id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='Knowledge graph evidence';

-- entity_extract_pending: candidate_type
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'entity_extract_pending' AND column_name = 'candidate_type'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE entity_extract_pending ADD COLUMN candidate_type VARCHAR(20) NOT NULL DEFAULT ''entity'' COMMENT ''entity/relation''',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- entity_extract_pending: payload_json
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'entity_extract_pending' AND column_name = 'payload_json'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE entity_extract_pending ADD COLUMN payload_json JSON NULL COMMENT ''normalized payload for relation/entity''',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- entity_extract_pending: confidence
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'entity_extract_pending' AND column_name = 'confidence'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE entity_extract_pending ADD COLUMN confidence DECIMAL(5,4) NOT NULL DEFAULT 0.7000',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- entity_extract_pending: reviewer_id
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'entity_extract_pending' AND column_name = 'reviewer_id'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE entity_extract_pending ADD COLUMN reviewer_id BIGINT NULL',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- entity_extract_pending: reviewed_at
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'entity_extract_pending' AND column_name = 'reviewed_at'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE entity_extract_pending ADD COLUMN reviewed_at DATETIME NULL',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- entity_extract_pending: review_comment
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'entity_extract_pending' AND column_name = 'review_comment'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE entity_extract_pending ADD COLUMN review_comment VARCHAR(255) NULL',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- rel_product_ingredient: confidence
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'rel_product_ingredient' AND column_name = 'confidence'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE rel_product_ingredient ADD COLUMN confidence DECIMAL(5,4) NOT NULL DEFAULT 0.8000',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- rel_product_ingredient: source
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'rel_product_ingredient' AND column_name = 'source'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE rel_product_ingredient ADD COLUMN source VARCHAR(100) NOT NULL DEFAULT ''manual''',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- rel_product_ingredient: status
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'rel_product_ingredient' AND column_name = 'status'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE rel_product_ingredient ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT ''ACTIVE''',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- rel_product_ingredient: evidence_count
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'rel_product_ingredient' AND column_name = 'evidence_count'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE rel_product_ingredient ADD COLUMN evidence_count INT NOT NULL DEFAULT 0',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- rel_product_ingredient: updated_at
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'rel_product_ingredient' AND column_name = 'updated_at'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE rel_product_ingredient ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- rel_ingredient_effect: status
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'rel_ingredient_effect' AND column_name = 'status'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE rel_ingredient_effect ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT ''ACTIVE''',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- rel_ingredient_effect: evidence_count
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'rel_ingredient_effect' AND column_name = 'evidence_count'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE rel_ingredient_effect ADD COLUMN evidence_count INT NOT NULL DEFAULT 0',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- rel_ingredient_effect: updated_at
SET @exists := (
    SELECT COUNT(1) FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'rel_ingredient_effect' AND column_name = 'updated_at'
);
SET @sql := IF(@exists = 0,
               'ALTER TABLE rel_ingredient_effect ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- indexes
SET @idx_exists := (
    SELECT COUNT(1) FROM information_schema.statistics
    WHERE table_schema = DATABASE() AND table_name = 'entity_extract_pending' AND index_name = 'idx_pending_candidate_status'
);
SET @sql := IF(@idx_exists = 0,
               'CREATE INDEX idx_pending_candidate_status ON entity_extract_pending (candidate_type, status)',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @idx_exists := (
    SELECT COUNT(1) FROM information_schema.statistics
    WHERE table_schema = DATABASE() AND table_name = 'entity_extract_pending' AND index_name = 'idx_pending_reviewed_at'
);
SET @sql := IF(@idx_exists = 0,
               'CREATE INDEX idx_pending_reviewed_at ON entity_extract_pending (reviewed_at)',
               'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
