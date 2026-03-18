package com.beauty.knowledge.module.cms.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.common.result.PageResult;
import com.beauty.knowledge.common.util.FileHashUtil;
import com.beauty.knowledge.common.util.SecurityUtil;
import com.beauty.knowledge.infrastructure.storage.MinioStorageService;
import com.beauty.knowledge.infrastructure.vector.MilvusVectorStore;
import com.beauty.knowledge.module.cms.domain.dto.KnowledgePageDTO;
import com.beauty.knowledge.module.cms.domain.dto.KnowledgeSaveDTO;
import com.beauty.knowledge.module.cms.domain.entity.KbChunk;
import com.beauty.knowledge.module.cms.domain.entity.KbFile;
import com.beauty.knowledge.module.cms.domain.entity.KbKnowledge;
import com.beauty.knowledge.module.cms.domain.vo.KnowledgeDetailVO;
import com.beauty.knowledge.module.cms.mapper.KbChunkMapper;
import com.beauty.knowledge.module.cms.mapper.KbFileMapper;
import com.beauty.knowledge.module.cms.mapper.KbKnowledgeMapper;
import com.beauty.knowledge.module.cms.mapper.ProcessTaskMapper;
import com.beauty.knowledge.module.cms.service.KnowledgeService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class KnowledgeServiceImpl implements KnowledgeService {

    private final KbKnowledgeMapper kbKnowledgeMapper;
    private final KbFileMapper kbFileMapper;
    private final KbChunkMapper kbChunkMapper;
    private final MilvusVectorStore milvusVectorStore;
    private final MinioStorageService minioStorageService;
    private final ProcessTaskMapper processTaskMapper;

    @Override
    public PageResult<KbKnowledge> page(KnowledgePageDTO dto) {
        Page<KbKnowledge> page = new Page<>(dto.getPageNum(), dto.getPageSize());
        LambdaQueryWrapper<KbKnowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.hasText(dto.getKeyword()), KbKnowledge::getTitle, dto.getKeyword())
                .eq(dto.getCategoryId() != null, KbKnowledge::getCategoryId, dto.getCategoryId())
                .eq(dto.getStatus() != null, KbKnowledge::getStatus, dto.getStatus())
                .eq(StringUtils.hasText(dto.getType()), KbKnowledge::getType, dto.getType())
                .orderByDesc(KbKnowledge::getId);
        return PageResult.of(kbKnowledgeMapper.selectPage(page, wrapper));
    }

    @Override
    public KnowledgeDetailVO getById(Long id) {
        KbKnowledge knowledge = kbKnowledgeMapper.selectById(id);
        if (knowledge == null) {
            throw new BusinessException(ErrorCode.KNOWLEDGE_NOT_FOUND);
        }
        List<KbFile> files = kbFileMapper.selectList(new LambdaQueryWrapper<KbFile>()
                .eq(KbFile::getKnowledgeId, id)
                .orderByDesc(KbFile::getId));
        return KnowledgeDetailVO.builder().knowledge(knowledge).files(files).build();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void save(KnowledgeSaveDTO dto) {
        KbKnowledge knowledge = new KbKnowledge();
        knowledge.setTitle(dto.getTitle());
        knowledge.setSummary(dto.getSummary());
        knowledge.setCategoryId(dto.getCategoryId());
        knowledge.setType(normalizeKnowledgeType(dto.getType()));
        knowledge.setContent(dto.getContent());
        knowledge.setStatus(dto.getStatus() == null ? 1 : dto.getStatus());
        knowledge.setCoverUrl(dto.getCoverUrl());
        knowledge.setViewCount(0);
        knowledge.setAuthorId(SecurityUtil.getCurrentUserId());
        kbKnowledgeMapper.insert(knowledge);
        createInitialTaskByKnowledgeContent(knowledge);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void update(Long id, KnowledgeSaveDTO dto) {
        KbKnowledge knowledge = kbKnowledgeMapper.selectById(id);
        if (knowledge == null) {
            throw new BusinessException(ErrorCode.KNOWLEDGE_NOT_FOUND);
        }
        knowledge.setTitle(dto.getTitle());
        knowledge.setSummary(dto.getSummary());
        knowledge.setCategoryId(dto.getCategoryId());
        knowledge.setType(normalizeKnowledgeType(dto.getType()));
        knowledge.setContent(dto.getContent());
        knowledge.setStatus(dto.getStatus() == null ? 1 : dto.getStatus());
        knowledge.setCoverUrl(dto.getCoverUrl());
        kbKnowledgeMapper.updateById(knowledge);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void remove(Long id) {
        KbKnowledge knowledge = kbKnowledgeMapper.selectById(id);
        if (knowledge == null) {
            throw new BusinessException(ErrorCode.KNOWLEDGE_NOT_FOUND);
        }

        List<KbFile> files = kbFileMapper.selectList(new LambdaQueryWrapper<KbFile>().eq(KbFile::getKnowledgeId, id));
        for (KbFile file : files) {
            milvusVectorStore.deleteByFileId(file.getId());
            kbChunkMapper.delete(new LambdaQueryWrapper<KbChunk>().eq(KbChunk::getFileId, file.getId()));
            if (StringUtils.hasText(file.getMinioPath())) {
                minioStorageService.remove(file.getMinioPath());
            }
            kbFileMapper.deleteById(file.getId());
        }

        kbKnowledgeMapper.deleteById(id);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void updateStatus(Long id, Integer status) {
        if (status == null || (status != 0 && status != 1)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "status must be 0 or 1");
        }
        KbKnowledge knowledge = kbKnowledgeMapper.selectById(id);
        if (knowledge == null) {
            throw new BusinessException(ErrorCode.KNOWLEDGE_NOT_FOUND);
        }
        knowledge.setStatus(status);
        kbKnowledgeMapper.updateById(knowledge);
    }

    @Override
    public PageResult<KbKnowledge> search(String keyword, Long pageNum, Long pageSize) {
        long p = pageNum == null || pageNum < 1 ? 1 : pageNum;
        long s = pageSize == null || pageSize < 1 ? 10 : pageSize;
        long offset = (p - 1) * s;
        if (!StringUtils.hasText(keyword)) {
            KnowledgePageDTO dto = new KnowledgePageDTO();
            dto.setPageNum(p);
            dto.setPageSize(s);
            dto.setStatus(1);
            return page(dto);
        }

        List<KbKnowledge> records = kbKnowledgeMapper.fullTextSearch(keyword, offset, s);
        long total = kbKnowledgeMapper.fullTextSearchCount(keyword);
        if (total == 0) {
            Page<KbKnowledge> fallbackPage = new Page<>(p, s);
            LambdaQueryWrapper<KbKnowledge> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(KbKnowledge::getStatus, 1)
                    .and(w -> w.like(KbKnowledge::getTitle, keyword).or().like(KbKnowledge::getContent, keyword))
                    .orderByDesc(KbKnowledge::getId);
            Page<KbKnowledge> pg = kbKnowledgeMapper.selectPage(fallbackPage, wrapper);
            return PageResult.of(pg);
        }

        long pages = (total + s - 1) / s;
        return PageResult.<KbKnowledge>builder()
                .records(records)
                .total(total)
                .pageNum(p)
                .pageSize(s)
                .pages(pages)
                .build();
    }

    private String normalizeKnowledgeType(String type) {
        if (!StringUtils.hasText(type)) {
            return "TEXT_TXT";
        }
        String normalized = type.trim().toUpperCase();
        if ("PDF".equals(normalized)) {
            return "DOC_PDF";
        }
        if ("DOC".equals(normalized)) {
            return "DOC_WORD";
        }
        if ("TEXT".equals(normalized)) {
            return "TEXT_TXT";
        }
        if ("IMAGE".equals(normalized)
                || "TEXT_TXT".equals(normalized)
                || "TEXT_MD".equals(normalized)
                || "DOC_PDF".equals(normalized)
                || "DOC_WORD".equals(normalized)
                || "DOC_PPT".equals(normalized)
                || "DOC_EXCEL".equals(normalized)) {
            return normalized;
        }
        return "TEXT_TXT";
    }

    private void createInitialTaskByKnowledgeContent(KbKnowledge knowledge) {
        String text = StringUtils.hasText(knowledge.getContent())
                ? knowledge.getContent()
                : (StringUtils.hasText(knowledge.getSummary()) ? knowledge.getSummary() : "暂无内容");

        byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
        String originalName = knowledge.getTitle() + "-正文.txt";
        String fileType = "text_txt";
        String minioPath = minioStorageService.buildPath(fileType, originalName);
        minioStorageService.upload(bytes, minioPath, "text/plain");

        KbFile file = new KbFile();
        file.setKnowledgeId(knowledge.getId());
        file.setOriginalName(originalName);
        file.setFileType(fileType);
        file.setFileSize((long) bytes.length);
        file.setMinioPath(minioPath);
        file.setFileHash(FileHashUtil.sha256(bytes));
        file.setVersion(1);
        file.setProcessStatus("SUCCESS");
        file.setUploadedBy(SecurityUtil.getCurrentUserId());
        kbFileMapper.insert(file);

        com.beauty.knowledge.module.cms.domain.entity.ProcessTask task =
                new com.beauty.knowledge.module.cms.domain.entity.ProcessTask();
        task.setFileId(file.getId());
        task.setTaskType("KNOWLEDGE_CREATE");
        task.setStatus("SUCCESS");
        task.setProgress(100);
        task.setResultMsg("知识创建完成");
        task.setRetryCount(0);
        task.setMaxRetry(3);
        task.setStartedAt(LocalDateTime.now());
        task.setFinishedAt(LocalDateTime.now());
        processTaskMapper.insert(task);
    }
}
