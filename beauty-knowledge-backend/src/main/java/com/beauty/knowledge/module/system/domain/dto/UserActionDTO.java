package com.beauty.knowledge.module.system.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class UserActionDTO {

    @NotBlank(message = "actionType is required")
    private String actionType;
    private String targetType;
    private Long targetId;
    private String keyword;
    private String extra;
    private String source;
}
