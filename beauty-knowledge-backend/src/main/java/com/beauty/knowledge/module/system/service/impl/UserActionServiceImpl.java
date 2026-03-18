package com.beauty.knowledge.module.system.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.util.SecurityUtil;
import com.beauty.knowledge.module.system.domain.dto.UserActionDTO;
import com.beauty.knowledge.module.system.domain.entity.UserActionLog;
import com.beauty.knowledge.module.system.mapper.SearchKeywordStatMapper;
import com.beauty.knowledge.module.system.mapper.UserActionLogMapper;
import com.beauty.knowledge.module.system.service.UserActionService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class UserActionServiceImpl implements UserActionService {

    private final UserActionLogMapper userActionLogMapper;
    private final SearchKeywordStatMapper searchKeywordStatMapper;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void record(UserActionDTO dto, String ip, String userAgent) {
        Long userId = SecurityUtil.getCurrentUserId();
        UserActionLog log = new UserActionLog();
        log.setUserId(userId);
        log.setActionType(normalize(dto.getActionType()));
        log.setTargetType(dto.getTargetType());
        log.setTargetId(dto.getTargetId());
        log.setKeyword(dto.getKeyword());
        String extra = StringUtils.hasText(dto.getExtra()) ? dto.getExtra().trim() : null;
        if (!StringUtils.hasText(extra) && StringUtils.hasText(dto.getSource())) {
            extra = dto.getSource().trim().toLowerCase();
        }
        log.setExtra(extra);
        log.setIp(ip);
        log.setUserAgent(userAgent);
        userActionLogMapper.insert(log);

        if ("search".equalsIgnoreCase(dto.getActionType()) && StringUtils.hasText(dto.getKeyword())) {
            String keyword = dto.getKeyword().trim();
            Long dailyCount = userActionLogMapper.selectCount(new LambdaQueryWrapper<UserActionLog>()
                    .eq(UserActionLog::getUserId, userId)
                    .eq(UserActionLog::getActionType, "search")
                    .eq(UserActionLog::getKeyword, keyword)
                    .ge(UserActionLog::getCreatedAt, LocalDate.now().atStartOfDay()));
            boolean isNewUserForKeywordToday = dailyCount == null || dailyCount <= 1;
            searchKeywordStatMapper.upsert(LocalDate.now(), keyword, isNewUserForKeywordToday);
        }
    }

    private String normalize(String actionType) {
        return actionType == null ? "" : actionType.trim().toLowerCase();
    }
}
