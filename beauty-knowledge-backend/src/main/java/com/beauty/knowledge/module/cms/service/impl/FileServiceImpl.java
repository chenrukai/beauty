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
import com.beauty.knowledge.module.cms.domain.entity.KbCategory;
import com.beauty.knowledge.module.cms.domain.entity.KbFile;
import com.beauty.knowledge.module.cms.domain.entity.KbKnowledge;
import com.beauty.knowledge.module.cms.domain.entity.ProcessTask;
import com.beauty.knowledge.module.cms.domain.vo.FileBinaryVO;
import com.beauty.knowledge.module.cms.domain.vo.FileUploadVO;
import com.beauty.knowledge.module.cms.domain.vo.ProcessTaskViewVO;
import com.beauty.knowledge.module.cms.mapper.KbChunkMapper;
import com.beauty.knowledge.module.cms.mapper.KbCategoryMapper;
import com.beauty.knowledge.module.cms.mapper.KbFileMapper;
import com.beauty.knowledge.module.cms.mapper.KbKnowledgeMapper;
import com.beauty.knowledge.module.cms.mapper.ProcessTaskMapper;
import com.beauty.knowledge.module.entity.domain.entity.EntityExtractPending;
import com.beauty.knowledge.module.entity.mapper.EntityExtractPendingMapper;
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

import java.nio.ByteBuffer;
import java.nio.CharBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.Charset;
import java.nio.charset.CharsetDecoder;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Objects;
import java.util.Locale;

@Service
@Slf4j
@RequiredArgsConstructor
public class FileServiceImpl implements FileService {

