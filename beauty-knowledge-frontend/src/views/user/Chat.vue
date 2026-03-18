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
            <StreamText :text="m.content" />
            <div v-if="m.sources?.length" class="sources">
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
        <el-input v-model="question" type="textarea" :rows="3" placeholder="请输入问题..." />
        <el-button type="primary" :loading="chat.isStreaming" @click="ask">发送</el-button>
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
import request from '../../api/request'

const route = useRoute()
const chat = useChatStore()
const question = ref('')
const sessionPageNum = ref(1)
const sessionPageSize = 10

const pagedSessions = computed(() => {
  const start = (sessionPageNum.value - 1) * sessionPageSize
  return chat.sessionList.slice(start, start + sessionPageSize)
})

const quickQuestions = [
  '烟酰胺适合敏感肌吗？',
  '刷酸后怎么修护屏障？',
  '油皮夏天该怎么分层护肤？',
  'VC 和 A 醇能一起用吗？',
  '痘印和暗沉分别怎么处理？'
]

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
})

async function ask() {
  const q = question.value.trim()
  if (!q) return
  await recordAction('search', { keyword: q, targetType: 'knowledge', source: 'chat' })
  await chat.streamAsk(q)
  question.value = ''
}

async function askQuick(q: string) {
  question.value = q
  await ask()
}

function newSession() {
  chat.currentSessionId = null
  chat.messages = []
  sessionPageNum.value = 1
}

function openSession(id: number) {
  chat.fetchMessages(id)
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
    ElMessage.error(e?.message || '删除会话失败')
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
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 8px 10px;
  background: #fafafa;
}

.metric span {
  display: block;
  color: #64748b;
  font-size: 12px;
}

.metric strong {
  font-size: 22px;
  color: #0f172a;
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
  background: #f3f4f6;
}

.session.active {
  background: #e5f3ff;
}

.title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-btn {
  margin: 0;
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
  color: #334155;
}

.messages {
  padding: 12px;
  overflow: auto;
  background: #fff;
  border: 1px solid #e5e7eb;
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
  color: #64748b;
}

.ask {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  display: grid;
  gap: 8px;
  background: #fff;
}

.sources {
  margin-top: 8px;
  display: grid;
  gap: 8px;
}

@media (max-width: 900px) {
  .chat-page {
    grid-template-columns: 1fr;
  }
}
</style>
