package com.beauty.knowledge.module.rag.domain.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class UploadAskRequest {

    @NotNull(message = "sessionId不能为空")
    private Long sessionId;

    @NotBlank(message = "问题不能为空")
    private String question;
}

