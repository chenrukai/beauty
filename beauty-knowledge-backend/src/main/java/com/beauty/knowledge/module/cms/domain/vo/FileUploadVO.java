package com.beauty.knowledge.module.cms.domain.vo;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class FileUploadVO {

    private Long fileId;
    private Long taskId;
    private String minioPath;
    private String processStatus;
}
