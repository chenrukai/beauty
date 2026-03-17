package com.beauty.knowledge.module.entity.controller;

import com.beauty.knowledge.common.result.Result;
import com.beauty.knowledge.module.entity.domain.dto.RelationBindDTO;
import com.beauty.knowledge.module.entity.domain.entity.RelIngredientEffect;
import com.beauty.knowledge.module.entity.domain.entity.RelProductIngredient;
import com.beauty.knowledge.module.entity.service.RelationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@Tag(name = "关系管理")
@RestController
@RequestMapping("/api/entity/relation")
@RequiredArgsConstructor
public class RelationController {

    private final RelationService relationService;

    @Operation(summary = "绑定成分-功效")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/ingredient-effect")
    public Result<Void> bindIngredientEffect(@Valid @RequestBody RelationBindDTO dto) {
        relationService.bindIngredientEffect(dto.getLeftId(), dto.getRightId());
        return Result.success();
    }

    @Operation(summary = "解绑成分-功效")
    @PreAuthorize("hasRole('admin')")
    @DeleteMapping("/ingredient-effect")
    public Result<Void> unbindIngredientEffect(@RequestParam Long ingredientId, @RequestParam Long effectId) {
        relationService.unbindIngredientEffect(ingredientId, effectId);
        return Result.success();
    }

    @Operation(summary = "成分-功效关系列表")
    @GetMapping("/ingredient-effect")
    public Result<List<RelIngredientEffect>> ingredientEffectList(@RequestParam(required = false) Long ingredientId) {
        return Result.success(relationService.listIngredientEffects(ingredientId));
    }

    @Operation(summary = "绑定产品-成分")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/product-ingredient")
    public Result<Void> bindProductIngredient(@Valid @RequestBody RelationBindDTO dto) {
        relationService.bindProductIngredient(dto.getLeftId(), dto.getRightId(), dto.getConcentration());
        return Result.success();
    }

    @Operation(summary = "解绑产品-成分")
    @PreAuthorize("hasRole('admin')")
    @DeleteMapping("/product-ingredient")
    public Result<Void> unbindProductIngredient(@RequestParam Long productId, @RequestParam Long ingredientId) {
        relationService.unbindProductIngredient(productId, ingredientId);
        return Result.success();
    }

    @Operation(summary = "产品-成分关系列表")
    @GetMapping("/product-ingredient")
    public Result<List<RelProductIngredient>> productIngredientList(@RequestParam(required = false) Long productId) {
        return Result.success(relationService.listProductIngredients(productId));
    }
}
