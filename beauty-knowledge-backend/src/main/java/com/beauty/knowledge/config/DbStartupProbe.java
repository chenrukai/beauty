package com.beauty.knowledge.config;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class DbStartupProbe implements CommandLineRunner {

    private final JdbcTemplate jdbcTemplate;

    @Value("${spring.datasource.url:}")
    private String datasourceUrl;

    @Value("${beauty.db.auto-create-chat-tables:false}")
    private boolean autoCreateChatTables;

    @Override
    public void run(String... args) {
        try {
            if (autoCreateChatTables) {
                ensureChatTables();
                log.warn("DB Probe -> auto chat table creation is enabled. This should be used in dev only.");
            }

            ensureEntityPendingCompatibleColumns();

            Map<String, Object> info = jdbcTemplate.queryForMap(
                    "SELECT DATABASE() AS db, @@hostname AS host, @@port AS port, @@version AS version"
            );
            Integer chatSessionCount = jdbcTemplate.queryForObject(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'chat_session'",
                    Integer.class
            );
            Integer chatMessageCount = jdbcTemplate.queryForObject(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'chat_message'",
                    Integer.class
            );

            log.info("DB Probe -> url={}, db={}, host={}, port={}, version={}",
                    datasourceUrl, info.get("db"), info.get("host"), info.get("port"), info.get("version"));
            log.info("DB Probe -> chat_session_exists={}, chat_message_exists={}",
                    chatSessionCount != null && chatSessionCount > 0,
                    chatMessageCount != null && chatMessageCount > 0);
        } catch (Exception e) {
            log.warn("DB Probe failed: {}", e.getMessage());
        }
    }

    private void ensureChatTables() {
        jdbcTemplate.execute("""
                CREATE TABLE IF NOT EXISTS chat_session
                (
                    id         BIGINT       NOT NULL AUTO_INCREMENT,
                    user_id    BIGINT       NOT NULL,
                    title      VARCHAR(200) NOT NULL,
                    status     TINYINT      NOT NULL DEFAULT 1,
                    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    KEY idx_user_updated (user_id, updated_at)
                ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4
                """);

        jdbcTemplate.execute("""
                CREATE TABLE IF NOT EXISTS chat_message
                (
                    id          BIGINT      NOT NULL AUTO_INCREMENT,
                    session_id  BIGINT      NOT NULL,
                    role        VARCHAR(20) NOT NULL,
                    content     LONGTEXT    NOT NULL,
                    token_count INT         NOT NULL DEFAULT 0,
                    sources     JSON                 DEFAULT NULL,
                    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    KEY idx_session_created (session_id, created_at)
                ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4
                """);
    }

    private void ensureEntityPendingCompatibleColumns() {
        if (!tableExists("entity_extract_pending")) {
            return;
        }

        ensureColumn(
                "entity_extract_pending",
                "candidate_type",
                "ALTER TABLE entity_extract_pending ADD COLUMN candidate_type VARCHAR(20) NOT NULL DEFAULT 'entity' COMMENT 'entity/relation'"
        );
        ensureColumn(
                "entity_extract_pending",
                "payload_json",
                "ALTER TABLE entity_extract_pending ADD COLUMN payload_json JSON NULL COMMENT 'normalized payload for relation/entity'"
        );
        ensureColumn(
                "entity_extract_pending",
                "confidence",
                "ALTER TABLE entity_extract_pending ADD COLUMN confidence DECIMAL(5,4) NOT NULL DEFAULT 0.7000"
        );
        ensureColumn(
                "entity_extract_pending",
                "reviewer_id",
                "ALTER TABLE entity_extract_pending ADD COLUMN reviewer_id BIGINT NULL"
        );
        ensureColumn(
                "entity_extract_pending",
                "reviewed_at",
                "ALTER TABLE entity_extract_pending ADD COLUMN reviewed_at DATETIME NULL"
        );
        ensureColumn(
                "entity_extract_pending",
                "review_comment",
                "ALTER TABLE entity_extract_pending ADD COLUMN review_comment VARCHAR(255) NULL"
        );
    }

    private boolean tableExists(String tableName) {
        Integer cnt = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = ?",
                Integer.class,
                tableName
        );
        return cnt != null && cnt > 0;
    }

    private void ensureColumn(String tableName, String columnName, String ddl) {
        Integer cnt = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = ? AND column_name = ?",
                Integer.class,
                tableName,
                columnName
        );
        if (cnt == null || cnt == 0) {
            jdbcTemplate.execute(ddl);
            log.warn("DB Probe -> added missing column {}.{}", tableName, columnName);
        }
    }
}
