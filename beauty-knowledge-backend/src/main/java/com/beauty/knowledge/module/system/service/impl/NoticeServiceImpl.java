package com.beauty.knowledge.module.system.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.common.result.PageResult;
import com.beauty.knowledge.common.util.SecurityUtil;
import com.beauty.knowledge.module.system.domain.dto.NoticeSaveDTO;
import com.beauty.knowledge.module.system.domain.entity.SysNotice;
import com.beauty.knowledge.module.system.mapper.SysNoticeMapper;
import com.beauty.knowledge.module.system.service.NoticeService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class NoticeServiceImpl implements NoticeService {

    private final SysNoticeMapper noticeMapper;

    @Override
    public PageResult<SysNotice> page(Long pageNum, Long pageSize, Integer status, String keyword) {
        long p = pageNum == null || pageNum < 1 ? 1 : pageNum;
        long s = pageSize == null || pageSize < 1 ? 10 : Math.min(pageSize, 100);
        Page<SysNotice> page = new Page<>(p, s);
        LambdaQueryWrapper<SysNotice> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(status != null, SysNotice::getStatus, status)
                .and(StringUtils.hasText(keyword), q -> q
                        .like(SysNotice::getTitle, keyword)
                        .or()
                        .like(SysNotice::getContent, keyword))
                .orderByDesc(SysNotice::getIsTop)
                .orderByDesc(SysNotice::getPublishTime)
                .orderByDesc(SysNotice::getId);
        return PageResult.of(noticeMapper.selectPage(page, wrapper));
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void save(NoticeSaveDTO dto) {
        validateStatus(dto.getStatus());
        SysNotice notice = new SysNotice();
        notice.setTitle(dto.getTitle());
        notice.setContent(dto.getContent());
        notice.setStatus(dto.getStatus());
        notice.setIsTop(dto.getIsTop() == null ? 0 : (dto.getIsTop() == 1 ? 1 : 0));
        notice.setExpireTime(dto.getExpireTime());
        notice.setPublishTime(LocalDateTime.now());
        notice.setCreatedBy(SecurityUtil.getCurrentUserId());
        noticeMapper.insert(notice);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void update(Long id, NoticeSaveDTO dto) {
        validateStatus(dto.getStatus());
        SysNotice db = noticeMapper.selectById(id);
        if (db == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "notice not found");
        }
        db.setTitle(dto.getTitle());
        db.setContent(dto.getContent());
        db.setStatus(dto.getStatus());
        db.setIsTop(dto.getIsTop() == null ? 0 : (dto.getIsTop() == 1 ? 1 : 0));
        db.setExpireTime(dto.getExpireTime());
        noticeMapper.updateById(db);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void setTop(Long id, Integer isTop) {
        if (isTop == null || (isTop != 0 && isTop != 1)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "isTop must be 0 or 1");
        }
        SysNotice db = noticeMapper.selectById(id);
        if (db == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "notice not found");
        }
        db.setIsTop(isTop);
        noticeMapper.updateById(db);
    }

    private void validateStatus(Integer status) {
        if (status == null || (status != 0 && status != 1)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "status must be 0 or 1");
        }
    }
}

