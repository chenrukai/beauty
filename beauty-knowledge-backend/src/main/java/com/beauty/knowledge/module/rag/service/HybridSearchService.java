package com.beauty.knowledge.module.rag.service;

import com.beauty.knowledge.infrastructure.ai.python.PythonAIClient;
import com.beauty.knowledge.infrastructure.vector.MilvusVectorStore;
import com.beauty.knowledge.infrastructure.vector.VectorSearchResult;
import com.beauty.knowledge.module.rag.domain.dto.ChunkResult;
import com.beauty.knowledge.module.rag.mapper.KbChunkSearchMapper;
import lombok.extern.slf4j.Slf4j;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@Slf4j
@RequiredArgsConstructor
public class HybridSearchService {

    private final KbChunkSearchMapper kbChunkSearchMapper;
    private final PythonAIClient pythonAIClient;
    private final MilvusVectorStore milvusVectorStore;

    @Value("${beauty.rag.bm25-topk:5}")
    private int bm25Topk;
    @Value("${beauty.rag.vector-topk:5}")
    private int vectorTopk;
    @Value("${beauty.rag.rrf-k:60}")
    private int rrfK;
    @Value("${beauty.rag.rerank-top:5}")
    private int rerankTop;

    public List<ChunkResult> search(String question, Long categoryId) {
        List<ChunkResult> bm25;
        try {
            bm25 = kbChunkSearchMapper.fullTextSearch(question, bm25Topk);
        } catch (Exception e) {
            // Allow chat to continue even when kb_chunk table/index is not ready.
            log.warn("RAG bm25 search unavailable, fallback to empty sources: {}", e.getMessage());
            bm25 = List.of();
        }

        List<float[]> embedded;
        try {
            embedded = pythonAIClient.embed(List.of(question));
        } catch (Exception e) {
            log.warn("RAG embedding unavailable, fallback to bm25-only: {}", e.getMessage());
            embedded = List.of();
        }
        float[] queryVector = embedded.isEmpty() ? null : embedded.get(0);
        List<VectorSearchResult> vector;
        try {
            vector = queryVector == null
                    ? List.of()
                    : milvusVectorStore.search(queryVector, vectorTopk, categoryId);
        } catch (Exception e) {
            log.warn("RAG vector search unavailable, fallback to empty vectors: {}", e.getMessage());
            vector = List.of();
        }

        List<ChunkResult> merged = rrfMerge(bm25, vector);
        return rerank(question, merged).stream().limit(rerankTop).toList();
    }

    private List<ChunkResult> rrfMerge(List<ChunkResult> bm25, List<VectorSearchResult> vector) {
        Map<Long, Double> scoreMap = new HashMap<>();
        Map<Long, ChunkResult> itemMap = new HashMap<>();

        for (int i = 0; i < bm25.size(); i++) {
            ChunkResult c = bm25.get(i);
            itemMap.put(c.getChunkId(), c);
            scoreMap.merge(c.getChunkId(), 1.0 / (rrfK + i + 1), Double::sum);
        }

        List<Long> vectorIds = vector.stream().map(VectorSearchResult::getChunkId).toList();
        if (!vectorIds.isEmpty()) {
            List<ChunkResult> vectorChunkRows;
            try {
                vectorChunkRows = kbChunkSearchMapper.selectByIds(vectorIds);
            } catch (Exception e) {
                log.warn("RAG selectByIds unavailable, skip vector id mapping: {}", e.getMessage());
                vectorChunkRows = List.of();
            }
            Map<Long, ChunkResult> vectorChunkMap = vectorChunkRows.stream()
                    .collect(Collectors.toMap(ChunkResult::getChunkId, r -> r));
            for (int i = 0; i < vector.size(); i++) {
                VectorSearchResult v = vector.get(i);
                ChunkResult row = vectorChunkMap.get(v.getChunkId());
                if (row != null) {
                    itemMap.putIfAbsent(v.getChunkId(), row);
                }
                scoreMap.merge(v.getChunkId(), 1.0 / (rrfK + i + 1), Double::sum);
            }
        }

        List<ChunkResult> merged = new ArrayList<>();
        for (Map.Entry<Long, Double> e : scoreMap.entrySet()) {
            ChunkResult c = itemMap.get(e.getKey());
            if (c != null) {
                c.setScore(e.getValue());
                merged.add(c);
            }
        }
        merged.sort(Comparator.comparingDouble(ChunkResult::getScore).reversed());
        for (int i = 0; i < merged.size(); i++) {
            merged.get(i).setRank(i + 1);
        }
        return merged;
    }

    private List<ChunkResult> rerank(String question, List<ChunkResult> merged) {
        if (merged == null || merged.isEmpty()) {
            return List.of();
        }
        Set<Character> qChars = compactChars(question);
        for (ChunkResult item : merged) {
            String content = item == null ? "" : String.valueOf(item.getContent());
            Set<Character> cChars = compactChars(content);
            double overlap = overlapScore(qChars, cChars);
            double base = item == null ? 0D : item.getScore();
            double finalScore = base * 0.7D + overlap * 0.3D;
            if (item != null) {
                item.setScore(finalScore);
            }
        }
        merged.sort(Comparator.comparingDouble(ChunkResult::getScore).reversed());
        for (int i = 0; i < merged.size(); i++) {
            merged.get(i).setRank(i + 1);
        }
        return merged;
    }

    private Set<Character> compactChars(String text) {
        Set<Character> out = new LinkedHashSet<>();
        if (text == null || text.isBlank()) {
            return out;
        }
        for (char ch : text.toCharArray()) {
            if (Character.isWhitespace(ch)) {
                continue;
            }
            if (isPunctuation(ch)) {
                continue;
            }
            out.add(Character.toLowerCase(ch));
        }
        return out;
    }

    private boolean isPunctuation(char c) {
        int type = Character.getType(c);
        return type == Character.CONNECTOR_PUNCTUATION
                || type == Character.DASH_PUNCTUATION
                || type == Character.START_PUNCTUATION
                || type == Character.END_PUNCTUATION
                || type == Character.OTHER_PUNCTUATION
                || type == Character.INITIAL_QUOTE_PUNCTUATION
                || type == Character.FINAL_QUOTE_PUNCTUATION;
    }

    private double overlapScore(Set<Character> q, Set<Character> c) {
        if (q == null || c == null || q.isEmpty() || c.isEmpty()) {
            return 0D;
        }
        int hit = 0;
        for (Character qc : q) {
            if (c.contains(qc)) {
                hit++;
            }
        }
        return (double) hit / (double) q.size();
    }
}
