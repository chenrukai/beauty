package com.beauty.knowledge.module.rag.service;

import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.infrastructure.ai.llm.LLMProvider;
import com.beauty.knowledge.infrastructure.ai.python.PythonAIClient;
import com.beauty.knowledge.module.rag.domain.dto.ChatMessage;
import com.beauty.knowledge.module.rag.domain.dto.ChatRequest;
import com.beauty.knowledge.module.rag.domain.dto.ChatStreamChunk;
import com.beauty.knowledge.module.rag.domain.dto.ChunkResult;
import com.beauty.knowledge.module.rag.domain.entity.ChatMessageEntity;
import com.beauty.knowledge.module.rag.domain.entity.ChatSession;
import com.beauty.knowledge.module.rag.domain.enums.IntentType;
import com.beauty.knowledge.module.rag.mapper.KbChunkSearchMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.io.ByteArrayInputStream;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.tika.Tika;

@Service
@RequiredArgsConstructor
public class ChatService {

    private final IntentService intentService;
    private final ContextService contextService;
    private final HybridSearchService hybridSearchService;
    private final PromptService promptService;
    private final ChatSessionService chatSessionService;
    private final ChatRecordService chatRecordService;
    private final KbChunkSearchMapper kbChunkSearchMapper;
    private final ObjectProvider<LLMProvider> llmProviderObjectProvider;
    private final PythonAIClient pythonAIClient;
    private final Tika tika = new Tika();

    @Value("${beauty.rag.display-source-top:4}")
    private int displaySourceTop;
    @Value("${beauty.rag.display-source-context-radius:1}")
    private int displaySourceContextRadius;
    @Value("${beauty.rag.display-source-context-limit:3}")
    private int displaySourceContextLimit;
    @Value("${beauty.rag.upload-summary-max-chars:12000}")
    private int uploadSummaryMaxChars;
    @Value("${beauty.rag.upload-ask-max-chars:24000}")
    private int uploadAskMaxChars;

    private final Map<Long, UploadContext> uploadContextBySession = new ConcurrentHashMap<>();

    public Flux<ChatStreamChunk> streamChat(Long userId, ChatRequest request) {
        LLMProvider llmProvider = llmProviderObjectProvider.getIfAvailable();
        if (llmProvider == null) {
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "未找到可用的LLMProvider");
        }

        Long sessionId = chatSessionService.getOrCreate(userId, request.getSessionId(), request.getQuestion());
        chatRecordService.saveUserQuestion(sessionId, request.getQuestion());

        IntentType intent = intentService.detect(request.getQuestion());
        List<ChunkResult> sources = hybridSearchService.search(request.getQuestion(), request.getCategoryId());
        String systemPrompt = promptService.buildSystemPrompt(intent, sources);
        List<com.beauty.knowledge.infrastructure.ai.llm.dto.ChatMessage> history = contextService.getRecentHistory(userId).stream()
                .map(h -> com.beauty.knowledge.infrastructure.ai.llm.dto.ChatMessage.builder()
                        .role(h.getRole())
                        .content(h.getContent())
                        .build())
                .toList();

        AtomicReference<StringBuilder> answerRef = new AtomicReference<>(new StringBuilder());
        Flux<ChatStreamChunk> tokenFlux = llmProvider.streamChat(systemPrompt, request.getQuestion(), history)
                .map(token -> {
                    answerRef.get().append(token);
                    return ChatStreamChunk.builder()
                            .type("token")
                            .content(token)
                            .sessionId(sessionId)
                            .build();
                });

