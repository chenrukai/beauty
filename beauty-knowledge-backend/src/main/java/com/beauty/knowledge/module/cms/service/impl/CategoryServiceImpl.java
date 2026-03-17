package com.beauty.knowledge.module.cms.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.module.cms.domain.dto.CategorySaveDTO;
import com.beauty.knowledge.module.cms.domain.entity.KbCategory;
import com.beauty.knowledge.module.cms.domain.entity.KbKnowledge;
import com.beauty.knowledge.module.cms.domain.vo.CategoryTreeVO;
import com.beauty.knowledge.module.cms.mapper.KbCategoryMapper;
import com.beauty.knowledge.module.cms.mapper.KbKnowledgeMapper;
import com.beauty.knowledge.module.cms.service.CategoryService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@Slf4j
@RequiredArgsConstructor
public class CategoryServiceImpl implements CategoryService {

    private final KbCategoryMapper kbCategoryMapper;
    private final KbKnowledgeMapper kbKnowledgeMapper;

    @Override
    public List<CategoryTreeVO> getTree() {
        List<KbCategory> all;
        try {
            all = kbCategoryMapper.selectList(new LambdaQueryWrapper<KbCategory>()
                    .orderByAsc(KbCategory::getSortOrder)
                    .orderByAsc(KbCategory::getId));
        } catch (Exception ex) {
            // Compatible with legacy schema that does not have `sort_order`.
            log.warn("kb_category missing sort_order, fallback to id ordering for category tree");
            all = kbCategoryMapper.selectList(new LambdaQueryWrapper<KbCategory>()
                    .select(KbCategory::getId, KbCategory::getName, KbCategory::getParentId)
                    .orderByAsc(KbCategory::getId));
        }

        Map<Long, List<KbCategory>> childMap = all.stream()
                .collect(Collectors.groupingBy(c -> c.getParentId() == null ? 0L : c.getParentId()));

        List<KbCategory> roots = childMap.getOrDefault(0L, new ArrayList<>());
        return roots.stream()
                .map(c -> buildTree(c, childMap))
                .sorted(Comparator.comparing(CategoryTreeVO::getSortOrder, Comparator.nullsLast(Integer::compareTo))
                        .thenComparing(CategoryTreeVO::getId, Comparator.nullsLast(Long::compareTo)))
                .toList();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void save(CategorySaveDTO dto) {
        KbCategory category = new KbCategory();
        category.setName(dto.getName());
        category.setParentId(dto.getParentId() == null ? 0L : dto.getParentId());
        category.setSortOrder(dto.getSortOrder() == null ? 0 : dto.getSortOrder());
        category.setStatus(dto.getStatus() == null ? 1 : dto.getStatus());
        kbCategoryMapper.insert(category);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void update(Long id, CategorySaveDTO dto) {
        KbCategory exist = kbCategoryMapper.selectById(id);
        if (exist == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "分类不存在");
        }
        exist.setName(dto.getName());
        exist.setParentId(dto.getParentId() == null ? 0L : dto.getParentId());
        exist.setSortOrder(dto.getSortOrder() == null ? 0 : dto.getSortOrder());
        exist.setStatus(dto.getStatus() == null ? 1 : dto.getStatus());
        kbCategoryMapper.updateById(exist);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void remove(Long id) {
        Long childrenCount = kbCategoryMapper.selectCount(new LambdaQueryWrapper<KbCategory>().eq(KbCategory::getParentId, id));
        if (childrenCount != null && childrenCount > 0) {
            throw new BusinessException(ErrorCode.CATEGORY_HAS_CHILDREN);
        }

        Long knowledgeCount = kbKnowledgeMapper.selectCount(new LambdaQueryWrapper<KbKnowledge>().eq(KbKnowledge::getCategoryId, id));
        if (knowledgeCount != null && knowledgeCount > 0) {
            throw new BusinessException(ErrorCode.CATEGORY_HAS_CHILDREN);
        }

        kbCategoryMapper.deleteById(id);
    }

    private CategoryTreeVO buildTree(KbCategory category, Map<Long, List<KbCategory>> childMap) {
        List<CategoryTreeVO> children = childMap.getOrDefault(category.getId(), List.of())
                .stream()
                .map(c -> buildTree(c, childMap))
                .sorted(Comparator.comparing(CategoryTreeVO::getSortOrder, Comparator.nullsLast(Integer::compareTo))
                        .thenComparing(CategoryTreeVO::getId, Comparator.nullsLast(Long::compareTo)))
                .toList();

        return CategoryTreeVO.builder()
                .id(category.getId())
                .name(category.getName())
                .parentId(category.getParentId())
                .sortOrder(category.getSortOrder())
                .children(new ArrayList<>(children))
                .build();
    }
}