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

        <el-scrollbar height="calc(100vh - 520px)">
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
          <strong>我的收藏</strong>
        </template>
        <el-input
          v-model="favoriteKeyword"
          placeholder="搜索收藏标题"
          clearable
          size="small"
          class="favorite-search"
          @change="fetchFavorites(1)"
          @keyup.enter="fetchFavorites(1)"
        />
        <div v-if="favoriteList.length" class="favorite-list">
          <div v-for="f in favoriteList" :key="f.knowledgeId" class="favorite-item">
            <div class="fav-title">{{ f.title }}</div>
            <div class="fav-actions">
              <el-button size="small" type="info" plain @click="openKnowledge(Number(f.knowledgeId), 'favorite')">
                查看
              </el-button>
              <el-button size="small" type="danger" plain @click="unfavoriteFromList(Number(f.knowledgeId))">
                取消收藏
              </el-button>
            </div>
            <div class="fav-meta">{{ f.type }} · 浏览 {{ f.viewCount || 0 }}</div>
          </div>
        </div>
        <el-empty v-else description="暂无收藏" :image-size="60" />
        <div class="pager-mini" v-if="favoriteTotal > favoritePageSize">
          <el-pagination
            small
            background
            layout="prev, pager, next"
            :total="favoriteTotal"
            :page-size="favoritePageSize"
            v-model:current-page="favoritePageNum"
            @current-change="fetchFavorites"
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
      <el-alert
        v-if="noticeList.length"
        type="info"
        :closable="false"
        class="notice"
        :title="`公告：${noticeList[0].title}`"
      >
        <template #default>
          <div class="notice-content">{{ noticeList[0].content }}</div>
        </template>
      </el-alert>

      <el-card shadow="never" class="welcome">
        <h3>今天想了解什么？</h3>
        <p>你可以先点击左侧快速提问，也可以直接输入护肤成分、肤质问题或产品对比需求。</p>
        <div class="tips">
          <span>提问建议：成分 + 肤质 + 使用场景</span>
          <span>例如：油敏肌晚间怎么用烟酰胺？</span>
        </div>
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
          <p>点击下方推荐问题即可开始，或直接输入你的问题。</p>
          <div class="empty-actions">
            <el-button v-for="q in quickQuestions.slice(0, 3)" :key="`empty-${q}`" @click="askQuick(q)">
              {{ q }}
            </el-button>
          </div>
        </div>
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
            <div class="recommend-meta">浏览 {{ item.viewCount || 0 }}</div>
            <div class="recommend-content">{{ item.content }}</div>
            <div class="recommend-actions">
              <el-button size="small" type="info" plain @click="openKnowledge(item.id)">查看详情</el-button>
              <el-button size="small" @click="askQuick(`请解释：${item.title}`)">去提问</el-button>
              <el-button
                size="small"
                :type="favoriteSet.has(item.id) ? 'danger' : 'primary'"
                plain
                @click="toggleFavorite(item.id)"
              >
                {{ favoriteSet.has(item.id) ? '取消收藏' : '收藏' }}
              </el-button>
            </div>
          </div>
        </div>
        <div v-else class="recommend-empty">暂无知识数据</div>
        <div class="pager-recommend" v-if="recommendTotal > recommendPageSize">
          <el-pagination
            background
            layout="total, prev, pager, next"
            :total="recommendTotal"
            :page-size="recommendPageSize"
            v-model:current-page="recommendPageNum"
            @current-change="fetchRecommend"
          />
        </div>
      </el-card>
    </section>
  </div>

  <el-dialog v-model="knowledgeDialogVisible" title="知识详情" width="760px" destroy-on-close>
    <template v-if="knowledgeDetail">
      <h3 style="margin-top: 0">{{ knowledgeDetail.title }}</h3>
      <p class="dialog-summary">{{ knowledgeDetail.summary || '暂无摘要' }}</p>
      <div class="dialog-content">{{ knowledgeDetail.content || '暂无正文' }}</div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
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
  viewCount: number
}

const chat = useChatStore()
const question = ref('')
const loadingRecommend = ref(false)
const recommendList = ref<RecommendItem[]>([])
const recommendPageNum = ref(1)
const recommendPageSize = 6
const recommendTotal = ref(0)
const noticeList = ref<any[]>([])
const favoriteList = ref<any[]>([])
const favoriteKeyword = ref('')
const favoritePageNum = ref(1)
const favoritePageSize = 5
const favoriteTotal = ref(0)
const favoriteSet = ref<Set<number>>(new Set())
const knowledgeDialogVisible = ref(false)
const knowledgeDetail = ref<any>(null)

const sessionPageNum = ref(1)
const sessionPageSize = 8

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

onMounted(async () => {
  await Promise.allSettled([chat.fetchSessions(), fetchRecommend(1), fetchNotices(), fetchFavorites()])
})

async function fetchNotices() {
  try {
    const res = await request.get('/notice/list', { params: { size: 3 } })
    noticeList.value = res.data || []
  } catch {
    noticeList.value = []
  }
}

