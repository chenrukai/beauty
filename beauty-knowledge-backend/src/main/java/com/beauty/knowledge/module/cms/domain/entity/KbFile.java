package com.beauty.knowledge.module.cms.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("kb_file")
public class KbFile {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long knowledgeId;
    private String originalName;
    private String fileType;
    private Long fileSize;
    private String minioPath;
    private String fileHash;
    private Integer version;
    private String processStatus;
    private Long uploadedBy;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
