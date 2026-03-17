package com.beauty.knowledge.module.rag.service;

import com.beauty.knowledge.common.constant.RedisKeyConstant;
import com.beauty.knowledge.module.rag.domain.dto.ChatMessage;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class ContextService {

    private final StringRedisTemplate stringRedisTemplate;
    private final ObjectMapper objectMapper;

    @Value("${beauty.rag.context-max-round:3}")
    private int maxRound;

    public List<ChatMessage> getRecentHistory(Long userId) {
        String key = RedisKeyConstant.chatSession(userId);
        List<String> list = stringRedisTemplate.opsForList().range(key, 0, -1);
        if (list == null || list.isEmpty()) {
            return List.of();
        }
        List<ChatMessage> messages = new ArrayList<>();
        for (String item : list) {
            try {
                messages.add(objectMapper.readValue(item, ChatMessage.class));
            } catch (Exception ex) {
                log.warn("parse context failed: {}", ex.getMessage());
            }
        }
        return messages;
    }

    public void appendRound(Long userId, String question, String answer) {
        String key = RedisKeyConstant.chatSession(userId);
        push(key, ChatMessage.builder().role("user").content(question).build());
        push(key, ChatMessage.builder().role("assistant").content(answer).build());
        long maxMessages = Math.max(1, maxRound * 2L);
        stringRedisTemplate.opsForList().trim(key, -maxMessages, -1);
    }

    private void push(String key, ChatMessage message) {
        try {
            stringRedisTemplate.opsForList().rightPush(key, objectMapper.writeValueAsString(message));
        } catch (Exception ex) {
            log.warn("push context failed: {}", ex.getMessage());
        }
    }
}
