package com.beauty.knowledge.module.auth.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.beauty.knowledge.common.constant.RedisKeyConstant;
import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import com.beauty.knowledge.common.util.JwtUtil;
import com.beauty.knowledge.common.util.SecurityUtil;
import com.beauty.knowledge.module.auth.domain.dto.LoginRequest;
import com.beauty.knowledge.module.auth.domain.dto.RegisterRequest;
import com.beauty.knowledge.module.auth.domain.entity.SysUser;
import com.beauty.knowledge.module.auth.domain.vo.LoginResponse;
import com.beauty.knowledge.module.auth.domain.vo.UserInfoVO;
import com.beauty.knowledge.module.auth.mapper.SysUserMapper;
import com.beauty.knowledge.module.auth.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private static final String LOGIN_FAIL_MESSAGE = "Invalid username or password";

    private final SysUserMapper sysUserMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final StringRedisTemplate stringRedisTemplate;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public LoginResponse login(LoginRequest request) {
        SysUser user = sysUserMapper.selectOne(new LambdaQueryWrapper<SysUser>()
                .eq(SysUser::getUsername, request.getUsername())
                .last("limit 1"));

        if (user == null || !passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, LOGIN_FAIL_MESSAGE);
        }

        if (user.getStatus() != null && user.getStatus() == 0) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "Account is disabled");
        }

        String token = jwtUtil.generateToken(user.getId(), user.getRole());
        return LoginResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .expireIn(86400L)
                .userInfo(UserInfoVO.builder()
                        .id(user.getId())
                        .username(user.getUsername())
                        .nickname(user.getNickname())
                        .role(user.getRole())
                        .build())
                .build();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void register(RegisterRequest request) {
        SysUser exist = sysUserMapper.selectOne(new LambdaQueryWrapper<SysUser>()
                .eq(SysUser::getUsername, request.getUsername())
                .last("limit 1"));
        if (exist != null) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "Username already exists");
        }

        SysUser user = new SysUser();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setNickname(request.getUsername());
        user.setRole("user");
        user.setStatus(1);
        sysUserMapper.insert(user);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void logout(String bearerToken) {
        if (!StringUtils.hasText(bearerToken) || !bearerToken.startsWith("Bearer ")) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED);
        }

        String token = bearerToken.substring(7);
        if (!jwtUtil.validate(token)) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED);
        }

        Long userId = jwtUtil.getUserId(token);
        long remainingMillis = jwtUtil.getRemainingExpire(token);
        if (remainingMillis > 0) {
            stringRedisTemplate.opsForValue().set(RedisKeyConstant.userToken(userId), token, Duration.ofMillis(remainingMillis));
        }
    }

    @Override
    public UserInfoVO getInfo() {
        Long userId = SecurityUtil.getCurrentUserId();
        SysUser user = sysUserMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED);
        }

        return UserInfoVO.builder()
                .id(user.getId())
                .username(user.getUsername())
                .nickname(user.getNickname())
                .role(user.getRole())
                .build();
    }
}
