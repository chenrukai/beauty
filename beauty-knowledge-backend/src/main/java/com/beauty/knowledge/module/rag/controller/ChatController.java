package com.beauty.knowledge.module.rag.controller;

import com.beauty.knowledge.common.result.Result;
import com.beauty.knowledge.common.util.SecurityUtil;
import com.beauty.knowledge.module.rag.domain.dto.ChatRequest;
import com.beauty.knowledge.module.rag.domain.dto.ChatStreamChunk;
import com.beauty.knowledge.module.rag.domain.dto.UploadAskRequest;
import com.beauty.knowledge.module.rag.domain.entity.ChatMessageEntity;
import com.beauty.knowledge.module.rag.domain.entity.ChatSession;
import com.beauty.knowledge.module.rag.service.ChatService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Flux;

import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.List;

@Tag(name = "问答管理")
@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    @Operation(summary = "流式问答（SSE，GET）")
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<ChatStreamChunk>> stream(@Valid @ModelAttribute ChatRequest request) {
        return streamInternal(request);
    }

    @Operation(summary = "流式问答（SSE，POST）")
    @PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<ChatStreamChunk>> streamPost(@Valid @RequestBody ChatRequest request) {
        return streamInternal(request);
    }

    @Operation(summary = "上传文件并总结")
    @PostMapping("/summarize-upload")
    public Result<Map<String, Object>> summarizeUpload(@RequestParam("file") MultipartFile file,
                                                       @RequestParam(value = "instruction", required = false) String instruction,
                                                       @RequestParam(value = "sessionId", required = false) Long sessionId) {
        Long userId = SecurityUtil.getCurrentUserId();
        ChatService.UploadSummaryResult result = chatService.summarizeUpload(userId, file, instruction, sessionId);
        return Result.success(Map.of(
                "summary", result.summary(),
                "sessionId", result.sessionId(),
                "fileName", result.fileName()
        ));
    }

    @Operation(summary = "打开会话最近上传的附件")
    @GetMapping("/session/{sessionId}/attachment")
    public ResponseEntity<byte[]> openAttachment(@PathVariable Long sessionId) {
        Long userId = SecurityUtil.getCurrentUserId();
        ChatService.UploadAttachment attachment = chatService.getSessionAttachment(userId, sessionId);
        MediaType mediaType = MediaType.APPLICATION_OCTET_STREAM;
        try {
            mediaType = MediaType.parseMediaType(attachment.contentType());
        } catch (Exception ignore) {
        }
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(mediaType);
        headers.setContentDisposition(ContentDisposition.inline()
                .filename(attachment.fileName(), StandardCharsets.UTF_8)
                .build());
        return ResponseEntity.ok()
                .headers(headers)
                .body(attachment.bytes());
    }

    @Operation(summary = "基于已上传文件继续提问")
    @PostMapping("/file/ask")
    public Result<Map<String, Object>> askByUploadedFile(@Valid @RequestBody UploadAskRequest request) {
        Long userId = SecurityUtil.getCurrentUserId();
        ChatService.UploadAskResult result =
                chatService.askByUploadedDocument(userId, request.getSessionId(), request.getQuestion());
        return Result.success(Map.of(
                "answer", result.answer(),
                "sessionId", result.sessionId(),
                "fileName", result.fileName()
        ));
    }

    private Flux<ServerSentEvent<ChatStreamChunk>> streamInternal(ChatRequest request) {
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

    @Operation(summary = "新建会话")
    @PostMapping("/session/new")
    public Result<ChatSession> createSession() {
        Long userId = SecurityUtil.getCurrentUserId();
        return Result.success(chatService.createSession(userId));
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
