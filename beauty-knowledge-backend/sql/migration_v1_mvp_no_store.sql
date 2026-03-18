USE beauty_knowledge;

-- ============================================================
-- MVP v1 Migration (No Store Module)
-- 执行前请先完成 sql/init.sql
-- ============================================================

-- 1) 扩展现有表
ALTER TABLE kb_knowledge
    ADD COLUMN publish_at DATETIME NULL COMMENT '发布时间' AFTER status,
    ADD COLUMN offline_at DATETIME NULL COMMENT '下线时间' AFTER publish_at,
    ADD COLUMN is_deleted TINYINT NOT NULL DEFAULT 0 COMMENT '软删除 0否1是' AFTER offline_at;

ALTER TABLE kb_file
    ADD COLUMN is_deleted TINYINT NOT NULL DEFAULT 0 COMMENT '软删除 0否1是' AFTER process_status,
    ADD COLUMN parse_cost_ms BIGINT NOT NULL DEFAULT 0 COMMENT '解析耗时毫秒' AFTER is_deleted;

ALTER TABLE process_task
    ADD COLUMN operator_id BIGINT NULL COMMENT '操作人ID' AFTER max_retry,
    ADD COLUMN cost_ms BIGINT NOT NULL DEFAULT 0 COMMENT '任务耗时毫秒' AFTER operator_id;

ALTER TABLE sys_user
    ADD COLUMN last_login_at DATETIME NULL COMMENT '最后登录时间' AFTER updated_at,
    ADD COLUMN last_login_ip VARCHAR(64) NULL COMMENT '最后登录IP' AFTER last_login_at;

-- 2) 用户行为日志
CREATE TABLE IF NOT EXISTS user_action_log (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '日志ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    action_type VARCHAR(32) NOT NULL COMMENT '行为类型 browse/search/favorite/share/click',
    target_type VARCHAR(32) DEFAULT NULL COMMENT '目标类型 knowledge/file/product/page',
    target_id BIGINT DEFAULT NULL COMMENT '目标ID',
    keyword VARCHAR(128) DEFAULT NULL COMMENT '搜索词',
    extra JSON DEFAULT NULL COMMENT '扩展信息',
    ip VARCHAR(64) DEFAULT NULL COMMENT 'IP',
    user_agent VARCHAR(255) DEFAULT NULL COMMENT 'UA',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_user_time (user_id, created_at),
    KEY idx_action_time (action_type, created_at),
    KEY idx_target (target_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户行为日志';

-- 3) 搜索词统计（日）
CREATE TABLE IF NOT EXISTS search_keyword_stat (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '统计ID',
    stat_date DATE NOT NULL COMMENT '统计日期',
    keyword VARCHAR(128) NOT NULL COMMENT '关键词',
    search_count INT NOT NULL DEFAULT 0 COMMENT '搜索次数',
    user_count INT NOT NULL DEFAULT 0 COMMENT '去重用户数',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_date_keyword (stat_date, keyword),
    KEY idx_keyword (keyword),
    KEY idx_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='搜索词统计';

-- 4) 收藏表
CREATE TABLE IF NOT EXISTS favorite_record (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '收藏ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    knowledge_id BIGINT NOT NULL COMMENT '知识ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_knowledge (user_id, knowledge_id),
    KEY idx_user_time (user_id, created_at),
    KEY idx_knowledge (knowledge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收藏关系';

-- 5) 系统公告
CREATE TABLE IF NOT EXISTS sys_notice (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '公告ID',
    title VARCHAR(120) NOT NULL COMMENT '标题',
    content TEXT NOT NULL COMMENT '内容',
    is_top TINYINT NOT NULL DEFAULT 0 COMMENT '是否置顶 0否1是',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态 1发布0下线',
    publish_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    expire_time DATETIME DEFAULT NULL COMMENT '过期时间',
    created_by BIGINT DEFAULT NULL COMMENT '创建人ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_notice_status_time (status, publish_time),
    KEY idx_notice_top (is_top, publish_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统公告';

-- 6) 常用索引补充
CREATE INDEX idx_kb_knowledge_deleted_status ON kb_knowledge(is_deleted, status);
CREATE INDEX idx_kb_file_deleted_status ON kb_file(is_deleted, process_status);
CREATE INDEX idx_process_task_status_time ON process_task(status, updated_at);
CREATE INDEX idx_process_task_operator ON process_task(operator_id);

