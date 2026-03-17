package com.beauty.knowledge.module.system.controller;

import com.beauty.knowledge.common.result.Result;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/debug")
@RequiredArgsConstructor
public class DebugController {

    private final JdbcTemplate jdbcTemplate;

    @GetMapping("/db")
    public Result<Map<String, Object>> db() {
        Map<String, Object> info = jdbcTemplate.queryForMap(
                "SELECT DATABASE() AS db, @@hostname AS host, @@port AS port, @@version AS version, @@server_uuid AS server_uuid"
        );

        Long sessionAll = safeCount("chat_session");
        Long sessionActive = safeQueryLong("SELECT COUNT(*) FROM chat_session WHERE status = 1");
        Long messageAll = safeCount("chat_message");
        Long kbChunkAll = safeCount("kb_chunk");

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("db", info.get("db"));
        data.put("host", info.get("host"));
        data.put("port", info.get("port"));
        data.put("version", info.get("version"));
        data.put("serverUuid", info.get("server_uuid"));
        data.put("chatSessionAll", sessionAll == null ? 0L : sessionAll);
        data.put("chatSessionActive", sessionActive == null ? 0L : sessionActive);
        data.put("chatMessageAll", messageAll == null ? 0L : messageAll);
        data.put("kbChunkAll", kbChunkAll == null ? 0L : kbChunkAll);
        return Result.success(data);
    }

    @GetMapping("/table-counts")
    public Result<Map<String, Long>> tableCounts() {
        String[] tables = {
                "sys_user",
                "kb_category",
                "kb_knowledge",
                "kb_file",
                "kb_chunk",
                "process_task",
                "chat_session",
                "chat_message",
                "beauty_ingredient",
                "beauty_effect",
                "beauty_product",
                "rel_ingredient_effect",
                "rel_product_ingredient",
                "entity_extract_pending"
        };
        Map<String, Long> data = new LinkedHashMap<>();
        for (String table : tables) {
            data.put(table, safeCount(table));
        }
        return Result.success(data);
    }

    private Long safeCount(String table) {
        return safeQueryLong("SELECT COUNT(*) FROM " + table);
    }

    private Long safeQueryLong(String sql) {
        try {
            Long v = jdbcTemplate.queryForObject(sql, Long.class);
            return v == null ? 0L : v;
        } catch (Exception ignored) {
            return 0L;
        }
    }
}
