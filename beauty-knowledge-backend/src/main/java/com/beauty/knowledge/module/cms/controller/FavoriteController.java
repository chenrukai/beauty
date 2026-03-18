package com.beauty.knowledge.module.cms.controller;

import com.beauty.knowledge.common.result.PageResult;
import com.beauty.knowledge.common.result.Result;
import com.beauty.knowledge.module.cms.domain.vo.FavoriteKnowledgeVO;
import com.beauty.knowledge.module.cms.service.FavoriteService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@Tag(name = "收藏管理")
@RestController
@RequestMapping("/api/user/favorite")
@RequiredArgsConstructor
public class FavoriteController {

    private final FavoriteService favoriteService;

    @Operation(summary = "收藏知识")
    @PostMapping("/{knowledgeId}")
    public Result<Void> add(@PathVariable Long knowledgeId) {
        favoriteService.addFavorite(knowledgeId);
        return Result.success();
    }

    @Operation(summary = "取消收藏")
    @DeleteMapping("/{knowledgeId}")
    public Result<Void> remove(@PathVariable Long knowledgeId) {
        favoriteService.removeFavorite(knowledgeId);
        return Result.success();
    }

    @Operation(summary = "我的收藏分页")
    @GetMapping("/page")
    public Result<PageResult<FavoriteKnowledgeVO>> page(@RequestParam(defaultValue = "1") Long pageNum,
                                                         @RequestParam(defaultValue = "10") Long pageSize,
                                                         @RequestParam(required = false) String keyword) {
        return Result.success(favoriteService.pageFavorites(pageNum, pageSize, keyword));
    }
}
