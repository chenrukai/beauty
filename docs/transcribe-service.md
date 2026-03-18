# 音视频转写服务接入说明

## 1. 已接入能力

后端已支持音频/视频文件在入库任务中自动转写：

- 先调用 `POST /transcribe`（JSON Base64）
- 若失败，自动回退调用 `POST /asr`（Whisper 常见 multipart 接口）

可用后端配置：

- `beauty.ai.python.base-url`：原 OCR/Embedding 服务地址
- `beauty.ai.python.transcribe-base-url`：转写服务地址（可独立配置）
- `beauty.ai.python.transcribe-timeout`：转写超时（毫秒）

## 2. 推荐本地启动（Docker）

项目 `docker-compose.yml` 已新增可选服务 `whisper-asr`（profile: `transcribe`）。

启动命令：

```bash
docker compose --profile transcribe up -d whisper-asr
```

默认端口：

- 宿主机：`9002`
- 容器：`9000`

## 3. 后端环境变量

在启动 Java 后端前，设置：

```bash
PYTHON_TRANSCRIBE_BASE_URL=http://localhost:9002
```

如果不设置，默认会跟随 `PYTHON_AI_BASE_URL`。

## 4. 验证方式

1. 管理端上传音频/视频文件（类型可选 `audio` 或 `video`，也可 `auto`）。
2. 到“任务监控”查看任务状态。
3. 成功后检查 `kb_chunk`，应有对应转写文本分块。

## 5. 注意事项

- 该转写能力依赖外部服务模型，首次拉取模型会较慢。
- 视频会走音轨提取与转写，长视频建议先剪辑到关键片段再上传。
- 若转写服务不可用，任务会保留失败信息，管理员可在任务监控中手动重试。