        Flux<ChatStreamChunk> doneFlux = Mono.defer(() -> {
                    String current = answerRef.get().toString();
                    if (current != null && !current.isBlank()) {
                        return Mono.just(current);
                    }
                    // Stream may fail on some local models; fallback once to non-stream chat.
                    return llmProvider.chatAsync(systemPrompt, request.getQuestion())
                            .defaultIfEmpty("");
                })
                .map(answer -> {
                    String finalAnswer = (answer == null || answer.isBlank())
                            ? "AI service is temporarily unavailable. Please check Ollama/model configuration and try again."
                            : answer;
                    List<ChunkResult> displaySources = buildDisplaySources(sources);
                    chatRecordService.saveAssistantAnswer(sessionId, finalAnswer, displaySources);
                    contextService.appendRound(userId, request.getQuestion(), finalAnswer);
                    return ChatStreamChunk.builder()
                            .type("done")
                            .content(finalAnswer)
                            .sessionId(sessionId)
                            .sources(displaySources)
                            .build();
                })
                .subscribeOn(Schedulers.boundedElastic())
                .flux();
        return tokenFlux.concatWith(doneFlux);
    }

    public List<ChatSession> listSessions(Long userId) {
        return chatSessionService.listByUser(userId);
    }

    public ChatSession createSession(Long userId) {
        return chatSessionService.createEmpty(userId);
    }

    public List<ChatMessageEntity> listMessages(Long userId, Long sessionId) {
        List<ChatSession> sessions = chatSessionService.listByUser(userId);
        boolean owned = sessions.stream().anyMatch(s -> s.getId().equals(sessionId));
        if (!owned) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "会话不存在");
        }
        return chatRecordService.listBySession(sessionId);
    }

    public void deleteSession(Long userId, Long sessionId) {
        chatSessionService.delete(userId, sessionId);
    }

    public UploadSummaryResult summarizeUpload(Long userId, MultipartFile file, String instruction, Long sessionId) {
        if (file == null || file.isEmpty()) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "上传文件不能为空");
        }
        LLMProvider llmProvider = llmProviderObjectProvider.getIfAvailable();
        if (llmProvider == null) {
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "未找到可用的LLMProvider");
        }

        String extractedText = extractUploadText(file);
        if (!StringUtils.hasText(extractedText)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "文件内容为空或无法解析");
        }
        String clipped = extractedText.length() > uploadSummaryMaxChars
                ? extractedText.substring(0, uploadSummaryMaxChars)
                : extractedText;

        String finalInstruction = StringUtils.hasText(instruction)
                ? instruction.trim()
                : "请总结这个文件内容";
        Long sid = chatSessionService.getOrCreate(userId, sessionId, finalInstruction);
        uploadContextBySession.put(sid, new UploadContext(
                safeFileName(file.getOriginalFilename()),
                extractedText
        ));
        String userQuestion = finalInstruction + "（附件：" + safeFileName(file.getOriginalFilename()) + "）";
        chatRecordService.saveUserQuestion(sid, userQuestion);

        String systemPrompt = """
                你是文档总结助手。请严格基于用户上传文件内容回答。
                输出必须是纯文本，不要使用 Markdown 符号（如 #、*、-、数字列表前缀）。
                结构要求：
                结论：
                关键要点：
                行动建议：
                若文件信息不足，明确指出不足，不要编造。
                """;
        String userPrompt = finalInstruction + "\n\n【文件内容】\n" + clipped;
        String answer = llmProvider.chatAsync(systemPrompt, userPrompt).block();
        String finalAnswer = StringUtils.hasText(answer)
                ? toPlainText(answer)
                : "AI service is temporarily unavailable. Please check Ollama/model configuration and try again.";
        chatRecordService.saveAssistantAnswer(sid, finalAnswer, List.of());
        contextService.appendRound(userId, userQuestion, finalAnswer);
        return new UploadSummaryResult(sid, finalAnswer);
    }

    public UploadAskResult askByUploadedDocument(Long userId, Long sessionId, String question) {
        if (sessionId == null) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "sessionId不能为空");
        }
        if (!StringUtils.hasText(question)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "问题不能为空");
        }
        ensureSessionOwned(userId, sessionId);
        UploadContext ctx = uploadContextBySession.get(sessionId);
        if (ctx == null || !StringUtils.hasText(ctx.content())) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "当前会话没有上传文件上下文，请先上传文件");
        }

        LLMProvider llmProvider = llmProviderObjectProvider.getIfAvailable();
        if (llmProvider == null) {
            throw new BusinessException(ErrorCode.AI_SERVICE_UNAVAILABLE, "未找到可用的LLMProvider");
        }

        String clipped = ctx.content().length() > uploadAskMaxChars
                ? ctx.content().substring(0, uploadAskMaxChars)
                : ctx.content();
        String cleanQuestion = question.trim();
        String userQuestion = cleanQuestion + "（基于附件：" + ctx.fileName() + "）";
        chatRecordService.saveUserQuestion(sessionId, userQuestion);

        String systemPrompt = """
                你是文档问答助手。请仅依据用户上传的文件内容回答。
                不要编造文件里没有的信息。
                输出必须是纯文本，不要使用 Markdown 符号（如 #、*、-、数字列表前缀）。
                若文件中找不到答案，请明确回复“文件中未找到该信息”。
                """;
        String userPrompt = "用户问题：" + cleanQuestion + "\n\n【文件内容】\n" + clipped;
        String answer = llmProvider.chatAsync(systemPrompt, userPrompt).block();
        String finalAnswer = StringUtils.hasText(answer)
                ? toPlainText(answer)
                : "AI service is temporarily unavailable. Please check Ollama/model configuration and try again.";
        chatRecordService.saveAssistantAnswer(sessionId, finalAnswer, List.of());
        contextService.appendRound(userId, userQuestion, finalAnswer);
        return new UploadAskResult(sessionId, finalAnswer, ctx.fileName());
    }

    private String extractUploadText(MultipartFile file) {
        try {
            byte[] bytes = file.getBytes();
            if (isImage(file)) {
                try {
                    String ocr = pythonAIClient.ocr(bytes);
                    if (StringUtils.hasText(ocr)) {
                        return ocr.replace("\u0000", " ").trim();
                    }
                } catch (Exception ignore) {
                    // fallback to tika
                }
            }
            String parsed = tika.parseToString(new ByteArrayInputStream(bytes));
            return parsed == null ? "" : parsed.replace("\u0000", " ").trim();
        } catch (Exception e) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "文件解析失败");
        }
    }

    private boolean isImage(MultipartFile file) {
        String contentType = file.getContentType();
        if (contentType != null && contentType.toLowerCase().startsWith("image/")) {
            return true;
        }
        String name = safeFileName(file.getOriginalFilename()).toLowerCase();
        return name.endsWith(".png")
                || name.endsWith(".jpg")
                || name.endsWith(".jpeg")
                || name.endsWith(".webp")
                || name.endsWith(".bmp")
                || name.endsWith(".gif");
    }

    private String safeFileName(String name) {
        return StringUtils.hasText(name) ? name.trim() : "未命名文件";
    }

    private void ensureSessionOwned(Long userId, Long sessionId) {
        List<ChatSession> sessions = chatSessionService.listByUser(userId);
        boolean owned = sessions.stream().anyMatch(s -> s.getId().equals(sessionId));
        if (!owned) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "会话不存在");
        }
    }

    private String toPlainText(String raw) {
        if (!StringUtils.hasText(raw)) {
            return "";
        }
        return raw
                .replace("\r", "")
                .replaceAll("(?m)^#{1,6}\\s*", "")
                .replaceAll("\\*\\*(.*?)\\*\\*", "$1")
                .replaceAll("\\*(.*?)\\*", "$1")
                .replaceAll("(?m)^\\s*[-*+]\\s+", "")
                .replaceAll("(?m)^\\s*\\d+\\.\\s+", "")
                .replace("`", "")
                .replaceAll("\n{3,}", "\n\n")
                .trim();
    }

    public record UploadSummaryResult(Long sessionId, String summary) {}
    private record UploadContext(String fileName, String content) {}
    public record UploadAskResult(Long sessionId, String answer, String fileName) {}

    private List<ChunkResult> buildDisplaySources(List<ChunkResult> sources) {
        if (sources == null || sources.isEmpty()) {
            return List.of();
        }
        int top = Math.max(1, displaySourceTop);
        List<ChunkResult> sorted = new ArrayList<>(sources);
        sorted.sort(Comparator.comparingDouble(ChunkResult::getScore).reversed()
                .thenComparing(ChunkResult::getRank));

        Set<String> seen = new LinkedHashSet<>();
        List<ChunkResult> out = new ArrayList<>();
        for (ChunkResult s : sorted) {
            if (s == null) {
                continue;
            }
            String normalized = normalizeContent(s.getContent());
            String key = (s.getFileId() == null ? 0L : s.getFileId()) + "#"
                    + (s.getPageNo() == null ? 0 : s.getPageNo()) + "#"
                    + normalized;
            if (!seen.add(key)) {
                continue;
            }
            out.add(enrichSourceContentForDisplay(s));
            if (out.size() >= top) {
                break;
            }
        }
        return out;
    }

    private String normalizeContent(String content) {
        if (content == null) {
            return "";
        }
        String normalized = content.replaceAll("\\s+", "");
        int maxLen = 120;
        if (normalized.length() > maxLen) {
            return normalized.substring(0, maxLen);
        }
        return normalized;
    }

    private ChunkResult enrichSourceContentForDisplay(ChunkResult source) {
        if (source == null || source.getFileId() == null || source.getChunkIndex() == null) {
            return source;
        }
        try {
            int radius = Math.max(0, displaySourceContextRadius);
            int limit = Math.max(1, displaySourceContextLimit);
            int start = Math.max(0, source.getChunkIndex() - radius);
            int end = source.getChunkIndex() + radius;
            List<ChunkResult> context = kbChunkSearchMapper.selectContextByRange(source.getFileId(), start, end, limit);
            if (context == null || context.isEmpty()) {
                return source;
            }
            List<ChunkResult> samePage = context.stream()
                    .filter(c -> c != null && (source.getPageNo() == null || source.getPageNo().equals(c.getPageNo())))
                    .toList();
            List<ChunkResult> used = samePage.isEmpty() ? context : samePage;
            List<ChunkResult> ordered = used.stream()
                    .sorted(Comparator.comparing(c -> c.getChunkIndex() == null ? Integer.MAX_VALUE : c.getChunkIndex()))
                    .toList();

            List<String> uniqueParts = new ArrayList<>();
            List<String> seenNormalized = new ArrayList<>();
            for (ChunkResult c : ordered) {
                if (c == null || c.getContent() == null || c.getContent().isBlank()) {
                    continue;
                }
                String raw = c.getContent().trim();
                String normalized = normalizeContent(raw);
                if (normalized.isBlank()) {
                    continue;
                }
                boolean duplicated = false;
                for (String seen : seenNormalized) {
                    if (seen.equals(normalized) || seen.contains(normalized) || normalized.contains(seen)) {
                        duplicated = true;
                        break;
                    }
                }
                if (duplicated) {
                    continue;
                }
                seenNormalized.add(normalized);
                uniqueParts.add(raw);
            }

            String mergedContent = uniqueParts.isEmpty()
                    ? source.getContent()
                    : String.join("\n", uniqueParts);
            source.setContent(mergedContent);
            return source;
        } catch (Exception ex) {
            return source;
        }
    }
}
