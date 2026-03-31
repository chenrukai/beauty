package com.beauty.knowledge.module.kg.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.module.entity.domain.entity.BeautyEffect;
import com.beauty.knowledge.module.entity.domain.entity.BeautyIngredient;
import com.beauty.knowledge.module.entity.domain.entity.BeautyProduct;
import com.beauty.knowledge.module.entity.domain.entity.EntityExtractPending;
import com.beauty.knowledge.module.entity.domain.entity.RelIngredientEffect;
import com.beauty.knowledge.module.entity.domain.entity.RelProductEffect;
import com.beauty.knowledge.module.entity.domain.entity.RelProductIngredient;
import com.beauty.knowledge.module.entity.mapper.BeautyEffectMapper;
import com.beauty.knowledge.module.entity.mapper.BeautyIngredientMapper;
import com.beauty.knowledge.module.entity.mapper.BeautyProductMapper;
import com.beauty.knowledge.module.entity.mapper.EntityExtractPendingMapper;
import com.beauty.knowledge.module.entity.mapper.RelIngredientEffectMapper;
import com.beauty.knowledge.module.entity.mapper.RelProductEffectMapper;
import com.beauty.knowledge.module.entity.mapper.RelProductIngredientMapper;
import com.beauty.knowledge.module.kg.domain.entity.KgEvidence;
import com.beauty.knowledge.module.kg.domain.vo.KgPendingViewVO;
import com.beauty.knowledge.module.kg.mapper.KgEvidenceMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Locale;

@Service
@RequiredArgsConstructor
public class KgReviewService {

    private static final BigDecimal DEFAULT_CONFIDENCE = new BigDecimal("0.7000");

    private final EntityExtractPendingMapper pendingMapper;
    private final BeautyIngredientMapper ingredientMapper;
    private final BeautyEffectMapper effectMapper;
    private final BeautyProductMapper productMapper;
    private final RelProductIngredientMapper relProductIngredientMapper;
    private final RelIngredientEffectMapper relIngredientEffectMapper;
    private final RelProductEffectMapper relProductEffectMapper;
    private final KgEvidenceMapper kgEvidenceMapper;
    private final ObjectMapper objectMapper;

    public List<KgPendingViewVO> listPending(String status) {
        LambdaQueryWrapper<EntityExtractPending> wrapper = new LambdaQueryWrapper<>();
        if (status == null || status.isBlank()) {
            wrapper.eq(EntityExtractPending::getStatus, "PENDING");
        } else {
            wrapper.eq(EntityExtractPending::getStatus, status.trim().toUpperCase(Locale.ROOT));
        }
        wrapper.orderByDesc(EntityExtractPending::getId);
        return pendingMapper.selectList(wrapper).stream()
                .map(this::toView)
                .toList();
    }

    @Transactional(rollbackFor = Exception.class)
    public EntityExtractPending confirmPending(Long pendingId, Long reviewerId, String comment) {
        EntityExtractPending pending = requirePending(pendingId);
        if (!"PENDING".equalsIgnoreCase(pending.getStatus())) {
            return pending;
        }

        String candidateType = normalizeCandidateType(pending.getCandidateType());
        if ("relation".equals(candidateType)) {
            RelationPayload payload = parseRelationPayload(pending);
            confirmRelation(payload, pending, reviewerId);
        } else {
            confirmEntity(pending, reviewerId);
        }

        pending.setStatus("CONFIRMED");
        pending.setReviewerId(reviewerId);
        pending.setReviewedAt(LocalDateTime.now());
        pending.setReviewComment(comment);
        pendingMapper.updateById(pending);
        return pending;
    }

    @Transactional(rollbackFor = Exception.class)
    public EntityExtractPending rejectPending(Long pendingId, Long reviewerId, String comment) {
        EntityExtractPending pending = requirePending(pendingId);
        if (!"PENDING".equalsIgnoreCase(pending.getStatus())) {
            return pending;
        }
        pending.setStatus("REJECTED");
        pending.setReviewerId(reviewerId);
        pending.setReviewedAt(LocalDateTime.now());
        pending.setReviewComment(comment);
        pendingMapper.updateById(pending);
        return pending;
    }

