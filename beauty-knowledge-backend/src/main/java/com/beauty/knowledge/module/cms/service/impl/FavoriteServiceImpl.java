package com.beauty.knowledge.module.cms.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.common.result.PageResult;
import com.beauty.knowledge.common.util.SecurityUtil;
import com.beauty.knowledge.module.cms.domain.entity.FavoriteRecord;
import com.beauty.knowledge.module.cms.domain.entity.KbKnowledge;
import com.beauty.knowledge.module.cms.domain.vo.FavoriteKnowledgeVO;
import com.beauty.knowledge.module.cms.mapper.FavoriteRecordMapper;
import com.beauty.knowledge.module.cms.mapper.KbKnowledgeMapper;
import com.beauty.knowledge.module.cms.service.FavoriteService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FavoriteServiceImpl implements FavoriteService {

    private final FavoriteRecordMapper favoriteRecordMapper;
    private final KbKnowledgeMapper knowledgeMapper;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void addFavorite(Long knowledgeId) {
        KbKnowledge knowledge = knowledgeMapper.selectById(knowledgeId);
        if (knowledge == null || knowledge.getStatus() == null || knowledge.getStatus() != 1
                || (knowledge.getIsDeleted() != null && knowledge.getIsDeleted() == 1)) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "knowledge not found");
        }

        Long userId = SecurityUtil.getCurrentUserId();
        FavoriteRecord exists = favoriteRecordMapper.selectOne(new LambdaQueryWrapper<FavoriteRecord>()
                .eq(FavoriteRecord::getUserId, userId)
                .eq(FavoriteRecord::getKnowledgeId, knowledgeId)
                .last("limit 1"));
        if (exists != null) {
            return;
        }
        FavoriteRecord record = new FavoriteRecord();
        record.setUserId(userId);
        record.setKnowledgeId(knowledgeId);
        favoriteRecordMapper.insert(record);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void removeFavorite(Long knowledgeId) {
        Long userId = SecurityUtil.getCurrentUserId();
        favoriteRecordMapper.delete(new LambdaQueryWrapper<FavoriteRecord>()
                .eq(FavoriteRecord::getUserId, userId)
                .eq(FavoriteRecord::getKnowledgeId, knowledgeId));
    }

    @Override
    public PageResult<FavoriteKnowledgeVO> pageFavorites(Long pageNum, Long pageSize, String keyword) {
        Long userId = SecurityUtil.getCurrentUserId();
        long p = pageNum == null || pageNum < 1 ? 1 : pageNum;
        long s = pageSize == null || pageSize < 1 ? 10 : Math.min(pageSize, 100);
        long offset = (p - 1) * s;
        String kw = StringUtils.hasText(keyword) ? keyword.trim() : null;
        List<FavoriteKnowledgeVO> records = favoriteRecordMapper.pageFavorites(userId, offset, s, kw);
        long total = favoriteRecordMapper.countFavorites(userId, kw);
        long pages = (total + s - 1) / s;
        return PageResult.<FavoriteKnowledgeVO>builder()
                .records(records)
                .total(total)
                .pageNum(p)
                .pageSize(s)
                .pages(pages)
                .build();
    }
}
