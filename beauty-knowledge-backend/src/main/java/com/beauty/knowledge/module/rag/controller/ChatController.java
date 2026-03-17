package com.beauty.knowledge.module.rag.controller;

import com.beauty.knowledge.common.result.Result;
import com.beauty.knowledge.common.util.SecurityUtil;
import com.beauty.knowledge.module.rag.domain.dto.ChatRequest;
import com.beauty.knowledge.module.rag.domain.dto.ChatStreamChunk;
import com.beauty.knowledge.module.rag.domain.entity.ChatMessageEntity;
import com.beauty.knowledge.module.rag.domain.entity.ChatSession;
import com.beauty.knowledge.module.rag.service.ChatService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.ModelAttribute;
import reactor.core.publisher.Flux;

import java.util.List;

@Tag(name = "问答管理")
@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    @Operation(summary = "流式问答（SSE）")
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<ChatStreamChunk>> stream(@Valid @ModelAttribute ChatRequest request) {
        Long userId = SecurityUtil.getCurrentUserId();
        return chatService.streamChat(userId, request)
                .map(data -> ServerSentEvent.<ChatStreamChunk>builder()
                        .event(data.getType())
                        .data(data)
                        .build());
    }

    @Operation(summary = "获取会话列表")
    @GetMapping("/session")
    public Result<List<ChatSession>> sessions() {
        Long userId = SecurityUtil.getCurrentUserId();
        return Result.success(chatService.listSessions(userId));
    }

    @Operation(summary = "获取会话消息")
    @GetMapping("/session/{sessionId}/messages")
    public Result<List<ChatMessageEntity>> messages(@PathVariable Long sessionId) {
        Long userId = SecurityUtil.getCurrentUserId();
        return Result.success(chatService.listMessages(userId, sessionId));
    }

    @Operation(summary = "删除会话")
    @DeleteMapping("/session/{sessionId}")
    public Result<Void> delete(@PathVariable Long sessionId) {
        Long userId = SecurityUtil.getCurrentUserId();
        chatService.deleteSession(userId, sessionId);
        return Result.success();
    }
}
