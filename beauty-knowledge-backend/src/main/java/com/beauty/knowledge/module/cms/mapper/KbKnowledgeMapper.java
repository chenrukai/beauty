package com.beauty.knowledge.module.cms.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.beauty.knowledge.module.cms.domain.entity.KbKnowledge;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface KbKnowledgeMapper extends BaseMapper<KbKnowledge> {

    List<KbKnowledge> fullTextSearch(@Param("keyword") String keyword,
                                     @Param("offset") long offset,
                                     @Param("pageSize") long pageSize);

    long fullTextSearchCount(@Param("keyword") String keyword);
}
