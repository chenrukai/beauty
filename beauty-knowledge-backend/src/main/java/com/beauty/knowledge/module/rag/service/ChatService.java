package com.beauty.knowledge.module.rag.service;

import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.infrastructure.ai.llm.LLMProvider;
import com.beauty.knowledge.module.rag.domain.dto.ChatMessage;
import com.beauty.knowledge.module.rag.domain.dto.ChatRequest;
import com.beauty.knowledge.module.rag.domain.dto.ChatStreamChunk;
import com.beauty.knowledge.module.rag.domain.dto.ChunkResult;
import com.beauty.knowledge.module.rag.domain.entity.ChatMessageEntity;
import com.beauty.knowledge.module.rag.domain.entity.ChatSession;
import com.beauty.knowledge.module.rag.domain.enums.IntentType;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

@Service
@RequiredArgsConstructor
public class ChatService {

    private final IntentService intentService;
    private final ContextService contextService;
    private final HybridSearchService hybridSearchService;
    private final PromptService promptService;
    private final ChatSessionService chatSessionService;
    private final ChatRecordService chatRecordService;
    private final ObjectProvider<LLMProvider> llmProviderObjectProvider;

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
                    chatRecordService.saveAssistantAnswer(sessionId, finalAnswer, sources);
                    contextService.appendRound(userId, request.getQuestion(), finalAnswer);
                    return ChatStreamChunk.builder()
                            .type("done")
                            .content(finalAnswer)
                            .sessionId(sessionId)
                            .sources(sources)
                            .build();
                })
                .subscribeOn(Schedulers.boundedElastic())
                .flux();
        return tokenFlux.concatWith(doneFlux);
    }

    public List<ChatSession> listSessions(Long userId) {
        return chatSessionService.listByUser(userId);
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
}
