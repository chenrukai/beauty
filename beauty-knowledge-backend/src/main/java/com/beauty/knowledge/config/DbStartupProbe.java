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

    @Override
    public void run(String... args) {
        try {
            ensureChatTables();

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
}
