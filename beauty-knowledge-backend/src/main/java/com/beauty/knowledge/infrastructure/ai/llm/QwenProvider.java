package com.beauty.knowledge.infrastructure.ai.llm;

import com.beauty.knowledge.infrastructure.ai.llm.dto.ChatMessage;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
@ConditionalOnProperty(name = "beauty.llm.provider", havingValue = "qwen")
public class QwenProvider implements LLMProvider {

    private final WebClient.Builder webClientBuilder;
    private final ObjectMapper objectMapper;

    @Value("${beauty.llm.qwen.base-url:https://dashscope.aliyuncs.com/compatible-mode/v1}")
    private String baseUrl;

    @Value("${beauty.llm.qwen.api-key:}")
    private String apiKey;

    @Value("${beauty.llm.qwen.model:qwen-plus}")
    private String model;

    @Value("${beauty.llm.qwen.timeout-ms:30000}")
    private long timeoutMs;

    @Override
    public Flux<String> streamChat(String systemPrompt, String userMessage, List<ChatMessage> history) {
        Map<String, Object> body = buildRequest(systemPrompt, userMessage, history, true);
        return client().post()
                .uri("/chat/completions")
                .contentType(MediaType.APPLICATION_JSON)
                .header("Authorization", "Bearer " + apiKey)
                .bodyValue(body)
                .retrieve()
                .bodyToFlux(String.class)
                .map(this::extractStreamContent)
                .filter(s -> s != null && !s.isEmpty())
                .onErrorResume(ex -> {
                    log.warn("qwen streamChat failed: {}", ex.getMessage());
                    return Flux.empty();
                });
    }

    @Override
    public String chat(String systemPrompt, String userMessage) {
        log.warn("Synchronous chat() is deprecated. Use chatAsync() to avoid blocking.");
        return "";
    }

    @Override
    public Mono<String> chatAsync(String systemPrompt, String userMessage) {
        Map<String, Object> body = buildRequest(systemPrompt, userMessage, List.of(), false);
        return client().post()
                .uri("/chat/completions")
                .contentType(MediaType.APPLICATION_JSON)
                .header("Authorization", "Bearer " + apiKey)
                .bodyValue(body)
                .retrieve()
                .bodyToMono(String.class)
                .timeout(Duration.ofMillis(timeoutMs))
                .map(this::extractChatContent)
                .onErrorResume(ex -> {
            log.warn("qwen chat failed: {}", ex.getMessage());
                    return Mono.just("");
                });
    }

    @Override
    public boolean isAvailable() {
        if (apiKey == null || apiKey.isBlank()) {
            return false;
        }
        try {
            String resp = client().get()
                    .uri("/models")
                    .header("Authorization", "Bearer " + apiKey)
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(Duration.ofSeconds(3))
                    .block();
            return resp != null;
        } catch (Exception ex) {
            return false;
        }
    }

    private WebClient client() {
        return webClientBuilder.baseUrl(baseUrl).build();
    }

    private Map<String, Object> buildRequest(String systemPrompt, String userMessage, List<ChatMessage> history, boolean stream) {
        List<Map<String, String>> messages = new ArrayList<>();
        if (systemPrompt != null && !systemPrompt.isBlank()) {
            messages.add(Map.of("role", "system", "content", systemPrompt));
        }
        for (ChatMessage h : history) {
            if (h != null && h.getRole() != null && h.getContent() != null) {
                messages.add(Map.of("role", h.getRole(), "content", h.getContent()));
            }
        }
        messages.add(Map.of("role", "user", "content", userMessage == null ? "" : userMessage));

        Map<String, Object> body = new HashMap<>();
        body.put("model", model);
        body.put("messages", messages);
        body.put("stream", stream);
        return body;
    }

    private String extractStreamContent(String raw) {
        if (raw == null || raw.isBlank()) {
            return "";
        }
        String line = raw.startsWith("data:") ? raw.substring(5).trim() : raw;
        if ("[DONE]".equals(line)) {
            return "";
        }
        try {
            JsonNode node = objectMapper.readTree(line);
            return node.path("choices").path(0).path("delta").path("content").asText("");
        } catch (Exception ignored) {
            return "";
        }
    }

    private String extractChatContent(String raw) {
        if (raw == null || raw.isBlank()) {
            return "";
        }
        try {
            JsonNode node = objectMapper.readTree(raw);
            return node.path("choices").path(0).path("message").path("content").asText("");
        } catch (Exception ignored) {
            return "";
        }
    }
}
