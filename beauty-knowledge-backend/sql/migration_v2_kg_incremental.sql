-- Incremental schema for knowledge-graph workflow (compatible mode).
-- This script extends existing beauty_* and rel_* tables instead of replacing them.

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

ALTER TABLE entity_extract_pending
    ADD COLUMN IF NOT EXISTS candidate_type VARCHAR(20) NOT NULL DEFAULT 'entity' COMMENT 'entity/relation',
    ADD COLUMN IF NOT EXISTS payload_json JSON NULL COMMENT 'normalized payload for relation/entity',
    ADD COLUMN IF NOT EXISTS confidence DECIMAL(5, 4) NOT NULL DEFAULT 0.7000,
    ADD COLUMN IF NOT EXISTS reviewer_id BIGINT NULL,
    ADD COLUMN IF NOT EXISTS reviewed_at DATETIME NULL,
    ADD COLUMN IF NOT EXISTS review_comment VARCHAR(255) NULL;

ALTER TABLE rel_product_ingredient
    ADD COLUMN IF NOT EXISTS confidence DECIMAL(5, 4) NOT NULL DEFAULT 0.8000,
    ADD COLUMN IF NOT EXISTS source VARCHAR(100) NOT NULL DEFAULT 'manual',
    ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    ADD COLUMN IF NOT EXISTS evidence_count INT NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

ALTER TABLE rel_ingredient_effect
    ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    ADD COLUMN IF NOT EXISTS evidence_count INT NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_pending_candidate_status ON entity_extract_pending (candidate_type, status);
CREATE INDEX IF NOT EXISTS idx_pending_reviewed_at ON entity_extract_pending (reviewed_at);
