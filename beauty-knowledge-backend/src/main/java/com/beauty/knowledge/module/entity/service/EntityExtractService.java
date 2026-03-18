package com.beauty.knowledge.module.entity.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.infrastructure.dictionary.BeautyDictionary;
import com.beauty.knowledge.module.entity.domain.entity.EntityExtractPending;
import com.beauty.knowledge.module.entity.mapper.EntityExtractPendingMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

@Service
@Slf4j
@RequiredArgsConstructor
public class EntityExtractService {

    private final EntityExtractPendingMapper pendingMapper;
    private final BeautyDictionary beautyDictionary;

    public List<EntityExtractPending> pendingList(String status) {
        try {
            LambdaQueryWrapper<EntityExtractPending> wrapper = new LambdaQueryWrapper<>();
            if (status != null && !status.isBlank() && !"ALL".equalsIgnoreCase(status)) {
                wrapper.eq(EntityExtractPending::getStatus, status.toUpperCase());
            }
            wrapper.orderByDesc(EntityExtractPending::getId);
            return pendingMapper.selectList(wrapper);
        } catch (Exception ex) {
            // Compatible with environments where entity_extract_pending is not initialized yet.
            log.warn("entity_extract_pending table not ready, return empty pending entity list");
            return List.of();
        }
    }

    public long pendingCount(String status) {
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
    public void extractByText(Long fileId, String text) {
        String safeText = text == null ? "" : text;
        List<String> ingredientHits = beautyDictionary.match(safeText);
        for (String term : ingredientHits) {
            insertPendingIfAbsent(fileId, "ingredient", term, safeText, "dictionary");
        }

        // Fallback for operation SOP-like text: extract common skincare effect keywords.
        for (String effect : matchEffects(safeText)) {
            insertPendingIfAbsent(fileId, "effect", effect, safeText, "rule");
        }
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

    private void insertPendingIfAbsent(Long fileId, String entityType, String entityName, String sourceText, String method) {
        Long exists = pendingMapper.selectCount(new LambdaQueryWrapper<EntityExtractPending>()
                .eq(EntityExtractPending::getFileId, fileId)
                .eq(EntityExtractPending::getEntityType, entityType)
                .eq(EntityExtractPending::getEntityName, entityName)
                .eq(EntityExtractPending::getStatus, "PENDING"));
        if (exists != null && exists > 0) {
            return;
        }
        EntityExtractPending row = new EntityExtractPending();
        row.setFileId(fileId);
        row.setEntityType(entityType);
        row.setEntityName(entityName);
        row.setSourceText(sourceText);
        row.setExtractMethod(method);
        row.setStatus("PENDING");
        pendingMapper.insert(row);
    }
}