    private void confirmEntity(EntityExtractPending pending, Long reviewerId) {
        String entityType = safeLower(pending.getEntityType());
        Long entityId;
        switch (entityType) {
            case "ingredient" -> entityId = upsertIngredient(pending.getEntityName());
            case "effect" -> entityId = upsertEffect(pending.getEntityName());
            case "product" -> entityId = upsertProduct(pending.getEntityName());
            default -> throw new BusinessException(ErrorCode.BAD_REQUEST, "unsupported entity type: " + pending.getEntityType());
        }
        insertEvidence(
                "ENTITY",
                entityType.toUpperCase(Locale.ROOT),
                entityId,
                null,
                null,
                pending,
                reviewerId
        );
    }

    private void confirmRelation(RelationPayload payload, EntityExtractPending pending, Long reviewerId) {
        String predicate = safeUpper(payload.getPredicate());
        RelationUpsertResult upsertResult;
        switch (predicate) {
            case "PRODUCT_CONTAINS_INGREDIENT" -> upsertResult = upsertProductContainsIngredient(payload);
            case "INGREDIENT_HAS_EFFECT" -> upsertResult = upsertIngredientHasEffect(payload);
            case "PRODUCT_TARGETS_EFFECT" -> upsertResult = upsertProductTargetsEffect(payload);
            default -> throw new BusinessException(ErrorCode.BAD_REQUEST, "unsupported relation predicate: " + predicate);
        }

        insertEvidence(
                predicate,
                upsertResult.subjectType(),
                upsertResult.subjectId(),
                upsertResult.objectType(),
                upsertResult.objectId(),
                pending,
                reviewerId
        );
    }

