package com.beauty.knowledge.module.entity.domain.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import lombok.Data;

import java.util.List;

@Data
public class EntityConfirmRequest {

    @Valid
    @NotEmpty
    private List<EntityConfirmItemDTO> items;
}
