package com.beauty.knowledge.module.system.domain.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDateTime;

@Data
public class NoticeSaveDTO {

    @NotBlank(message = "title is required")
    private String title;

    @NotBlank(message = "content is required")
    private String content;

    @NotNull(message = "status is required")
    private Integer status;

    private Integer isTop;
    private LocalDateTime expireTime;
}

