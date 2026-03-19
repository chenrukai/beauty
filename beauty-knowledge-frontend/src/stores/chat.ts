import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../api/request'
import { useAuthStore } from './auth'

export interface Source {
  chunkId: number
  fileId: number
  pageNo: number
  content: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
}

export const useChatStore = defineStore('chat', () => {
  const configuredBaseURL = import.meta.env.VITE_API_BASE_URL?.trim()
  const apiBaseURL = configuredBaseURL || 'http://127.0.0.1:8080/api'

  const sessionList = ref<any[]>([])
  const currentSessionId = ref<number | null>(null)
  const messages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)
  const streamingContent = ref('')
  const sources = ref<Source[]>([])

  async function fetchSessions() {
    const res = await request.get('/chat/session')
    sessionList.value = res.data || []
  }

  async function fetchMessages(sessionId: number) {
    const res = await request.get(`/chat/session/${sessionId}/messages`)
    currentSessionId.value = sessionId
    messages.value = (res.data || []).map((x: any) => ({
      role: x.role,
      content: x.content,
      sources: normalizeSources(x.sources)
    }))
    const lastAssistant = [...messages.value].reverse().find((m) => m.role === 'assistant' && m.sources?.length)
    sources.value = (lastAssistant?.sources || []) as Source[]
  }

  async function createSession() {
    const res = await request.post('/chat/session/new')
    const session = res.data
    if (session?.id) {
      currentSessionId.value = Number(session.id)
      messages.value = []
      sources.value = []
      await fetchSessions()
    }
    return session
  }

  async function streamAsk(question: string, displayQuestion?: string) {
    messages.value.push({ role: 'user', content: displayQuestion || question })
    messages.value.push({ role: 'assistant', content: '' })
    isStreaming.value = true
    streamingContent.value = ''
    sources.value = []

    try {
      const auth = useAuthStore().token || localStorage.getItem('bk_token') || ''
      const controller = new AbortController()
      const timeout = window.setTimeout(() => controller.abort(), 190000)
      const res = await fetch(`${apiBaseURL}/chat/stream`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${auth}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question,
          ...(currentSessionId.value ? { sessionId: Number(currentSessionId.value) } : {})
        }),
        signal: controller.signal
      })
      window.clearTimeout(timeout)

      if (!res.ok) {
        const errorText = await res.text()
        if (res.status === 401) {
          useAuthStore().clearAuth()
        }
        throw new Error(errorText || `Chat request failed (HTTP ${res.status})`)
      }

      const contentType = res.headers.get('content-type') || ''
      if (!contentType.includes('text/event-stream')) {
        const text = await res.text()
        try {
          const payload = JSON.parse(text)
          throw new Error(payload?.message || text || 'Chat service returned non-stream response')
        } catch {
          throw new Error(text || 'Chat service returned non-stream response')
        }
      }

      const reader = res.body?.getReader()
      if (!reader) {
        throw new Error('Chat response is empty, please check backend service')
      }

      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const chunks = buffer.split('\n\n')
        buffer = chunks.pop() || ''

        for (const chunk of chunks) {
          const normalized = chunk.replace(/\r/g, '')
          const lines = normalized.split('\n')
          const eventLine = lines.find((line) => line.startsWith('event:'))
          const dataLines = lines.filter((line) => line.startsWith('data:'))
          if (!dataLines.length) continue

          const event = eventLine?.replace('event:', '').trim()
          const dataRaw = dataLines.map((line) => line.replace('data:', '').trim()).join('')

          let payload: any
          try {
            payload = JSON.parse(dataRaw)
          } catch {
            continue
          }

          const eventType = event || payload?.type

          if (eventType === 'token') {
            streamingContent.value += payload.content || ''
            const last = messages.value[messages.value.length - 1]
            if (last) last.content = streamingContent.value
          }

          if (eventType === 'done') {
            currentSessionId.value = payload.sessionId || currentSessionId.value
            sources.value = payload.sources || []
            const last = messages.value[messages.value.length - 1]
            if (last) {
              if (!last.content && payload.content) {
                last.content = payload.content
              }
              last.sources = sources.value
            }
          }
        }
      }
    } catch (e: any) {
      const last = messages.value[messages.value.length - 1]
      if (last && !last.content) {
        last.content = 'Sorry, AI service is unavailable. Please try again later.'
      }
      const msg = e?.name === 'AbortError'
        ? 'Chat timeout, please try again'
        : (e?.message || 'Chat failed, please check login state and backend AI service')
      ElMessage.error(msg)
    } finally {
      isStreaming.value = false
      await fetchSessions()
    }
  }

  async function deleteSession(sessionId: number) {
    await request.delete(`/chat/session/${sessionId}`)
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = null
      messages.value = []
      sources.value = []
    }
    await fetchSessions()
  }

  function normalizeSources(raw: any): Source[] | undefined {
    if (!raw) return undefined
    let parsed: any = raw
    if (typeof raw === 'string') {
      try {
        parsed = JSON.parse(raw)
      } catch {
        return undefined
      }
    }
    if (!Array.isArray(parsed)) return undefined
    const normalized = parsed
      .map((s: any) => ({
        chunkId: Number(s?.chunkId || 0),
        fileId: Number(s?.fileId || 0),
        pageNo: Number(s?.pageNo || 0),
        content: String(s?.content || '')
      }))
      .filter((s: Source) => s.content && s.fileId > 0)
    return normalized.length ? normalized : undefined
  }

  return {
    sessionList,
    currentSessionId,
    messages,
    isStreaming,
    streamingContent,
    sources,
    fetchSessions,
    fetchMessages,
    createSession,
    streamAsk,
    deleteSession
  }
})
