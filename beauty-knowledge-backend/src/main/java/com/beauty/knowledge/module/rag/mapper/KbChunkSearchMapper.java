package com.beauty.knowledge.module.rag.mapper;

import com.beauty.knowledge.module.rag.domain.dto.ChunkResult;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface KbChunkSearchMapper {

    List<ChunkResult> fullTextSearch(@Param("keyword") String keyword, @Param("topk") int topk);

    List<ChunkResult> selectByIds(@Param("ids") List<Long> ids);
}
