package com.beauty.knowledge.common.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Slf4j
@Component
public class JwtUtil {

    @Value("${beauty.jwt.secret}")
    private String secret;

    @Value("${beauty.jwt.expire-in-seconds}")
    private long expireInSeconds;

    @PostConstruct
    public void validateConfig() {
        if (secret == null || secret.isBlank()) {
            throw new IllegalStateException("beauty.jwt.secret is empty. Set BEAUTY_JWT_SECRET before starting application.");
        }
        if (secret.getBytes(StandardCharsets.UTF_8).length < 32) {
            throw new IllegalStateException("beauty.jwt.secret must be at least 32 bytes.");
        }
    }

    public String generateToken(Long userId, String role) {
        Date now = new Date();
        Date expireAt = new Date(now.getTime() + expireInSeconds * 1000);
        return Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("role", role)
                .issuedAt(now)
                .expiration(expireAt)
                .signWith(secretKey())
                .compact();
    }

    public Claims parseToken(String token) {
        return Jwts.parser()
                .verifyWith(secretKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    public boolean validate(String token) {
        try {
            parseToken(token);
            return true;
        } catch (Exception ex) {
            return false;
        }
    }

    public Long getUserId(String token) {
        return Long.parseLong(parseToken(token).getSubject());
    }

    public String getRole(String token) {
        return String.valueOf(parseToken(token).get("role"));
    }

    public long getRemainingExpire(String token) {
        Date expiration = parseToken(token).getExpiration();
        return Math.max(expiration.getTime() - System.currentTimeMillis(), 0);
    }

    private SecretKey secretKey() {
        return Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }
}
