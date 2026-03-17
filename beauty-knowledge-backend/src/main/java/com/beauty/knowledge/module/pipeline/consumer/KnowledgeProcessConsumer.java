package com.beauty.knowledge.module.pipeline.consumer;

import com.beauty.knowledge.common.constant.RabbitMQConstant;
import com.beauty.knowledge.infrastructure.ai.python.PythonAIClient;
import com.beauty.knowledge.infrastructure.storage.MinioStorageService;
import com.beauty.knowledge.infrastructure.vector.MilvusVectorStore;
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
                processTaskService.markFailed(fileId, "文本抽取为空");
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

            List<String> texts = entities.stream().map(KbChunk::getContent).toList();
            List<float[]> vectors = pythonAIClient.embed(texts);
            List<Long> chunkIds = entities.stream().map(KbChunk::getId).toList();
            milvusVectorStore.batchInsert(chunkIds, vectors, fileId, msg.getCategoryId(), texts);

            processTaskService.markSuccess(fileId);
            log.info("Process file success, fileId={}, chunks={}", fileId, entities.size());
        } catch (Exception ex) {
            log.error("Process file failed, fileId={}", fileId, ex);
            processTaskService.markFailed(fileId, ex.getMessage());
            throw new IllegalStateException("文件处理失败", ex);
        }
    }

    private String parseText(String fileType, byte[] bytes) throws Exception {
        if ("image".equalsIgnoreCase(fileType)) {
            return pythonAIClient.ocr(bytes);
        }
        String parsed = tika.parseToString(new ByteArrayInputStream(bytes));
        if (!StringUtils.hasText(parsed)) {
            return "";
        }
        return parsed.replace("\u0000", " ").trim();
    }
}
