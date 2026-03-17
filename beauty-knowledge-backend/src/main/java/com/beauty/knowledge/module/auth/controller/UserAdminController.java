package com.beauty.knowledge.module.auth.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.common.result.PageResult;
import com.beauty.knowledge.common.result.Result;
import com.beauty.knowledge.common.util.SecurityUtil;
import com.beauty.knowledge.module.auth.domain.entity.SysUser;
import com.beauty.knowledge.module.auth.mapper.SysUserMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@Tag(name = "User Admin")
@RestController
@RequestMapping("/api/admin/user")
@RequiredArgsConstructor
@PreAuthorize("hasRole('admin')")
public class UserAdminController {

    private final SysUserMapper sysUserMapper;

    @Operation(summary = "User pagination")
    @GetMapping("/page")
    public Result<PageResult<SysUser>> page(@RequestParam(defaultValue = "1") Long pageNum,
                                            @RequestParam(defaultValue = "20") Long pageSize,
                                            @RequestParam(required = false) String keyword,
                                            @RequestParam(required = false) String role,
                                            @RequestParam(required = false) Integer status) {
        Page<SysUser> page = new Page<>(pageNum, pageSize);
        LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
        wrapper.and(StringUtils.hasText(keyword), q -> q
                        .like(SysUser::getUsername, keyword)
                        .or()
                        .like(SysUser::getNickname, keyword))
                .eq(StringUtils.hasText(role), SysUser::getRole, role)
                .eq(status != null, SysUser::getStatus, status)
                .orderByDesc(SysUser::getId);
        return Result.success(PageResult.of(sysUserMapper.selectPage(page, wrapper)));
    }

    @Operation(summary = "Update user status")
    @PutMapping("/{id}/status")
    public Result<Void> updateStatus(@PathVariable Long id, @RequestParam Integer status) {
        if (status == null || (status != 0 && status != 1)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "status must be 0 or 1");
        }
        Long currentUserId = SecurityUtil.getCurrentUserId();
        if (id.equals(currentUserId) && status == 0) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "cannot disable current admin");
        }
        SysUser user = sysUserMapper.selectById(id);
        if (user == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "user not found");
        }
        user.setStatus(status);
        sysUserMapper.updateById(user);
        return Result.success();
    }
}
