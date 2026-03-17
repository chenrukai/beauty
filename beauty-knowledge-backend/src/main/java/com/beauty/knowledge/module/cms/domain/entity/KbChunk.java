package com.beauty.knowledge.module.cms.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("kb_chunk")
public class KbChunk {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long knowledgeId;
    private Long fileId;
    private Integer chunkIndex;
    private Integer pageNo;
    private String content;
    private Integer charCount;
    private Integer vectorStatus;
}
