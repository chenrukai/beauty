package com.beauty.knowledge.common.util;

import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.security.MessageDigest;

public final class FileHashUtil {

    private FileHashUtil() {
    }

    public static String sha256(MultipartFile file) {
        try {
            return sha256(file.getInputStream());
        } catch (Exception ex) {
            throw new IllegalStateException("计算文件哈希失败", ex);
        }
    }

    public static String sha256(byte[] data) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            return toHex(digest.digest(data));
        } catch (Exception ex) {
            throw new IllegalStateException("计算哈希失败", ex);
        }
    }

    public static String sha256(InputStream inputStream) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] buffer = new byte[8192];
            int len;
            while ((len = inputStream.read(buffer)) != -1) {
                digest.update(buffer, 0, len);
            }
            return toHex(digest.digest());
        } catch (Exception ex) {
            throw new IllegalStateException("计算哈希失败", ex);
        }
    }

    private static String toHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder(bytes.length * 2);
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
