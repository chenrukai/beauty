package com.beauty.knowledge.module.pipeline.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("kb_chunk")
public class KbChunk {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long fileId;
    private Long knowledgeId;
    private Integer chunkIndex;
    private String content;
    private Integer pageNo;
    private Integer charCount;
    private Integer vectorStatus;
}
