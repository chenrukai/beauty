package com.beauty.knowledge.module.entity.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("beauty_product")
public class BeautyProduct {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String name;
    private String brand;
    private String productType;
    private String skinType;
    private String intro;
    private Integer status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
