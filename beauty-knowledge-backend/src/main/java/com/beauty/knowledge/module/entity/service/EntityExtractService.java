package com.beauty.knowledge.module.entity.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.infrastructure.dictionary.BeautyDictionary;
import com.beauty.knowledge.module.entity.domain.entity.EntityExtractPending;
import com.beauty.knowledge.module.entity.mapper.EntityExtractPendingMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Slf4j
@RequiredArgsConstructor
public class EntityExtractService {

    private final EntityExtractPendingMapper pendingMapper;
    private final BeautyDictionary beautyDictionary;

    public List<EntityExtractPending> pendingList() {
        try {
            return pendingMapper.selectList(new LambdaQueryWrapper<EntityExtractPending>()
                    .eq(EntityExtractPending::getStatus, "PENDING")
                    .orderByAsc(EntityExtractPending::getId));
        } catch (Exception ex) {
            // Compatible with environments where entity_extract_pending is not initialized yet.
            log.warn("entity_extract_pending table not ready, return empty pending entity list");
            return List.of();
        }
    }

    public long pendingCount() {
        try {
            Long c = pendingMapper.selectCount(new LambdaQueryWrapper<EntityExtractPending>()
                    .eq(EntityExtractPending::getStatus, "PENDING"));
            return c == null ? 0 : c;
        } catch (Exception ex) {
            // Compatible with environments where entity_extract_pending is not initialized yet.
            log.warn("entity_extract_pending table not ready, return pending count as 0");
            return 0;
        }
    }

    @Transactional(rollbackFor = Exception.class)
    public void extractByText(Long fileId, String text) {
        List<String> hits = beautyDictionary.match(text);
        for (String term : hits) {
            EntityExtractPending row = new EntityExtractPending();
            row.setFileId(fileId);
            row.setEntityType("ingredient");
            row.setEntityName(term);
            row.setSourceText(text);
            row.setExtractMethod("dictionary");
            row.setStatus("PENDING");
            pendingMapper.insert(row);
        }
    }
}
