# OCR Service (IDEA + Docker Compose)

本项目图片解析依赖 Python OCR 服务（`/health`、`/ocr`）。

## 一键启动（推荐）

1. 在 IDEA 中打开：
   - `C:\Users\YLDN\Desktop\beauty\beauty-knowledge-backend\docker-compose.yml`
2. 点击 `Run`（绿色三角）启动 compose。
3. 确认 `beauty-ocr-ai` 服务状态为 `healthy`。

## 默认端口

- OCR 服务：`http://127.0.0.1:8001`
- 健康检查：`GET /health`

## 后端配置

`application-dev.yml` 默认读取：

```yaml
beauty:
  ai:
    python:
      base-url: ${PYTHON_AI_BASE_URL:http://localhost:8001}
```

如端口改动，请同步设置 `PYTHON_AI_BASE_URL`。

## 常见问题

- 图片任务报 `No text extracted...`：
  - 多数是 OCR 服务未启动或未健康。
  - 先检查 `beauty-ocr-ai` 容器状态，再重试任务。
