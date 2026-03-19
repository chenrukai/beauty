package com.beauty.knowledge.module.cms.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.util.ArrayList;
import java.util.List;

@Data
@Builder
public class CategoryTreeVO {

    private Long id;
    private String name;
    private Long parentId;
    private Integer sortOrder;
    private Integer status;

    @Builder.Default
    private List<CategoryTreeVO> children = new ArrayList<>();
}
