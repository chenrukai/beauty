package com.beauty.knowledge.module.cms.service;

import com.beauty.knowledge.module.cms.domain.entity.ProcessTask;
import com.beauty.knowledge.module.cms.domain.vo.FileUploadVO;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

public interface FileService {

    FileUploadVO upload(MultipartFile file, Long knowledgeId, Long categoryId, String fileType);

    ProcessTask getTask(Long taskId);

    List<ProcessTask> recentTasks(Integer size);

    void retry(Long taskId);

    void remove(Long fileId);
}
