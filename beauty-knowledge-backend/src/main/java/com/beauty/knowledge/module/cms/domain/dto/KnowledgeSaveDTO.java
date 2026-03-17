package com.beauty.knowledge.module.cms.domain.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class KnowledgeSaveDTO {

    @NotBlank(message = "标题不能为空")
    private String title;
    private String summary;
    @NotNull(message = "分类不能为空")
    private Long categoryId;
    private String type;
    @NotBlank(message = "内容不能为空")
    private String content;
    private Integer status;
    private String coverUrl;
}
