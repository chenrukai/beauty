package com.beauty.knowledge.module.system.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("search_keyword_stat")
public class SearchKeywordStat {

    @TableId(type = IdType.AUTO)
    private Long id;
    private LocalDate statDate;
    private String keyword;
    private Integer searchCount;
    private Integer userCount;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

