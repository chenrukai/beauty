package com.beauty.knowledge.module.cms.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.constant.RabbitMQConstant;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.common.util.FileHashUtil;
import com.beauty.knowledge.common.util.SecurityUtil;
import com.beauty.knowledge.infrastructure.storage.MinioStorageService;
import com.beauty.knowledge.infrastructure.vector.MilvusVectorStore;
import com.beauty.knowledge.module.cms.domain.entity.KbChunk;
import com.beauty.knowledge.module.cms.domain.entity.KbFile;
import com.beauty.knowledge.module.cms.domain.entity.KbKnowledge;
import com.beauty.knowledge.module.cms.domain.entity.ProcessTask;
import com.beauty.knowledge.module.cms.domain.vo.FileUploadVO;
import com.beauty.knowledge.module.cms.mapper.KbChunkMapper;
import com.beauty.knowledge.module.cms.mapper.KbFileMapper;
import com.beauty.knowledge.module.cms.mapper.KbKnowledgeMapper;
import com.beauty.knowledge.module.cms.mapper.ProcessTaskMapper;
import com.beauty.knowledge.module.cms.service.FileService;
import com.beauty.knowledge.module.pipeline.domain.mq.ProcessMessage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@Service
@Slf4j
@RequiredArgsConstructor
public class FileServiceImpl implements FileService {

    private final KbFileMapper kbFileMapper;
    private final ProcessTaskMapper processTaskMapper;
    private final KbChunkMapper kbChunkMapper;
    private final KbKnowledgeMapper kbKnowledgeMapper;
    private final RabbitTemplate rabbitTemplate;
    private final MinioStorageService minioStorageService;
    private final MilvusVectorStore milvusVectorStore;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public FileUploadVO upload(MultipartFile file, Long knowledgeId, Long categoryId, String fileType) {
        if (file == null || file.isEmpty()) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "上传文件不能为空");
        }
        if (knowledgeId == null) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "knowledgeId不能为空");
        }

        KbKnowledge knowledge = kbKnowledgeMapper.selectById(knowledgeId);
        if (knowledge == null) {
            throw new BusinessException(ErrorCode.KNOWLEDGE_NOT_FOUND);
        }

        String detectedType = StringUtils.hasText(fileType) ? fileType : detectFileType(file.getOriginalFilename());
        String fileHash = FileHashUtil.sha256(file);

        KbFile existing = kbFileMapper.selectOne(new LambdaQueryWrapper<KbFile>()
                .eq(KbFile::getFileHash, fileHash)
                .last("limit 1"));
        if (existing != null) {
            throw new BusinessException(ErrorCode.FILE_HASH_DUPLICATE);
        }

        try {
            String minioPath = minioStorageService.buildPath(detectedType, file.getOriginalFilename());
            minioStorageService.upload(file.getBytes(), minioPath, file.getContentType());

            KbFile kbFile = new KbFile();
            kbFile.setKnowledgeId(knowledgeId);
            kbFile.setOriginalName(file.getOriginalFilename());
            kbFile.setFileType(detectedType);
            kbFile.setFileSize(file.getSize());
            kbFile.setMinioPath(minioPath);
            kbFile.setFileHash(fileHash);
            kbFile.setVersion(1);
            kbFile.setProcessStatus("PENDING");
            kbFile.setUploadedBy(SecurityUtil.getCurrentUserId());
            kbFileMapper.insert(kbFile);

            ProcessTask task = new ProcessTask();
            task.setFileId(kbFile.getId());
            task.setTaskType("KNOWLEDGE_PROCESS");
            task.setStatus("PENDING");
            task.setProgress(0);
            task.setRetryCount(0);
            task.setMaxRetry(3);
            processTaskMapper.insert(task);

            Long finalFileId = kbFile.getId();
            Long finalTaskId = task.getId();
            TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
                @Override
                public void afterCommit() {
                    ProcessMessage msg = ProcessMessage.builder()
                            .fileId(finalFileId)
                            .fileType(detectedType)
                            .minioPath(minioPath)
                            .categoryId(categoryId)
                            .knowledgeId(knowledgeId)
                            .build();
                    rabbitTemplate.convertAndSend(
                            RabbitMQConstant.PROCESS_EXCHANGE,
                            RabbitMQConstant.PROCESS_ROUTING_KEY,
                            msg
                    );
                }
            });

            return FileUploadVO.builder()
                    .fileId(finalFileId)
                    .taskId(finalTaskId)
                    .minioPath(minioPath)
                    .processStatus("PENDING")
                    .build();
        } catch (BusinessException ex) {
            throw ex;
        } catch (Exception ex) {
            throw new BusinessException(ErrorCode.INTERNAL_ERROR, "文件上传失败");
        }
    }

    @Override
    public ProcessTask getTask(Long taskId) {
        ProcessTask task = processTaskMapper.selectById(taskId);
        if (task == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "任务不存在");
        }
        return task;
    }

    @Override
    public List<ProcessTask> recentTasks(Integer size) {
        int limit = (size == null || size <= 0) ? 10 : Math.min(size, 50);
        try {
            return processTaskMapper.selectList(new LambdaQueryWrapper<ProcessTask>()
                    .orderByDesc(ProcessTask::getId)
                    .last("limit " + limit));
        } catch (Exception ex) {
            // Compatible with environments where process_task table is not initialized yet.
            log.warn("process_task table not ready, return empty recent task list");
            return List.of();
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void retry(Long taskId) {
        ProcessTask task = processTaskMapper.selectById(taskId);
        if (task == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "任务不存在");
        }
        if (!"FAILED".equalsIgnoreCase(task.getStatus())) {
            throw new BusinessException(ErrorCode.FILE_PROCESSING);
        }

        KbFile kbFile = kbFileMapper.selectById(task.getFileId());
        if (kbFile == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "文件不存在");
        }

        task.setStatus("PENDING");
        task.setProgress(0);
        task.setResultMsg(null);
        task.setRetryCount(0);
        task.setStartedAt(null);
        task.setFinishedAt(null);
        processTaskMapper.updateById(task);

        kbFile.setProcessStatus("PENDING");
        kbFileMapper.updateById(kbFile);

        ProcessMessage msg = ProcessMessage.builder()
                .fileId(kbFile.getId())
                .fileType(kbFile.getFileType())
                .minioPath(kbFile.getMinioPath())
                .knowledgeId(kbFile.getKnowledgeId())
                .retryCount(1)
                .build();
        rabbitTemplate.convertAndSend(RabbitMQConstant.PROCESS_EXCHANGE, RabbitMQConstant.PROCESS_ROUTING_KEY, msg);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void remove(Long fileId) {
        KbFile file = kbFileMapper.selectById(fileId);
        if (file == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "文件不存在");
        }

        milvusVectorStore.deleteByFileId(fileId);
        kbChunkMapper.delete(new LambdaQueryWrapper<KbChunk>().eq(KbChunk::getFileId, fileId));
        processTaskMapper.delete(new LambdaQueryWrapper<ProcessTask>().eq(ProcessTask::getFileId, fileId));

        if (StringUtils.hasText(file.getMinioPath())) {
            minioStorageService.remove(file.getMinioPath());
        }
        kbFileMapper.deleteById(fileId);
    }

    private String detectFileType(String originalName) {
        if (!StringUtils.hasText(originalName)) {
            return "pdf";
        }
        String lower = originalName.toLowerCase();
        if (lower.endsWith(".png") || lower.endsWith(".jpg") || lower.endsWith(".jpeg") || lower.endsWith(".webp")) {
            return "image";
        }
        return "pdf";
    }
}
