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
        <el-scrollbar height="calc(100vh - 420px)">
          <div
            v-for="s in chat.sessionList"
            :key="s.id"
            class="session"
            :class="{ active: chat.currentSessionId === s.id }"
            @click="openSession(s.id)"
          >
            <span class="title">{{ s.title }}</span>
            <el-button text type="danger" size="small" @click.stop="removeSession(s.id)">删除</el-button>
          </div>
        </el-scrollbar>
      </el-card>

      <el-card shadow="never" class="panel">
        <template #header>
          <strong>快速提问</strong>
        </template>
        <div class="quick-list">
          <el-button
            v-for="q in quickQuestions"
            :key="q"
            class="quick-btn"
            @click="askQuick(q)"
          >
            {{ q }}
          </el-button>
        </div>
      </el-card>
    </aside>

    <section class="right">
      <el-card shadow="never" class="welcome">
        <h3>今天想了解什么？</h3>
        <p>你可以先点左侧“快速提问”，也可以直接输入护肤成分、肤质问题或产品对比需求。</p>
        <div class="tips">
          <span>提问建议：成分 + 肤质 + 使用场景</span>
          <span>例如：油敏肌晚间怎么用烟酰胺？</span>
        </div>
      </el-card>

      <div class="messages">
        <MessageBubble v-for="(m, idx) in chat.messages" :key="idx" :role="m.role">
          <StreamText :text="m.content" />
          <div v-if="m.sources?.length" class="sources">
            <SourceCard v-for="(s, i) in m.sources" :key="i" :source="s" />
          </div>
        </MessageBubble>
      </div>

      <div class="ask">
        <el-input v-model="question" type="textarea" :rows="3" placeholder="请输入问题..." />
        <el-button type="primary" :loading="chat.isStreaming" @click="ask">发送</el-button>
      </div>

      <el-card shadow="never" class="recommend">
        <template #header>
          <strong>知识推荐</strong>
        </template>
        <div v-if="loadingRecommend" class="recommend-loading">加载中...</div>
        <div v-else-if="recommendList.length" class="recommend-grid">
          <div v-for="item in recommendList" :key="item.id" class="recommend-item">
            <h4>{{ item.title }}</h4>
            <p>{{ item.content }}</p>
          </div>
        </div>
        <div v-else class="recommend-empty">暂无知识数据，先让管理员在“知识列表”新增内容。</div>
      </el-card>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import MessageBubble from '../../components/chat/MessageBubble.vue'
import StreamText from '../../components/chat/StreamText.vue'
import SourceCard from '../../components/chat/SourceCard.vue'
import { useChatStore } from '../../stores/chat'
import request from '../../api/request'

interface RecommendItem {
  id: number
  title: string
  content: string
}

const chat = useChatStore()
const question = ref('')
const loadingRecommend = ref(false)
const recommendList = ref<RecommendItem[]>([])

const quickQuestions = [
  '烟酰胺适合敏感肌吗？',
  '刷酸后怎么修护屏障？',
  '油皮夏天该怎么分层护肤？',
  'VC 和 A 醇能一起用吗？',
  '痘印和暗沉分别怎么处理？'
]

onMounted(async () => {
  await Promise.allSettled([chat.fetchSessions(), fetchRecommend()])
})

async function fetchRecommend() {
  loadingRecommend.value = true
  try {
    const res = await request.get('/knowledge/page', {
      params: {
        pageNum: 1,
        pageSize: 6,
        status: 1
      }
    })
    recommendList.value = (res.data?.records || []).map((item: any) => ({
      id: item.id,
      title: item.title,
      content: String(item.content || '').slice(0, 90)
    }))
  } catch {
    recommendList.value = []
  } finally {
    loadingRecommend.value = false
  }
}

async function ask() {
  const q = question.value.trim()
  if (!q) return
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
  } catch (e: any) {
    ElMessage.error(e?.message || '删除会话失败')
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

.panel :deep(.el-card__header) {
  padding-bottom: 12px;
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

.right {
  display: grid;
  grid-template-rows: auto 1fr auto auto;
  gap: 12px;
}

.welcome h3 {
  margin: 0 0 8px;
}

.welcome p {
  margin: 0;
  color: #334155;
}

.tips {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tips span {
  font-size: 12px;
  color: #0f766e;
  background: #e8faf8;
  border-radius: 999px;
  padding: 6px 10px;
}

.messages {
  padding: 12px;
  overflow: auto;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
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

.recommend-loading,
.recommend-empty {
  color: #64748b;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.recommend-item {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fafafa;
  padding: 10px;
}

.recommend-item h4 {
  margin: 0 0 6px;
  font-size: 14px;
}

.recommend-item p {
  margin: 0;
  color: #475569;
  line-height: 1.6;
}

@media (max-width: 1100px) {
  .recommend-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 900px) {
  .chat-page {
    grid-template-columns: 1fr;
  }

  .right {
    grid-template-rows: auto 1fr auto auto;
  }

  .recommend-grid {
    grid-template-columns: 1fr;
  }
}
</style>
