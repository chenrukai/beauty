package com.beauty.knowledge.module.rag.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("chat_attachment")
public class ChatAttachment {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long sessionId;
    private Long userId;
    private String fileName;
    private String minioPath;
    private String contentType;
    private Integer status;
    private LocalDateTime createdAt;
}
