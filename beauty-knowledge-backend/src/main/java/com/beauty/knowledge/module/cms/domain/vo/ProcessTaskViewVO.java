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
    private String stageCode;
    private String stageText;
    private Integer progress;
    private String resultMsg;
    private String failureReason;
    private Boolean canRetry;
    private Boolean canReExtract;
    private Boolean canConfirm;
    private Integer pendingEntityCount;
    private Integer confirmedEntityCount;
    private Integer rejectedEntityCount;
    private Integer retryCount;
    private Integer maxRetry;
    private LocalDateTime startedAt;
    private LocalDateTime finishedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
