package com.beauty.knowledge.module.cms.controller;

import com.beauty.knowledge.common.result.Result;
import com.beauty.knowledge.infrastructure.ai.python.PythonAIClient;
import com.beauty.knowledge.module.cms.domain.vo.FileUploadVO;
import com.beauty.knowledge.module.cms.domain.vo.ProcessTaskViewVO;
import com.beauty.knowledge.module.cms.service.FileService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@Tag(name = "文件管理")
@RestController
@RequestMapping("/api/file")
@RequiredArgsConstructor
public class FileController {

    private final FileService fileService;
    private final PythonAIClient pythonAIClient;

    @Operation(summary = "上传文件并入队")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/upload")
    public Result<FileUploadVO> upload(@RequestParam("file") MultipartFile file,
                                       @RequestParam("knowledgeId") Long knowledgeId,
                                       @RequestParam(value = "categoryId", required = false) Long categoryId,
                                       @RequestParam(value = "fileType", required = false) String fileType) {
        return Result.success(fileService.upload(file, knowledgeId, categoryId, fileType));
    }

    @Operation(summary = "查询任务详情")
    @GetMapping("/task/{taskId}")
    public Result<ProcessTaskViewVO> getTask(@PathVariable Long taskId) {
        return Result.success(fileService.getTask(taskId));
    }

    @Operation(summary = "查询最近任务")
    @GetMapping("/task/recent")
    public Result<List<ProcessTaskViewVO>> recentTasks(@RequestParam(value = "size", required = false) Integer size) {
        return Result.success(fileService.recentTasks(size));
    }

    @Operation(summary = "重试任务")
    @PreAuthorize("hasRole('admin')")
    @PostMapping("/task/{taskId}/retry")
    public Result<Void> retry(@PathVariable Long taskId) {
        fileService.retry(taskId);
        return Result.success();
    }

    @Operation(summary = "删除文件")
    @PreAuthorize("hasRole('admin')")
    @DeleteMapping("/{fileId}")
    public Result<Void> remove(@PathVariable Long fileId) {
        fileService.remove(fileId);
        return Result.success();
    }

    @Operation(summary = "视频转写能力检测")
    @PreAuthorize("hasRole('admin')")
    @GetMapping("/capability/transcribe")
    public Result<Map<String, Object>> transcribeCapability() {
        boolean ok = pythonAIClient.transcribeHealthCheck();
        String message = ok
                ? "视频转写服务可用"
                : "视频转写服务不可用：请检查 Python transcribe 接口与 ffmpeg";
        return Result.success(Map.of(
                "available", ok,
                "code", ok ? "OK" : "TRANSCRIBE_UNAVAILABLE",
                "message", message
        ));
    }
}
