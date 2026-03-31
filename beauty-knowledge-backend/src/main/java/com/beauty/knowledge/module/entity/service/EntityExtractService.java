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
import com.beauty.knowledge.module.entity.domain.entity.BeautyProduct;
import com.beauty.knowledge.module.entity.mapper.BeautyProductMapper;
import com.beauty.knowledge.module.entity.mapper.EntityExtractPendingMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.LinkedHashMap;
import java.util.Locale;

@Service
@Slf4j
@RequiredArgsConstructor
public class EntityExtractService {

    private final EntityExtractPendingMapper pendingMapper;
    private final BeautyDictionary beautyDictionary;
    private final KbChunkMapper kbChunkMapper;
    private final KbFileMapper kbFileMapper;
    private final BeautyProductMapper beautyProductMapper;
    private final ObjectMapper objectMapper;
    private final JdbcTemplate jdbcTemplate;

    @Value("${beauty.kg.extraction.min-segment-length:4}")
    private int kgMinSegmentLength;

    @Value("${beauty.kg.extraction.product-ingredient-confidence:0.85}")
    private BigDecimal productIngredientConfidence;

    @Value("${beauty.kg.extraction.ingredient-effect-confidence:0.82}")
    private BigDecimal ingredientEffectConfidence;

    @Value("${beauty.kg.extraction.product-ingredient-cues:含有,添加,富含,contains,include}")
    private String productIngredientCues;

    @Value("${beauty.kg.extraction.ingredient-effect-cues:改善,有助于,抑制,缓解,提升,reduce,improve}")
    private String ingredientEffectCues;

    public record ExtractStat(int matchedCount, int insertedCount) {
    }

