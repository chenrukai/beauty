package com.beauty.knowledge.module.kg.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.module.entity.domain.entity.BeautyEffect;
import com.beauty.knowledge.module.entity.domain.entity.BeautyIngredient;
import com.beauty.knowledge.module.entity.domain.entity.BeautyProduct;
import com.beauty.knowledge.module.entity.domain.entity.RelIngredientEffect;
import com.beauty.knowledge.module.entity.domain.entity.RelProductEffect;
import com.beauty.knowledge.module.entity.domain.entity.RelProductIngredient;
import com.beauty.knowledge.module.entity.mapper.BeautyEffectMapper;
import com.beauty.knowledge.module.entity.mapper.BeautyIngredientMapper;
import com.beauty.knowledge.module.entity.mapper.BeautyProductMapper;
import com.beauty.knowledge.module.entity.mapper.RelIngredientEffectMapper;
import com.beauty.knowledge.module.entity.mapper.RelProductEffectMapper;
import com.beauty.knowledge.module.entity.mapper.RelProductIngredientMapper;
import com.beauty.knowledge.module.kg.domain.entity.KgEvidence;
import com.beauty.knowledge.module.kg.domain.vo.KgGraphEdgeVO;
import com.beauty.knowledge.module.kg.domain.vo.KgGraphNodeVO;
import com.beauty.knowledge.module.kg.domain.vo.KgGraphVO;
import com.beauty.knowledge.module.kg.domain.vo.KgEvidenceVO;
import com.beauty.knowledge.module.kg.domain.vo.KgPathVO;
import com.beauty.knowledge.module.kg.mapper.KgEvidenceMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class KgQueryService {

    private final BeautyProductMapper productMapper;
    private final BeautyIngredientMapper ingredientMapper;
    private final BeautyEffectMapper effectMapper;
    private final RelProductIngredientMapper relProductIngredientMapper;
    private final RelIngredientEffectMapper relIngredientEffectMapper;
    private final RelProductEffectMapper relProductEffectMapper;
    private final KgEvidenceMapper kgEvidenceMapper;

    public KgGraphVO getProductGraph(Long productId) {
        BeautyProduct product = productMapper.selectById(productId);
        if (product == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "product not found");
        }

        GraphBuilder graph = new GraphBuilder(nodeKey("PRODUCT", product.getId()));
        graph.addNode("PRODUCT", product.getId(), product.getName());

        List<RelProductIngredient> productIngredientRels = relProductIngredientMapper.selectList(
                new LambdaQueryWrapper<RelProductIngredient>()
                        .eq(RelProductIngredient::getProductId, productId)
                        .and(w -> w.eq(RelProductIngredient::getStatus, "ACTIVE")
                                .or()
                                .isNull(RelProductIngredient::getStatus))
        );
        if (productIngredientRels.isEmpty()) {
            return graph.build();
        }

        Set<Long> ingredientIds = productIngredientRels.stream()
                .map(RelProductIngredient::getIngredientId)
                .collect(Collectors.toSet());
        Map<Long, BeautyIngredient> ingredientMap = ingredientMapper.selectBatchIds(ingredientIds).stream()
                .collect(Collectors.toMap(BeautyIngredient::getId, v -> v));

        for (RelProductIngredient rel : productIngredientRels) {
            BeautyIngredient ingredient = ingredientMap.get(rel.getIngredientId());
            if (ingredient == null) {
                continue;
            }
            graph.addNode("INGREDIENT", ingredient.getId(), ingredient.getName());
            graph.addEdge(
                    nodeKey("PRODUCT", productId),
                    "PRODUCT_CONTAINS_INGREDIENT",
                    nodeKey("INGREDIENT", ingredient.getId()),
                    defaultConfidence(rel.getConfidence(), new BigDecimal("0.8000")),
                    defaultEvidenceCount(rel.getEvidenceCount()),
                    false
            );
        }

        List<RelIngredientEffect> ingredientEffectRels = relIngredientEffectMapper.selectList(
                new LambdaQueryWrapper<RelIngredientEffect>()
                        .in(RelIngredientEffect::getIngredientId, ingredientIds)
                        .and(w -> w.eq(RelIngredientEffect::getStatus, "ACTIVE")
                                .or()
                                .isNull(RelIngredientEffect::getStatus))
        );

        List<RelProductEffect> productEffectRels = relProductEffectMapper.selectList(
                new LambdaQueryWrapper<RelProductEffect>()
                        .eq(RelProductEffect::getProductId, productId)
                        .and(w -> w.eq(RelProductEffect::getStatus, "ACTIVE")
                                .or()
                                .isNull(RelProductEffect::getStatus))
        );

        Set<Long> effectIds = new HashSet<>();
        effectIds.addAll(ingredientEffectRels.stream().map(RelIngredientEffect::getEffectId).collect(Collectors.toSet()));
        effectIds.addAll(productEffectRels.stream().map(RelProductEffect::getEffectId).collect(Collectors.toSet()));
        if (effectIds.isEmpty()) {
            return graph.build();
        }
        Map<Long, BeautyEffect> effectMap = effectMapper.selectBatchIds(effectIds).stream()
                .collect(Collectors.toMap(BeautyEffect::getId, v -> v));

        Set<Long> directEffectIds = productEffectRels.stream().map(RelProductEffect::getEffectId).collect(Collectors.toSet());
        for (RelProductEffect rel : productEffectRels) {
            BeautyEffect effect = effectMap.get(rel.getEffectId());
            if (effect == null) {
                continue;
            }
            graph.addNode("EFFECT", effect.getId(), effect.getName());
            graph.addEdge(
                    nodeKey("PRODUCT", productId),
                    "PRODUCT_TARGETS_EFFECT",
                    nodeKey("EFFECT", effect.getId()),
                    defaultConfidence(rel.getConfidence(), new BigDecimal("0.7800")),
                    defaultEvidenceCount(rel.getEvidenceCount()),
                    false
            );
        }

        Map<Long, BigDecimal> inferredProductEffectConfidence = new LinkedHashMap<>();
        for (RelIngredientEffect rel : ingredientEffectRels) {
            BeautyEffect effect = effectMap.get(rel.getEffectId());
            if (effect == null) {
                continue;
            }
            graph.addNode("EFFECT", effect.getId(), effect.getName());
            graph.addEdge(
                    nodeKey("INGREDIENT", rel.getIngredientId()),
                    "INGREDIENT_HAS_EFFECT",
                    nodeKey("EFFECT", effect.getId()),
                    defaultConfidence(rel.getConfidence(), new BigDecimal("0.8000")),
                    defaultEvidenceCount(rel.getEvidenceCount()),
                    false
            );

            BigDecimal oldScore = inferredProductEffectConfidence.get(effect.getId());
            BigDecimal newScore = defaultConfidence(rel.getConfidence(), new BigDecimal("0.8000"));
            if (oldScore == null || oldScore.compareTo(newScore) < 0) {
                inferredProductEffectConfidence.put(effect.getId(), newScore);
            }
        }

        for (Map.Entry<Long, BigDecimal> entry : inferredProductEffectConfidence.entrySet()) {
            if (directEffectIds.contains(entry.getKey())) {
                continue;
            }
            graph.addEdge(
                    nodeKey("PRODUCT", productId),
                    "PRODUCT_TARGETS_EFFECT",
                    nodeKey("EFFECT", entry.getKey()),
                    entry.getValue(),
                    0,
                    true
            );
        }

        return graph.build();
    }

    public KgGraphVO getNeighbors(Long entityId, String entityType) {
        String type = (entityType == null || entityType.isBlank())
                ? "PRODUCT"
                : entityType.trim().toUpperCase();
        return switch (type) {
            case "PRODUCT" -> getProductGraph(entityId);
            case "INGREDIENT" -> getIngredientNeighbors(entityId);
            case "EFFECT" -> getEffectNeighbors(entityId);
            default -> throw new BusinessException(ErrorCode.BAD_REQUEST, "unsupported entity type");
        };
    }

    public KgPathVO findPath(String fromType, Long fromId, String toType, Long toId, Integer maxDepth) {
        String safeFromType = safeType(fromType);
        String safeToType = safeType(toType);
        if (fromId == null || toId == null) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "fromId and toId are required");
        }
        int depthLimit = Math.max(1, Math.min(maxDepth == null ? 4 : maxDepth, 6));
        String fromKey = nodeKey(safeFromType, fromId);
        String toKey = nodeKey(safeToType, toId);

        KgGraphVO graph = buildGlobalGraph();
        Map<String, KgGraphNodeVO> nodeByKey = graph.getNodes().stream()
                .collect(Collectors.toMap(KgGraphNodeVO::getNodeKey, v -> v, (a, b) -> a));
        if (!nodeByKey.containsKey(fromKey) || !nodeByKey.containsKey(toKey)) {
            return KgPathVO.builder()
                    .fromKey(fromKey)
                    .toKey(toKey)
                    .found(false)
                    .hopCount(0)
                    .nodes(List.of())
                    .edges(List.of())
                    .build();
        }

        Map<String, List<KgGraphEdgeVO>> adjacency = buildAdjacency(graph.getEdges());
        Queue<String> queue = new ArrayDeque<>();
        Map<String, String> parentNode = new HashMap<>();
        Map<String, KgGraphEdgeVO> parentEdge = new HashMap<>();
        Map<String, Integer> depth = new HashMap<>();
        Set<String> visited = new HashSet<>();
        queue.add(fromKey);
        visited.add(fromKey);
        depth.put(fromKey, 0);

        while (!queue.isEmpty()) {
            String current = queue.poll();
            if (toKey.equals(current)) {
                break;
            }
            int currentDepth = depth.getOrDefault(current, 0);
            if (currentDepth >= depthLimit) {
                continue;
            }
            for (KgGraphEdgeVO edge : adjacency.getOrDefault(current, List.of())) {
                String next = edge.getObjectKey();
                if (visited.contains(next)) {
                    continue;
                }
                visited.add(next);
                parentNode.put(next, current);
                parentEdge.put(next, edge);
                depth.put(next, currentDepth + 1);
                queue.add(next);
            }
        }

        if (!visited.contains(toKey)) {
            return KgPathVO.builder()
                    .fromKey(fromKey)
                    .toKey(toKey)
                    .found(false)
                    .hopCount(0)
                    .nodes(List.of())
                    .edges(List.of())
                    .build();
        }

        List<KgGraphEdgeVO> pathEdges = new ArrayList<>();
        List<KgGraphNodeVO> pathNodes = new ArrayList<>();
        String cursor = toKey;
        pathNodes.add(nodeByKey.get(cursor));
        while (!fromKey.equals(cursor)) {
            KgGraphEdgeVO edge = parentEdge.get(cursor);
            if (edge == null) {
                break;
            }
            pathEdges.add(edge);
            cursor = parentNode.get(cursor);
            if (cursor == null) {
                break;
            }
            pathNodes.add(nodeByKey.get(cursor));
        }
        java.util.Collections.reverse(pathEdges);
        java.util.Collections.reverse(pathNodes);

        return KgPathVO.builder()
                .fromKey(fromKey)
                .toKey(toKey)
                .found(true)
                .hopCount(pathEdges.size())
                .nodes(pathNodes)
                .edges(pathEdges)
                .build();
    }

    public List<KgEvidenceVO> relationEvidence(String predicate,
                                               String subjectType,
                                               Long subjectId,
                                               String objectType,
                                               Long objectId,
                                               Integer size) {
        int limit = Math.max(1, Math.min(size == null ? 20 : size, 100));
        LambdaQueryWrapper<KgEvidence> wrapper = new LambdaQueryWrapper<KgEvidence>()
                .eq(predicate != null && !predicate.isBlank(), KgEvidence::getRelationType, predicate.toUpperCase())
                .eq(subjectType != null && !subjectType.isBlank(), KgEvidence::getSubjectType, subjectType.toUpperCase())
                .eq(subjectId != null, KgEvidence::getSubjectId, subjectId)
                .eq(objectType != null && !objectType.isBlank(), KgEvidence::getObjectType, objectType.toUpperCase())
                .eq(objectId != null, KgEvidence::getObjectId, objectId)
                .orderByDesc(KgEvidence::getId)
                .last("limit " + limit);
        return kgEvidenceMapper.selectList(wrapper).stream()
                .map(e -> KgEvidenceVO.builder()
                        .id(e.getId())
                        .relationType(e.getRelationType())
                        .subjectType(e.getSubjectType())
                        .subjectId(e.getSubjectId())
                        .objectType(e.getObjectType())
                        .objectId(e.getObjectId())
                        .fileId(e.getFileId())
                        .chunkId(e.getChunkId())
                        .pageNo(e.getPageNo())
                        .sourceText(e.getSourceText())
                        .extractor(e.getExtractor())
                        .confidence(e.getConfidence())
                        .reviewerId(e.getReviewerId())
                        .createdAt(e.getCreatedAt())
                        .build())
                .toList();
    }

    private KgGraphVO getIngredientNeighbors(Long ingredientId) {
        BeautyIngredient ingredient = ingredientMapper.selectById(ingredientId);
        if (ingredient == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "ingredient not found");
        }

        GraphBuilder graph = new GraphBuilder(nodeKey("INGREDIENT", ingredientId));
        graph.addNode("INGREDIENT", ingredient.getId(), ingredient.getName());

        List<RelProductIngredient> productRels = relProductIngredientMapper.selectList(
                new LambdaQueryWrapper<RelProductIngredient>()
                        .eq(RelProductIngredient::getIngredientId, ingredientId)
                        .and(w -> w.eq(RelProductIngredient::getStatus, "ACTIVE")
                                .or()
                                .isNull(RelProductIngredient::getStatus))
        );
        if (!productRels.isEmpty()) {
            Set<Long> productIds = productRels.stream().map(RelProductIngredient::getProductId).collect(Collectors.toSet());
            Map<Long, BeautyProduct> productMap = productMapper.selectBatchIds(productIds).stream()
                    .collect(Collectors.toMap(BeautyProduct::getId, v -> v));
            for (RelProductIngredient rel : productRels) {
                BeautyProduct product = productMap.get(rel.getProductId());
                if (product == null) {
                    continue;
                }
                graph.addNode("PRODUCT", product.getId(), product.getName());
                graph.addEdge(
                        nodeKey("PRODUCT", product.getId()),
                        "PRODUCT_CONTAINS_INGREDIENT",
                        nodeKey("INGREDIENT", ingredientId),
                        defaultConfidence(rel.getConfidence(), new BigDecimal("0.8000")),
                        defaultEvidenceCount(rel.getEvidenceCount()),
                        false
                );
            }
        }

        List<RelIngredientEffect> effectRels = relIngredientEffectMapper.selectList(
                new LambdaQueryWrapper<RelIngredientEffect>()
                        .eq(RelIngredientEffect::getIngredientId, ingredientId)
                        .and(w -> w.eq(RelIngredientEffect::getStatus, "ACTIVE")
                                .or()
                                .isNull(RelIngredientEffect::getStatus))
        );
        if (!effectRels.isEmpty()) {
            Set<Long> effectIds = effectRels.stream().map(RelIngredientEffect::getEffectId).collect(Collectors.toSet());
            Map<Long, BeautyEffect> effectMap = effectMapper.selectBatchIds(effectIds).stream()
                    .collect(Collectors.toMap(BeautyEffect::getId, v -> v));
            for (RelIngredientEffect rel : effectRels) {
                BeautyEffect effect = effectMap.get(rel.getEffectId());
                if (effect == null) {
                    continue;
                }
                graph.addNode("EFFECT", effect.getId(), effect.getName());
                graph.addEdge(
                        nodeKey("INGREDIENT", ingredientId),
                        "INGREDIENT_HAS_EFFECT",
                        nodeKey("EFFECT", effect.getId()),
                        defaultConfidence(rel.getConfidence(), new BigDecimal("0.8000")),
                        defaultEvidenceCount(rel.getEvidenceCount()),
                        false
                );
            }
        }

        return graph.build();
    }

    private KgGraphVO getEffectNeighbors(Long effectId) {
        BeautyEffect effect = effectMapper.selectById(effectId);
        if (effect == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "effect not found");
        }

        GraphBuilder graph = new GraphBuilder(nodeKey("EFFECT", effectId));
        graph.addNode("EFFECT", effect.getId(), effect.getName());

        List<RelIngredientEffect> effectRels = relIngredientEffectMapper.selectList(
                new LambdaQueryWrapper<RelIngredientEffect>()
                        .eq(RelIngredientEffect::getEffectId, effectId)
                        .and(w -> w.eq(RelIngredientEffect::getStatus, "ACTIVE")
                                .or()
                                .isNull(RelIngredientEffect::getStatus))
        );
        if (effectRels.isEmpty()) {
            return graph.build();
        }

        Set<Long> ingredientIds = effectRels.stream()
                .map(RelIngredientEffect::getIngredientId)
                .collect(Collectors.toSet());
        Map<Long, BeautyIngredient> ingredientMap = ingredientMapper.selectBatchIds(ingredientIds).stream()
                .collect(Collectors.toMap(BeautyIngredient::getId, v -> v));

        for (RelIngredientEffect rel : effectRels) {
            BeautyIngredient ingredient = ingredientMap.get(rel.getIngredientId());
            if (ingredient == null) {
                continue;
            }
            graph.addNode("INGREDIENT", ingredient.getId(), ingredient.getName());
            graph.addEdge(
                    nodeKey("INGREDIENT", ingredient.getId()),
                    "INGREDIENT_HAS_EFFECT",
                    nodeKey("EFFECT", effectId),
                    defaultConfidence(rel.getConfidence(), new BigDecimal("0.8000")),
                    defaultEvidenceCount(rel.getEvidenceCount()),
                    false
            );
        }

        List<RelProductEffect> productEffectRels = relProductEffectMapper.selectList(
                new LambdaQueryWrapper<RelProductEffect>()
                        .eq(RelProductEffect::getEffectId, effectId)
                        .and(w -> w.eq(RelProductEffect::getStatus, "ACTIVE")
                                .or()
                                .isNull(RelProductEffect::getStatus))
        );
        Set<Long> directProductIds = productEffectRels.stream().map(RelProductEffect::getProductId).collect(Collectors.toSet());
        if (!productEffectRels.isEmpty()) {
            Map<Long, BeautyProduct> productMap = productMapper.selectBatchIds(directProductIds).stream()
                    .collect(Collectors.toMap(BeautyProduct::getId, v -> v));
            for (RelProductEffect rel : productEffectRels) {
                BeautyProduct product = productMap.get(rel.getProductId());
                if (product == null) {
                    continue;
                }
                graph.addNode("PRODUCT", product.getId(), product.getName());
                graph.addEdge(
                        nodeKey("PRODUCT", product.getId()),
                        "PRODUCT_TARGETS_EFFECT",
                        nodeKey("EFFECT", effectId),
                        defaultConfidence(rel.getConfidence(), new BigDecimal("0.7800")),
                        defaultEvidenceCount(rel.getEvidenceCount()),
                        false
                );
            }
        }

        List<RelProductIngredient> productRels = relProductIngredientMapper.selectList(
                new LambdaQueryWrapper<RelProductIngredient>()
                        .in(RelProductIngredient::getIngredientId, ingredientIds)
                        .and(w -> w.eq(RelProductIngredient::getStatus, "ACTIVE")
                                .or()
                                .isNull(RelProductIngredient::getStatus))
        );
        if (!productRels.isEmpty()) {
            Set<Long> productIds = productRels.stream().map(RelProductIngredient::getProductId).collect(Collectors.toSet());
            Map<Long, BeautyProduct> productMap = productMapper.selectBatchIds(productIds).stream()
                    .collect(Collectors.toMap(BeautyProduct::getId, v -> v));
            for (RelProductIngredient rel : productRels) {
                BeautyProduct product = productMap.get(rel.getProductId());
                if (product == null) {
                    continue;
                }
                graph.addNode("PRODUCT", product.getId(), product.getName());
                graph.addEdge(
                        nodeKey("PRODUCT", product.getId()),
                        "PRODUCT_CONTAINS_INGREDIENT",
                        nodeKey("INGREDIENT", rel.getIngredientId()),
                        defaultConfidence(rel.getConfidence(), new BigDecimal("0.8000")),
                        defaultEvidenceCount(rel.getEvidenceCount()),
                        false
                );
                if (directProductIds.contains(product.getId())) {
                    continue;
                }
                graph.addEdge(
                        nodeKey("PRODUCT", product.getId()),
                        "PRODUCT_TARGETS_EFFECT",
                    nodeKey("EFFECT", effectId),
                    defaultConfidence(rel.getConfidence(), new BigDecimal("0.7000")),
                    0,
                    true
                );
            }
        }

        return graph.build();
    }

    private String nodeKey(String type, Long id) {
        return type + ":" + id;
    }

    private String safeType(String type) {
        if (type == null || type.isBlank()) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "entity type is required");
        }
        return type.trim().toUpperCase();
    }

    private BigDecimal defaultConfidence(BigDecimal value, BigDecimal fallback) {
        return value == null ? fallback : value;
    }

    private Integer defaultEvidenceCount(Integer value) {
        return value == null ? 0 : value;
    }

    private KgGraphVO buildGlobalGraph() {
        GraphBuilder graph = new GraphBuilder("GLOBAL");

        List<BeautyProduct> products = productMapper.selectList(new LambdaQueryWrapper<BeautyProduct>()
                .eq(BeautyProduct::getStatus, 1));
        for (BeautyProduct product : products) {
            graph.addNode("PRODUCT", product.getId(), product.getName());
        }
        List<BeautyIngredient> ingredients = ingredientMapper.selectList(new LambdaQueryWrapper<BeautyIngredient>()
                .eq(BeautyIngredient::getStatus, 1));
        for (BeautyIngredient ingredient : ingredients) {
            graph.addNode("INGREDIENT", ingredient.getId(), ingredient.getName());
        }
        List<BeautyEffect> effects = effectMapper.selectList(new LambdaQueryWrapper<BeautyEffect>()
                .eq(BeautyEffect::getStatus, 1));
        for (BeautyEffect effect : effects) {
            graph.addNode("EFFECT", effect.getId(), effect.getName());
        }

        List<RelProductIngredient> productIngredientRels = relProductIngredientMapper.selectList(
                new LambdaQueryWrapper<RelProductIngredient>()
                        .and(w -> w.eq(RelProductIngredient::getStatus, "ACTIVE")
                                .or()
                                .isNull(RelProductIngredient::getStatus))
        );
        for (RelProductIngredient rel : productIngredientRels) {
            graph.addEdge(
                    nodeKey("PRODUCT", rel.getProductId()),
                    "PRODUCT_CONTAINS_INGREDIENT",
                    nodeKey("INGREDIENT", rel.getIngredientId()),
                    defaultConfidence(rel.getConfidence(), new BigDecimal("0.8000")),
                    defaultEvidenceCount(rel.getEvidenceCount()),
                    false
            );
        }

        List<RelIngredientEffect> ingredientEffectRels = relIngredientEffectMapper.selectList(
                new LambdaQueryWrapper<RelIngredientEffect>()
                        .and(w -> w.eq(RelIngredientEffect::getStatus, "ACTIVE")
                                .or()
                                .isNull(RelIngredientEffect::getStatus))
        );
        for (RelIngredientEffect rel : ingredientEffectRels) {
            graph.addEdge(
                    nodeKey("INGREDIENT", rel.getIngredientId()),
                    "INGREDIENT_HAS_EFFECT",
                    nodeKey("EFFECT", rel.getEffectId()),
                    defaultConfidence(rel.getConfidence(), new BigDecimal("0.8000")),
                    defaultEvidenceCount(rel.getEvidenceCount()),
                    false
            );
        }

        List<RelProductEffect> productEffectRels = relProductEffectMapper.selectList(
                new LambdaQueryWrapper<RelProductEffect>()
                        .and(w -> w.eq(RelProductEffect::getStatus, "ACTIVE")
                                .or()
                                .isNull(RelProductEffect::getStatus))
        );
        for (RelProductEffect rel : productEffectRels) {
            graph.addEdge(
                    nodeKey("PRODUCT", rel.getProductId()),
                    "PRODUCT_TARGETS_EFFECT",
                    nodeKey("EFFECT", rel.getEffectId()),
                    defaultConfidence(rel.getConfidence(), new BigDecimal("0.7800")),
                    defaultEvidenceCount(rel.getEvidenceCount()),
                    false
            );
        }
        return graph.build();
    }

    private Map<String, List<KgGraphEdgeVO>> buildAdjacency(List<KgGraphEdgeVO> edges) {
        Map<String, List<KgGraphEdgeVO>> out = new HashMap<>();
        for (KgGraphEdgeVO edge : edges) {
            out.computeIfAbsent(edge.getSubjectKey(), k -> new ArrayList<>()).add(edge);
            KgGraphEdgeVO reverse = KgGraphEdgeVO.builder()
                    .edgeKey(edge.getEdgeKey() + "#R")
                    .subjectKey(edge.getObjectKey())
                    .predicate("REVERSE_" + edge.getPredicate())
                    .objectKey(edge.getSubjectKey())
                    .confidence(edge.getConfidence())
                    .evidenceCount(edge.getEvidenceCount())
                    .inferred(edge.getInferred())
                    .build();
            out.computeIfAbsent(reverse.getSubjectKey(), k -> new ArrayList<>()).add(reverse);
        }
        return out;
    }

    private static final class GraphBuilder {
        private final String centerKey;
        private final Map<String, KgGraphNodeVO> nodes = new LinkedHashMap<>();
        private final Map<String, KgGraphEdgeVO> edges = new LinkedHashMap<>();

        private GraphBuilder(String centerKey) {
            this.centerKey = centerKey;
        }

        private void addNode(String type, Long id, String name) {
            String key = type + ":" + id;
            nodes.putIfAbsent(key, KgGraphNodeVO.builder()
                    .nodeKey(key)
                    .type(type)
                    .id(id)
                    .name(name)
                    .build());
        }

        private void addEdge(String subjectKey,
                             String predicate,
                             String objectKey,
                             BigDecimal confidence,
                             Integer evidenceCount,
                             boolean inferred) {
            String edgeKey = subjectKey + "|" + predicate + "|" + objectKey;
            KgGraphEdgeVO old = edges.get(edgeKey);
            if (old != null) {
                if (old.getConfidence() == null || (confidence != null && old.getConfidence().compareTo(confidence) < 0)) {
                    old.setConfidence(confidence);
                }
                old.setEvidenceCount((old.getEvidenceCount() == null ? 0 : old.getEvidenceCount()) + evidenceCount);
                old.setInferred(old.getInferred() && inferred);
                return;
            }
            edges.put(edgeKey, KgGraphEdgeVO.builder()
                    .edgeKey(edgeKey)
                    .subjectKey(subjectKey)
                    .predicate(predicate)
                    .objectKey(objectKey)
                    .confidence(confidence)
                    .evidenceCount(evidenceCount)
                    .inferred(inferred)
                    .build());
        }

        private KgGraphVO build() {
            return KgGraphVO.builder()
                    .centerKey(centerKey)
                    .nodes(new ArrayList<>(nodes.values()))
                    .edges(new ArrayList<>(edges.values()))
                    .build();
        }
    }
}
