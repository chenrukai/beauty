<template>
  <div class="chat-page">
    <aside class="left">
      <el-card shadow="never" class="panel">
        <template #header>
          <div class="panel-head">
            <strong>会话中心</strong>
            <el-button type="primary" plain @click="newSession">新会话</el-button>
          </div>
        </template>

        <div class="metrics">
          <div class="metric">
            <span>会话数</span>
            <strong>{{ chat.sessionList.length }}</strong>
          </div>
          <div class="metric">
            <span>消息数</span>
            <strong>{{ chat.messages.length }}</strong>
          </div>
        </div>

        <el-scrollbar height="calc(100vh - 360px)">
          <div
            v-for="s in pagedSessions"
            :key="s.id"
            class="session"
            :class="{ active: chat.currentSessionId === s.id }"
            @click="openSession(s.id)"
          >
            <span class="title">{{ s.title }}</span>
            <el-button text type="danger" size="small" @click.stop="removeSession(s.id)">删除</el-button>
          </div>
        </el-scrollbar>

        <div class="pager-mini" v-if="chat.sessionList.length > sessionPageSize">
          <el-pagination
            small
            background
            layout="prev, pager, next"
            :total="chat.sessionList.length"
            :page-size="sessionPageSize"
            v-model:current-page="sessionPageNum"
          />
        </div>
      </el-card>

      <el-card shadow="never" class="panel">
        <template #header>
          <strong>快速提问</strong>
        </template>
        <div class="quick-list">
          <el-button v-for="q in quickQuestions" :key="q" class="quick-btn" @click="askQuick(q)">
            {{ q }}
          </el-button>
        </div>
      </el-card>
    </aside>

    <section class="right">
      <el-card shadow="never" class="welcome">
        <h3>问答助手</h3>
        <p>输入护肤成分、肤质问题或产品对比需求，系统会结合知识库给你答复。</p>
      </el-card>

      <div class="messages">
        <template v-if="chat.messages.length">
          <MessageBubble v-for="(m, idx) in chat.messages" :key="idx" :role="m.role">
            <div v-if="m.role === 'assistant'" class="msg-tools">
              <el-button text size="small" @click="copyAnswer(m.content)">复制回答</el-button>
            </div>
            <StreamText :text="displayMessageText(m, idx)" />
            <div v-if="m.role === 'user' && hasUploadedAttachment(m.content)" class="msg-tools">
              <el-button text size="small" @click="openSessionAttachment">打开附件</el-button>
            </div>
            <div v-if="idx === lastAssistantWithSourcesIndex && m.sources?.length" class="sources">
              <SourceCard v-for="(s, i) in m.sources" :key="i" :source="s" />
            </div>
          </MessageBubble>
        </template>
        <div v-else class="empty-state">
          <h4>还没有对话内容</h4>
          <p>可以先点左侧快速提问，或者直接输入你的问题。</p>
        </div>
      </div>

      <div class="ask">
        <el-input
          v-model="question"
          type="textarea"
          :rows="3"
          placeholder="请输入问题..."
          @keydown="onAskInputKeydown"
        />
        <div
          class="ask-tools"
          @dragover.prevent
          @drop.prevent="onDropFiles"
        >
          <input
            ref="fileInputRef"
            class="file-input"
            type="file"
            multiple
            accept=".txt,.md,.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.png,.jpg,.jpeg,.webp,.bmp,.gif,.mp4,.mov,.avi,.mkv,.webm,.m4v"
            @change="onPickFiles"
          />
          <el-button plain @click="triggerFilePick">上传文件（文档/图片/视频）</el-button>
          <span class="file-text">{{ selectedFileName }}</span>
          <el-button v-if="attachedFiles.length" text type="danger" @click="clearFile">移除</el-button>
        </div>
        <el-button type="primary" :loading="chat.isStreaming || summarizing" @click="ask">发送</el-button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import MessageBubble from '../../components/chat/MessageBubble.vue'
