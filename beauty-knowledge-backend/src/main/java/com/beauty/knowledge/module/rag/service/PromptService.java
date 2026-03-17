package com.beauty.knowledge.module.rag.service;

import com.beauty.knowledge.module.rag.domain.dto.ChunkResult;
import com.beauty.knowledge.module.rag.domain.enums.IntentType;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PromptService {

    public String buildSystemPrompt(IntentType intent, List<ChunkResult> sources) {
        String rolePrompt = switch (intent) {
            case INGREDIENT -> "You are a skincare ingredient assistant.";
            case EFFECT -> "You are a skincare effect assistant.";
            case PRODUCT -> "You are a product recommendation assistant.";
            default -> "You are a beauty knowledge assistant.";
        };

        String answerRule = """
                Answer in simplified Chinese.
                Keep the answer short and practical.
                Use this format only:
                1. Conclusion: one sentence
                2. Reasons: up to 3 bullet points
                3. Caution: one short sentence
                Avoid long paragraphs, repetition, and markdown tables.
                """;

        if (sources == null || sources.isEmpty()) {
            return rolePrompt + "\n" + answerRule
                    + "\nNo KB chunks are available. Answer from general skincare knowledge only.";
        }

        StringBuilder sourcePrompt = new StringBuilder();
        sourcePrompt.append("\nUse the following KB chunks first. Do not make up facts.\n");
        for (int i = 0; i < sources.size(); i++) {
            ChunkResult source = sources.get(i);
            sourcePrompt.append("[")
                    .append(i + 1)
                    .append("] ")
                    .append(source.getContent())
                    .append("\n");
        }
        return rolePrompt + "\n" + answerRule + sourcePrompt;
    }
}
