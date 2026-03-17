package com.beauty.knowledge.module.entity.domain.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class EntityConfirmItemDTO {

    @NotNull
    private Long pendingId;
    @NotNull
    private Boolean accept;
}