async function fetchFavorites(page = favoritePageNum.value) {
  favoritePageNum.value = Number(page || 1)
  try {
    const res = await request.get('/user/favorite/page', {
      params: {
        pageNum: favoritePageNum.value,
        pageSize: favoritePageSize,
        keyword: favoriteKeyword.value || undefined
      }
    })
    favoriteList.value = res.data?.records || []
    favoriteTotal.value = Number(res.data?.total || 0)
    favoriteSet.value = new Set(favoriteList.value.map((it: any) => Number(it.knowledgeId)))
  } catch {
    favoriteList.value = []
    favoriteTotal.value = 0
    favoriteSet.value = new Set()
  }
}

async function fetchRecommend(page = recommendPageNum.value) {
  recommendPageNum.value = Number(page || 1)
  loadingRecommend.value = true
  try {
    const res = await request.get('/knowledge/page', {
      params: {
        pageNum: recommendPageNum.value,
        pageSize: recommendPageSize,
        status: 1,
        sortBy: 'hot'
      }
    })
    recommendList.value = (res.data?.records || []).map((item: any) => ({
      id: item.id,
      title: String(item.title || `知识 #${item.id}`),
      content: toTeaser(item.content || item.summary || '', 15),
      viewCount: Number(item.viewCount || 0)
    }))
    recommendTotal.value = Number(res.data?.total || 0)
  } catch {
    recommendList.value = []
    recommendTotal.value = 0
  } finally {
    loadingRecommend.value = false
  }
}

function toTeaser(text: string, limit = 15) {
  const chars = Array.from(String(text || ''))
  if (chars.length <= limit) return chars.join('')
  return `${chars.slice(0, limit).join('')}...`
}

async function ask() {
  const q = question.value.trim()
  if (!q) return
  await recordAction('search', { keyword: q, targetType: 'knowledge', source: 'search' })
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
    if (sessionPageNum.value > maxPage) {
      sessionPageNum.value = maxPage
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '删除会话失败')
  }
}

async function toggleFavorite(knowledgeId: number) {
  try {
    if (favoriteSet.value.has(knowledgeId)) {
      await request.delete(`/user/favorite/${knowledgeId}`)
      favoriteSet.value.delete(knowledgeId)
      ElMessage.success('已取消收藏')
    } else {
      await request.post(`/user/favorite/${knowledgeId}`)
      favoriteSet.value.add(knowledgeId)
      ElMessage.success('已收藏')
      await recordAction('favorite', { targetType: 'knowledge', targetId: knowledgeId })
    }
    await fetchFavorites(favoritePageNum.value)
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  }
}

async function unfavoriteFromList(knowledgeId: number) {
  try {
    await request.delete(`/user/favorite/${knowledgeId}`)
    favoriteSet.value.delete(knowledgeId)
    await fetchFavorites(favoritePageNum.value)
    ElMessage.success('已取消收藏')
  } catch (e: any) {
    ElMessage.error(e?.message || '取消收藏失败')
  }
}

async function openKnowledge(knowledgeId: number, source: 'recommend' | 'favorite' = 'recommend') {
  try {
    const res = await request.get(`/knowledge/${knowledgeId}`)
    const data = res.data || {}
    knowledgeDetail.value = data.knowledge || null
    const idx = recommendList.value.findIndex((it) => it.id === knowledgeId)
    if (idx >= 0) {
      recommendList.value[idx].viewCount = Number(recommendList.value[idx].viewCount || 0) + 1
    }
    knowledgeDialogVisible.value = true
    await recordAction('click', { targetType: 'knowledge', targetId: knowledgeId, source })
    await recordAction('browse', { targetType: 'knowledge', targetId: knowledgeId, source })
    await fetchFavorites()
    await fetchRecommend(recommendPageNum.value)
  } catch (e: any) {
    ElMessage.error(e?.message || '加载知识详情失败')
  }
}

async function recordAction(actionType: string, payload: any = {}) {
  try {
    await request.post('/user/action', {
      actionType,
      ...payload
    })
  } catch {
    // do not block user flow
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

.pager-mini {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-btn {
  margin: 0;
}

.favorite-search {
  margin-bottom: 8px;
}

.favorite-list {
  display: grid;
  gap: 8px;
}

.favorite-item {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 8px;
}

.fav-title {
  font-weight: 600;
  color: #0f172a;
}

.fav-meta {
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}

.fav-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.right {
  display: grid;
  grid-template-rows: auto auto 1fr auto auto;
  gap: 12px;
}

.notice {
  margin-bottom: 0;
}

.notice-content {
  white-space: pre-wrap;
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

.empty-actions {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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

.recommend-meta {
  margin-bottom: 6px;
  color: #64748b;
  font-size: 12px;
}

.recommend-content {
  margin: 0;
  color: #475569;
  line-height: 1.6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recommend-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.dialog-summary {
  color: #64748b;
  margin-bottom: 10px;
}

.dialog-content {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #334155;
}

.pager-recommend {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
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
    grid-template-rows: auto auto 1fr auto auto;
  }

  .recommend-grid {
    grid-template-columns: 1fr;
  }
}
</style>
