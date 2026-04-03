package com.beauty.knowledge.module.cms.domain.vo;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class FileBinaryVO {
    private String fileName;
    private String contentType;
    private byte[] bytes;
}

