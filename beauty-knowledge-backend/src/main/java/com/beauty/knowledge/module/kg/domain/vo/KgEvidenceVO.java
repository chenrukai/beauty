package com.beauty.knowledge.module.kg.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
public class KgEvidenceVO {
    private Long id;
    private String relationType;
    private String subjectType;
    private Long subjectId;
    private String objectType;
    private Long objectId;
    private Long fileId;
    private Long chunkId;
    private Integer pageNo;
    private String sourceText;
    private String extractor;
    private BigDecimal confidence;
    private Long reviewerId;
    private LocalDateTime createdAt;
}
