package com.beauty.knowledge.common.exception;

import com.beauty.knowledge.common.result.Result;
import jakarta.validation.ConstraintViolationException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DataAccessException;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.jdbc.BadSqlGrammarException;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.validation.BindException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusinessException(BusinessException ex) {
        return Result.fail(ex.getCode(), ex.getMessage());
    }

    @ExceptionHandler({MethodArgumentNotValidException.class, BindException.class, ConstraintViolationException.class, HttpMessageNotReadableException.class})
    public Result<Void> handleValidationException(Exception ex) {
        String msg = ex.getMessage();
        if (ex instanceof MethodArgumentNotValidException validEx && validEx.getBindingResult().hasFieldErrors()) {
            msg = validEx.getBindingResult().getFieldErrors().get(0).getDefaultMessage();
        }
        return Result.fail(ErrorCode.BAD_REQUEST.getCode(), msg == null || msg.isBlank() ? ErrorCode.BAD_REQUEST.getMessage() : msg);
    }

    @ExceptionHandler(AuthenticationException.class)
    public Result<Void> handleAuthenticationException(AuthenticationException ex) {
        return Result.fail(ErrorCode.UNAUTHORIZED.getCode(), ErrorCode.UNAUTHORIZED.getMessage());
    }

    @ExceptionHandler(AccessDeniedException.class)
    public Result<Void> handleAccessDeniedException(AccessDeniedException ex) {
        return Result.fail(ErrorCode.FORBIDDEN.getCode(), ErrorCode.FORBIDDEN.getMessage());
    }

    @ExceptionHandler(BadSqlGrammarException.class)
    public Result<Void> handleBadSqlGrammar(BadSqlGrammarException ex) {
        log.error("Bad SQL grammar", ex);
        return Result.fail(
                ErrorCode.INTERNAL_ERROR.getCode(),
                "数据库结构未同步，请执行 sql/migration_v2_kg_incremental.sql 后重试"
        );
    }

    @ExceptionHandler(DataAccessException.class)
    public Result<Void> handleDataAccessException(DataAccessException ex) {
        log.error("Database access exception", ex);
        return Result.fail(
                ErrorCode.INTERNAL_ERROR.getCode(),
                "数据库访问异常，请稍后重试"
        );
    }

    @ExceptionHandler(Exception.class)
    public Result<Void> handleException(Exception ex) {
        log.error("Unhandled exception", ex);
        return Result.fail(ErrorCode.INTERNAL_ERROR.getCode(), ErrorCode.INTERNAL_ERROR.getMessage());
    }
}