import StreamText from '../../components/chat/StreamText.vue'
import SourceCard from '../../components/chat/SourceCard.vue'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'
import request from '../../api/request'
import { unwrapData } from '../../api/response'
import { mapTextToUserErrorMessage, toUserErrorMessage } from '../../utils/error-message'

const route = useRoute()
const chat = useChatStore()
const auth = useAuthStore()
const configuredBaseURL = import.meta.env.VITE_API_BASE_URL?.trim()
const apiBaseURL = configuredBaseURL || 'http://127.0.0.1:8080/api'
const question = ref('')
const fileInputRef = ref<HTMLInputElement | null>(null)
const attachedFiles = ref<File[]>([])
const summarizing = ref(false)
const documentModeSession = ref<number | null>(null)
const documentModeFileName = ref('')
const sessionAttachments = ref<Array<{ index: number; fileName: string; contentType?: string }>>([])
const sessionPageNum = ref(1)
const sessionPageSize = 10

const pagedSessions = computed(() => {
  const start = (sessionPageNum.value - 1) * sessionPageSize
  return chat.sessionList.slice(start, start + sessionPageSize)
})

const lastAssistantWithSourcesIndex = computed(() => {
  for (let i = chat.messages.length - 1; i >= 0; i--) {
    const m = chat.messages[i]
    if (m?.role === 'assistant' && m.sources?.length) {
      return i
    }
  }
  return -1
})

const quickQuestions = [
  '烟酰胺适合敏感肌吗？',
  '刷酸后怎么修护屏障？',
  '油皮夏天怎么分层护肤？',
  'VC 和 A 醇能一起用吗？',
  '痘印和暗沉分别怎么处理？'
]

const selectedFileName = computed(() => {
  if (!attachedFiles.value.length) return '未选择文件'
  if (attachedFiles.value.length === 1) return attachedFiles.value[0].name
  const first = attachedFiles.value.slice(0, 2).map((f) => f.name).join('、')
  return `${attachedFiles.value.length}个文件：${first}${attachedFiles.value.length > 2 ? '...' : ''}`
})

watch(
  () => route.query.q,
  (q) => {
    if (typeof q === 'string' && q.trim()) {
      question.value = q.trim()
    }
  },
  { immediate: true }
)

onMounted(async () => {
  await chat.fetchSessions()
  await refreshSessionAttachments()
})

watch(
  () => chat.currentSessionId,
  () => {
    refreshSessionAttachments()
  }
)

async function ask() {
  const q = question.value.trim() || '总结这个文件的内容'
  if (chat.isStreaming || summarizing.value) return
  await recordAction('search', { keyword: q, targetType: 'knowledge', source: 'chat' })
  if (attachedFiles.value.length) {
    await askWithUploads(q)
    question.value = ''
    clearFile()
    return
  }
  if (documentModeSession.value && chat.currentSessionId === documentModeSession.value) {
    await askInDocumentMode(q)
    question.value = ''
    return
  }
  await chat.streamAsk(q, q)
  question.value = ''
}

function onAskInputKeydown(e: KeyboardEvent) {
  if (e.key !== 'Enter') return
  if (e.shiftKey || e.isComposing) return
  e.preventDefault()
  ask()
}

async function askQuick(q: string) {
  question.value = q
  await ask()
}

function triggerFilePick() {
  fileInputRef.value?.click()
}

async function onPickFiles(e: Event) {
  const input = e.target as HTMLInputElement
  const picked = Array.from(input.files || [])
  if (!picked.length) return
  await appendPickedFiles(picked)
}

async function onDropFiles(e: DragEvent) {
  const picked = Array.from(e.dataTransfer?.files || [])
  if (!picked.length) return
  await appendPickedFiles(picked)
}

async function appendPickedFiles(picked: File[]) {
  const merged = [...attachedFiles.value]
  const exists = new Set(merged.map((f) => `${f.name}#${f.size}#${f.lastModified}`))
  for (const f of picked) {
    const key = `${f.name}#${f.size}#${f.lastModified}`
    if (!exists.has(key)) {
      merged.push(f)
      exists.add(key)
    }
  }
  attachedFiles.value = merged
  await recordAction('upload', { targetType: 'chat', source: 'chat', extra: picked.map((f) => f.name).join(',') })
}

