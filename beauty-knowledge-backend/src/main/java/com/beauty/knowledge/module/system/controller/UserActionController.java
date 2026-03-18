package com.beauty.knowledge.module.system.controller;

import com.beauty.knowledge.common.result.Result;
import com.beauty.knowledge.module.system.domain.dto.UserActionDTO;
import com.beauty.knowledge.module.system.service.UserActionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Tag(name = "用户行为")
@RestController
@RequestMapping("/api/user/action")
@RequiredArgsConstructor
public class UserActionController {

    private final UserActionService userActionService;

    @Operation(summary = "记录用户行为")
    @PostMapping
    public Result<Void> record(@Valid @RequestBody UserActionDTO dto, HttpServletRequest request) {
        userActionService.record(dto, request.getRemoteAddr(), request.getHeader("User-Agent"));
        return Result.success();
    }
}

