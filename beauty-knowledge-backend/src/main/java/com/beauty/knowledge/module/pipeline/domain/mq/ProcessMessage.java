package com.beauty.knowledge.module.pipeline.domain.mq;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProcessMessage {

    private Long fileId;
    private String fileType;
    private String minioPath;
    private Long categoryId;
    private Long knowledgeId;
    @Builder.Default
    private Integer retryCount = 0;
}
