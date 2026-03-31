package com.beauty.knowledge.module.kg.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;

@Data
@Builder
public class KgGraphEdgeVO {
    private String edgeKey;
    private String subjectKey;
    private String predicate;
    private String objectKey;
    private BigDecimal confidence;
    private Integer evidenceCount;
    private Boolean inferred;
}
