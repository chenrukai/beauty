package com.beauty.knowledge.module.system.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("sys_notice")
public class SysNotice {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String title;
    private String content;
    private Integer isTop;
    private Integer status;
    private LocalDateTime publishTime;
    private LocalDateTime expireTime;
    private Long createdBy;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

