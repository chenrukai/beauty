package com.beauty.knowledge.module.system.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.result.PageResult;
import com.beauty.knowledge.common.result.Result;
import com.beauty.knowledge.module.system.domain.dto.NoticeSaveDTO;
import com.beauty.knowledge.module.system.domain.entity.SysNotice;
import com.beauty.knowledge.module.system.mapper.SysNoticeMapper;
import com.beauty.knowledge.module.system.service.NoticeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.List;

@Tag(name = "公告管理")
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class NoticeController {

    private final NoticeService noticeService;
    private final SysNoticeMapper noticeMapper;

    @Operation(summary = "管理员分页查询公告")
    @PreAuthorize("hasRole('admin')")
    @GetMapping("/admin/notice/page")
    public Result<PageResult<SysNotice>> page(@RequestParam(defaultValue = "1") Long pageNum,
                                               @RequestParam(defaultValue = "10") Long pageSize,
                                               @RequestParam(required = false) Integer status,
                                               @RequestParam(required = false) String keyword) {
        return Result.success(noticeService.page(pageNum, pageSize, status, keyword));
    }

    @Operation(summary = "新增公告")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/admin/notice")
    public Result<Void> save(@Valid @RequestBody NoticeSaveDTO dto) {
        noticeService.save(dto);
        return Result.success();
    }

    @Operation(summary = "更新公告")
    @PreAuthorize("hasRole('admin')")
    @PutMapping("/admin/notice/{id}")
    public Result<Void> update(@PathVariable Long id, @Valid @RequestBody NoticeSaveDTO dto) {
        noticeService.update(id, dto);
        return Result.success();
    }

    @Operation(summary = "设置置顶")
    @PreAuthorize("hasRole('admin')")
    @PutMapping("/admin/notice/{id}/top")
    public Result<Void> setTop(@PathVariable Long id, @RequestParam Integer isTop) {
        noticeService.setTop(id, isTop);
        return Result.success();
    }

    @Operation(summary = "用户端公告列表")
    @GetMapping("/notice/list")
    public Result<List<SysNotice>> list(@RequestParam(defaultValue = "5") Integer size) {
        int limit = Math.max(1, Math.min(size, 20));
        List<SysNotice> list = noticeMapper.selectList(new LambdaQueryWrapper<SysNotice>()
                .eq(SysNotice::getStatus, 1)
                .and(w -> w.isNull(SysNotice::getExpireTime).or().gt(SysNotice::getExpireTime, LocalDateTime.now()))
                .orderByDesc(SysNotice::getIsTop)
                .orderByDesc(SysNotice::getPublishTime)
                .last("limit " + limit));
        return Result.success(list);
    }
}

