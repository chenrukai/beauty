package com.beauty.knowledge.module.cms.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.beauty.knowledge.module.cms.domain.entity.FavoriteRecord;
import com.beauty.knowledge.module.cms.domain.vo.FavoriteKnowledgeVO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface FavoriteRecordMapper extends BaseMapper<FavoriteRecord> {

    List<FavoriteKnowledgeVO> pageFavorites(@Param("userId") Long userId,
                                            @Param("offset") long offset,
                                            @Param("pageSize") long pageSize,
                                            @Param("keyword") String keyword);

    long countFavorites(@Param("userId") Long userId,
                        @Param("keyword") String keyword);
}
