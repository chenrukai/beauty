package com.beauty.knowledge.module.entity.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.module.cms.domain.entity.KbChunk;
import com.beauty.knowledge.module.cms.domain.entity.KbFile;
import com.beauty.knowledge.module.cms.mapper.KbChunkMapper;
import com.beauty.knowledge.module.cms.mapper.KbFileMapper;
import com.beauty.knowledge.infrastructure.dictionary.BeautyDictionary;
import com.beauty.knowledge.module.entity.domain.entity.EntityExtractPending;
import com.beauty.knowledge.module.entity.mapper.EntityExtractPendingMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.LinkedHashMap;

@Service
@Slf4j
@RequiredArgsConstructor
public class EntityExtractService {

    private final EntityExtractPendingMapper pendingMapper;
    private final BeautyDictionary beautyDictionary;
    private final KbChunkMapper kbChunkMapper;
    private final KbFileMapper kbFileMapper;
    private final JdbcTemplate jdbcTemplate;

    public record ExtractStat(int matchedCount, int insertedCount) {
    }

    public List<EntityExtractPending> pendingList(String status) {
        ensurePendingTableReady();
        try {
            LambdaQueryWrapper<EntityExtractPending> wrapper = new LambdaQueryWrapper<>();
            if (status != null && !status.isBlank() && !"ALL".equalsIgnoreCase(status)) {
                wrapper.eq(EntityExtractPending::getStatus, status.toUpperCase());
            }
            wrapper.orderByDesc(EntityExtractPending::getId);
            List<EntityExtractPending> rows = deduplicatePendingRows(pendingMapper.selectList(wrapper));
            hydrateSourceTextAsFileName(rows);
            return rows;
        } catch (Exception ex) {
            // Compatible with environments where entity_extract_pending is not initialized yet.
            log.warn("entity_extract_pending table not ready, return empty pending entity list");
            return List.of();
        }
    }

    public long pendingCount(String status) {
        ensurePendingTableReady();
        try {
            LambdaQueryWrapper<EntityExtractPending> wrapper = new LambdaQueryWrapper<>();
            if (status != null && !status.isBlank() && !"ALL".equalsIgnoreCase(status)) {
                wrapper.eq(EntityExtractPending::getStatus, status.toUpperCase());
            } else {
                wrapper.eq(EntityExtractPending::getStatus, "PENDING");
            }
            Long c = pendingMapper.selectCount(wrapper);
            return c == null ? 0 : c;
        } catch (Exception ex) {
            // Compatible with environments where entity_extract_pending is not initialized yet.
            log.warn("entity_extract_pending table not ready, return pending count as 0");
            return 0;
        }
    }

    @Transactional(rollbackFor = Exception.class)
    public ExtractStat extractByText(Long fileId, String text) {
        ensurePendingTableReady();
        String safeText = text == null ? "" : text;
        List<String> ingredientHits = beautyDictionary.match(safeText);
        int insertedCount = 0;
        for (String term : ingredientHits) {
            if (insertPendingIfAbsent(fileId, "ingredient", term, safeText, "dictionary")) {
                insertedCount++;
            }
        }

        // Fallback for operation SOP-like text: extract common skincare effect keywords.
        Set<String> effectHits = matchEffects(safeText);
        for (String effect : effectHits) {
            if (insertPendingIfAbsent(fileId, "effect", effect, safeText, "rule")) {
                insertedCount++;
            }
        }
        return new ExtractStat(ingredientHits.size() + effectHits.size(), insertedCount);
    }

