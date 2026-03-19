package com.beauty.knowledge.module.rag.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.module.rag.domain.entity.ChatSession;
import com.beauty.knowledge.module.rag.mapper.ChatSessionMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ChatSessionService {

    private static final String DEFAULT_TITLE = "新会话";

    private final ChatSessionMapper chatSessionMapper;

    public List<ChatSession> listByUser(Long userId) {
        return chatSessionMapper.selectList(new LambdaQueryWrapper<ChatSession>()
                .eq(ChatSession::getUserId, userId)
                .eq(ChatSession::getStatus, 1)
                .orderByDesc(ChatSession::getUpdatedAt));
    }

    @Transactional(rollbackFor = Exception.class)
    public Long getOrCreate(Long userId, Long sessionId, String question) {
        String normalizedQuestion = normalizeTitle(question);
        if (sessionId != null) {
            ChatSession exist = chatSessionMapper.selectById(sessionId);
            if (exist == null || !exist.getUserId().equals(userId) || exist.getStatus() == 0) {
                throw new BusinessException(ErrorCode.NOT_FOUND, "会话不存在");
            }
            if (DEFAULT_TITLE.equals(exist.getTitle()) && !normalizedQuestion.isBlank()) {
                exist.setTitle(normalizedQuestion);
                chatSessionMapper.updateById(exist);
            }
            return sessionId;
        }
        return create(userId, normalizedQuestion.isBlank() ? DEFAULT_TITLE : normalizedQuestion);
    }

    @Transactional(rollbackFor = Exception.class)
    public ChatSession createEmpty(Long userId) {
        Long id = create(userId, DEFAULT_TITLE);
        return chatSessionMapper.selectById(id);
    }

    @Transactional(rollbackFor = Exception.class)
    public void delete(Long userId, Long sessionId) {
        ChatSession session = chatSessionMapper.selectById(sessionId);
        if (session == null || !session.getUserId().equals(userId)) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "会话不存在");
        }
        session.setStatus(0);
        chatSessionMapper.updateById(session);
    }

    private Long create(Long userId, String title) {
        ChatSession session = new ChatSession();
        session.setUserId(userId);
        session.setTitle(normalizeTitle(title).isBlank() ? DEFAULT_TITLE : normalizeTitle(title));
        session.setStatus(1);
        chatSessionMapper.insert(session);
        return session.getId();
    }

    private String normalizeTitle(String raw) {
        String value = raw == null ? "" : raw.trim();
        if (value.isEmpty()) {
            return "";
        }
        return value.substring(0, Math.min(24, value.length()));
    }
}
