package com.beauty.knowledge.infrastructure.ai.python;

import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.client.WebClient;

import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.zip.CRC32;

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

    @Value("${beauty.ai.python.transcribe-base-url:}")
    private String transcribeBaseUrl;

    @Value("${beauty.ai.python.transcribe-timeout:180000}")
    private long transcribeTimeoutMs;

    @Value("${beauty.pipeline.embed-batch-size:32}")
    private int embedBatchSize;

    @Value("${beauty.ai.python.mock-embed-enabled:true}")
    private boolean mockEmbedEnabled;

    @Value("${beauty.ai.python.mock-embed-dim:384}")
    private int mockEmbedDim;

    private final AtomicLong lastEmbedWarnAt = new AtomicLong(0L);
    private final AtomicInteger suppressedEmbedWarn = new AtomicInteger(0);

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
            logEmbedFallback(ex);
            if (mockEmbedEnabled) {
                return mockEmbed(texts);
            }
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "Embedding service unavailable");
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
            return parseTextResponse(resp);
        } catch (Exception ex) {
            log.warn("python ocr failed: {}", ex.getMessage());
            return "";
        }
    }

    public String transcribe(byte[] mediaBytes, String mediaType) {
        String text = transcribeByJson(mediaBytes, mediaType);
        if (text != null && !text.isBlank()) {
            return text;
        }
        return transcribeByWhisperAsr(mediaBytes);
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

    private String transcribeByJson(byte[] mediaBytes, String mediaType) {
        try {
            Map<String, Object> req = new HashMap<>();
            req.put("audioBase64", Base64.getEncoder().encodeToString(mediaBytes));
            req.put("mediaType", mediaType == null ? "audio" : mediaType);
            String resp = transcribeClient().post()
                    .uri("/transcribe")
                    .bodyValue(req)
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(Duration.ofMillis(transcribeTimeoutMs))
                    .block();
            return parseTextResponse(resp);
        } catch (Exception ex) {
            log.warn("python /transcribe failed: {}", ex.getMessage());
            return "";
        }
    }

    private String transcribeByWhisperAsr(byte[] mediaBytes) {
        try {
            ByteArrayResource resource = new ByteArrayResource(mediaBytes) {
                @Override
                public String getFilename() {
                    return "input.wav";
                }
            };
            MultiValueMap<String, Object> form = new LinkedMultiValueMap<>();
            form.add("audio_file", resource);
            form.add("task", "transcribe");
            form.add("encode", "true");
            form.add("output", "json");

            String resp = transcribeClient().post()
                    .uri("/asr")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .bodyValue(form)
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(Duration.ofMillis(transcribeTimeoutMs))
                    .block();
            return parseTextResponse(resp);
        } catch (Exception ex) {
            log.warn("python /asr failed: {}", ex.getMessage());
            return "";
        }
    }

    private String parseTextResponse(String resp) throws Exception {
        if (resp == null || resp.isBlank()) {
            return "";
        }
        JsonNode node = objectMapper.readTree(resp);
        if (node.has("text")) {
            return node.path("text").asText("");
        }
        if (node.has("result")) {
            return node.path("result").asText("");
        }
        return "";
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
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "Embedding empty response");
        }
        JsonNode root = objectMapper.readTree(resp);
        JsonNode vectors = root.path("vectors");
        if (!vectors.isArray()) {
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "Embedding response format error");
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

    /**
     * Deterministic local embedding fallback.
     * Ensures vector retrieval remains available when external python embedding service is down.
     */
    private List<float[]> mockEmbed(List<String> texts) {
        int dim = Math.max(64, mockEmbedDim);
        List<float[]> vectors = new ArrayList<>(texts.size());
        for (String text : texts) {
            vectors.add(mockVector(text, dim));
        }
        return vectors;
    }

    private float[] mockVector(String text, int dim) {
        float[] vec = new float[dim];
        String safe = text == null ? "" : text;
        String[] tokens = safe.toLowerCase().split("\\s+|[，。！？；：,.!?;:\\-_/()\\[\\]{}\"'“”‘’]+");
        for (String token : tokens) {
            if (token == null || token.isBlank()) {
                continue;
            }
            CRC32 crc = new CRC32();
            crc.update(token.getBytes(StandardCharsets.UTF_8));
            long v = crc.getValue();
            int i1 = (int) (v % dim);
            int i2 = (int) ((v / 97) % dim);
            vec[i1] += 1.0f;
            vec[i2] += 0.5f;
        }
        // L2 normalize
        double norm = 0d;
        for (float x : vec) {
            norm += x * x;
        }
        if (norm > 0d) {
            double inv = 1d / Math.sqrt(norm);
            for (int i = 0; i < vec.length; i++) {
                vec[i] = (float) (vec[i] * inv);
            }
        }
        return vec;
    }

    private void logEmbedFallback(Exception ex) {
        long now = System.currentTimeMillis();
        long last = lastEmbedWarnAt.get();
        // Avoid startup log storms when warmup processes many chunks.
        if (now - last >= 60_000 && lastEmbedWarnAt.compareAndSet(last, now)) {
            int suppressed = suppressedEmbedWarn.getAndSet(0);
            if (suppressed > 0) {
                log.warn("python /embed unavailable, reason={}, fallback={}, suppressed={} similar logs in last 60s",
                        ex.getMessage(), mockEmbedEnabled ? "mock-vector" : "disabled", suppressed);
            } else {
                log.warn("python /embed unavailable, reason={}, fallback={}",
                        ex.getMessage(), mockEmbedEnabled ? "mock-vector" : "disabled");
            }
            return;
        }
        suppressedEmbedWarn.incrementAndGet();
    }

    private WebClient client() {
        return webClientBuilder.baseUrl(baseUrl).build();
    }

    private WebClient transcribeClient() {
        String url = (transcribeBaseUrl == null || transcribeBaseUrl.isBlank()) ? baseUrl : transcribeBaseUrl;
        return webClientBuilder.baseUrl(url).build();
    }
}
