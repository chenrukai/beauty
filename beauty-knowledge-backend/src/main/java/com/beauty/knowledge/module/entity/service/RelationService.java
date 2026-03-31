package com.beauty.knowledge.module.entity.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.module.entity.domain.entity.RelIngredientEffect;
import com.beauty.knowledge.module.entity.domain.entity.RelProductEffect;
import com.beauty.knowledge.module.entity.domain.entity.RelProductIngredient;
import com.beauty.knowledge.module.entity.mapper.RelIngredientEffectMapper;
import com.beauty.knowledge.module.entity.mapper.RelProductEffectMapper;
import com.beauty.knowledge.module.entity.mapper.RelProductIngredientMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Service
@RequiredArgsConstructor
public class RelationService {

    private final IngredientService ingredientService;
    private final EffectService effectService;
    private final ProductService productService;
    private final RelIngredientEffectMapper relIngredientEffectMapper;
    private final RelProductIngredientMapper relProductIngredientMapper;
    private final RelProductEffectMapper relProductEffectMapper;

    @Transactional(rollbackFor = Exception.class)
    public void bindIngredientEffect(Long ingredientId, Long effectId) {
        if (ingredientService.getById(ingredientId) == null || effectService.getById(effectId) == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "实体不存在");
        }
        RelIngredientEffect exist = relIngredientEffectMapper.selectOne(new LambdaQueryWrapper<RelIngredientEffect>()
                .eq(RelIngredientEffect::getIngredientId, ingredientId)
                .eq(RelIngredientEffect::getEffectId, effectId)
                .last("limit 1"));
        if (exist != null) {
            return;
        }
        RelIngredientEffect rel = new RelIngredientEffect();
        rel.setIngredientId(ingredientId);
        rel.setEffectId(effectId);
        rel.setConfidence(new BigDecimal("0.80"));
        rel.setSource("manual");
        relIngredientEffectMapper.insert(rel);
    }

    @Transactional(rollbackFor = Exception.class)
    public void unbindIngredientEffect(Long ingredientId, Long effectId) {
        relIngredientEffectMapper.delete(new LambdaQueryWrapper<RelIngredientEffect>()
                .eq(RelIngredientEffect::getIngredientId, ingredientId)
                .eq(RelIngredientEffect::getEffectId, effectId));
    }

    @Transactional(rollbackFor = Exception.class)
    public void bindProductIngredient(Long productId, Long ingredientId, String concentration) {
        if (productService.getById(productId) == null || ingredientService.getById(ingredientId) == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "实体不存在");
        }
        RelProductIngredient exist = relProductIngredientMapper.selectOne(new LambdaQueryWrapper<RelProductIngredient>()
                .eq(RelProductIngredient::getProductId, productId)
                .eq(RelProductIngredient::getIngredientId, ingredientId)
                .last("limit 1"));
        if (exist != null) {
            return;
        }
        RelProductIngredient rel = new RelProductIngredient();
        rel.setProductId(productId);
        rel.setIngredientId(ingredientId);
        rel.setConcentration(concentration);
        relProductIngredientMapper.insert(rel);
    }

    @Transactional(rollbackFor = Exception.class)
    public void unbindProductIngredient(Long productId, Long ingredientId) {
        relProductIngredientMapper.delete(new LambdaQueryWrapper<RelProductIngredient>()
                .eq(RelProductIngredient::getProductId, productId)
                .eq(RelProductIngredient::getIngredientId, ingredientId));
    }

    public List<RelIngredientEffect> listIngredientEffects(Long ingredientId) {
        return relIngredientEffectMapper.selectList(new LambdaQueryWrapper<RelIngredientEffect>()
                .eq(ingredientId != null, RelIngredientEffect::getIngredientId, ingredientId)
                .orderByDesc(RelIngredientEffect::getId));
    }

    public List<RelProductIngredient> listProductIngredients(Long productId) {
        return relProductIngredientMapper.selectList(new LambdaQueryWrapper<RelProductIngredient>()
                .eq(productId != null, RelProductIngredient::getProductId, productId)
                .orderByDesc(RelProductIngredient::getId));
    }

    @Transactional(rollbackFor = Exception.class)
    public void bindProductEffect(Long productId, Long effectId) {
        if (productService.getById(productId) == null || effectService.getById(effectId) == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "实体不存在");
        }
        RelProductEffect exist = relProductEffectMapper.selectOne(new LambdaQueryWrapper<RelProductEffect>()
                .eq(RelProductEffect::getProductId, productId)
                .eq(RelProductEffect::getEffectId, effectId)
                .last("limit 1"));
        if (exist != null) {
            return;
        }
        RelProductEffect rel = new RelProductEffect();
        rel.setProductId(productId);
        rel.setEffectId(effectId);
        rel.setConfidence(new BigDecimal("0.78"));
        rel.setSource("manual");
        rel.setStatus("ACTIVE");
        rel.setEvidenceCount(0);
        relProductEffectMapper.insert(rel);
    }

    @Transactional(rollbackFor = Exception.class)
    public void unbindProductEffect(Long productId, Long effectId) {
        relProductEffectMapper.delete(new LambdaQueryWrapper<RelProductEffect>()
                .eq(RelProductEffect::getProductId, productId)
                .eq(RelProductEffect::getEffectId, effectId));
    }

    public List<RelProductEffect> listProductEffects(Long productId) {
        return relProductEffectMapper.selectList(new LambdaQueryWrapper<RelProductEffect>()
                .eq(productId != null, RelProductEffect::getProductId, productId)
                .orderByDesc(RelProductEffect::getId));
    }
}
