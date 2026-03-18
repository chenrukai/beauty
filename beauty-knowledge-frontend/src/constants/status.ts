export function knowledgeStatusText(status?: number) {
  const val = Number(status)
  if (val === 0) return '草稿'
  if (val === 1) return '已发布'
  if (val === 2) return '已下线'
  return '未知'
}

export function knowledgeStatusTag(status?: number) {
  const val = Number(status)
  if (val === 1) return 'success'
  if (val === 0) return 'info'
  if (val === 2) return 'warning'
  return 'info'
}

export function noticeStatusText(status?: number) {
  return Number(status) === 1 ? '已发布' : '已下线'
}

export function noticeStatusTag(status?: number) {
  return Number(status) === 1 ? 'success' : 'info'
}

export function taskStatusText(status?: string) {
  const s = String(status || '').toUpperCase()
  if (s.includes('SUCCESS')) return '成功'
  if (s.includes('FAIL') || s.includes('ERROR')) return '失败'
  if (s.includes('PROCESS') || s.includes('RUN')) return '处理中'
  if (s.includes('PENDING')) return '待处理'
  return status || '-'
}

export function taskStatusTag(status?: string) {
  const s = String(status || '').toUpperCase()
  if (s.includes('SUCCESS')) return 'success'
  if (s.includes('FAIL') || s.includes('ERROR')) return 'danger'
  if (s.includes('PROCESS') || s.includes('RUN') || s.includes('PENDING')) return 'warning'
  return 'info'
}

export function taskTypeText(taskType?: string) {
  const t = String(taskType || '').toUpperCase()
  if (t === 'KNOWLEDGE_CREATE') return '创建知识'
  if (t === 'KNOWLEDGE_PROCESS') return '处理文件'
  return taskType || '-'
}

