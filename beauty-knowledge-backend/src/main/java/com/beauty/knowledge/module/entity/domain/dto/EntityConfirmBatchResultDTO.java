package com.beauty.knowledge.module.entity.domain.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class EntityConfirmBatchResultDTO {
    private int total;
    private int successCount;
    private int failedCount;
    private List<EntityConfirmItemResultDTO> itemResults;
}

