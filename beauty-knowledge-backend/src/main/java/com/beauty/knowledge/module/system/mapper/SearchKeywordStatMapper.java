package com.beauty.knowledge.module.system.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.beauty.knowledge.module.system.domain.entity.SearchKeywordStat;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDate;

@Mapper
public interface SearchKeywordStatMapper extends BaseMapper<SearchKeywordStat> {

    @Insert("""
            INSERT INTO search_keyword_stat (stat_date, keyword, search_count, user_count)
            VALUES (#{statDate}, #{keyword}, 1, 1)
            ON DUPLICATE KEY UPDATE
              search_count = search_count + 1,
              user_count = user_count + IF(#{isNewUser}, 1, 0),
              updated_at = CURRENT_TIMESTAMP
            """)
    int upsert(@Param("statDate") LocalDate statDate,
               @Param("keyword") String keyword,
               @Param("isNewUser") boolean isNewUser);
}