function clearFile() {
  attachedFiles.value = []
  if (fileInputRef.value) fileInputRef.value.value = ''
}

function normalizeUploadErrorMessage(message: string) {
  return mapTextToUserErrorMessage(message, '')
}

async function askWithUploads(q: string) {
  if (!attachedFiles.value.length) return
  const lines = attachedFiles.value.map((f) => `- ${f.name}（${formatFileSize(f.size)}）`)
  const displayQuestion = `${q}\n\n[已上传附件]\n${lines.join('\n')}`
  chat.messages.push({ role: 'user', content: displayQuestion })
  chat.messages.push({ role: 'assistant', content: '' })
  summarizing.value = true
  try {
    const chunks: string[] = []
    for (let i = 0; i < attachedFiles.value.length; i++) {
      const f = attachedFiles.value[i]
      const fd = new FormData()
      fd.append('file', f)
      fd.append('instruction', `${q}（附件${i + 1}/${attachedFiles.value.length}：${f.name}）`)
      if (chat.currentSessionId) {
        fd.append('sessionId', String(chat.currentSessionId))
      }
      const res = await request.post('/chat/summarize-upload', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const data = unwrapData<any>(res, {})
      const summary = String(data?.summary || '').trim()
      const sid = Number(data?.sessionId || 0)
      if (sid > 0) {
        chat.currentSessionId = sid
        documentModeSession.value = sid
        documentModeFileName.value = f.name
      }
      chunks.push(`【${f.name}】\n${summary || 'AI service is unavailable. Please try again later.'}`)
    }
    const last = chat.messages[chat.messages.length - 1]
    if (last && last.role === 'assistant') {
      last.content = chunks.join('\n\n')
    }
    await chat.fetchSessions()
    await refreshSessionAttachments()
  } catch (e: any) {
    const raw = String(e?.message || '').trim()
    const normalized = normalizeUploadErrorMessage(raw)
    const last = chat.messages[chat.messages.length - 1]
    if (last && last.role === 'assistant') {
      last.content = normalized || 'Sorry, AI service is unavailable. Please try again later.'
    }
    ElMessage.error(normalized || toUserErrorMessage(e, '文档总结失败，请稍后重试'))
  } finally {
    summarizing.value = false
  }
}

async function askInDocumentMode(q: string) {
  if (!chat.currentSessionId) return
  chat.messages.push({ role: 'user', content: q })
  chat.messages.push({ role: 'assistant', content: '' })
  summarizing.value = true
  try {
    const res = await request.post('/chat/file/ask', {
      sessionId: chat.currentSessionId,
      question: q
    })
    const data = unwrapData<any>(res, {})
    const answer = String(data?.answer || '').trim()
    const last = chat.messages[chat.messages.length - 1]
    if (last && last.role === 'assistant') {
      last.content = answer || 'AI service is unavailable. Please try again later.'
    }
    await chat.fetchSessions()
    await refreshSessionAttachments()
  } catch (e: any) {
    const raw = String(e?.message || '').trim()
    const normalized = normalizeUploadErrorMessage(raw)
    const last = chat.messages[chat.messages.length - 1]
    if (last && last.role === 'assistant') {
      last.content = normalized || 'Sorry, AI service is unavailable. Please try again later.'
    }
    ElMessage.error(normalized || toUserErrorMessage(e, '文档追问失败，请先重新上传文件'))
  } finally {
    summarizing.value = false
  }
}

function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(2)} MB`
}

function hasUploadedAttachment(content: string) {
  if (!content) return false
  return /\[已上传附件/.test(content)
}

async function openSessionAttachment(index?: number | 'all') {
  const sid = chat.currentSessionId
  if (!sid) {
    ElMessage.warning('请先进入对应会话')
    return
  }
  try {
    const token = auth.token || localStorage.getItem('bk_token') || ''
    const listRes = await request.get(`/chat/session/${sid}/attachments`)
    const list = unwrapData<any[]>(listRes, [])
    sessionAttachments.value = list
    if (!list.length) {
      ElMessage.warning('当前会话没有可打开的附件')
      return
    }

    let indexes: number[] = [0]
    if (index === 'all') {
      indexes = list.map((it: any, i: number) => {
        const n = Number(it?.index)
        return Number.isFinite(n) ? n : i
      })
    } else if (typeof index === 'number') {
      indexes = [index]
    } else if (list.length > 1) {
      const options = list.map((it: any) => `${it.index}: ${it.fileName}`).join('\n')
      const picked = window.prompt(
        `当前会话有多个附件，请输入要打开的序号（例如 0），或输入 all 打开全部：\n${options}`,
        '0'
      )
      if (picked === null) return
      const input = picked.trim().toLowerCase()
      if (input === 'all') {
        indexes = list.map((it: any, i: number) => {
          const n = Number(it?.index)
          return Number.isFinite(n) ? n : i
        })
      } else {
        const n = Number(input)
        if (Number.isNaN(n) || n < 0 || n >= list.length) {
          ElMessage.warning('附件序号无效')
          return
        }
        indexes = [n]
      }
    }

    for (const idx of indexes) {
      const q = Number.isFinite(idx) ? `?index=${idx}` : ''
      const resp = await fetch(`${apiBaseURL}/chat/session/${sid}/attachment${q}`, {
        method: 'GET',
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      })
      if (!resp.ok) {
        const text = await resp.text()
        let message = text
        try {
          const parsed = JSON.parse(text || '{}')
          message = String(parsed?.message || parsed?.msg || text || '')
        } catch {
          // keep raw text
        }
        throw new Error(message || `附件打开失败（HTTP ${resp.status}）`)
      }
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      const win = window.open(url, '_blank', 'noopener')
      if (!win) {
        const a = document.createElement('a')
        a.href = url
        a.target = '_blank'
        a.rel = 'noopener'
        document.body.appendChild(a)
        a.click()
        a.remove()
      }
      window.setTimeout(() => URL.revokeObjectURL(url), 60000)
    }
  } catch (e: any) {
    ElMessage.error(toUserErrorMessage(e, '打开附件失败'))
  }
}

async function refreshSessionAttachments(sessionId?: number) {
  const sid = sessionId ?? chat.currentSessionId
  if (!sid) {
    sessionAttachments.value = []
    return
  }
  try {
    const listRes = await request.get(`/chat/session/${sid}/attachments`)
    sessionAttachments.value = unwrapData<any[]>(listRes, [])
  } catch {
    sessionAttachments.value = []
  }
}

async function copyAnswer(text: string) {
  if (!text?.trim()) return
  try {
    await navigator.clipboard.writeText(sanitizeAssistantText(text))
    ElMessage.success('已复制回答')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

function sanitizeAssistantText(text: string) {
  if (!text) return ''
  return text
    .replace(/\r/g, '')
    .replace(/^#{1,6}\s*/gm, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/^\s*[-*+]\s+/gm, '')
    .replace(/^\s*\d+\.\s+/gm, '')
    .replace(/`+/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