    private final KbFileMapper kbFileMapper;
    private final ProcessTaskMapper processTaskMapper;
    private final KbChunkMapper kbChunkMapper;
    private final KbCategoryMapper kbCategoryMapper;
    private final KbKnowledgeMapper kbKnowledgeMapper;
    private final RabbitTemplate rabbitTemplate;
    private final MinioStorageService minioStorageService;
    private final MilvusVectorStore milvusVectorStore;
    private final EntityExtractPendingMapper entityExtractPendingMapper;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public FileUploadVO upload(MultipartFile file, Long knowledgeId, Long categoryId, String fileType) {
        if (file == null || file.isEmpty()) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "uploaded file is empty");
        }
        if (knowledgeId == null) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "knowledgeId is required");
        }

        KbKnowledge knowledge = kbKnowledgeMapper.selectById(knowledgeId);
        if (knowledge == null) {
            throw new BusinessException(ErrorCode.KNOWLEDGE_NOT_FOUND);
        }
        if (categoryId != null) {
            KbCategory category = kbCategoryMapper.selectById(categoryId);
            if (category == null) {
                throw new BusinessException(ErrorCode.BAD_REQUEST, "category node not found");
            }
            if (!Integer.valueOf(1).equals(category.getStatus())) {
                throw new BusinessException(ErrorCode.BAD_REQUEST, "category is disabled and cannot be used for upload");
            }
        }

        String detectedType = resolveFileType(fileType, file.getOriginalFilename());
        validateFileExtension(detectedType, file.getOriginalFilename());
        String knowledgeType = normalizeKnowledgeType(knowledge.getType());
        String uploadMappedType = mapUploadTypeToKnowledgeType(detectedType);
        if (!isKnowledgeTypeCompatible(knowledgeType, uploadMappedType)) {
            throw new BusinessException(
                    ErrorCode.BAD_REQUEST,
                    "file type is incompatible with knowledge type: knowledge=" + knowledgeType + ", file=" + uploadMappedType
            );
        }

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
            throw new BusinessException(ErrorCode.INTERNAL_ERROR, "file upload failed");
        }
    }

    @Override
    public ProcessTaskViewVO getTask(Long taskId) {
        ProcessTask task = processTaskMapper.selectById(taskId);
        if (task == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "task not found");
        }
        ProcessTaskViewVO view = toTaskView(task);
        if (view == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "task not found");
        }
        return view;
    }

    @Override
    public List<ProcessTaskViewVO> recentTasks(Integer size) {
        int limit = (size == null || size <= 0) ? 10 : Math.min(size, 50);
        try {
            List<ProcessTask> tasks = processTaskMapper.selectList(new LambdaQueryWrapper<ProcessTask>()
                    .orderByDesc(ProcessTask::getId)
                    .last("limit " + limit));
            return tasks.stream()
                    .map(this::toTaskView)
                    .filter(Objects::nonNull)
                    .toList();
        } catch (Exception ex) {
            log.warn("process_task table not ready, return empty recent task list");
            return List.of();
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void retry(Long taskId) {
        ProcessTask task = processTaskMapper.selectById(taskId);
        if (task == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "task not found");
        }
        if (!"FAILED".equalsIgnoreCase(task.getStatus())) {
            throw new BusinessException(ErrorCode.FILE_PROCESSING);
        }

        KbFile kbFile = kbFileMapper.selectById(task.getFileId());
        if (kbFile == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "file not found");
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
    public FileBinaryVO openFile(Long fileId) {
        if (fileId == null || fileId <= 0) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "fileId is required");
        }
        KbFile file = kbFileMapper.selectById(fileId);
        if (file == null || Integer.valueOf(1).equals(file.getIsDeleted())) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "file not found");
        }
        KbKnowledge knowledge = file.getKnowledgeId() == null ? null : kbKnowledgeMapper.selectById(file.getKnowledgeId());
        if (knowledge == null || Integer.valueOf(1).equals(knowledge.getIsDeleted())) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "knowledge not found");
        }
        // Normal users can only preview published knowledge attachments.
        if (!SecurityUtil.isAdmin() && !Integer.valueOf(1).equals(knowledge.getStatus())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "file is not accessible");
        }
        if (!StringUtils.hasText(file.getMinioPath())) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "file storage path is missing");
        }
        String fileName = StringUtils.hasText(file.getOriginalName()) ? file.getOriginalName() : ("file-" + file.getId());
        String contentType = detectContentTypeByName(fileName);
        byte[] bytes = buildGeneratedKnowledgeBodyBytes(file, knowledge);
        if (bytes == null) {
            try {
                bytes = minioStorageService.download(file.getMinioPath());
            } catch (Exception ex) {
                throw new BusinessException(ErrorCode.NOT_FOUND, "file binary not found");
            }
        }
        bytes = normalizeTextBytesIfNeeded(fileName, contentType, bytes);
        return new FileBinaryVO(fileName, contentType, bytes);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void remove(Long fileId) {
        KbFile file = kbFileMapper.selectById(fileId);
        if (file == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "file not found");
        }

        milvusVectorStore.deleteByFileId(fileId);
        kbChunkMapper.delete(new LambdaQueryWrapper<KbChunk>().eq(KbChunk::getFileId, fileId));
        processTaskMapper.delete(new LambdaQueryWrapper<ProcessTask>().eq(ProcessTask::getFileId, fileId));

        if (StringUtils.hasText(file.getMinioPath())) {
            minioStorageService.remove(file.getMinioPath());
        }
        kbFileMapper.deleteById(fileId);
    }

    private ProcessTaskViewVO toTaskView(ProcessTask task) {
        KbFile file = task.getFileId() == null ? null : kbFileMapper.selectById(task.getFileId());
        if (file == null) {
            return null;
        }
        KbKnowledge knowledge = (file == null || file.getKnowledgeId() == null)
                ? null
                : kbKnowledgeMapper.selectById(file.getKnowledgeId());
        if (knowledge == null) {
            return null;
        }
        int pendingEntityCount = countEntityByStatus(task.getFileId(), "PENDING");
        int confirmedEntityCount = countEntityByStatus(task.getFileId(), "CONFIRMED");
        int rejectedEntityCount = countEntityByStatus(task.getFileId(), "REJECTED");
        String stageCode = resolveStageCode(task, pendingEntityCount, confirmedEntityCount, rejectedEntityCount);
        String stageText = stageText(stageCode);
        boolean canRetry = canRetry(task);
        boolean canReExtract = canReExtract(task);
        boolean canConfirm = pendingEntityCount > 0;
        String failureReason = ("PARSE_FAILED".equals(stageCode) || "FAILED".equalsIgnoreCase(task.getStatus()))
                ? task.getResultMsg()
                : null;

        return ProcessTaskViewVO.builder()
                .id(task.getId())
                .fileId(task.getFileId())
                .fileName(file == null ? null : file.getOriginalName())
                .knowledgeId(file == null ? null : file.getKnowledgeId())
                .knowledgeTitle(knowledge == null ? null : knowledge.getTitle())
                .taskType(task.getTaskType())
                .status(task.getStatus())
                .stageCode(stageCode)
                .stageText(stageText)
                .progress(task.getProgress())
                .resultMsg(task.getResultMsg())
                .failureReason(failureReason)
                .canRetry(canRetry)
                .canReExtract(canReExtract)
                .canConfirm(canConfirm)
                .pendingEntityCount(pendingEntityCount)
                .confirmedEntityCount(confirmedEntityCount)
                .rejectedEntityCount(rejectedEntityCount)
                .retryCount(task.getRetryCount())
                .maxRetry(task.getMaxRetry())
                .startedAt(task.getStartedAt())
                .finishedAt(task.getFinishedAt())
                .createdAt(task.getCreatedAt())
                .updatedAt(task.getUpdatedAt())
                .build();
    }

    private int countEntityByStatus(Long fileId, String status) {
        if (fileId == null || fileId <= 0) {
            return 0;
        }
        Long c = entityExtractPendingMapper.selectCount(new LambdaQueryWrapper<EntityExtractPending>()
                .eq(EntityExtractPending::getFileId, fileId)
                .eq(EntityExtractPending::getStatus, status));
        return c == null ? 0 : c.intValue();
    }

    private String resolveStageCode(ProcessTask task, int pending, int confirmed, int rejected) {
        String taskType = String.valueOf(task.getTaskType()).toUpperCase();
        String status = String.valueOf(task.getStatus()).toUpperCase();
        if ("KNOWLEDGE_CREATE".equals(taskType)) {
            return "CONFIRMED";
        }
        if (status.contains("FAIL") || status.contains("ERROR")) {
            return "PARSE_FAILED";
        }
        if ("EXTRACTING".equals(status)) {
            return "EXTRACTING";
        }
        if (status.contains("PROCESS") || status.contains("RUN")) {
            return "PARSING";
        }
        if (status.contains("PENDING")) {
            return "UPLOADED";
        }
        if (pending > 0) {
            return "PENDING_CONFIRM";
        }
        if (confirmed > 0 && pending == 0) {
            return "CONFIRMED";
        }
        if (rejected > 0 && pending == 0 && confirmed == 0) {
            return "CONFIRMED";
        }
        return "PARSE_SUCCESS";
    }

    private String stageText(String stageCode) {
        return switch (stageCode) {
            case "UPLOADED" -> "上传";
            case "PARSING" -> "解析中";
            case "PARSE_SUCCESS" -> "解析成功";
            case "PARSE_FAILED" -> "解析失败";
            case "EXTRACTING" -> "抽取中";
            case "PENDING_CONFIRM" -> "待确认";
            case "CONFIRMED" -> "已确认";
            default -> "未知";
        };
    }

    private boolean canRetry(ProcessTask task) {
        String s = String.valueOf(task.getStatus()).toUpperCase();
        return s.contains("FAIL") || s.contains("ERROR");
    }

    private boolean canReExtract(ProcessTask task) {
        if (task == null || task.getFileId() == null || task.getFileId() <= 0) {
            return false;
        }
        String type = String.valueOf(task.getTaskType()).toUpperCase();
        String status = String.valueOf(task.getStatus()).toUpperCase();
        return "KNOWLEDGE_PROCESS".equals(type) && "SUCCESS".equals(status);
    }

    private String resolveFileType(String requestFileType, String originalName) {
        if (StringUtils.hasText(requestFileType) && !"auto".equalsIgnoreCase(requestFileType)) {
            return requestFileType.toLowerCase();
        }
        return detectFileType(originalName);
    }

    private String detectFileType(String originalName) {
        if (!StringUtils.hasText(originalName)) {
            return "doc_word";
        }
        String lower = originalName.toLowerCase();
        if (lower.endsWith(".png") || lower.endsWith(".jpg") || lower.endsWith(".jpeg")
                || lower.endsWith(".webp") || lower.endsWith(".bmp") || lower.endsWith(".gif")) {
            return "image";
        }
        if (lower.endsWith(".mp4") || lower.endsWith(".mov") || lower.endsWith(".avi")
                || lower.endsWith(".mkv") || lower.endsWith(".webm") || lower.endsWith(".m4v")) {
            return "video";
        }
        if (lower.endsWith(".mp3") || lower.endsWith(".wav") || lower.endsWith(".m4a")
                || lower.endsWith(".aac") || lower.endsWith(".flac") || lower.endsWith(".ogg")) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "audio upload is disabled");
        }
        if (lower.endsWith(".txt") || lower.endsWith(".csv") || lower.endsWith(".json")) {
            return "text_txt";
        }
        if (lower.endsWith(".md")) {
            return "text_md";
        }
        if (lower.endsWith(".pdf")) {
            return "doc_pdf";
        }
        if (lower.endsWith(".ppt") || lower.endsWith(".pptx")) {
            return "doc_ppt";
        }
        if (lower.endsWith(".xls") || lower.endsWith(".xlsx")) {
            return "doc_excel";
        }
        return "doc_word";
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
        if ("VIDEO".equals(normalized)) {
            return "VIDEO";
        }
        if ("AUDIO".equals(normalized)) {
            return "AUDIO";
        }
        if ("MEDIA".equals(normalized) || "MEDIA_AV".equals(normalized)) {
            return "MEDIA_AV";
        }
        if ("IMAGE".equals(normalized)
                || "TEXT_TXT".equals(normalized)
                || "TEXT_MD".equals(normalized)
                || "DOC_PDF".equals(normalized)
                || "DOC_WORD".equals(normalized)
                || "DOC_PPT".equals(normalized)
                || "DOC_EXCEL".equals(normalized)
                || "VIDEO".equals(normalized)
                || "AUDIO".equals(normalized)
                || "MEDIA_AV".equals(normalized)) {
            return normalized;
        }
        return "TEXT_TXT";
    }

    private String mapUploadTypeToKnowledgeType(String uploadType) {
        if (!StringUtils.hasText(uploadType)) {
            return "DOC_WORD";
        }
        String normalized = uploadType.trim().toLowerCase();
        if ("image".equals(normalized)) {
            return "IMAGE";
        }
        if ("video".equals(normalized)) {
            return "VIDEO";
        }
        if ("audio".equals(normalized)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "audio upload is disabled");
        }
        if ("text_txt".equals(normalized)) {
            return "TEXT_TXT";
        }
        if ("text_md".equals(normalized)) {
            return "TEXT_MD";
        }
        if ("doc_pdf".equals(normalized) || "pdf".equals(normalized)) {
            return "DOC_PDF";
        }
        if ("doc_word".equals(normalized) || "doc".equals(normalized)) {
            return "DOC_WORD";
        }
        if ("doc_ppt".equals(normalized)) {
            return "DOC_PPT";
        }
        if ("doc_excel".equals(normalized)) {
            return "DOC_EXCEL";
        }
        return "DOC_WORD";
    }

    private boolean isKnowledgeTypeCompatible(String knowledgeType, String uploadType) {
        if (knowledgeType.equals(uploadType)) {
            return true;
        }
        // Media upload (image/video) is allowed for CMS unified multimedia knowledge.
        if (isMediaUploadType(uploadType)) {
            return true;
        }
        // Text knowledge and document knowledge both accept common document/text uploads.
        // This keeps the upload entry practical for CMS scenarios where the knowledge record
        // represents a topic and the attachment may be txt/md/doc/docx/pdf/ppt/xlsx.
        if (isTextKnowledgeType(knowledgeType) && isDocumentUploadType(uploadType)) {
            return true;
        }
        // Document knowledge accepts common document/text uploads to avoid hard blocking by legacy type values.
        if (isDocumentKnowledgeType(knowledgeType) && isDocumentUploadType(uploadType)) {
            return true;
        }
        return false;
    }

    private boolean isTextKnowledgeType(String type) {
        return "TEXT_TXT".equals(type) || "TEXT_MD".equals(type);
    }

    private boolean isDocumentKnowledgeType(String type) {
        return "DOC_PDF".equals(type)
                || "DOC_WORD".equals(type)
                || "DOC_PPT".equals(type)
                || "DOC_EXCEL".equals(type);
    }

    private boolean isDocumentUploadType(String type) {
        return "DOC_PDF".equals(type)
                || "DOC_WORD".equals(type)
                || "DOC_PPT".equals(type)
                || "DOC_EXCEL".equals(type)
                || "TEXT_TXT".equals(type)
                || "TEXT_MD".equals(type);
    }

    private String detectContentTypeByName(String fileName) {
        if (!StringUtils.hasText(fileName)) {
            return "application/octet-stream";
        }
        String lower = fileName.toLowerCase(Locale.ROOT);
        if (lower.endsWith(".pdf")) return "application/pdf";
        if (lower.endsWith(".txt")) return "text/plain; charset=UTF-8";
        if (lower.endsWith(".md")) return "text/markdown; charset=UTF-8";
        if (lower.endsWith(".csv")) return "text/csv; charset=UTF-8";
        if (lower.endsWith(".json")) return "application/json; charset=UTF-8";
        if (lower.endsWith(".doc")) return "application/msword";
        if (lower.endsWith(".docx")) return "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
        if (lower.endsWith(".ppt")) return "application/vnd.ms-powerpoint";
        if (lower.endsWith(".pptx")) return "application/vnd.openxmlformats-officedocument.presentationml.presentation";
        if (lower.endsWith(".xls")) return "application/vnd.ms-excel";
        if (lower.endsWith(".xlsx")) return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
        if (lower.endsWith(".png")) return "image/png";
        if (lower.endsWith(".jpg") || lower.endsWith(".jpeg")) return "image/jpeg";
        if (lower.endsWith(".webp")) return "image/webp";
        if (lower.endsWith(".bmp")) return "image/bmp";
        if (lower.endsWith(".gif")) return "image/gif";
        if (lower.endsWith(".mp4")) return "video/mp4";
        if (lower.endsWith(".mov")) return "video/quicktime";
        if (lower.endsWith(".avi")) return "video/x-msvideo";
        if (lower.endsWith(".mkv")) return "video/x-matroska";
        if (lower.endsWith(".webm")) return "video/webm";
        if (lower.endsWith(".m4v")) return "video/x-m4v";
        return "application/octet-stream";
    }

    private boolean isMediaUploadType(String type) {
        return "IMAGE".equals(type)
                || "VIDEO".equals(type);
    }

    private byte[] normalizeTextBytesIfNeeded(String fileName, String contentType, byte[] bytes) {
        if (bytes == null || bytes.length == 0 || !isTextLikeFile(fileName, contentType)) {
            return bytes;
        }
        if (isValidUtf8(bytes)) {
            return bytes;
        }
        return new String(bytes, Charset.forName("GB18030")).getBytes(StandardCharsets.UTF_8);
    }

    private byte[] buildGeneratedKnowledgeBodyBytes(KbFile file, KbKnowledge knowledge) {
        if (file == null || knowledge == null) {
            return null;
        }
        String fileName = StringUtils.hasText(file.getOriginalName()) ? file.getOriginalName() : "";
        if (!"text_txt".equalsIgnoreCase(String.valueOf(file.getFileType()))) {
            return null;
        }
        if (!fileName.endsWith("-正文.txt")) {
            return null;
        }
        String text = StringUtils.hasText(knowledge.getContent())
                ? knowledge.getContent()
                : (StringUtils.hasText(knowledge.getSummary()) ? knowledge.getSummary() : "");
        if (!StringUtils.hasText(text)) {
            return null;
        }
        return text.getBytes(StandardCharsets.UTF_8);
    }

    private boolean isTextLikeFile(String fileName, String contentType) {
        String lowerName = StringUtils.hasText(fileName) ? fileName.toLowerCase(Locale.ROOT) : "";
        String lowerType = StringUtils.hasText(contentType) ? contentType.toLowerCase(Locale.ROOT) : "";
        return lowerType.startsWith("text/")
                || lowerType.contains("json")
                || lowerName.endsWith(".txt")
                || lowerName.endsWith(".md")
                || lowerName.endsWith(".csv")
                || lowerName.endsWith(".json");
    }

    private boolean isValidUtf8(byte[] bytes) {
        CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder()
                .onMalformedInput(CodingErrorAction.REPORT)
                .onUnmappableCharacter(CodingErrorAction.REPORT);
        try {
            CharBuffer ignored = decoder.decode(ByteBuffer.wrap(bytes));
            return true;
        } catch (CharacterCodingException ex) {
            return false;
        }
    }

    private void validateFileExtension(String uploadType, String originalName) {
        if (!StringUtils.hasText(originalName)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "original file name is required");
        }
        String name = originalName.toLowerCase();
        boolean ok = switch (uploadType) {
            case "image" -> hasAnySuffix(name, ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif");
            case "video" -> hasAnySuffix(name, ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v");
            case "audio" -> false;
            case "text_txt" -> hasAnySuffix(name, ".txt", ".csv", ".json");
            case "text_md" -> hasAnySuffix(name, ".md");
            case "doc_pdf" -> hasAnySuffix(name, ".pdf");
            case "doc_word" -> hasAnySuffix(name, ".doc", ".docx");
            case "doc_ppt" -> hasAnySuffix(name, ".ppt", ".pptx");
            case "doc_excel" -> hasAnySuffix(name, ".xls", ".xlsx");
            default -> false;
        };
        if (!ok) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "file extension does not match declared file type");
        }
    }

    private boolean hasAnySuffix(String name, String... suffixes) {
        for (String suffix : suffixes) {
            if (name.endsWith(suffix)) {
                return true;
            }
        }
        return false;
    }
}

