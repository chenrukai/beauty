package com.beauty.knowledge.infrastructure.ai.llm;

import com.beauty.knowledge.infrastructure.ai.llm.dto.ChatMessage;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.List;

public interface LLMProvider {

    Flux<String> streamChat(String systemPrompt, String userMessage, List<ChatMessage> history);

    String chat(String systemPrompt, String userMessage);

    default Mono<String> chatAsync(String systemPrompt, String userMessage) {
        return Mono.fromCallable(() -> chat(systemPrompt, userMessage));
    }

    boolean isAvailable();
}
