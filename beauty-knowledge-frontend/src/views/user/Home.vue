<template>
  <div class="home-page">
    <section class="hero">
      <div class="hero-copy">
        <div class="hero-top">
          <div>
            <h2>今天想了解什么？</h2>
            <p>从推荐知识开始，或直接去问答助手发起咨询。</p>
          </div>
          <div class="hero-shortcuts">
            <span class="shortcut-label">快捷入口</span>
            <div class="hero-actions">
              <el-button type="primary" @click="goChat()">去提问</el-button>
              <el-button @click="router.push('/user/favorites')">查看收藏</el-button>
            </div>
          </div>
        </div>
        <div class="hero-toolbar">
          <div class="hero-search">
            <div class="hero-search-shell">
              <span class="search-label">知识检索</span>
              <el-input
                v-model.trim="searchKeyword"
                clearable
                placeholder="按知识标题搜索，例如：门店接待、夜间建立耐受"
                size="large"
                @keyup.enter="runSearch(1)"
                @clear="resetSearch"
              />
            </div>
            <div class="hero-search-actions">
              <el-button type="primary" size="large" :loading="loadingSearch" @click="runSearch(1)">搜索</el-button>
              <el-button v-if="isSearchMode" size="large" plain @click="resetSearch">返回推荐</el-button>
            </div>
          </div>
        </div>
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

    <el-card shadow="never" class="recommend-card">
      <template #header>
        <div class="head">
          <div class="head-copy">
            <strong>{{ isSearchMode ? '搜索结果' : '知识推荐' }}</strong>
            <span class="muted">
              {{ isSearchMode ? `关键词：${activeKeyword}` : '为你展示当前热门知识内容' }}
            </span>
          </div>
          <el-button text @click="refreshCurrentList">{{ isSearchMode ? '重新搜索' : '刷新' }}</el-button>
        </div>
      </template>

      <div v-if="currentLoading" class="muted">加载中...</div>
      <div v-else-if="currentList.length" class="recommend-grid">
        <div v-for="item in currentList" :key="item.id" class="recommend-item">
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
      <div v-else class="muted">{{ isSearchMode ? '没有找到相关知识，换个关键词试试。' : '暂无知识数据' }}</div>

      <div class="pager" v-if="currentTotal > recommendPageSize">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="currentTotal"
          :page-size="recommendPageSize"
          :current-page="currentPageNum"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>

  <el-dialog v-model="knowledgeDialogVisible" title="知识详情" width="760px" destroy-on-close>
    <template v-if="knowledgeDetail">
      <h3 style="margin-top: 0">{{ knowledgeDetail.title }}</h3>
      <p class="dialog-summary">{{ knowledgeDetail.summary || '暂无摘要' }}</p>
      <LinkifiedText class="dialog-content" :text="knowledgeDetail.content || '暂无正文'" />

      <div class="file-section">
        <h4>关联文件（{{ knowledgeFiles.length }}）</h4>
        <el-table
          v-if="knowledgeFiles.length"
          :data="knowledgeFiles"
          size="small"
          border
          class="file-table"
        >
          <el-table-column label="文件名" min-width="280" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row?.originalName || row?.fileName || `文件-${row?.id ?? '-'}` }}
            </template>
          </el-table-column>
          <el-table-column prop="fileType" label="类型" width="120" />
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <el-tag size="small" :type="String(row?.processStatus || row?.status || '').toUpperCase() === 'SUCCESS' ? 'success' : 'info'">
                {{ row?.processStatus || row?.status || '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="上传时间" min-width="170" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click="openRelatedFile(row)">打开</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div v-else class="muted">暂无关联文件</div>
      </div>

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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../../api/request'
import { unwrapData } from '../../api/response'
import { useAuthStore } from '../../stores/auth'
import LinkifiedText from '../../components/common/LinkifiedText.vue'

interface RecommendItem {
  id: number
  title: string
  content: string
  viewCount: number
}

const router = useRouter()
const auth = useAuthStore()
const configuredBaseURL = import.meta.env.VITE_API_BASE_URL?.trim()
const apiBaseURL = configuredBaseURL || 'http://127.0.0.1:8080/api'
const loadingRecommend = ref(false)
const loadingSearch = ref(false)
const recommendList = ref<RecommendItem[]>([])
const searchList = ref<RecommendItem[]>([])
const recommendPageNum = ref(1)
const searchPageNum = ref(1)
const recommendPageSize = 6
const recommendTotal = ref(0)
const searchTotal = ref(0)
const searchKeyword = ref('')
const activeKeyword = ref('')
const noticeList = ref<any[]>([])
const knowledgeDialogVisible = ref(false)
const knowledgeDetail = ref<any>(null)
const knowledgeFiles = ref<any[]>([])
const favoriteMap = ref<Record<number, boolean>>({})
const openingFileIds = ref<Set<number>>(new Set())
const isSearchMode = computed(() => Boolean(activeKeyword.value))
const currentLoading = computed(() => (isSearchMode.value ? loadingSearch.value : loadingRecommend.value))
const currentList = computed(() => (isSearchMode.value ? searchList.value : recommendList.value))
const currentTotal = computed(() => (isSearchMode.value ? searchTotal.value : recommendTotal.value))
const currentPageNum = computed(() => (isSearchMode.value ? searchPageNum.value : recommendPageNum.value))

onMounted(async () => {
  await Promise.allSettled([fetchRecommend(1), fetchNotices()])
})

function goChat(q = '') {
  router.push({ path: '/user/chat', query: q ? { q } : undefined })
}

async function fetchNotices() {
  try {
    const res = await request.get('/notice/list', { params: { size: 3 } })
    noticeList.value = unwrapData<any[]>(res, [])
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
    const page = unwrapData<any>(res, {})
    recommendList.value = (page?.records || []).map((item: any) => ({
      id: item.id,
      title: String(item.title || `知识 #${item.id}`),
      content: toTeaser(item.content || item.summary || '', 15),
      viewCount: Number(item.viewCount || 0)
    }))
    recommendTotal.value = Number(page?.total || 0)
    await syncFavoriteState(recommendList.value.map((item) => item.id))
  } catch {
    recommendList.value = []
    recommendTotal.value = 0
  } finally {
    loadingRecommend.value = false
  }
}

async function runSearch(page = searchPageNum.value) {
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    resetSearch()
    return
  }

  searchPageNum.value = Number(page || 1)
  loadingSearch.value = true
  activeKeyword.value = keyword
  try {
    const res = await request.get('/knowledge/page', {
      params: {
        keyword,
        pageNum: searchPageNum.value,
        pageSize: recommendPageSize,
        status: 1,
        sortBy: 'hot'
      }
    })
    const pageData = unwrapData<any>(res, {})
    searchList.value = (pageData?.records || []).map((item: any) => ({
      id: item.id,
      title: String(item.title || `知识 #${item.id}`),
      content: toTeaser(item.content || item.summary || '', 15),
      viewCount: Number(item.viewCount || 0)
    }))
    searchTotal.value = Number(pageData?.total || 0)
    await syncFavoriteState(searchList.value.map((item) => item.id))
    await recordAction('search', { keyword, targetType: 'knowledge', source: 'home' })
  } catch (e: any) {
    searchList.value = []
    searchTotal.value = 0
    ElMessage.error(e?.message || '搜索失败')
  } finally {
    loadingSearch.value = false
  }
}

function resetSearch() {
  searchKeyword.value = ''
  activeKeyword.value = ''
  searchPageNum.value = 1
  searchList.value = []
  searchTotal.value = 0
}

function refreshCurrentList() {
  if (isSearchMode.value) {
    runSearch(searchPageNum.value)
    return
  }
  fetchRecommend(1)
}

function handlePageChange(page: number) {
  if (isSearchMode.value) {
    runSearch(page)
    return
  }
  fetchRecommend(page)
}

function toTeaser(text: string, limit = 15) {
  const chars = Array.from(String(text || ''))
  if (chars.length <= limit) return chars.join('')
  return `${chars.slice(0, limit).join('')}...`
}

async function openKnowledge(knowledgeId: number) {
  const source = isSearchMode.value ? 'search' : 'recommend'
  try {
    const res = await request.get(`/knowledge/${knowledgeId}`)
    const data = unwrapData<any>(res, {})
    knowledgeDetail.value = data.knowledge || null
    knowledgeFiles.value = Array.isArray(data.files) ? data.files : []
    await syncFavoriteState([knowledgeId])
    knowledgeDialogVisible.value = true
    await recordAction('click', { targetType: 'knowledge', targetId: knowledgeId, source })
    await recordAction('browse', { targetType: 'knowledge', targetId: knowledgeId, source })
    refreshCurrentList()
  } catch (e: any) {
    ElMessage.error(e?.message || '加载知识详情失败')
  }
}

async function openRelatedFile(row: any) {
  const fileId = Number(row?.id || 0)
  if (!fileId) {
    ElMessage.warning('文件ID无效，无法打开')
    return
  }
  if (openingFileIds.value.has(fileId)) {
    return
  }
  openingFileIds.value.add(fileId)
  const opened = window.open('', '_blank')
  if (!opened) {
    openingFileIds.value.delete(fileId)
    ElMessage.error('浏览器拦截了弹窗，请允许当前站点打开新页面')
    return
  }
  try {
    const token = auth.token || localStorage.getItem('bk_token') || ''
    const resp = await fetch(`${apiBaseURL}/file/${fileId}/open`, {
      method: 'GET',
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })
    if (!resp.ok) {
      const text = await resp.text()
      throw new Error(text || `文件打开失败（HTTP ${resp.status}）`)
    }
    const blob = await resp.blob()
    const url = URL.createObjectURL(blob)
    opened.location.href = url
    window.setTimeout(() => URL.revokeObjectURL(url), 60000)
  } catch (e: any) {
    opened.close()
    ElMessage.error(e?.message || '文件打开失败')
  } finally {
    window.setTimeout(() => {
      openingFileIds.value.delete(fileId)
    }, 800)
  }
}

async function syncFavoriteState(ids: number[]) {
  const uniqueIds = Array.from(new Set(ids.filter((id) => Number.isFinite(id))))
  if (!uniqueIds.length) return
  await Promise.allSettled(
    uniqueIds.map(async (id) => {
      try {
        const res = await request.get(`/user/favorite/check/${id}`)
        const data = unwrapData<any>(res, {})
        favoriteMap.value[id] = Boolean(data?.favorited)
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
  gap: 14px;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-radius: 16px;
  padding: 20px;
  background: linear-gradient(130deg, #0f766e 0%, #1f9d8f 75%);
  color: #fff;
  box-shadow: var(--app-shadow-sm);
}

.hero-copy {
  flex: 1;
}

.hero-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.hero-toolbar {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.hero h2 {
  margin: 0 0 6px;
  font-size: 28px;
}

.hero p {
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
}

.hero-search {
  display: flex;
  align-items: center;
  gap: 14px;
}

.hero-search-shell {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 12px 10px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.24);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(8px);
}

.search-label {
  flex: 0 0 auto;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: rgba(255, 255, 255, 0.76);
}

.hero-search-shell :deep(.el-input) {
  flex: 1;
}

.hero-search-shell :deep(.el-input__wrapper) {
  min-height: 48px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 0 0 1px rgba(16, 124, 112, 0.14);
  padding: 0 16px;
}

.hero-search-shell :deep(.el-input__wrapper.is-focus) {
  box-shadow:
    0 0 0 2px rgba(255, 255, 255, 0.34),
    0 0 0 4px rgba(15, 118, 110, 0.22);
}

.hero-search-shell :deep(.el-input__inner) {
  font-size: 15px;
  color: #123b35;
}

.hero-search-shell :deep(.el-input__inner::placeholder) {
  color: #7b8b87;
}

.hero-search-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hero-search-actions :deep(.el-button) {
  min-width: 112px;
  min-height: 48px;
  border-radius: 14px;
  font-weight: 700;
}

.hero-search-actions :deep(.el-button--primary) {
  border-color: rgba(9, 89, 82, 0.75);
  background: linear-gradient(135deg, #0b6e64 0%, #095d56 100%);
}

.hero-search-actions :deep(.el-button.is-plain) {
  background: rgba(255, 255, 255, 0.96);
  border-color: rgba(255, 255, 255, 0.68);
  color: #0e5f58;
}

.hero-shortcuts {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: fit-content;
  min-width: 244px;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(6, 74, 69, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.shortcut-label {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.72);
}

.hero-actions {
  display: flex;
  gap: 10px;
}

.hero-actions :deep(.el-button) {
  flex: 1;
  min-height: 42px;
  border-radius: 14px;
  font-weight: 700;
  border-color: rgba(255, 255, 255, 0.24);
}

.hero-actions :deep(.el-button--primary) {
  border-color: rgba(123, 198, 255, 0.22);
  background: linear-gradient(135deg, #6eb6ff 0%, #4f8dff 100%);
  box-shadow: 0 10px 22px rgba(47, 115, 255, 0.2);
}

.hero-actions :deep(.el-button:not(.el-button--primary)) {
  background: rgba(255, 255, 255, 0.98);
  color: #174842;
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.head-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
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
  gap: 12px;
}

.recommend-card {
  border: 1px solid var(--app-border);
  border-radius: 14px;
}

.recommend-item {
  border: 1px solid var(--app-border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--app-card-bg) 86%, transparent);
  padding: 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.recommend-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--app-shadow-sm);
}

.recommend-item h4 {
  margin: 0 0 6px;
  font-size: 15px;
}

.recommend-meta {
  margin-bottom: 6px;
  color: var(--app-text-muted);
  font-size: 12px;
}

.recommend-content {
  margin: 0;
  color: var(--app-text);
  line-height: 1.6;
}

.recommend-actions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

.muted {
  color: var(--app-text-muted);
}

.pager {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
}

.dialog-summary {
  color: var(--app-text-muted);
  margin-bottom: 10px;
}

.dialog-content {
  white-space: pre-wrap;
  line-height: 1.8;
  color: var(--app-text);
}

.file-section {
  margin-top: 14px;
}

.file-section h4 {
  margin: 0 0 8px;
  font-size: 14px;
}

.file-table {
  margin-top: 6px;
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

  .hero-top {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .hero-toolbar {
    align-items: stretch;
  }

  .hero-search {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .hero-search-shell {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .hero-search-actions {
    width: 100%;
  }

  .hero-search-actions :deep(.el-button) {
    flex: 1;
    min-width: 0;
  }

  .hero-actions {
    width: 100%;
  }

  .hero-actions :deep(.el-button) {
    flex: 1;
  }

  .hero-shortcuts {
    width: 100%;
    min-width: 0;
  }

  .recommend-grid {
    grid-template-columns: 1fr;
  }
}
</style>
