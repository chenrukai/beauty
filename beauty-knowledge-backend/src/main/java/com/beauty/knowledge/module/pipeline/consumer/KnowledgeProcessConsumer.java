package com.beauty.knowledge.module.pipeline.consumer;

import com.beauty.knowledge.common.constant.RabbitMQConstant;
import com.beauty.knowledge.infrastructure.ai.python.PythonAIClient;
import com.beauty.knowledge.infrastructure.storage.MinioStorageService;
import com.beauty.knowledge.infrastructure.vector.MilvusVectorStore;
import com.beauty.knowledge.module.entity.service.EntityExtractService;
import com.beauty.knowledge.module.pipeline.domain.dto.ChunkDTO;
import com.beauty.knowledge.module.pipeline.domain.entity.KbChunk;
import com.beauty.knowledge.module.pipeline.domain.mq.ProcessMessage;
import com.beauty.knowledge.module.pipeline.mapper.PipelineKbChunkMapper;
import com.beauty.knowledge.module.pipeline.service.ChunkService;
import com.beauty.knowledge.module.pipeline.service.ProcessTaskService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.tika.Tika;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.io.ByteArrayInputStream;
import java.util.List;

@Slf4j
@Component
@RequiredArgsConstructor
public class KnowledgeProcessConsumer {

    private final ProcessTaskService processTaskService;
    private final MinioStorageService minioStorageService;
    private final ChunkService chunkService;
    private final PipelineKbChunkMapper kbChunkMapper;
    private final PythonAIClient pythonAIClient;
    private final MilvusVectorStore milvusVectorStore;
    private final EntityExtractService entityExtractService;
    private final Tika tika = new Tika();

    @RabbitListener(queues = RabbitMQConstant.PROCESS_QUEUE)
    public void process(ProcessMessage msg) {
        Long fileId = msg.getFileId();
        try {
            log.info("Process file start, fileId={}, type={}", fileId, msg.getFileType());
            processTaskService.markProcessing(fileId);

            byte[] bytes = minioStorageService.download(msg.getMinioPath());
            String text = parseText(msg.getFileType(), bytes);
            List<ChunkDTO> chunks = chunkService.split(text);
            if (chunks.isEmpty()) {
                processTaskService.markFailed(fileId, "No text extracted. Check parseable content or transcription availability.");
                return;
            }

            List<KbChunk> entities = chunks.stream().map(c -> {
                KbChunk e = new KbChunk();
                e.setFileId(fileId);
                e.setKnowledgeId(msg.getKnowledgeId());
                e.setChunkIndex(c.getChunkIndex());
                e.setPageNo(c.getPage());
                e.setContent(c.getContent());
                e.setCharCount(c.getCharCount());
                e.setVectorStatus(1);
                return e;
            }).toList();
            kbChunkMapper.insertBatch(entities);

            try {
                List<String> texts = entities.stream().map(KbChunk::getContent).toList();
                List<float[]> vectors = pythonAIClient.embed(texts);
                List<Long> chunkIds = entities.stream().map(KbChunk::getId).toList();
                milvusVectorStore.batchInsert(chunkIds, vectors, fileId, msg.getCategoryId(), texts);
            } catch (Exception embedEx) {
                log.warn("Embedding/vector unavailable, continue with bm25-only flow. fileId={}, reason={}", fileId, embedEx.getMessage());
            }
            try {
                // Auto-generate pending entity confirmation items after successful parsing.
                processTaskService.markExtracting(fileId);
                entityExtractService.extractByText(fileId, text);
            } catch (Exception extractEx) {
                log.warn("Entity extraction skipped. fileId={}, reason={}", fileId, extractEx.getMessage());
            }

            processTaskService.markSuccess(fileId);
            log.info("Process file success, fileId={}, chunks={}", fileId, entities.size());
        } catch (Exception ex) {
            log.error("Process file failed, fileId={}", fileId, ex);
            processTaskService.markFailed(fileId, ex.getMessage());
            // Keep FAILED state and let admin trigger explicit retry.
            // Avoid broker redelivery loops that cause "failed then success" jitter.
        }
    }

    private String parseText(String fileType, byte[] bytes) throws Exception {
        if ("image".equalsIgnoreCase(fileType)) {
            if (!pythonAIClient.healthCheck()) {
                throw new IllegalStateException("OCR_UNAVAILABLE: 图片识别服务不可用，请先启动 ocr-ai 服务");
            }
            String text = pythonAIClient.ocr(bytes);
            if (!StringUtils.hasText(text)) {
                throw new IllegalStateException("OCR_EMPTY_TEXT: 图片未识别到可用文字，请上传包含清晰文字的图片");
            }
            return text;
        }
        if ("video".equalsIgnoreCase(fileType)) {
            String text = pythonAIClient.transcribe(bytes, "video");
            if (!StringUtils.hasText(text)) {
                throw new IllegalStateException("TRANSCRIBE_UNAVAILABLE: 视频转写不可用，请检查 Python transcribe 服务与 ffmpeg");
            }
            return text;
        }
        if ("audio".equalsIgnoreCase(fileType)) {
            throw new IllegalStateException("AUDIO_DISABLED: 音频上传已禁用");
        }
        String parsed = tika.parseToString(new ByteArrayInputStream(bytes));
        if (!StringUtils.hasText(parsed)) {
            return "";
        }
        return parsed.replace("\u0000", " ").trim();
    }
}
