package com.beauty.knowledge.module.entity.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("rel_product_effect")
public class RelProductEffect {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long productId;
    private Long effectId;
    private BigDecimal confidence;
    private String source;
    private String status;
    private Integer evidenceCount;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
