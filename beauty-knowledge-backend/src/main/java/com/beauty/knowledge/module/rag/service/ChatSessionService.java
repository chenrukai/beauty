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

    private final ChatSessionMapper chatSessionMapper;

    public List<ChatSession> listByUser(Long userId) {
        return chatSessionMapper.selectList(new LambdaQueryWrapper<ChatSession>()
                .eq(ChatSession::getUserId, userId)
                .eq(ChatSession::getStatus, 1)
                .orderByDesc(ChatSession::getUpdatedAt));
    }

    @Transactional(rollbackFor = Exception.class)
    public Long getOrCreate(Long userId, Long sessionId, String question) {
        if (sessionId != null) {
            ChatSession exist = chatSessionMapper.selectById(sessionId);
            if (exist == null || !exist.getUserId().equals(userId) || exist.getStatus() == 0) {
                throw new BusinessException(ErrorCode.NOT_FOUND, "会话不存在");
            }
            return sessionId;
        }
        ChatSession session = new ChatSession();
        session.setUserId(userId);
        session.setTitle((question == null ? "新会话" : question).substring(0, Math.min(24, (question == null ? "新会话" : question).length())));
        session.setStatus(1);
        chatSessionMapper.insert(session);
        return session.getId();
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
}
