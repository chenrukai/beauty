package com.beauty.knowledge.module.entity.domain.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class RelationBindDTO {

    @NotNull
    private Long leftId;
    @NotNull
    private Long rightId;
    private String concentration;
}
