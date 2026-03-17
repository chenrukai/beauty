package com.beauty.knowledge.module.cms.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("kb_knowledge")
public class KbKnowledge {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String title;
    private String summary;
    private String content;
    private Long categoryId;
    private String type;
    private String coverUrl;
    private Integer status;
    private Integer viewCount;
    private Long authorId;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
