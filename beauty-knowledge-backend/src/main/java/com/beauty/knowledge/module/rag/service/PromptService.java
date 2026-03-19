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
                请使用简体中文回答。
                回答要完整，不要为了简短而省略关键步骤或要点。
                在用户未明确要求“简短”时，优先给出较详细版本。
                优先使用以下结构：
                1. 结论
                2. 原理/原因
                3. 实操建议（分步骤）
                4. 注意事项
                当知识库片段包含分点或分步骤时，要尽量覆盖完整逻辑，避免只回答一半。
                当引用片段本身可能被截断时，不要原样停在半句，需基于可用信息补全成完整可执行建议。
                不要编造事实；如信息不足，明确说明“根据当前知识库仅能回答到此”。
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
