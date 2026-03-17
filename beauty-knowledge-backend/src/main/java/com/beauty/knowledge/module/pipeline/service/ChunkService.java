package com.beauty.knowledge.module.pipeline.service;

import com.beauty.knowledge.module.pipeline.domain.dto.ChunkDTO;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class ChunkService {

    @Value("${beauty.pipeline.chunk-size:400}")
    private int chunkSize;

    @Value("${beauty.pipeline.chunk-overlap:80}")
    private int chunkOverlap;

    public List<ChunkDTO> split(String text) {
        return split(text, chunkSize, chunkOverlap);
    }

    public List<ChunkDTO> split(String text, int size, int overlap) {
        if (text == null || text.isBlank()) {
            return List.of();
        }
        int step = Math.max(1, size - overlap);
        List<ChunkDTO> chunks = new ArrayList<>();
        int index = 0;
        int chunkIndex = 0;
        while (index < text.length()) {
            int end = Math.min(index + size, text.length());
            String content = text.substring(index, end).trim();
            if (!content.isEmpty()) {
                chunks.add(new ChunkDTO(chunkIndex++, content, 1, content.length()));
            }
            if (end >= text.length()) {
                break;
            }
            index += step;
        }
        return chunks;
    }
}
