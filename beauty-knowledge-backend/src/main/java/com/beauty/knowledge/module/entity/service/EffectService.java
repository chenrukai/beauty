package com.beauty.knowledge.module.entity.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.module.entity.domain.entity.BeautyEffect;
import com.beauty.knowledge.module.entity.mapper.BeautyEffectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.List;

@Service
@RequiredArgsConstructor
public class EffectService {

    private final BeautyEffectMapper effectMapper;

    public List<BeautyEffect> list(String keyword) {
        return effectMapper.selectList(new LambdaQueryWrapper<BeautyEffect>()
                .like(StringUtils.hasText(keyword), BeautyEffect::getName, keyword)
                .orderByDesc(BeautyEffect::getId));
    }

    @Transactional(rollbackFor = Exception.class)
    public void save(BeautyEffect entity) {
        checkNameUnique(entity.getName(), null);
        if (entity.getStatus() == null) {
            entity.setStatus(1);
        }
        effectMapper.insert(entity);
    }

    @Transactional(rollbackFor = Exception.class)
    public void update(Long id, BeautyEffect entity) {
        BeautyEffect db = effectMapper.selectById(id);
        if (db == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "功效不存在");
        }
        checkNameUnique(entity.getName(), id);
        db.setName(entity.getName());
        db.setScene(entity.getScene());
        db.setIntro(entity.getIntro());
        db.setStatus(entity.getStatus() == null ? 1 : entity.getStatus());
        effectMapper.updateById(db);
    }

    @Transactional(rollbackFor = Exception.class)
    public void delete(Long id) {
        effectMapper.deleteById(id);
    }

    public BeautyEffect getById(Long id) {
        return effectMapper.selectById(id);
    }

    private void checkNameUnique(String name, Long excludeId) {
        BeautyEffect exist = effectMapper.selectOne(new LambdaQueryWrapper<BeautyEffect>()
                .eq(BeautyEffect::getName, name)
                .ne(excludeId != null, BeautyEffect::getId, excludeId)
                .last("limit 1"));
        if (exist != null) {
            throw new BusinessException(ErrorCode.ENTITY_NAME_EXISTS);
        }
    }
}
