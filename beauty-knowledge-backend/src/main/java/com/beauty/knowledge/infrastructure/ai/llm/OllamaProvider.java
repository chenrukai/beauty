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
@ConditionalOnProperty(name = "beauty.llm.provider", havingValue = "ollama")
public class OllamaProvider implements LLMProvider {

    private final WebClient.Builder webClientBuilder;
    private final ObjectMapper objectMapper;

    @Value("${beauty.llm.ollama.base-url:http://localhost:11434}")
    private String baseUrl;

    @Value("${beauty.llm.ollama.model:qwen2.5:7b}")
    private String model;

    @Value("${beauty.llm.ollama.timeout-ms:30000}")
    private long timeoutMs;

    @Value("${beauty.llm.ollama.num-predict:220}")
    private int numPredict;

    @Value("${beauty.llm.ollama.temperature:0.2}")
    private double temperature;

    @Value("${beauty.llm.ollama.num-ctx:2048}")
    private int numCtx;

    @Value("${beauty.llm.ollama.think:false}")
    private boolean think;

    @Override
    public Flux<String> streamChat(String systemPrompt, String userMessage, List<ChatMessage> history) {
        Map<String, Object> body = buildRequest(systemPrompt, userMessage, history, true);
        return client().post()
                .uri("/api/chat")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(body)
                .retrieve()
                .bodyToFlux(String.class)
                .flatMapIterable(this::extractContents)
                .filter(s -> s != null && !s.isEmpty())
                .timeout(Duration.ofMillis(timeoutMs))
                .onErrorResume(ex -> {
                    log.warn("ollama streamChat failed: {}", ex.getMessage());
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
                .uri("/api/chat")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(body)
                .retrieve()
                .bodyToMono(String.class)
                .timeout(Duration.ofMillis(timeoutMs))
                .map(this::extractContent)
                .onErrorResume(ex -> {
            log.warn("ollama chat failed: {}", ex.getMessage());
                    return Mono.just("");
                });
    }

    @Override
    public boolean isAvailable() {
        try {
            String resp = client().get()
                    .uri("/api/tags")
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
        body.put("think", think);
        body.put("options", Map.of(
                "num_predict", numPredict,
                "temperature", temperature,
                "num_ctx", numCtx
        ));
        return body;
    }

    private String extractContent(String raw) {
        if (raw == null || raw.isBlank()) {
            return "";
        }
        try {
            JsonNode node = objectMapper.readTree(raw);
            JsonNode msg = node.path("message").path("content");
            if (!msg.isMissingNode()) {
                return msg.asText("");
            }
        } catch (Exception ignored) {
            // noop
        }
        return "";
    }

    private List<String> extractContents(String raw) {
        if (raw == null || raw.isBlank()) {
            return List.of();
        }
        List<String> out = new ArrayList<>();
        String[] lines = raw.split("\\r?\\n");
        for (String line : lines) {
            String payload = line == null ? "" : line.trim();
            if (payload.isEmpty()) {
                continue;
            }
            if (payload.startsWith("data:")) {
                payload = payload.substring(5).trim();
            }
            if ("[DONE]".equals(payload)) {
                continue;
            }
            try {
                JsonNode node = objectMapper.readTree(payload);
                if (node.has("error")) {
                    log.warn("ollama stream error payload: {}", node.path("error").asText(""));
                    continue;
                }
                String content = node.path("message").path("content").asText("");
                if (content.isBlank()) {
                    content = node.path("response").asText("");
                }
                if (!content.isBlank()) {
                    out.add(content);
                }
            } catch (Exception ignored) {
                // ignore malformed line and continue parsing next segment
            }
        }
        if (!out.isEmpty()) {
            return out;
        }
        String single = extractContent(raw);
        return single.isBlank() ? List.of() : List.of(single);
    }
}
