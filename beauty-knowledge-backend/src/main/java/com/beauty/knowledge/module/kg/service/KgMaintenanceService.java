package com.beauty.knowledge.module.kg.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.module.entity.domain.entity.BeautyEffect;
import com.beauty.knowledge.module.entity.domain.entity.BeautyIngredient;
import com.beauty.knowledge.module.entity.domain.entity.BeautyProduct;
import com.beauty.knowledge.module.entity.domain.entity.RelIngredientEffect;
import com.beauty.knowledge.module.entity.domain.entity.RelProductIngredient;
import com.beauty.knowledge.module.entity.mapper.BeautyEffectMapper;
import com.beauty.knowledge.module.entity.mapper.BeautyIngredientMapper;
import com.beauty.knowledge.module.entity.mapper.BeautyProductMapper;
import com.beauty.knowledge.module.entity.mapper.RelIngredientEffectMapper;
import com.beauty.knowledge.module.entity.mapper.RelProductIngredientMapper;
import com.beauty.knowledge.module.kg.domain.entity.KgEvidence;
import com.beauty.knowledge.module.kg.domain.vo.KgBackfillResultVO;
import com.beauty.knowledge.module.kg.mapper.KgEvidenceMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class KgMaintenanceService {

    private final RelProductIngredientMapper relProductIngredientMapper;
    private final RelIngredientEffectMapper relIngredientEffectMapper;
    private final BeautyProductMapper productMapper;
    private final BeautyIngredientMapper ingredientMapper;
    private final BeautyEffectMapper effectMapper;
    private final KgEvidenceMapper kgEvidenceMapper;

    @Transactional(rollbackFor = Exception.class)
    public KgBackfillResultVO backfillEvidence(Integer limit) {
        int maxRows = Math.max(1, Math.min(limit == null ? 2000 : limit, 10000));
        int inserted = 0;
        int updated = 0;
        int scannedPI = 0;
        int scannedIE = 0;

        var productIngredient = relProductIngredientMapper.selectList(new LambdaQueryWrapper<RelProductIngredient>()
                .and(w -> w.eq(RelProductIngredient::getStatus, "ACTIVE").or().isNull(RelProductIngredient::getStatus))
                .last("limit " + maxRows));
        scannedPI = productIngredient.size();
        if (!productIngredient.isEmpty()) {
            Set<Long> productIds = productIngredient.stream().map(RelProductIngredient::getProductId).collect(Collectors.toSet());
            Set<Long> ingredientIds = productIngredient.stream().map(RelProductIngredient::getIngredientId).collect(Collectors.toSet());
            Map<Long, String> productNameById = productMapper.selectBatchIds(productIds).stream()
                    .collect(Collectors.toMap(BeautyProduct::getId, BeautyProduct::getName));
            Map<Long, String> ingredientNameById = ingredientMapper.selectBatchIds(ingredientIds).stream()
                    .collect(Collectors.toMap(BeautyIngredient::getId, BeautyIngredient::getName));

            for (RelProductIngredient rel : productIngredient) {
                int evidenceCount = relationEvidenceCount(
                        "PRODUCT_CONTAINS_INGREDIENT", "PRODUCT", rel.getProductId(), "INGREDIENT", rel.getIngredientId()
                );
                if (evidenceCount == 0) {
                    KgEvidence evidence = new KgEvidence();
                    evidence.setRelationType("PRODUCT_CONTAINS_INGREDIENT");
                    evidence.setSubjectType("PRODUCT");
                    evidence.setSubjectId(rel.getProductId());
                    evidence.setObjectType("INGREDIENT");
                    evidence.setObjectId(rel.getIngredientId());
                    evidence.setExtractor("backfill");
                    evidence.setConfidence(rel.getConfidence() == null ? new BigDecimal("0.8000") : rel.getConfidence());
                    String pName = productNameById.getOrDefault(rel.getProductId(), "product#" + rel.getProductId());
                    String iName = ingredientNameById.getOrDefault(rel.getIngredientId(), "ingredient#" + rel.getIngredientId());
                    evidence.setSourceText("Backfill from existing relation: " + pName + " contains " + iName);
                    kgEvidenceMapper.insert(evidence);
                    evidenceCount = 1;
                    inserted++;
                }
                Integer oldCount = rel.getEvidenceCount();
                if (oldCount == null || oldCount != evidenceCount) {
                    rel.setEvidenceCount(evidenceCount);
                    relProductIngredientMapper.updateById(rel);
                    updated++;
                }
            }
        }

        var ingredientEffect = relIngredientEffectMapper.selectList(new LambdaQueryWrapper<RelIngredientEffect>()
                .and(w -> w.eq(RelIngredientEffect::getStatus, "ACTIVE").or().isNull(RelIngredientEffect::getStatus))
                .last("limit " + maxRows));
        scannedIE = ingredientEffect.size();
        if (!ingredientEffect.isEmpty()) {
            Set<Long> ingredientIds = ingredientEffect.stream().map(RelIngredientEffect::getIngredientId).collect(Collectors.toSet());
            Set<Long> effectIds = ingredientEffect.stream().map(RelIngredientEffect::getEffectId).collect(Collectors.toSet());
            Map<Long, String> ingredientNameById = ingredientMapper.selectBatchIds(ingredientIds).stream()
                    .collect(Collectors.toMap(BeautyIngredient::getId, BeautyIngredient::getName));
            Map<Long, String> effectNameById = effectMapper.selectBatchIds(effectIds).stream()
                    .collect(Collectors.toMap(BeautyEffect::getId, BeautyEffect::getName));

            for (RelIngredientEffect rel : ingredientEffect) {
                int evidenceCount = relationEvidenceCount(
                        "INGREDIENT_HAS_EFFECT", "INGREDIENT", rel.getIngredientId(), "EFFECT", rel.getEffectId()
                );
                if (evidenceCount == 0) {
                    KgEvidence evidence = new KgEvidence();
                    evidence.setRelationType("INGREDIENT_HAS_EFFECT");
                    evidence.setSubjectType("INGREDIENT");
                    evidence.setSubjectId(rel.getIngredientId());
                    evidence.setObjectType("EFFECT");
                    evidence.setObjectId(rel.getEffectId());
                    evidence.setExtractor("backfill");
                    evidence.setConfidence(rel.getConfidence() == null ? new BigDecimal("0.8000") : rel.getConfidence());
                    String iName = ingredientNameById.getOrDefault(rel.getIngredientId(), "ingredient#" + rel.getIngredientId());
                    String eName = effectNameById.getOrDefault(rel.getEffectId(), "effect#" + rel.getEffectId());
                    evidence.setSourceText("Backfill from existing relation: " + iName + " has effect " + eName);
                    kgEvidenceMapper.insert(evidence);
                    evidenceCount = 1;
                    inserted++;
                }
                Integer oldCount = rel.getEvidenceCount();
                if (oldCount == null || oldCount != evidenceCount) {
                    rel.setEvidenceCount(evidenceCount);
                    relIngredientEffectMapper.updateById(rel);
                    updated++;
                }
            }
        }

        return KgBackfillResultVO.builder()
                .scannedProductIngredient(scannedPI)
                .scannedIngredientEffect(scannedIE)
                .insertedEvidence(inserted)
                .updatedRelations(updated)
                .build();
    }

    private int relationEvidenceCount(String relationType, String subjectType, Long subjectId, String objectType, Long objectId) {
        Long c = kgEvidenceMapper.selectCount(new LambdaQueryWrapper<KgEvidence>()
                .eq(KgEvidence::getRelationType, relationType)
                .eq(KgEvidence::getSubjectType, subjectType)
                .eq(KgEvidence::getSubjectId, subjectId)
                .eq(KgEvidence::getObjectType, objectType)
                .eq(KgEvidence::getObjectId, objectId));
        return c == null ? 0 : c.intValue();
    }
}
