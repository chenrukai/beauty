package com.beauty.knowledge.module.system.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Mapper
public interface DashboardReportMapper {

    @Select("""
            SELECT LOWER(COALESCE(extra, 'unknown')) AS source, COUNT(1) AS cnt
            FROM user_action_log
            WHERE action_type = 'browse'
              AND target_type = 'knowledge'
              AND created_at >= #{start}
              AND created_at < #{end}
            GROUP BY LOWER(COALESCE(extra, 'unknown'))
            """)
    List<Map<String, Object>> sourceRatio(@Param("start") LocalDateTime start,
                                          @Param("end") LocalDateTime end);

    @Select("""
            SELECT DATE_FORMAT(created_at, '%m-%d') AS label, COUNT(1) AS cnt
            FROM user_action_log
            WHERE action_type = 'browse'
              AND target_type = 'knowledge'
              AND created_at >= #{start}
              AND created_at < #{end}
            GROUP BY DATE_FORMAT(created_at, '%Y-%m-%d')
            ORDER BY MIN(created_at)
            """)
    List<Map<String, Object>> browseTrendDaily(@Param("start") LocalDateTime start,
                                               @Param("end") LocalDateTime end);

    @Select("""
            SELECT DATE_FORMAT(created_at, '%H:00') AS label, COUNT(1) AS cnt
            FROM user_action_log
            WHERE action_type = 'browse'
              AND target_type = 'knowledge'
              AND created_at >= #{start}
              AND created_at < #{end}
            GROUP BY DATE_FORMAT(created_at, '%Y-%m-%d %H')
            ORDER BY MIN(created_at)
            """)
    List<Map<String, Object>> browseTrendHourly(@Param("start") LocalDateTime start,
                                                @Param("end") LocalDateTime end);

    @Select("""
            SELECT k.id AS knowledgeId, k.title AS title, COUNT(1) AS browseCount
            FROM user_action_log l
            INNER JOIN kb_knowledge k ON k.id = l.target_id
            WHERE l.action_type = 'browse'
              AND l.target_type = 'knowledge'
              AND l.created_at >= #{start}
              AND l.created_at < #{end}
              AND k.is_deleted = 0
            GROUP BY k.id, k.title
            ORDER BY browseCount DESC, k.id DESC
            LIMIT 10
            """)
    List<Map<String, Object>> hotKnowledge(@Param("start") LocalDateTime start,
                                           @Param("end") LocalDateTime end);

    @Select("""
            SELECT keyword, SUM(search_count) AS searchCount
            FROM search_keyword_stat
            WHERE stat_date >= #{startDate}
              AND stat_date <= #{endDate}
            GROUP BY keyword
            ORDER BY searchCount DESC, keyword ASC
            LIMIT 10
            """)
    List<Map<String, Object>> hotKeywords(@Param("startDate") LocalDate startDate,
                                          @Param("endDate") LocalDate endDate);

    @Select("""
            SELECT COUNT(DISTINCT user_id)
            FROM user_action_log
            WHERE created_at >= #{start}
              AND created_at < #{end}
            """)
    Long activeUserCount(@Param("start") LocalDateTime start,
                         @Param("end") LocalDateTime end);

    @Select("""
            SELECT COUNT(1)
            FROM user_action_log
            WHERE created_at >= #{start}
              AND created_at < #{end}
            """)
    Long actionCount(@Param("start") LocalDateTime start,
                     @Param("end") LocalDateTime end);

    @Select("""
            SELECT COUNT(1)
            FROM user_action_log
            WHERE action_type = 'search'
              AND created_at >= #{start}
              AND created_at < #{end}
            """)
    Long searchActionCount(@Param("start") LocalDateTime start,
                           @Param("end") LocalDateTime end);
}
