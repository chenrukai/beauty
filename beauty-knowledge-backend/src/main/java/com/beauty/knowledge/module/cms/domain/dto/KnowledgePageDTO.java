package com.beauty.knowledge.module.cms.domain.dto;

import lombok.Data;

@Data
public class KnowledgePageDTO {

    private Long pageNum = 1L;
    private Long pageSize = 10L;
    private String keyword;
    private Long categoryId;
    private Integer status;
    private String type;
}
