package com.beauty.knowledge.module.kg.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class KgGraphVO {
    private String centerKey;
    private List<KgGraphNodeVO> nodes;
    private List<KgGraphEdgeVO> edges;
}
