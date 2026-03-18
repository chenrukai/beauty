package com.beauty.knowledge.module.cms.service;

import com.beauty.knowledge.common.result.PageResult;
import com.beauty.knowledge.module.cms.domain.dto.KnowledgePageDTO;
import com.beauty.knowledge.module.cms.domain.dto.KnowledgeSaveDTO;
import com.beauty.knowledge.module.cms.domain.entity.KbKnowledge;
import com.beauty.knowledge.module.cms.domain.vo.KnowledgeDetailVO;

public interface KnowledgeService {

    PageResult<KbKnowledge> page(KnowledgePageDTO dto);

    KnowledgeDetailVO getById(Long id);

    void save(KnowledgeSaveDTO dto);

    void update(Long id, KnowledgeSaveDTO dto);

    void remove(Long id);

    void updateStatus(Long id, Integer status);

    PageResult<KbKnowledge> search(String keyword, Long pageNum, Long pageSize);
}
