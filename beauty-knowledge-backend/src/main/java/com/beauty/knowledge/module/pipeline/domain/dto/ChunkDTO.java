package com.beauty.knowledge.module.pipeline.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class ChunkDTO {

    private Integer chunkIndex;
    private String content;
    private Integer page;
    private Integer charCount;
}
