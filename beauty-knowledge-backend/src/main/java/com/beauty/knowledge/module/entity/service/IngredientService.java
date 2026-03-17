package com.beauty.knowledge.module.entity.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.module.entity.domain.entity.BeautyIngredient;
import com.beauty.knowledge.module.entity.mapper.BeautyIngredientMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.List;

@Service
@RequiredArgsConstructor
public class IngredientService {

    private final BeautyIngredientMapper ingredientMapper;

    public List<BeautyIngredient> list(String keyword) {
        return ingredientMapper.selectList(new LambdaQueryWrapper<BeautyIngredient>()
                .like(StringUtils.hasText(keyword), BeautyIngredient::getName, keyword)
                .orderByDesc(BeautyIngredient::getId));
    }

    @Transactional(rollbackFor = Exception.class)
    public void save(BeautyIngredient entity) {
        checkNameUnique(entity.getName(), null);
        if (entity.getStatus() == null) {
            entity.setStatus(1);
        }
        ingredientMapper.insert(entity);
    }

    @Transactional(rollbackFor = Exception.class)
    public void update(Long id, BeautyIngredient entity) {
        BeautyIngredient db = ingredientMapper.selectById(id);
        if (db == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "成分不存在");
        }
        checkNameUnique(entity.getName(), id);
        db.setName(entity.getName());
        db.setAliasName(entity.getAliasName());
        db.setCategory(entity.getCategory());
        db.setSafetyLevel(entity.getSafetyLevel());
        db.setIntro(entity.getIntro());
        db.setStatus(entity.getStatus() == null ? 1 : entity.getStatus());
        ingredientMapper.updateById(db);
    }

    @Transactional(rollbackFor = Exception.class)
    public void delete(Long id) {
        ingredientMapper.deleteById(id);
    }

    public BeautyIngredient getById(Long id) {
        return ingredientMapper.selectById(id);
    }

    private void checkNameUnique(String name, Long excludeId) {
        BeautyIngredient exist = ingredientMapper.selectOne(new LambdaQueryWrapper<BeautyIngredient>()
                .eq(BeautyIngredient::getName, name)
                .ne(excludeId != null, BeautyIngredient::getId, excludeId)
                .last("limit 1"));
        if (exist != null) {
            throw new BusinessException(ErrorCode.ENTITY_NAME_EXISTS);
        }
    }
}
