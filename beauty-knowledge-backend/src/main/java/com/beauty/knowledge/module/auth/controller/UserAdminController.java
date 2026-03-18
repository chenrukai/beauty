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
import com.beauty.knowledge.module.rag.domain.entity.ChatMessageEntity;
import com.beauty.knowledge.module.rag.domain.entity.ChatSession;
import com.beauty.knowledge.module.rag.mapper.ChatMessageMapper;
import com.beauty.knowledge.module.rag.mapper.ChatSessionMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

@Tag(name = "User Admin")
@RestController
@RequestMapping("/api/admin/user")
@RequiredArgsConstructor
@PreAuthorize("hasRole('admin')")
public class UserAdminController {

    private final SysUserMapper sysUserMapper;
    private final ChatSessionMapper chatSessionMapper;
    private final ChatMessageMapper chatMessageMapper;

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
                .in(SysUser::getRole, "admin", "user")
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
        if ("admin".equalsIgnoreCase(user.getRole()) && status == 0) {
            Long enabledAdminCount = sysUserMapper.selectCount(new LambdaQueryWrapper<SysUser>()
                    .eq(SysUser::getRole, "admin")
                    .eq(SysUser::getStatus, 1));
            if (enabledAdminCount != null && enabledAdminCount <= 1) {
                throw new BusinessException(ErrorCode.BAD_REQUEST, "cannot disable the last enabled admin");
            }
        }
        user.setStatus(status);
        sysUserMapper.updateById(user);
        return Result.success();
    }

    @Operation(summary = "Update user role")
    @PutMapping("/{id}/role")
    public Result<Void> updateRole(@PathVariable Long id, @RequestParam String role) {
        String normalizedRole = role == null ? "" : role.trim().toLowerCase();
        if (!"admin".equals(normalizedRole) && !"user".equals(normalizedRole)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "role must be admin or user");
        }

        SysUser user = sysUserMapper.selectById(id);
        if (user == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "user not found");
        }

        String currentRole = user.getRole() == null ? "user" : user.getRole().toLowerCase();
        if (currentRole.equals(normalizedRole)) {
            return Result.success();
        }

        if ("admin".equals(currentRole) && "user".equals(normalizedRole)) {
            Long adminCount = sysUserMapper.selectCount(new LambdaQueryWrapper<SysUser>()
                    .eq(SysUser::getRole, "admin"));
            if (adminCount != null && adminCount <= 1) {
                throw new BusinessException(ErrorCode.BAD_REQUEST, "must keep at least one admin account");
            }

            // If this admin is enabled, also ensure at least one enabled admin remains.
            Long enabledAdminCount = sysUserMapper.selectCount(new LambdaQueryWrapper<SysUser>()
                    .eq(SysUser::getRole, "admin")
                    .eq(SysUser::getStatus, 1));
            if (user.getStatus() != null && user.getStatus() == 1
                    && enabledAdminCount != null && enabledAdminCount <= 1) {
                throw new BusinessException(ErrorCode.BAD_REQUEST, "cannot downgrade the last enabled admin");
            }
        }

        user.setRole(normalizedRole);
        sysUserMapper.updateById(user);
        return Result.success();
    }

    @Operation(summary = "Prune users to admin and user only")
    @PostMapping("/prune-core")
    @Transactional(rollbackFor = Exception.class)
    public Result<Map<String, Integer>> pruneCoreUsers() {
        Set<String> keepUsernames = Set.of("admin", "user");
        List<SysUser> allUsers = sysUserMapper.selectList(new LambdaQueryWrapper<SysUser>()
                .orderByAsc(SysUser::getId));

        List<SysUser> removeUsers = allUsers.stream()
                .filter(u -> !keepUsernames.contains((u.getUsername() == null ? "" : u.getUsername()).toLowerCase()))
                .toList();

        if (removeUsers.isEmpty()) {
            return Result.success(Map.of("removedUsers", 0, "removedSessions", 0, "removedMessages", 0));
        }

        Set<Long> removeUserIds = removeUsers.stream().map(SysUser::getId).collect(Collectors.toSet());
        List<ChatSession> sessions = chatSessionMapper.selectList(new LambdaQueryWrapper<ChatSession>()
                .in(ChatSession::getUserId, removeUserIds));
        List<Long> sessionIds = sessions.stream().map(ChatSession::getId).toList();

        int removedMessages = 0;
        if (!sessionIds.isEmpty()) {
            removedMessages = chatMessageMapper.delete(new LambdaQueryWrapper<ChatMessageEntity>()
                    .in(ChatMessageEntity::getSessionId, sessionIds));
        }

        int removedSessions = 0;
        if (!removeUserIds.isEmpty()) {
            removedSessions = chatSessionMapper.delete(new LambdaQueryWrapper<ChatSession>()
                    .in(ChatSession::getUserId, removeUserIds));
        }

        int removedUsers = 0;
        if (!removeUserIds.isEmpty()) {
            removedUsers = sysUserMapper.delete(new LambdaQueryWrapper<SysUser>()
                    .in(SysUser::getId, removeUserIds));
        }

        return Result.success(Map.of(
                "removedUsers", removedUsers,
                "removedSessions", removedSessions,
                "removedMessages", removedMessages
        ));
    }
}
