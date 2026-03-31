package com.beauty.knowledge.module.kg.controller;

import com.beauty.knowledge.common.result.Result;
import com.beauty.knowledge.common.util.SecurityUtil;
import com.beauty.knowledge.module.entity.domain.entity.EntityExtractPending;
import com.beauty.knowledge.module.kg.domain.dto.KgReviewRequest;
import com.beauty.knowledge.module.kg.domain.vo.KgEvidenceVO;
import com.beauty.knowledge.module.kg.domain.vo.KgGraphVO;
import com.beauty.knowledge.module.kg.domain.vo.KgBackfillResultVO;
import com.beauty.knowledge.module.kg.domain.vo.KgPendingViewVO;
import com.beauty.knowledge.module.kg.domain.vo.KgPathVO;
import com.beauty.knowledge.module.kg.service.KgExtractionService;
import com.beauty.knowledge.module.kg.service.KgMaintenanceService;
import com.beauty.knowledge.module.kg.service.KgQueryService;
import com.beauty.knowledge.module.kg.service.KgReviewService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@Tag(name = "Knowledge Graph")
@RestController
@RequestMapping("/api/kg")
@RequiredArgsConstructor
public class KgController {

    private final KgExtractionService kgExtractionService;
    private final KgReviewService kgReviewService;
    private final KgQueryService kgQueryService;
    private final KgMaintenanceService kgMaintenanceService;

    @Operation(summary = "Trigger extraction from file")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/extract/file/{fileId}")
    public Result<Map<String, Object>> extractByFile(@PathVariable Long fileId) {
        return Result.success(kgExtractionService.extractByFileId(fileId));
    }

    @Operation(summary = "Get extraction strategy config")
    @PreAuthorize("hasRole('admin')")
    @GetMapping("/config/extraction")
    public Result<Map<String, Object>> extractionConfig() {
        return Result.success(kgExtractionService.extractionConfig());
    }

    @Operation(summary = "List pending KG candidates")
    @PreAuthorize("hasRole('admin')")
    @GetMapping("/pending")
    public Result<List<KgPendingViewVO>> pending(@RequestParam(required = false) String status) {
        return Result.success(kgReviewService.listPending(status));
    }

    @Operation(summary = "Confirm one pending candidate")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/pending/{id}/confirm")
    public Result<Map<String, Object>> confirm(@PathVariable Long id,
                                               @RequestBody(required = false) KgReviewRequest request) {
        EntityExtractPending row = kgReviewService.confirmPending(id, SecurityUtil.getCurrentUserId(), request == null ? null : request.getComment());
        return Result.success(Map.of(
                "id", row.getId(),
                "status", row.getStatus()
        ));
    }

    @Operation(summary = "Reject one pending candidate")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/pending/{id}/reject")
    public Result<Map<String, Object>> reject(@PathVariable Long id,
                                              @RequestBody(required = false) KgReviewRequest request) {
        EntityExtractPending row = kgReviewService.rejectPending(id, SecurityUtil.getCurrentUserId(), request == null ? null : request.getComment());
        return Result.success(Map.of(
                "id", row.getId(),
                "status", row.getStatus()
        ));
    }

    @Operation(summary = "Get product graph")
    @GetMapping("/product/{id}/graph")
    public Result<KgGraphVO> productGraph(@PathVariable Long id) {
        return Result.success(kgQueryService.getProductGraph(id));
    }

    @Operation(summary = "Get neighbors by entity id and type")
    @GetMapping("/entity/{id}/neighbors")
    public Result<KgGraphVO> neighbors(@PathVariable Long id,
                                       @RequestParam(name = "type", required = false) String type) {
        return Result.success(kgQueryService.getNeighbors(id, type));
    }

    @Operation(summary = "Find path between two entities")
    @GetMapping("/path")
    public Result<KgPathVO> path(@RequestParam String fromType,
                                 @RequestParam Long fromId,
                                 @RequestParam String toType,
                                 @RequestParam Long toId,
                                 @RequestParam(required = false) Integer maxDepth) {
        return Result.success(kgQueryService.findPath(fromType, fromId, toType, toId, maxDepth));
    }

    @Operation(summary = "Query relation evidence")
    @GetMapping("/evidence")
    public Result<List<KgEvidenceVO>> evidence(@RequestParam String predicate,
                                               @RequestParam(required = false) String subjectType,
                                               @RequestParam(required = false) Long subjectId,
                                               @RequestParam(required = false) String objectType,
                                               @RequestParam(required = false) Long objectId,
                                               @RequestParam(required = false) Integer size) {
        return Result.success(kgQueryService.relationEvidence(predicate, subjectType, subjectId, objectType, objectId, size));
    }

    @Operation(summary = "Backfill missing evidence for existing relations")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/evidence/backfill")
    public Result<KgBackfillResultVO> backfillEvidence(@RequestParam(required = false) Integer limit) {
        return Result.success(kgMaintenanceService.backfillEvidence(limit));
    }
}
