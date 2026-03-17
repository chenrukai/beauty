USE beauty_knowledge;

CREATE TABLE IF NOT EXISTS chat_session
(
    id         BIGINT       NOT NULL AUTO_INCREMENT COMMENT '会话ID',
    user_id    BIGINT       NOT NULL COMMENT '用户ID',
    title      VARCHAR(200) NOT NULL COMMENT '会话标题',
    status     TINYINT      NOT NULL DEFAULT 1 COMMENT '1有效 0删除',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_user_updated (user_id, updated_at)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='聊天会话表';

CREATE TABLE IF NOT EXISTS chat_message
(
    id          BIGINT      NOT NULL AUTO_INCREMENT COMMENT '消息ID',
    session_id  BIGINT      NOT NULL COMMENT '会话ID',
    role        VARCHAR(20) NOT NULL COMMENT 'user/assistant',
    content     LONGTEXT    NOT NULL COMMENT '消息内容',
    token_count INT         NOT NULL DEFAULT 0 COMMENT 'token计数',
    sources     JSON                 DEFAULT NULL COMMENT '引用来源',
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_session_created (session_id, created_at)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='聊天消息表';

