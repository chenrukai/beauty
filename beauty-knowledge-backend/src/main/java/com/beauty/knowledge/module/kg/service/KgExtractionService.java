package com.beauty.knowledge.module.kg.service;

import com.beauty.knowledge.module.entity.service.EntityExtractService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class KgExtractionService {

    private final EntityExtractService entityExtractService;

    public Map<String, Object> extractByFileId(Long fileId) {
        EntityExtractService.ExtractStat stat = entityExtractService.extractByFileId(fileId);
        return Map.of(
                "fileId", fileId,
                "matchedCount", stat.matchedCount(),
                "insertedCount", stat.insertedCount()
        );
    }

    public Map<String, Object> extractionConfig() {
        return entityExtractService.kgExtractionConfig();
    }
}