function displayMessageText(m: { role: 'user' | 'assistant'; content: string }, idx: number) {
  if (m.role !== 'assistant') return m.content
  const isStreamingLastAssistant = chat.isStreaming && idx === chat.messages.length - 1
  if (isStreamingLastAssistant) return m.content || ''
  return sanitizeAssistantText(m.content || '')
}

async function newSession() {
  try {
    await chat.createSession()
    sessionPageNum.value = 1
  } catch (e: any) {
    ElMessage.error(toUserErrorMessage(e, '创建会话失败'))
  }
}

function openSession(id: number) {
  if (documentModeSession.value !== id) {
    documentModeSession.value = null
    documentModeFileName.value = ''
  }
  chat.fetchMessages(id)
  refreshSessionAttachments(id)
}

async function removeSession(id: number) {
  await ElMessageBox.confirm('确定删除这个会话吗？', '提示', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  try {
    await chat.deleteSession(id)
    const maxPage = Math.max(1, Math.ceil(chat.sessionList.length / sessionPageSize))
    if (sessionPageNum.value > maxPage) sessionPageNum.value = maxPage
  } catch (e: any) {
    ElMessage.error(toUserErrorMessage(e, '删除会话失败'))
  }
}

async function recordAction(actionType: string, payload: any = {}) {
  try {
    await request.post('/user/action', {
      actionType,
      ...payload
    })
  } catch {
    // 不影响主流程
  }
}
</script>

<style scoped>
.chat-page {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 12px;
  min-height: calc(100vh - 94px);
  color: var(--app-text);
  --chat-surface: #ffffff;
  --chat-soft-bg: #f8fafc;
  --chat-hover-bg: #f3f4f6;
  --chat-active-bg: #e5f3ff;
  --chat-muted: #64748b;
  --chat-subtle: #334155;
}

html[data-theme='night'] .chat-page {
  --chat-surface: #171f2d;
  --chat-soft-bg: #202d42;
  --chat-hover-bg: #243247;
  --chat-active-bg: #2f4466;
  --chat-muted: #c3d0e3;
  --chat-subtle: #d7e3f5;
}

html[data-theme='eye'] .chat-page {
  --chat-surface: #f7f9e8;
  --chat-soft-bg: #eef3d8;
  --chat-hover-bg: #e7eed2;
  --chat-active-bg: #dbe8bc;
  --chat-muted: #50633b;
  --chat-subtle: #2f4628;
}

.left {
  display: grid;
  gap: 12px;
  align-content: start;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.metrics {
  margin-bottom: 10px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.metric {
  border: 1px solid var(--app-border);
  border-radius: 10px;
  padding: 8px 10px;
  background: var(--chat-soft-bg);
}

.metric span {
  display: block;
  color: var(--chat-muted);
  font-size: 12px;
}

.metric strong {
  font-size: 22px;
  color: var(--app-text);
}

.session {
  padding: 8px;
  cursor: pointer;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.session:hover {
  background: var(--chat-hover-bg);
}

.session.active {
  background: var(--chat-active-bg);
}

.title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--app-text);
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-btn {
  margin: 0;
  --el-button-bg-color: var(--chat-surface);
  --el-button-text-color: var(--app-text);
  --el-button-border-color: var(--app-border);
  --el-button-hover-bg-color: var(--chat-hover-bg);
  --el-button-hover-text-color: var(--app-text);
  --el-button-hover-border-color: var(--app-border);
  --el-button-active-bg-color: var(--chat-active-bg);
  --el-button-active-text-color: var(--app-text);
  --el-button-active-border-color: var(--app-border);
}

.pager-mini {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}

.right {
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 12px;
}

.welcome h3 {
  margin: 0 0 8px;
}

.welcome p {
  margin: 0;
  color: var(--chat-subtle);
}

.messages {
  padding: 12px;
  overflow: auto;
  background: var(--chat-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
}

.empty-state {
  min-height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: 12px;
}

.empty-state h4 {
  margin: 0 0 6px;
}

.empty-state p {
  margin: 0;
  color: var(--chat-muted);
}

.ask {
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 12px;
  display: grid;
  gap: 8px;
  background: var(--chat-surface);
}

.ask-tools {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  min-height: 44px;
  border: 1px dashed var(--app-border);
  border-radius: 10px;
  padding: 8px;
}

.file-input {
  display: none;
}

.file-text {
  color: var(--chat-muted);
  font-size: 12px;
}

.msg-tools {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 4px;
}

.sources {
  margin-top: 8px;
  display: grid;
  gap: 8px;
}

:deep(.el-textarea__inner) {
  background: var(--chat-surface);
  color: var(--app-text);
}

:deep(.el-textarea__inner::placeholder) {
  color: var(--chat-muted);
}

@media (max-width: 900px) {
  .chat-page {
    grid-template-columns: 1fr;
  }
}
</style>
