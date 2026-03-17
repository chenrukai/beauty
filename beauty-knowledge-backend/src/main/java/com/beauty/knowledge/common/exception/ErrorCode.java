package com.beauty.knowledge.common.exception;

import com.beauty.knowledge.common.result.ResultCode;
import lombok.Getter;

@Getter
public enum ErrorCode {

    BAD_REQUEST(ResultCode.BAD_REQUEST),
    UNAUTHORIZED(ResultCode.UNAUTHORIZED),
    FORBIDDEN(ResultCode.FORBIDDEN),
    NOT_FOUND(ResultCode.NOT_FOUND),
    INTERNAL_ERROR(ResultCode.INTERNAL_ERROR),

    FILE_HASH_DUPLICATE(ResultCode.FILE_HASH_DUPLICATE),
    FILE_PROCESSING(ResultCode.FILE_PROCESSING),
    KNOWLEDGE_NOT_FOUND(ResultCode.KNOWLEDGE_NOT_FOUND),
    ENTITY_NAME_EXISTS(ResultCode.ENTITY_NAME_EXISTS),
    CATEGORY_HAS_CHILDREN(ResultCode.CATEGORY_HAS_CHILDREN),
    AI_SERVICE_UNAVAILABLE(ResultCode.AI_SERVICE_UNAVAILABLE);

    private final Integer code;
    private final String message;

    ErrorCode(ResultCode resultCode) {
        this.code = resultCode.getCode();
        this.message = resultCode.getMessage();
    }
}
