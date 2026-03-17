package com.beauty.knowledge.module.entity.domain.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class EntityExtractRequest {

    @NotNull
    private Long fileId;
    @NotBlank
    private String text;
}
