package com.beauty.knowledge.module.kg.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("kg_evidence")
public class KgEvidence {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String relationType;
    private String subjectType;
    private Long subjectId;
    private String objectType;
    private Long objectId;
    private Long fileId;
    private Long chunkId;
    private Integer pageNo;
    private String sourceText;
    private String extractor;
    private BigDecimal confidence;
    private Long reviewerId;
    private LocalDateTime createdAt;
}
