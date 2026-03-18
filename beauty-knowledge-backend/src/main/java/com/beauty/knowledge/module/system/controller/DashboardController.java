package com.beauty.knowledge.module.system.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.result.Result;
import com.beauty.knowledge.module.cms.domain.entity.KbKnowledge;
import com.beauty.knowledge.module.cms.domain.entity.ProcessTask;
import com.beauty.knowledge.module.cms.mapper.KbKnowledgeMapper;
import com.beauty.knowledge.module.cms.mapper.ProcessTaskMapper;
import com.beauty.knowledge.module.entity.domain.entity.EntityExtractPending;
import com.beauty.knowledge.module.entity.mapper.EntityExtractPendingMapper;
import com.beauty.knowledge.module.system.domain.entity.SearchKeywordStat;
import com.beauty.knowledge.module.system.mapper.DashboardReportMapper;
import com.beauty.knowledge.module.system.mapper.SearchKeywordStatMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.LinkedHashMap;
import java.util.Map;

@Tag(name = "仪表盘")
@RestController
@RequestMapping("/api/admin/dashboard")
@RequiredArgsConstructor
@PreAuthorize("hasRole('admin')")
public class DashboardController {

    private final KbKnowledgeMapper knowledgeMapper;
    private final ProcessTaskMapper taskMapper;
    private final EntityExtractPendingMapper pendingMapper;
    private final SearchKeywordStatMapper searchKeywordStatMapper;
    private final DashboardReportMapper dashboardReportMapper;

    @Operation(summary = "总览统计")
    @GetMapping("/overview")
    public Result<Map<String, Object>> overview() {
        LocalDateTime todayStart = LocalDate.now().atStartOfDay();
        LocalDateTime weekStart = LocalDate.now().minusDays(6).atStartOfDay();

        Long totalKnowledge = knowledgeMapper.selectCount(new LambdaQueryWrapper<KbKnowledge>()
                .eq(KbKnowledge::getIsDeleted, 0));
        Long publishedKnowledge = knowledgeMapper.selectCount(new LambdaQueryWrapper<KbKnowledge>()
                .eq(KbKnowledge::getIsDeleted, 0)
                .eq(KbKnowledge::getStatus, 1));
        Long todayAdded = knowledgeMapper.selectCount(new LambdaQueryWrapper<KbKnowledge>()
                .eq(KbKnowledge::getIsDeleted, 0)
                .ge(KbKnowledge::getCreatedAt, todayStart));
        Long weekAdded = knowledgeMapper.selectCount(new LambdaQueryWrapper<KbKnowledge>()
                .eq(KbKnowledge::getIsDeleted, 0)
                .ge(KbKnowledge::getCreatedAt, weekStart));

        Long pendingTasks = taskMapper.selectCount(new LambdaQueryWrapper<ProcessTask>()
                .in(ProcessTask::getStatus, "PENDING", "PROCESSING", "RUNNING"));
        Long failedTasks = taskMapper.selectCount(new LambdaQueryWrapper<ProcessTask>()
                .in(ProcessTask::getStatus, "FAILED", "ERROR"));

        Long pendingEntities = pendingMapper.selectCount(new LambdaQueryWrapper<EntityExtractPending>()
                .eq(EntityExtractPending::getStatus, "PENDING"));

        return Result.success(Map.of(
                "knowledgeTotal", totalKnowledge == null ? 0 : totalKnowledge,
                "knowledgePublished", publishedKnowledge == null ? 0 : publishedKnowledge,
                "knowledgeTodayAdded", todayAdded == null ? 0 : todayAdded,
                "knowledgeWeekAdded", weekAdded == null ? 0 : weekAdded,
                "taskPending", pendingTasks == null ? 0 : pendingTasks,
                "taskFailed", failedTasks == null ? 0 : failedTasks,
                "entityPending", pendingEntities == null ? 0 : pendingEntities
        ));
    }

    @Operation(summary = "热门内容 Top10")
    @GetMapping("/hot-content")
    public Result<List<KbKnowledge>> hotContent() {
        List<KbKnowledge> list = knowledgeMapper.selectList(new LambdaQueryWrapper<KbKnowledge>()
                .eq(KbKnowledge::getIsDeleted, 0)
                .eq(KbKnowledge::getStatus, 1)
                .orderByDesc(KbKnowledge::getViewCount)
                .orderByDesc(KbKnowledge::getId)
                .last("limit 10"));
        return Result.success(list);
    }

