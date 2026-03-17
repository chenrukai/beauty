package com.beauty.knowledge.infrastructure.ai.python;

import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class PythonAIClient {

    private final WebClient.Builder webClientBuilder;
    private final ObjectMapper objectMapper;

    @Value("${beauty.ai.python.base-url}")
    private String baseUrl;

    @Value("${beauty.ai.python.timeout:30000}")
    private long timeoutMs;

    @Value("${beauty.pipeline.embed-batch-size:32}")
    private int embedBatchSize;

    public List<float[]> embed(List<String> texts) {
        if (texts == null || texts.isEmpty()) {
            return List.of();
        }
        try {
            List<float[]> all = new ArrayList<>();
            for (int i = 0; i < texts.size(); i += embedBatchSize) {
                int end = Math.min(i + embedBatchSize, texts.size());
                List<String> batch = texts.subList(i, end);
                all.addAll(embedBatch(batch));
            }
            return all;
        } catch (BusinessException ex) {
            throw ex;
        } catch (Exception ex) {
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "Embedding服务不可用");
        }
    }

    public String ocr(byte[] imageBytes) {
        try {
            Map<String, Object> req = new HashMap<>();
            req.put("imageBase64", Base64.getEncoder().encodeToString(imageBytes));
            String resp = client().post()
                    .uri("/ocr")
                    .bodyValue(req)
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(Duration.ofMillis(timeoutMs))
                    .block();
            if (resp == null || resp.isBlank()) {
                return "";
            }
            JsonNode node = objectMapper.readTree(resp);
            if (node.has("text")) {
                return node.path("text").asText("");
            }
            return "";
        } catch (Exception ex) {
            log.warn("python ocr failed: {}", ex.getMessage());
            return "";
        }
    }

    public boolean healthCheck() {
        try {
            String resp = client().get()
                    .uri("/health")
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(Duration.ofSeconds(3))
                    .block();
            return resp != null && !resp.isBlank();
        } catch (Exception ex) {
            return false;
        }
    }

    private List<float[]> embedBatch(List<String> batch) throws Exception {
        Map<String, Object> req = new HashMap<>();
        req.put("texts", batch);
        String resp = client().post()
                .uri("/embed")
                .bodyValue(req)
                .retrieve()
                .bodyToMono(String.class)
                .timeout(Duration.ofMillis(timeoutMs))
                .block();
        if (resp == null || resp.isBlank()) {
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "Embedding返回为空");
        }
        JsonNode root = objectMapper.readTree(resp);
        JsonNode vectors = root.path("vectors");
        if (!vectors.isArray()) {
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "Embedding返回格式错误");
        }
        List<float[]> result = new ArrayList<>();
        for (JsonNode v : vectors) {
            if (!v.isArray()) {
                continue;
            }
            float[] arr = new float[v.size()];
            for (int i = 0; i < v.size(); i++) {
                arr[i] = (float) v.get(i).asDouble();
            }
            result.add(arr);
        }
        return result;
    }

    private WebClient client() {
        return webClientBuilder.baseUrl(baseUrl).build();
    }
}
