package com.beauty.knowledge.common.result;

import lombok.Getter;

@Getter
public enum ResultCode {

    SUCCESS(200, "success"),
    BAD_REQUEST(400, "请求参数错误"),
    UNAUTHORIZED(401, "未登录或Token过期"),
    FORBIDDEN(403, "无权限访问"),
    NOT_FOUND(404, "资源不存在"),
    INTERNAL_ERROR(500, "服务器内部错误"),

    FILE_HASH_DUPLICATE(1001, "文件重复上传"),
    FILE_PROCESSING(1002, "任务处理中，暂不可操作"),
    KNOWLEDGE_NOT_FOUND(1003, "知识不存在"),
    ENTITY_NAME_EXISTS(1004, "实体名称已存在"),
    CATEGORY_HAS_CHILDREN(1005, "分类下存在子节点或内容"),
    AI_SERVICE_UNAVAILABLE(1006, "AI服务不可用");

    private final Integer code;
    private final String message;

    ResultCode(Integer code, String message) {
        this.code = code;
        this.message = message;
    }
}
