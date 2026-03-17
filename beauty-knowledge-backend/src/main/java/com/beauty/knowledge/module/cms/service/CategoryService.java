package com.beauty.knowledge.module.cms.service;

import com.beauty.knowledge.module.cms.domain.dto.CategorySaveDTO;
import com.beauty.knowledge.module.cms.domain.vo.CategoryTreeVO;

import java.util.List;

public interface CategoryService {

    List<CategoryTreeVO> getTree();

    void save(CategorySaveDTO dto);

    void update(Long id, CategorySaveDTO dto);

    void remove(Long id);
}
