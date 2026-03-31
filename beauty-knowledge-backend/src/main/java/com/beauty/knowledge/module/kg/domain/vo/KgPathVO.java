package com.beauty.knowledge.module.kg.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class KgPathVO {
    private String fromKey;
    private String toKey;
    private Boolean found;
    private Integer hopCount;
    private List<KgGraphNodeVO> nodes;
    private List<KgGraphEdgeVO> edges;
}
