package com.beauty.knowledge.module.auth.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.module.auth.domain.entity.SysUser;
import com.beauty.knowledge.module.auth.mapper.SysUserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.DisabledException;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserDetailsServiceImpl implements UserDetailsService {

    private final SysUserMapper sysUserMapper;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        SysUser user = sysUserMapper.selectOne(new LambdaQueryWrapper<SysUser>()
                .eq(SysUser::getUsername, username)
                .last("limit 1"));

        if (user == null) {
            throw new UsernameNotFoundException("用户名或密码错误");
        }
        if (user.getStatus() != null && user.getStatus() == 0) {
            throw new DisabledException("账号已禁用");
        }

        String roleCode = user.getRole() == null ? "user" : user.getRole();
        roleCode = roleCode.startsWith("ROLE_") ? roleCode.substring(5) : roleCode;

        return User.withUsername(String.valueOf(user.getId()))
                .password(user.getPassword())
                .roles(roleCode.toUpperCase())
                .build();
    }
}