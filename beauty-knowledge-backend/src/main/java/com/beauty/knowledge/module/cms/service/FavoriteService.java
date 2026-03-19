package com.beauty.knowledge.module.cms.service;

import com.beauty.knowledge.common.result.PageResult;
import com.beauty.knowledge.module.cms.domain.vo.FavoriteKnowledgeVO;

public interface FavoriteService {

    void addFavorite(Long knowledgeId);

    void removeFavorite(Long knowledgeId);

    PageResult<FavoriteKnowledgeVO> pageFavorites(Long pageNum, Long pageSize, String keyword);

    boolean isFavorited(Long knowledgeId);
}