    @Operation(summary = "热门搜索词 Top10")
    @GetMapping("/hot-keywords")
    public Result<List<SearchKeywordStat>> hotKeywords() {
        List<SearchKeywordStat> list = searchKeywordStatMapper.selectList(new LambdaQueryWrapper<SearchKeywordStat>()
                .eq(SearchKeywordStat::getStatDate, LocalDate.now())
                .orderByDesc(SearchKeywordStat::getSearchCount)
                .orderByDesc(SearchKeywordStat::getId)
                .last("limit 10"));
        return Result.success(list);
    }

    @Operation(summary = "浏览来源占比")
    @GetMapping("/source-ratio")
    public Result<List<Map<String, Object>>> sourceRatio(@RequestParam(defaultValue = "week") String range) {
        TimeRange tr = resolveRange(range);
        List<Map<String, Object>> raw = dashboardReportMapper.sourceRatio(tr.start, tr.end);
        long searchCount = safeLong(dashboardReportMapper.searchActionCount(tr.start, tr.end));
        return Result.success(normalizeSourceRatio(raw, searchCount));
    }

    @Operation(summary = "运营报表")
    @GetMapping("/report")
    public Result<Map<String, Object>> report(@RequestParam(defaultValue = "week") String range) {
        TimeRange tr = resolveRange(range);
        List<Map<String, Object>> trend = tr.hourly
                ? dashboardReportMapper.browseTrendHourly(tr.start, tr.end)
                : dashboardReportMapper.browseTrendDaily(tr.start, tr.end);
        long searchCount = safeLong(dashboardReportMapper.searchActionCount(tr.start, tr.end));
        List<Map<String, Object>> sources = normalizeSourceRatio(dashboardReportMapper.sourceRatio(tr.start, tr.end), searchCount);
        List<Map<String, Object>> hotKnowledge = dashboardReportMapper.hotKnowledge(tr.start, tr.end);
        List<Map<String, Object>> hotKeywords = dashboardReportMapper.hotKeywords(tr.startDate, tr.endDate);
        long activeUsers = safeLong(dashboardReportMapper.activeUserCount(tr.start, tr.end));
        long actionCount = safeLong(dashboardReportMapper.actionCount(tr.start, tr.end));
        double avgActions = activeUsers == 0 ? 0D : (double) actionCount / activeUsers;

        return Result.success(Map.of(
                "range", tr.name,
                "browseTrend", trend == null ? List.of() : trend,
                "sourceRatio", sources,
                "hotKnowledge", hotKnowledge == null ? List.of() : hotKnowledge,
                "hotKeywords", hotKeywords == null ? List.of() : hotKeywords,
                "active", Map.of(
                        "activeUsers", activeUsers,
                        "actionCount", actionCount,
                        "avgActionsPerUser", Math.round(avgActions * 100.0) / 100.0
                )
        ));
    }

    private List<Map<String, Object>> normalizeSourceRatio(List<Map<String, Object>> raw, long searchCount) {
        Map<String, Long> counter = new LinkedHashMap<>();
        counter.put("recommend", 0L);
        counter.put("search", 0L);
        counter.put("favorite", 0L);
        counter.put("other", 0L);
        if (raw != null) {
            for (Map<String, Object> row : raw) {
                String source = String.valueOf(row.getOrDefault("source", "other")).toLowerCase();
                long cnt = safeLong(row.get("cnt"));
                if (counter.containsKey(source)) {
                    counter.put(source, counter.get(source) + cnt);
                } else {
                    counter.put("other", counter.get("other") + cnt);
                }
            }
        }
        counter.put("search", counter.get("search") + Math.max(0L, searchCount));
        return counter.entrySet().stream()
                .map(e -> Map.<String, Object>of("source", e.getKey(), "count", e.getValue()))
                .toList();
    }

    private long safeLong(Object value) {
        if (value == null) return 0L;
        if (value instanceof Number n) return n.longValue();
        try {
            return Long.parseLong(String.valueOf(value));
        } catch (Exception e) {
            return 0L;
        }
    }

    private TimeRange resolveRange(String range) {
        boolean day = "day".equalsIgnoreCase(range);
        LocalDateTime end = LocalDateTime.now();
        if (day) {
            LocalDateTime start = LocalDate.now().atStartOfDay();
            return new TimeRange("day", start, end, start.toLocalDate(), end.toLocalDate(), true);
        }
        LocalDateTime start = LocalDate.now().minusDays(6).atStartOfDay();
        return new TimeRange("week", start, end, start.toLocalDate(), end.toLocalDate(), false);
    }

    private record TimeRange(String name,
                             LocalDateTime start,
                             LocalDateTime end,
                             LocalDate startDate,
                             LocalDate endDate,
                             boolean hourly) {
    }
}