    @Transactional(rollbackFor = Exception.class)
    public ExtractStat extractByFileId(Long fileId) {
        ensurePendingTableReady();
        if (fileId == null || fileId <= 0) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "fileId is required");
        }
        List<KbChunk> chunks = kbChunkMapper.selectList(new LambdaQueryWrapper<KbChunk>()
                .eq(KbChunk::getFileId, fileId)
                .orderByAsc(KbChunk::getChunkIndex)
                .orderByAsc(KbChunk::getId));
        if (chunks == null || chunks.isEmpty()) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "文件尚未解析成功，请先确认任务状态为成功后再重抽取");
        }

        StringBuilder sb = new StringBuilder();
        for (KbChunk chunk : chunks) {
            if (chunk == null || chunk.getContent() == null || chunk.getContent().isBlank()) {
                continue;
            }
            if (!sb.isEmpty()) {
                sb.append('\n');
            }
            sb.append(chunk.getContent());
        }
        if (sb.isEmpty()) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "未发现可抽取文本，请检查文件内容是否可解析");
        }
        try {
            return extractByText(fileId, sb.toString());
        } catch (BusinessException ex) {
            throw ex;
        } catch (Exception ex) {
            String msg = ex.getMessage() == null ? "" : ex.getMessage().toLowerCase();
            if (msg.contains("entity_extract_pending")) {
                throw new BusinessException(ErrorCode.INTERNAL_ERROR, "实体待确认表未初始化，请先执行数据库初始化脚本");
            }
            throw new BusinessException(ErrorCode.INTERNAL_ERROR, "重抽取失败: " + ex.getMessage());
        }
    }

    private void ensurePendingTableReady() {
        jdbcTemplate.execute("""
                CREATE TABLE IF NOT EXISTS entity_extract_pending (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    file_id BIGINT NOT NULL,
                    entity_type VARCHAR(20) NOT NULL,
                    entity_name VARCHAR(120) NOT NULL,
                    source_text VARCHAR(500) DEFAULT NULL,
                    extract_method VARCHAR(20) NOT NULL DEFAULT 'dictionary',
                    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    KEY idx_file_status (file_id, status),
                    KEY idx_entity_type (entity_type)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """);
    }

    private Set<String> matchEffects(String text) {
        Set<String> out = new LinkedHashSet<>();
        addIfContains(text, out, "舒缓");
        addIfContains(text, out, "修护");
        addIfContains(text, out, "保湿");
        addIfContains(text, out, "维稳");
        addIfContains(text, out, "抗炎");
        addIfContains(text, out, "提亮");
        addIfContains(text, out, "控油");
        return out;
    }

    private void addIfContains(String text, Set<String> out, String keyword) {
        if (text.contains(keyword)) {
            out.add(keyword);
        }
    }

    private boolean insertPendingIfAbsent(Long fileId, String entityType, String entityName, String sourceText, String method) {
        Long exists = pendingMapper.selectCount(new LambdaQueryWrapper<EntityExtractPending>()
                .eq(EntityExtractPending::getFileId, fileId)
                .eq(EntityExtractPending::getEntityType, entityType)
                .eq(EntityExtractPending::getEntityName, entityName));
        if (exists != null && exists > 0) {
            return false;
        }
        EntityExtractPending row = new EntityExtractPending();
        row.setFileId(fileId);
        row.setEntityType(entityType);
        row.setEntityName(entityName);
        row.setSourceText(resolveSourceFileName(fileId));
        row.setExtractMethod(method);
        row.setStatus("PENDING");
        pendingMapper.insert(row);
        return true;
    }

    private void hydrateSourceTextAsFileName(List<EntityExtractPending> rows) {
        if (rows == null || rows.isEmpty()) {
            return;
        }
        Set<Long> fileIds = new LinkedHashSet<>();
        for (EntityExtractPending row : rows) {
            if (row != null && row.getFileId() != null && row.getFileId() > 0) {
                fileIds.add(row.getFileId());
            }
        }
        if (fileIds.isEmpty()) {
            return;
        }
        Map<Long, String> fileNameById = new HashMap<>();
        List<KbFile> files = kbFileMapper.selectBatchIds(fileIds);
        if (files != null) {
            for (KbFile f : files) {
                if (f == null || f.getId() == null) {
                    continue;
                }
                fileNameById.put(f.getId(), f.getOriginalName());
            }
        }
        for (EntityExtractPending row : rows) {
            if (row == null || row.getFileId() == null) {
                continue;
            }
            row.setSourceText(resolveSourceFileName(row.getFileId(), fileNameById));
        }
    }

    private List<EntityExtractPending> deduplicatePendingRows(List<EntityExtractPending> rows) {
        if (rows == null || rows.isEmpty()) {
            return List.of();
        }
        Map<String, EntityExtractPending> latest = new LinkedHashMap<>();
        for (EntityExtractPending row : rows) {
            if (row == null) {
                continue;
            }
            String key = row.getFileId() + "#" + row.getEntityType() + "#" + row.getEntityName();
            latest.putIfAbsent(key, row);
        }
        return List.copyOf(latest.values());
    }

    private String resolveSourceFileName(Long fileId) {
        if (fileId == null || fileId <= 0) {
            return "unknown-file";
        }
        KbFile file = kbFileMapper.selectById(fileId);
        String name = file == null ? null : file.getOriginalName();
        return (name == null || name.isBlank()) ? ("file-" + fileId) : name;
    }

    private String resolveSourceFileName(Long fileId, Map<Long, String> fileNameById) {
        if (fileId == null || fileId <= 0) {
            return "unknown-file";
        }
        String name = fileNameById == null ? null : fileNameById.get(fileId);
        return (name == null || name.isBlank()) ? ("file-" + fileId) : name;
    }

    private String clipSourceText(String text) {
        if (text == null) {
            return null;
        }
        String normalized = text.replace('\r', ' ').replace('\n', ' ').trim();
        final int maxLen = 500;
        if (normalized.length() <= maxLen) {
            return normalized;
        }
        return normalized.substring(0, maxLen);
    }
}
