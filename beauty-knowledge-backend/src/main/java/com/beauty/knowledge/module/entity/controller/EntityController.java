package com.beauty.knowledge.module.entity.controller;

import com.beauty.knowledge.common.result.Result;
import com.beauty.knowledge.module.entity.domain.dto.EntityConfirmRequest;
import com.beauty.knowledge.module.entity.domain.dto.EntityExtractRequest;
import com.beauty.knowledge.module.entity.domain.entity.BeautyEffect;
import com.beauty.knowledge.module.entity.domain.entity.BeautyIngredient;
import com.beauty.knowledge.module.entity.domain.entity.BeautyProduct;
import com.beauty.knowledge.module.entity.domain.entity.EntityExtractPending;
import com.beauty.knowledge.module.entity.service.EffectService;
import com.beauty.knowledge.module.entity.service.EntityConfirmService;
import com.beauty.knowledge.module.entity.service.EntityExtractService;
import com.beauty.knowledge.module.entity.service.IngredientService;
import com.beauty.knowledge.module.entity.service.ProductService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@Tag(name = "实体管理")
@RestController
@RequestMapping("/api/entity")
@RequiredArgsConstructor
public class EntityController {

    private final IngredientService ingredientService;
    private final EffectService effectService;
    private final ProductService productService;
    private final EntityExtractService entityExtractService;
    private final EntityConfirmService entityConfirmService;

    @Operation(summary = "成分列表")
    @GetMapping("/ingredient")
    public Result<List<BeautyIngredient>> ingredientList(@RequestParam(required = false) String keyword) {
        return Result.success(ingredientService.list(keyword));
    }

    @Operation(summary = "新增成分")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/ingredient")
    public Result<Void> ingredientSave(@RequestBody BeautyIngredient entity) {
        ingredientService.save(entity);
        return Result.success();
    }

    @Operation(summary = "修改成分")
    @PreAuthorize("hasRole('admin')")
    @PutMapping("/ingredient/{id}")
    public Result<Void> ingredientUpdate(@PathVariable Long id, @RequestBody BeautyIngredient entity) {
        ingredientService.update(id, entity);
        return Result.success();
    }

    @Operation(summary = "删除成分")
    @PreAuthorize("hasRole('admin')")
    @DeleteMapping("/ingredient/{id}")
    public Result<Void> ingredientDelete(@PathVariable Long id) {
        ingredientService.delete(id);
        return Result.success();
    }

    @Operation(summary = "功效列表")
    @GetMapping("/effect")
    public Result<List<BeautyEffect>> effectList(@RequestParam(required = false) String keyword) {
        return Result.success(effectService.list(keyword));
    }

    @Operation(summary = "新增功效")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/effect")
    public Result<Void> effectSave(@RequestBody BeautyEffect entity) {
        effectService.save(entity);
        return Result.success();
    }

    @Operation(summary = "修改功效")
    @PreAuthorize("hasRole('admin')")
    @PutMapping("/effect/{id}")
    public Result<Void> effectUpdate(@PathVariable Long id, @RequestBody BeautyEffect entity) {
        effectService.update(id, entity);
        return Result.success();
    }

    @Operation(summary = "删除功效")
    @PreAuthorize("hasRole('admin')")
    @DeleteMapping("/effect/{id}")
    public Result<Void> effectDelete(@PathVariable Long id) {
        effectService.delete(id);
        return Result.success();
    }

    @Operation(summary = "产品列表")
    @GetMapping("/product")
    public Result<List<BeautyProduct>> productList(@RequestParam(required = false) String keyword) {
        return Result.success(productService.list(keyword));
    }

    @Operation(summary = "新增产品")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/product")
    public Result<Void> productSave(@RequestBody BeautyProduct entity) {
        productService.save(entity);
        return Result.success();
    }

    @Operation(summary = "修改产品")
    @PreAuthorize("hasRole('admin')")
    @PutMapping("/product/{id}")
    public Result<Void> productUpdate(@PathVariable Long id, @RequestBody BeautyProduct entity) {
        productService.update(id, entity);
        return Result.success();
    }

    @Operation(summary = "删除产品")
    @PreAuthorize("hasRole('admin')")
    @DeleteMapping("/product/{id}")
    public Result<Void> productDelete(@PathVariable Long id) {
        productService.delete(id);
        return Result.success();
    }

    @Operation(summary = "待确认实体列表")
    @PreAuthorize("hasRole('admin')")
    @GetMapping("/pending")
    public Result<List<EntityExtractPending>> pendingList(@RequestParam(required = false) String status) {
        return Result.success(entityExtractService.pendingList(status));
    }

    @Operation(summary = "待确认数量")
    @PreAuthorize("hasRole('admin')")
    @GetMapping("/pending/count")
    public Result<Map<String, Long>> pendingCount(@RequestParam(required = false) String status) {
        return Result.success(Map.of("count", entityExtractService.pendingCount(status)));
    }

    @Operation(summary = "批量确认实体")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/confirm")
    public Result<Void> confirm(@Valid @RequestBody EntityConfirmRequest request) {
        entityConfirmService.confirmBatch(request.getItems());
        return Result.success();
    }

    @Operation(summary = "执行实体抽取")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/extract")
    public Result<Void> extract(@Valid @RequestBody EntityExtractRequest request) {
        entityExtractService.extractByText(request.getFileId(), request.getText());
        return Result.success();
    }
}
