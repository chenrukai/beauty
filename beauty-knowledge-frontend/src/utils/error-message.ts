import { getErrorMessage } from '../api/response'

type Rule = {
  test: (raw: string) => boolean
  message: string
}

const RULES: Rule[] = [
  {
    test: (raw) => raw.includes('transcribe_unavailable'),
    message: '视频转写不可用：请检查 Python transcribe 服务与 ffmpeg。'
  },
  {
    test: (raw) => raw.includes('image_text_empty'),
    message: '当前仅支持识别图片文字，未检测到可识别文本。请上传更清晰图片或文档。'
  },
  {
    test: (raw) => raw.includes('entity_extract_pending'),
    message: '实体待确认表未初始化：请先执行数据库初始化脚本。'
  },
  {
    test: (raw) => raw.includes('connection refused') && raw.includes('5672'),
    message: '消息队列未连接（RabbitMQ 5672 拒绝连接）。'
  },
  {
    test: (raw) => raw.includes('附件内容不存在或无法访问'),
    message: '附件内容不存在或无法访问，请重新上传后重试。'
  },
  {
    test: (raw) => raw.includes('当前会话未找到可打开附件'),
    message: '当前会话未找到可打开附件。若该会话较旧，建议重新上传附件。'
  }
]

export function toUserErrorMessage(error: any, fallback = '操作失败，请稍后重试'): string {
  const msg = getErrorMessage(error, fallback)
  const normalized = String(msg || '').trim()
  if (!normalized) return fallback
  const raw = normalized.toLowerCase()
  const hit = RULES.find((rule) => rule.test(raw))
  return hit?.message || normalized
}

export function mapTextToUserErrorMessage(text: string, fallback = '操作失败，请稍后重试'): string {
  const normalized = String(text || '').trim()
  if (!normalized) return fallback
  const raw = normalized.toLowerCase()
  const hit = RULES.find((rule) => rule.test(raw))
  return hit?.message || normalized
}

