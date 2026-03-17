package com.beauty.knowledge.infrastructure.vector;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class VectorSearchResult {

    private Long chunkId;
    private double score;
    private int rank;
    private String content;
}
