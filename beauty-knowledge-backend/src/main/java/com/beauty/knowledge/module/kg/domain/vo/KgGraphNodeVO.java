package com.beauty.knowledge.module.kg.domain.vo;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class KgGraphNodeVO {
    private String nodeKey;
    private String type;
    private Long id;
    private String name;
}