    private RelationUpsertResult upsertProductContainsIngredient(RelationPayload payload) {
        Long subjectId = payload.getSubjectId() == null ? findProductIdByName(payload.getSubjectName()) : payload.getSubjectId();
        Long objectId = payload.getObjectId() == null ? findIngredientIdByName(payload.getObjectName()) : payload.getObjectId();
        if (subjectId == null || objectId == null) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "relation payload missing subjectId/objectId");
        }
        RelProductIngredient rel = relProductIngredientMapper.selectOne(new LambdaQueryWrapper<RelProductIngredient>()
                .eq(RelProductIngredient::getProductId, subjectId)
                .eq(RelProductIngredient::getIngredientId, objectId)
                .last("limit 1"));
        if (rel == null) {
            rel = new RelProductIngredient();
            rel.setProductId(subjectId);
            rel.setIngredientId(objectId);
            rel.setConcentration(payload.getConcentration());
            rel.setConfidence(firstNonNull(payload.getConfidence(), new BigDecimal("0.8000")));
            rel.setSource("review");
            rel.setStatus("ACTIVE");
            rel.setEvidenceCount(0);
            relProductIngredientMapper.insert(rel);
        } else {
            rel.setStatus("ACTIVE");
            relProductIngredientMapper.updateById(rel);
        }
        rel.setEvidenceCount((rel.getEvidenceCount() == null ? 0 : rel.getEvidenceCount()) + 1);
        relProductIngredientMapper.updateById(rel);
        return new RelationUpsertResult("PRODUCT", rel.getProductId(), "INGREDIENT", rel.getIngredientId());
    }

    private RelationUpsertResult upsertIngredientHasEffect(RelationPayload payload) {
        Long subjectId = payload.getSubjectId() == null ? findIngredientIdByName(payload.getSubjectName()) : payload.getSubjectId();
        Long objectId = payload.getObjectId() == null ? findEffectIdByName(payload.getObjectName()) : payload.getObjectId();
        if (subjectId == null || objectId == null) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "relation payload missing subjectId/objectId");
        }
        RelIngredientEffect rel = relIngredientEffectMapper.selectOne(new LambdaQueryWrapper<RelIngredientEffect>()
                .eq(RelIngredientEffect::getIngredientId, subjectId)
                .eq(RelIngredientEffect::getEffectId, objectId)
                .last("limit 1"));
        if (rel == null) {
            rel = new RelIngredientEffect();
            rel.setIngredientId(subjectId);
            rel.setEffectId(objectId);
            rel.setConfidence(firstNonNull(payload.getConfidence(), new BigDecimal("0.8000")));
            rel.setSource("review");
            rel.setStatus("ACTIVE");
            rel.setEvidenceCount(0);
            relIngredientEffectMapper.insert(rel);
        } else {
            rel.setStatus("ACTIVE");
            relIngredientEffectMapper.updateById(rel);
        }
        rel.setEvidenceCount((rel.getEvidenceCount() == null ? 0 : rel.getEvidenceCount()) + 1);
        relIngredientEffectMapper.updateById(rel);
        return new RelationUpsertResult("INGREDIENT", rel.getIngredientId(), "EFFECT", rel.getEffectId());
    }

    private RelationUpsertResult upsertProductTargetsEffect(RelationPayload payload) {
        Long subjectId = payload.getSubjectId() == null ? findProductIdByName(payload.getSubjectName()) : payload.getSubjectId();
        Long objectId = payload.getObjectId() == null ? findEffectIdByName(payload.getObjectName()) : payload.getObjectId();
        if (subjectId == null || objectId == null) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "relation payload missing subjectId/objectId");
        }
        RelProductEffect rel = relProductEffectMapper.selectOne(new LambdaQueryWrapper<RelProductEffect>()
                .eq(RelProductEffect::getProductId, subjectId)
                .eq(RelProductEffect::getEffectId, objectId)
                .last("limit 1"));
        if (rel == null) {
            rel = new RelProductEffect();
            rel.setProductId(subjectId);
            rel.setEffectId(objectId);
            rel.setConfidence(firstNonNull(payload.getConfidence(), new BigDecimal("0.7800")));
            rel.setSource("review");
            rel.setStatus("ACTIVE");
            rel.setEvidenceCount(0);
            relProductEffectMapper.insert(rel);
        } else {
            rel.setStatus("ACTIVE");
            relProductEffectMapper.updateById(rel);
        }
        rel.setEvidenceCount((rel.getEvidenceCount() == null ? 0 : rel.getEvidenceCount()) + 1);
        relProductEffectMapper.updateById(rel);
        return new RelationUpsertResult("PRODUCT", rel.getProductId(), "EFFECT", rel.getEffectId());
    }

    private void insertEvidence(String relationType,
                                String subjectType,
                                Long subjectId,
                                String objectType,
                                Long objectId,
                                EntityExtractPending pending,
                                Long reviewerId) {
        KgEvidence evidence = new KgEvidence();
        evidence.setRelationType(relationType);
        evidence.setSubjectType(subjectType);
        evidence.setSubjectId(subjectId);
        evidence.setObjectType(objectType);
        evidence.setObjectId(objectId);
        evidence.setFileId(pending.getFileId());
        evidence.setSourceText(pending.getSourceText());
        evidence.setExtractor(pending.getExtractMethod() == null ? "review" : pending.getExtractMethod());
        evidence.setConfidence(firstNonNull(pending.getConfidence(), DEFAULT_CONFIDENCE));
        evidence.setReviewerId(reviewerId);
        kgEvidenceMapper.insert(evidence);
    }

    private Long upsertIngredient(String name) {
        BeautyIngredient exists = ingredientMapper.selectOne(new LambdaQueryWrapper<BeautyIngredient>()
                .eq(BeautyIngredient::getName, name)
                .last("limit 1"));
        if (exists != null) {
            return exists.getId();
        }
        BeautyIngredient row = new BeautyIngredient();
        row.setName(name);
        row.setStatus(1);
        ingredientMapper.insert(row);
        return row.getId();
    }

    private Long upsertEffect(String name) {
        BeautyEffect exists = effectMapper.selectOne(new LambdaQueryWrapper<BeautyEffect>()
                .eq(BeautyEffect::getName, name)
                .last("limit 1"));
        if (exists != null) {
            return exists.getId();
        }
        BeautyEffect row = new BeautyEffect();
        row.setName(name);
        row.setStatus(1);
        effectMapper.insert(row);
        return row.getId();
    }

    private Long upsertProduct(String name) {
        BeautyProduct exists = productMapper.selectOne(new LambdaQueryWrapper<BeautyProduct>()
                .eq(BeautyProduct::getName, name)
                .last("limit 1"));
        if (exists != null) {
            return exists.getId();
        }
        BeautyProduct row = new BeautyProduct();
        row.setName(name);
        row.setBrand("pending");
        row.setStatus(1);
        productMapper.insert(row);
        return row.getId();
    }

    private RelationPayload parseRelationPayload(EntityExtractPending pending) {
        try {
            String payloadJson = pending.getPayloadJson();
            if (payloadJson == null || payloadJson.isBlank()) {
                throw new BusinessException(ErrorCode.BAD_REQUEST, "relation payload is empty");
            }
            return objectMapper.readValue(payloadJson, RelationPayload.class);
        } catch (BusinessException ex) {
            throw ex;
        } catch (Exception ex) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "invalid relation payload json");
        }
    }

    private EntityExtractPending requirePending(Long pendingId) {
        if (pendingId == null || pendingId <= 0) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "pending id is required");
        }
        EntityExtractPending pending = pendingMapper.selectById(pendingId);
        if (pending == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "pending record not found");
        }
        return pending;
    }

    private KgPendingViewVO toView(EntityExtractPending row) {
        return KgPendingViewVO.builder()
                .id(row.getId())
                .candidateType(normalizeCandidateType(row.getCandidateType()))
                .entityType(row.getEntityType())
                .entityName(row.getEntityName())
                .payloadJson(row.getPayloadJson())
                .fileId(row.getFileId())
                .sourceText(row.getSourceText())
                .extractMethod(row.getExtractMethod())
                .confidence(firstNonNull(row.getConfidence(), DEFAULT_CONFIDENCE))
                .status(row.getStatus())
                .createdAt(row.getCreatedAt())
                .build();
    }

    private Long findProductIdByName(String name) {
        if (name == null || name.isBlank()) {
            return null;
        }
        BeautyProduct row = productMapper.selectOne(new LambdaQueryWrapper<BeautyProduct>()
                .eq(BeautyProduct::getName, name)
                .last("limit 1"));
        return row == null ? null : row.getId();
    }

    private Long findIngredientIdByName(String name) {
        if (name == null || name.isBlank()) {
            return null;
        }
        BeautyIngredient row = ingredientMapper.selectOne(new LambdaQueryWrapper<BeautyIngredient>()
                .eq(BeautyIngredient::getName, name)
                .last("limit 1"));
        return row == null ? null : row.getId();
    }

    private Long findEffectIdByName(String name) {
        if (name == null || name.isBlank()) {
            return null;
        }
        BeautyEffect row = effectMapper.selectOne(new LambdaQueryWrapper<BeautyEffect>()
                .eq(BeautyEffect::getName, name)
                .last("limit 1"));
        return row == null ? null : row.getId();
    }

    private String normalizeCandidateType(String candidateType) {
        if (candidateType == null || candidateType.isBlank()) {
            return "entity";
        }
        return candidateType.trim().toLowerCase(Locale.ROOT);
    }

    private String safeLower(String value) {
        return value == null ? "" : value.trim().toLowerCase(Locale.ROOT);
    }

    private String safeUpper(String value) {
        return value == null ? "" : value.trim().toUpperCase(Locale.ROOT);
    }

    private BigDecimal firstNonNull(BigDecimal value, BigDecimal fallback) {
        return value == null ? fallback : value;
    }

    private record RelationUpsertResult(String subjectType, Long subjectId, String objectType, Long objectId) {
    }

    @Data
    private static class RelationPayload {
        private String predicate;
        private Long subjectId;
        private Long objectId;
        private String subjectName;
        private String objectName;
        private String concentration;
        private BigDecimal confidence;
    }
}
