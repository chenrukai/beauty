package com.beauty.knowledge.module.cms.domain.vo;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class ProcessTaskViewVO {
    private Long id;
    private Long fileId;
    private String fileName;
    private Long knowledgeId;
    private String knowledgeTitle;
    private String taskType;
    private String status;
    private Integer progress;
    private String resultMsg;
    private Integer retryCount;
    private Integer maxRetry;
    private LocalDateTime startedAt;
    private LocalDateTime finishedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