    public Map<String, Object> kgExtractionConfig() {
        return Map.of(
                "minSegmentLength", Math.max(1, kgMinSegmentLength),
                "productIngredientConfidence", productIngredientConfidence,
                "ingredientEffectConfidence", ingredientEffectConfidence,
                "productIngredientCues", List.copyOf(parseCues(productIngredientCues)),
                "ingredientEffectCues", List.copyOf(parseCues(ingredientEffectCues))
        );
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

        int relationInserted = extractRelationCandidates(fileId, safeText);
        return new ExtractStat(ingredientHits.size() + effectHits.size(), insertedCount + relationInserted);
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
        row.setCandidateType("entity");
        row.setConfidence(new BigDecimal("0.7000"));
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

    private int extractRelationCandidates(Long fileId, String text) {
        List<String> segments = splitSegments(text);
        if (segments.isEmpty()) {
            return 0;
        }

        List<String> productNames = activeProductNames();
        int inserted = 0;
        for (String segment : segments) {
            if (segment == null || segment.isBlank()) {
                continue;
            }
            List<String> products = matchProducts(segment, productNames);
            List<String> ingredients = beautyDictionary.match(segment);
            List<String> effects = new ArrayList<>(matchEffects(segment));

            if (containsProductIngredientCue(segment)) {
                for (String product : products) {
                    for (String ingredient : ingredients) {
                        if (insertRelationPendingIfAbsent(
                                fileId,
                                "PRODUCT_CONTAINS_INGREDIENT",
                                product,
                                ingredient,
                                segment,
                                "rule",
                                productIngredientConfidence,
                                null
                        )) {
                            inserted++;
                        }
                    }
                }
            }

            if (containsIngredientEffectCue(segment)) {
                for (String ingredient : ingredients) {
                    for (String effect : effects) {
                        if (insertRelationPendingIfAbsent(
                                fileId,
                                "INGREDIENT_HAS_EFFECT",
                                ingredient,
                                effect,
                                segment,
                                "rule",
                                ingredientEffectConfidence,
                                null
                        )) {
                            inserted++;
                        }
                    }
                }
            }
        }
        return inserted;
    }

    private List<String> splitSegments(String text) {
        if (text == null || text.isBlank()) {
            return List.of();
        }
        String[] parts = text.split("[\\r\\n。！？；;.!?]+");
        List<String> segments = new ArrayList<>(parts.length);
        for (String part : parts) {
            if (part == null) {
                continue;
            }
            String trimmed = part.trim();
            if (trimmed.length() >= Math.max(1, kgMinSegmentLength)) {
                segments.add(trimmed);
            }
        }
        return segments;
    }

    private List<String> activeProductNames() {
        List<BeautyProduct> rows = beautyProductMapper.selectList(new LambdaQueryWrapper<BeautyProduct>()
                .select(BeautyProduct::getName)
                .eq(BeautyProduct::getStatus, 1));
        if (rows == null || rows.isEmpty()) {
            return List.of();
        }
        List<String> names = new ArrayList<>(rows.size());
        for (BeautyProduct row : rows) {
            if (row == null || row.getName() == null || row.getName().isBlank()) {
                continue;
            }
            names.add(row.getName().trim());
        }
        return names;
    }

    private List<String> matchProducts(String text, List<String> productNames) {
        if (text == null || text.isBlank() || productNames == null || productNames.isEmpty()) {
            return List.of();
        }
        List<String> out = new ArrayList<>();
        for (String name : productNames) {
            if (text.contains(name)) {
                out.add(name);
            }
        }
        return out;
    }

    private boolean containsProductIngredientCue(String segment) {
        String lower = segment.toLowerCase(Locale.ROOT);
        for (String cue : parseCues(productIngredientCues)) {
            if (lower.contains(cue)) {
                return true;
            }
        }
        return false;
    }

    private boolean containsIngredientEffectCue(String segment) {
        String lower = segment.toLowerCase(Locale.ROOT);
        for (String cue : parseCues(ingredientEffectCues)) {
            if (lower.contains(cue)) {
                return true;
            }
        }
        return false;
    }

    private boolean insertRelationPendingIfAbsent(Long fileId,
                                                  String predicate,
                                                  String subjectName,
                                                  String objectName,
                                                  String sourceText,
                                                  String method,
                                                  BigDecimal confidence,
                                                  Integer pageNo) {
        if (subjectName == null || subjectName.isBlank() || objectName == null || objectName.isBlank()) {
            return false;
        }
        String relationName = predicate + ":" + subjectName + "->" + objectName;
        Long exists = pendingMapper.selectCount(new LambdaQueryWrapper<EntityExtractPending>()
                .eq(EntityExtractPending::getFileId, fileId)
                .eq(EntityExtractPending::getCandidateType, "relation")
                .eq(EntityExtractPending::getEntityName, relationName));
        if (exists != null && exists > 0) {
            return false;
        }

        String payloadJson = buildRelationPayloadJson(predicate, subjectName, objectName, confidence, pageNo);
        EntityExtractPending row = new EntityExtractPending();
        row.setFileId(fileId);
        row.setEntityType("relation");
        row.setEntityName(relationName);
        row.setSourceText(clipSourceText(sourceText));
        row.setExtractMethod(method);
        row.setCandidateType("relation");
        row.setPayloadJson(payloadJson);
        row.setConfidence(confidence == null ? new BigDecimal("0.7000") : confidence);
        row.setStatus("PENDING");
        pendingMapper.insert(row);
        return true;
    }

    private String buildRelationPayloadJson(String predicate,
                                            String subjectName,
                                            String objectName,
                                            BigDecimal confidence,
                                            Integer pageNo) {
        try {
            Map<String, Object> payload = new LinkedHashMap<>();
            payload.put("predicate", predicate);
            payload.put("subjectName", subjectName);
            payload.put("objectName", objectName);
            payload.put("confidence", confidence);
            payload.put("pageNo", pageNo);
            payload.put("subjectId", resolveEntityIdByName(predicate, true, subjectName));
            payload.put("objectId", resolveEntityIdByName(predicate, false, objectName));
            return objectMapper.writeValueAsString(payload);
        } catch (Exception ex) {
            throw new BusinessException(ErrorCode.INTERNAL_ERROR, "build relation payload failed");
        }
    }

    private Long resolveEntityIdByName(String predicate, boolean subject, String name) {
        String safePredicate = predicate == null ? "" : predicate.trim().toUpperCase(Locale.ROOT);
        String safeName = name == null ? "" : name.trim();
        if (safeName.isBlank()) {
            return null;
        }
        switch (safePredicate) {
            case "PRODUCT_CONTAINS_INGREDIENT" -> {
                if (subject) {
                    BeautyProduct p = beautyProductMapper.selectOne(new LambdaQueryWrapper<BeautyProduct>()
                            .eq(BeautyProduct::getName, safeName)
                            .last("limit 1"));
                    return p == null ? null : p.getId();
                }
                Long ingredientId = resolveIngredientIdByName(safeName);
                return ingredientId;
            }
            case "INGREDIENT_HAS_EFFECT" -> {
                if (subject) {
                    return resolveIngredientIdByName(safeName);
                }
                return resolveEffectIdByName(safeName);
            }
            default -> {
                return null;
            }
        }
    }

    private Long resolveIngredientIdByName(String name) {
        return jdbcTemplate.query(
                        "SELECT id FROM beauty_ingredient WHERE name = ? LIMIT 1",
                        rs -> rs.next() ? rs.getLong(1) : null,
                        name
                );
    }

    private Long resolveEffectIdByName(String name) {
        return jdbcTemplate.query(
                "SELECT id FROM beauty_effect WHERE name = ? LIMIT 1",
                rs -> rs.next() ? rs.getLong(1) : null,
                name
        );
    }

    private Set<String> parseCues(String raw) {
        if (raw == null || raw.isBlank()) {
            return Set.of();
        }
        String[] parts = raw.split(",");
        Set<String> cues = new LinkedHashSet<>();
        for (String part : parts) {
            if (part == null) {
                continue;
            }
            String cue = part.trim().toLowerCase(Locale.ROOT);
            if (!cue.isBlank()) {
                cues.add(cue);
            }
        }
        return cues;
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
