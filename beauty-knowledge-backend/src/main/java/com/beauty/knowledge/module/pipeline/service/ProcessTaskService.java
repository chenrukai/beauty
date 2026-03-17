package com.beauty.knowledge.module.pipeline.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.module.cms.domain.entity.KbFile;
import com.beauty.knowledge.module.cms.domain.entity.ProcessTask;
import com.beauty.knowledge.module.cms.mapper.KbFileMapper;
import com.beauty.knowledge.module.cms.mapper.ProcessTaskMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class ProcessTaskService {

    private final ProcessTaskMapper processTaskMapper;
    private final KbFileMapper kbFileMapper;

    @Transactional(rollbackFor = Exception.class)
    public void markProcessing(Long fileId) {
        ProcessTask task = getByFileId(fileId);
        if (task != null) {
            task.setStatus("PROCESSING");
            task.setProgress(5);
            task.setStartedAt(LocalDateTime.now());
            task.setResultMsg(null);
            processTaskMapper.updateById(task);
        }

        KbFile file = kbFileMapper.selectById(fileId);
        if (file != null) {
            file.setProcessStatus("PROCESSING");
            kbFileMapper.updateById(file);
        }
    }

    @Transactional(rollbackFor = Exception.class)
    public void markSuccess(Long fileId) {
        ProcessTask task = getByFileId(fileId);
        if (task != null) {
            task.setStatus("SUCCESS");
            task.setProgress(100);
            task.setFinishedAt(LocalDateTime.now());
            task.setResultMsg("处理成功");
            processTaskMapper.updateById(task);
        }

        KbFile file = kbFileMapper.selectById(fileId);
        if (file != null) {
            file.setProcessStatus("SUCCESS");
            kbFileMapper.updateById(file);
        }
    }

    @Transactional(rollbackFor = Exception.class)
    public void markFailed(Long fileId, String message) {
        ProcessTask task = getByFileId(fileId);
        if (task != null) {
            task.setStatus("FAILED");
            task.setFinishedAt(LocalDateTime.now());
            task.setResultMsg(message);
            processTaskMapper.updateById(task);
        }

        KbFile file = kbFileMapper.selectById(fileId);
        if (file != null) {
            file.setProcessStatus("FAILED");
            kbFileMapper.updateById(file);
        }
    }

    public ProcessTask getByFileId(Long fileId) {
        return processTaskMapper.selectOne(new LambdaQueryWrapper<ProcessTask>()
                .eq(ProcessTask::getFileId, fileId)
                .last("limit 1"));
    }
}
