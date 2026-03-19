<template>
  <div class="home-page">
    <section class="hero">
      <div>
        <h2>今天想了解什么？</h2>
        <p>从推荐知识开始，或直接去问答助手发起咨询。</p>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="goChat()">去提问</el-button>
        <el-button @click="router.push('/user/favorites')">查看收藏</el-button>
      </div>
    </section>

    <el-alert
      v-if="noticeList.length"
      type="info"
      :closable="false"
      class="notice"
      :title="`最新公告：${noticeList[0].title}`"
    >
      <template #default>
        <LinkifiedText class="notice-content" :text="noticeList[0].content" />
      </template>
    </el-alert>

    <el-card shadow="never">
      <template #header>
        <div class="head">
          <strong>知识推荐</strong>
          <el-button text @click="fetchRecommend(1)">刷新</el-button>
        </div>
      </template>

      <div v-if="loadingRecommend" class="muted">加载中...</div>
      <div v-else-if="recommendList.length" class="recommend-grid">
        <div v-for="item in recommendList" :key="item.id" class="recommend-item">
          <h4>{{ item.title }}</h4>
          <div class="recommend-meta">浏览 {{ item.viewCount || 0 }}</div>
          <div class="recommend-content">{{ item.content }}</div>
          <div class="recommend-actions">
            <el-button size="small" type="info" plain @click="openKnowledge(item.id)">查看详情</el-button>
            <el-button
              size="small"
              :type="favoriteMap[item.id] ? 'warning' : 'default'"
              plain
              @click="toggleFavorite(item.id)"
            >
              {{ favoriteMap[item.id] ? '已收藏' : '收藏' }}
            </el-button>
            <el-button size="small" @click="goChat(`请解释：${item.title}`)">继续追问</el-button>
          </div>
        </div>
      </div>
      <div v-else class="muted">暂无知识数据</div>

      <div class="pager" v-if="recommendTotal > recommendPageSize">
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
  </div>

  <el-dialog v-model="knowledgeDialogVisible" title="知识详情" width="760px" destroy-on-close>
    <template v-if="knowledgeDetail">
      <h3 style="margin-top: 0">{{ knowledgeDetail.title }}</h3>
      <p class="dialog-summary">{{ knowledgeDetail.summary || '暂无摘要' }}</p>
      <LinkifiedText class="dialog-content" :text="knowledgeDetail.content || '暂无正文'" />
      <div class="dialog-actions">
        <el-button
          size="small"
          :type="favoriteMap[Number(knowledgeDetail.id)] ? 'warning' : 'primary'"
          plain
          @click="toggleFavorite(Number(knowledgeDetail.id))"
        >
          {{ favoriteMap[Number(knowledgeDetail.id)] ? '取消收藏' : '收藏知识' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../../api/request'
import LinkifiedText from '../../components/common/LinkifiedText.vue'

interface RecommendItem {
  id: number
  title: string
  content: string
  viewCount: number
}

const router = useRouter()
const loadingRecommend = ref(false)
const recommendList = ref<RecommendItem[]>([])
const recommendPageNum = ref(1)
const recommendPageSize = 6
const recommendTotal = ref(0)
const noticeList = ref<any[]>([])
const knowledgeDialogVisible = ref(false)
const knowledgeDetail = ref<any>(null)
const favoriteMap = ref<Record<number, boolean>>({})

onMounted(async () => {
  await Promise.allSettled([fetchRecommend(1), fetchNotices()])
})

function goChat(q = '') {
  router.push({ path: '/user/chat', query: q ? { q } : undefined })
}

async function fetchNotices() {
  try {
    const res = await request.get('/notice/list', { params: { size: 3 } })
    noticeList.value = res.data || []
  } catch {
    noticeList.value = []
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
    await syncFavoriteState(recommendList.value.map((item) => item.id))
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

async function openKnowledge(knowledgeId: number) {
  try {
    const res = await request.get(`/knowledge/${knowledgeId}`)
    const data = res.data || {}
    knowledgeDetail.value = data.knowledge || null
    await syncFavoriteState([knowledgeId])
    knowledgeDialogVisible.value = true
    await recordAction('click', { targetType: 'knowledge', targetId: knowledgeId, source: 'recommend' })
    await recordAction('browse', { targetType: 'knowledge', targetId: knowledgeId, source: 'recommend' })
    await fetchRecommend(recommendPageNum.value)
  } catch (e: any) {
    ElMessage.error(e?.message || '加载知识详情失败')
  }
}

async function syncFavoriteState(ids: number[]) {
  const uniqueIds = Array.from(new Set(ids.filter((id) => Number.isFinite(id))))
  if (!uniqueIds.length) return
  await Promise.allSettled(
    uniqueIds.map(async (id) => {
      try {
        const res = await request.get(`/user/favorite/check/${id}`)
        favoriteMap.value[id] = Boolean(res.data?.favorited)
      } catch {
        favoriteMap.value[id] = false
      }
    })
  )
}

async function toggleFavorite(knowledgeId: number) {
  if (!knowledgeId) return
  try {
    if (favoriteMap.value[knowledgeId]) {
      await request.delete(`/user/favorite/${knowledgeId}`)
      favoriteMap.value[knowledgeId] = false
      ElMessage.success('已取消收藏')
    } else {
      await request.post(`/user/favorite/${knowledgeId}`)
      favoriteMap.value[knowledgeId] = true
      ElMessage.success('收藏成功')
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '收藏操作失败')
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
.home-page {
  display: grid;
  gap: 12px;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-radius: 14px;
  padding: 18px;
  background: linear-gradient(130deg, #0f766e 0%, #1f9d8f 75%);
  color: #fff;
}

.hero h2 {
  margin: 0 0 6px;
  font-size: 28px;
}

.hero p {
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
}

.hero-actions {
  display: flex;
  gap: 10px;
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.notice {
  margin: 0;
}

.notice-content {
  white-space: pre-wrap;
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
  padding: 12px;
}

.recommend-item h4 {
  margin: 0 0 6px;
  font-size: 15px;
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
}

.recommend-actions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

.muted {
  color: #64748b;
}

.pager {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
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

.dialog-actions {
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
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .recommend-grid {
    grid-template-columns: 1fr;
  }
}
</style>
