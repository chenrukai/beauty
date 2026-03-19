package com.beauty.knowledge.module.rag.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChunkResult {

    private Long chunkId;
    private Long fileId;
    private Integer pageNo;
    private Integer chunkIndex;
    private String content;
    private double score;
    private int rank;
}
