package com.beauty.knowledge.module.kg.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
public class KgPendingViewVO {
    private Long id;
    private String candidateType;
    private String entityType;
    private String entityName;
    private String payloadJson;
    private Long fileId;
    private String sourceText;
    private String extractMethod;
    private BigDecimal confidence;
    private String status;
    private LocalDateTime createdAt;
}
