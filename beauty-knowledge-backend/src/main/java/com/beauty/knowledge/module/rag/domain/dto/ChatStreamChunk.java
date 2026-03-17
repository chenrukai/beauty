package com.beauty.knowledge.module.rag.domain.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class ChatStreamChunk {

    private String type;
    private String content;
    private Long sessionId;
    private List<ChunkResult> sources;
}
