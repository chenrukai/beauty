package com.beauty.knowledge.config.security;

import com.beauty.knowledge.common.constant.RedisKeyConstant;
import com.beauty.knowledge.common.util.JwtUtil;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;

@Component
@RequiredArgsConstructor
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;
    private final StringRedisTemplate stringRedisTemplate;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String bearer = request.getHeader("Authorization");
        if (!StringUtils.hasText(bearer) || !bearer.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        String token = bearer.substring(7);
        if (!jwtUtil.validate(token)) {
            writeUnauthorized(response, "Token invalid or expired");
            return;
        }

        Long userId = jwtUtil.getUserId(token);
        String blacklistKey = RedisKeyConstant.userToken(userId);
        String blacklistedToken = stringRedisTemplate.opsForValue().get(blacklistKey);
        // Only reject the exact token that was logged out.
        if (StringUtils.hasText(blacklistedToken) && token.equals(blacklistedToken)) {
            writeUnauthorized(response, "Token has been logged out");
            return;
        }

        String role = jwtUtil.getRole(token);
        String roleCode = role.startsWith("ROLE_") ? role.substring(5) : role;
        UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
                String.valueOf(userId),
                null,
                List.of(new SimpleGrantedAuthority("ROLE_" + roleCode))
        );
        SecurityContextHolder.getContext().setAuthentication(authentication);
        filterChain.doFilter(request, response);
    }

    @Override
    protected boolean shouldNotFilterAsyncDispatch() {
        // SSE/stream endpoints use async dispatch; keep JWT auth for each dispatch.
        return false;
    }

    @Override
    protected boolean shouldNotFilterErrorDispatch() {
        return false;
    }

    private void writeUnauthorized(HttpServletResponse response, String message) throws IOException {
        if (response.isCommitted()) {
            return;
        }
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.getWriter().write("{\"code\":401,\"message\":\"" + message + "\",\"timestamp\":" + System.currentTimeMillis() + "}");
    }
}
