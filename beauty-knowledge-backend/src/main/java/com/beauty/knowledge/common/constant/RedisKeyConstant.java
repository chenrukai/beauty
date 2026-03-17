package com.beauty.knowledge.common.constant;

public interface RedisKeyConstant {

    long TOKEN_TTL_SECONDS = 86400L;

    String CHAT_SESSION_TEMPLATE = "chat:session:%d";
    String USER_TOKEN_TEMPLATE = "user:token:%d";
    String KNOWLEDGE_HOT_TEMPLATE = "knowledge:hot:%d";
    String FILE_HASH_TEMPLATE = "file:hash:%s";
    String TASK_STATUS_TEMPLATE = "task:status:%d";
    String CATEGORY_TREE_KEY = "category:tree";
    String RATE_LIMIT_CHAT_TEMPLATE = "rate:chat:%d";

    static String chatSession(long userId) {
        return CHAT_SESSION_TEMPLATE.formatted(userId);
    }

    static String userToken(long userId) {
        return USER_TOKEN_TEMPLATE.formatted(userId);
    }

    static String knowledgeHot(long knowledgeId) {
        return KNOWLEDGE_HOT_TEMPLATE.formatted(knowledgeId);
    }

    static String fileHash(String hash) {
        return FILE_HASH_TEMPLATE.formatted(hash);
    }

    static String taskStatus(long taskId) {
        return TASK_STATUS_TEMPLATE.formatted(taskId);
    }

    static String rateLimitChat(long userId) {
        return RATE_LIMIT_CHAT_TEMPLATE.formatted(userId);
    }
}
