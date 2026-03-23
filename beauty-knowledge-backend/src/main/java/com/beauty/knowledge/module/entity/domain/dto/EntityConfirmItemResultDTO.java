package com.beauty.knowledge.module.entity.domain.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class EntityConfirmItemResultDTO {
    private Long pendingId;
    private Boolean accept;
    private String status;
    private String message;
    private String entityType;
    private String entityName;
}

