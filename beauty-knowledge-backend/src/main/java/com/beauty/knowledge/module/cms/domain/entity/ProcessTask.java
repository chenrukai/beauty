package com.beauty.knowledge.module.cms.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("process_task")
public class ProcessTask {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long fileId;
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
