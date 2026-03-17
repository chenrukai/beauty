package com.beauty.knowledge.common.util;

import com.beauty.knowledge.common.exception.BusinessException;
import com.beauty.knowledge.common.exception.ErrorCode;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

public final class SecurityUtil {

    private SecurityUtil() {
    }

    public static Long getCurrentUserId() {
        Authentication authentication = getAuthentication();
        try {
            return Long.parseLong(authentication.getName());
        } catch (NumberFormatException ex) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED);
        }
    }

    public static String getCurrentUserRole() {
        Authentication authentication = getAuthentication();
        return authentication.getAuthorities().stream()
                .findFirst()
                .map(grantedAuthority -> grantedAuthority.getAuthority())
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED));
    }

    public static boolean isAdmin() {
        return "ROLE_ADMIN".equalsIgnoreCase(getCurrentUserRole());
    }

    private static Authentication getAuthentication() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated() || authentication instanceof AnonymousAuthenticationToken) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED);
        }
        return authentication;
    }
}
