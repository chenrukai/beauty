package com.beauty.knowledge.module.rag.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.module.rag.domain.dto.ChunkResult;
import com.beauty.knowledge.module.rag.domain.entity.ChatMessageEntity;
import com.beauty.knowledge.module.rag.mapper.ChatMessageMapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ChatRecordService {

    private final ChatMessageMapper chatMessageMapper;
    private final ObjectMapper objectMapper;

    public List<ChatMessageEntity> listBySession(Long sessionId) {
        return chatMessageMapper.selectList(new LambdaQueryWrapper<ChatMessageEntity>()
                .eq(ChatMessageEntity::getSessionId, sessionId)
                .orderByAsc(ChatMessageEntity::getId));
    }

    @Transactional(rollbackFor = Exception.class)
    public void saveUserQuestion(Long sessionId, String question) {
        ChatMessageEntity msg = new ChatMessageEntity();
        msg.setSessionId(sessionId);
        msg.setRole("user");
        msg.setContent(question);
        msg.setTokenCount(question == null ? 0 : question.length());
        chatMessageMapper.insert(msg);
    }

    @Transactional(rollbackFor = Exception.class)
    public void saveAssistantAnswer(Long sessionId, String answer, List<ChunkResult> sources) {
        ChatMessageEntity msg = new ChatMessageEntity();
        msg.setSessionId(sessionId);
        msg.setRole("assistant");
        msg.setContent(answer);
        msg.setTokenCount(answer == null ? 0 : answer.length());
        try {
            msg.setSources(objectMapper.writeValueAsString(sources));
        } catch (JsonProcessingException e) {
            msg.setSources("[]");
        }
        chatMessageMapper.insert(msg);
    }
}
