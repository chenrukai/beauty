package com.beauty.knowledge.module.pipeline.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.beauty.knowledge.module.pipeline.domain.entity.KbChunk;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface PipelineKbChunkMapper extends BaseMapper<KbChunk> {

    int insertBatch(@Param("list") List<KbChunk> list);
}
