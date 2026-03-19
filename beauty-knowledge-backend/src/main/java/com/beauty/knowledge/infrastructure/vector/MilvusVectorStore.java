package com.beauty.knowledge.infrastructure.vector;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.infrastructure.ai.python.PythonAIClient;
import com.beauty.knowledge.module.cms.domain.entity.KbChunk;
import com.beauty.knowledge.module.cms.mapper.KbChunkMapper;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Component
@RequiredArgsConstructor
public class MilvusVectorStore {

    private final KbChunkMapper kbChunkMapper;
    private final PythonAIClient pythonAIClient;

    @Value("${beauty.vector.warmup-enabled:true}")
    private boolean warmupEnabled;

    @Value("${beauty.vector.warmup-batch-size:200}")
    private int warmupBatchSize;

    private final Map<Long, float[]> vectorMap = new ConcurrentHashMap<>();
    private final Map<Long, Long> fileMap = new ConcurrentHashMap<>();
    private final Map<Long, Long> categoryMap = new ConcurrentHashMap<>();
    private final Map<Long, String> contentMap = new ConcurrentHashMap<>();

    @PostConstruct
    public void loadCollection() {
        try {
            if (!warmupEnabled) {
                log.info("Milvus collection warmup skipped (disabled).");
                return;
            }

            List<KbChunk> chunks = kbChunkMapper.selectList(new LambdaQueryWrapper<KbChunk>()
                    .select(KbChunk::getId, KbChunk::getFileId, KbChunk::getContent)
                    .orderByAsc(KbChunk::getId));
            if (chunks == null || chunks.isEmpty()) {
                log.info("Milvus warmup skipped (no kb_chunk rows).");
                return;
            }

            int batchSize = Math.max(50, warmupBatchSize);
            int loaded = 0;
            for (int i = 0; i < chunks.size(); i += batchSize) {
                int end = Math.min(i + batchSize, chunks.size());
                List<KbChunk> batch = chunks.subList(i, end);
                List<String> texts = batch.stream().map(c -> c.getContent() == null ? "" : c.getContent()).toList();
                List<float[]> vectors = pythonAIClient.embed(texts);
                int size = Math.min(batch.size(), vectors.size());
                for (int j = 0; j < size; j++) {
                    KbChunk chunk = batch.get(j);
                    Long chunkId = chunk.getId();
                    vectorMap.put(chunkId, vectors.get(j));
                    if (chunk.getFileId() != null) {
                        fileMap.put(chunkId, chunk.getFileId());
                    }
                    contentMap.put(chunkId, texts.get(j));
                }
                loaded += size;
            }
            log.info("Milvus collection loaded (safe mode), warmed vectors={}/{}", loaded, chunks.size());
        } catch (Exception ex) {
            log.warn("Milvus collection load failed but app keeps running: {}", ex.getMessage());
        }
    }

    public void batchInsert(List<Long> chunkIds,
                            List<float[]> vectors,
                            Long fileId,
                            Long categoryId,
                            List<String> contents) {
        if (chunkIds == null || vectors == null) {
            return;
        }
        int size = Math.min(chunkIds.size(), vectors.size());
        for (int i = 0; i < size; i++) {
            Long chunkId = chunkIds.get(i);
            vectorMap.put(chunkId, vectors.get(i));
            if (fileId != null) {
                fileMap.put(chunkId, fileId);
            }
            if (categoryId != null) {
                categoryMap.put(chunkId, categoryId);
            }
            if (contents != null && i < contents.size()) {
                contentMap.put(chunkId, contents.get(i));
            }
        }
        log.debug("Batch insert vectors success, size={}", size);
    }

    public List<VectorSearchResult> search(float[] queryVector, int topk, Long categoryId) {
        if (queryVector == null || topk <= 0) {
            return List.of();
        }

        List<VectorSearchResult> results = new ArrayList<>();
        for (Map.Entry<Long, float[]> e : vectorMap.entrySet()) {
            Long chunkId = e.getKey();
            if (categoryId != null && !categoryId.equals(categoryMap.get(chunkId))) {
                continue;
            }
            double score = cosine(queryVector, e.getValue());
            results.add(VectorSearchResult.builder()
                    .chunkId(chunkId)
                    .score(score)
                    .content(contentMap.getOrDefault(chunkId, ""))
                    .build());
        }

        results.sort(Comparator.comparingDouble(VectorSearchResult::getScore).reversed());
        List<VectorSearchResult> top = results.stream().limit(topk).toList();
        for (int i = 0; i < top.size(); i++) {
            top.get(i).setRank(i + 1);
        }
        return top;
    }

    public void upsert(Long chunkId, float[] vector) {
        log.debug("Upsert vector, chunkId={}, dim={}", chunkId, vector == null ? 0 : vector.length);
        if (chunkId != null && vector != null) {
            vectorMap.put(chunkId, vector);
        }
    }

    public void deleteByFileId(Long fileId) {
        log.debug("Delete vectors by fileId={}", fileId);
        if (fileId == null) {
            return;
        }
        List<Long> toDelete = fileMap.entrySet().stream()
                .filter(e -> fileId.equals(e.getValue()))
                .map(Map.Entry::getKey)
                .toList();
        deleteByChunkIds(toDelete);
    }

    public void deleteByChunkIds(List<Long> chunkIds) {
        if (chunkIds == null || chunkIds.isEmpty()) {
            return;
        }
        for (Long id : chunkIds) {
            vectorMap.remove(id);
            fileMap.remove(id);
            categoryMap.remove(id);
            contentMap.remove(id);
        }
    }

    private double cosine(float[] a, float[] b) {
        if (a == null || b == null || a.length == 0 || b.length == 0 || a.length != b.length) {
            return 0d;
        }
        double dot = 0d;
        double na = 0d;
        double nb = 0d;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            na += a[i] * a[i];
            nb += b[i] * b[i];
        }
        if (na == 0 || nb == 0) {
            return 0d;
        }
        return dot / (Math.sqrt(na) * Math.sqrt(nb));
    }
}
