<template>
  <div class="favorites-page">
    <el-card shadow="never">
      <template #header>
        <div class="head">
          <strong>我的收藏</strong>
          <span class="muted">支持搜索与分页，收藏多了也好找。</span>
        </div>
      </template>

      <div class="toolbar">
        <el-input
          v-model="keyword"
          clearable
          placeholder="搜索收藏标题"
          @keyup.enter="fetchFavorites(1)"
          @change="fetchFavorites(1)"
        />
        <el-button type="primary" @click="fetchFavorites(1)">搜索</el-button>
        <el-button @click="resetKeyword">重置</el-button>
      </div>

      <div v-if="loading" class="muted">加载中...</div>
      <div v-else-if="list.length" class="list">
        <div v-for="item in list" :key="item.knowledgeId" class="item">
          <div class="meta">
            <h4>{{ item.title }}</h4>
            <p>类型：{{ item.type || '-' }} · 浏览：{{ item.viewCount || 0 }}</p>
          </div>
          <div class="actions">
            <el-button size="small" type="info" plain @click="openKnowledge(Number(item.knowledgeId))">查看</el-button>
            <el-button size="small" type="danger" plain @click="removeFavorite(Number(item.knowledgeId))">
              取消收藏
            </el-button>
            <el-button size="small" @click="goChat(item.title)">继续提问</el-button>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无收藏内容" :image-size="80" />

      <div class="pager" v-if="total > pageSize">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          :page-size="pageSize"
          v-model:current-page="pageNum"
          @current-change="fetchFavorites"
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
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../../api/request'
import { unwrapData } from '../../api/response'
import { useAuthStore } from '../../stores/auth'
import LinkifiedText from '../../components/common/LinkifiedText.vue'

const router = useRouter()
const auth = useAuthStore()
const configuredBaseURL = import.meta.env.VITE_API_BASE_URL?.trim()
const apiBaseURL = configuredBaseURL || 'http://127.0.0.1:8080/api'
const list = ref<any[]>([])
const loading = ref(false)
const keyword = ref('')
const pageNum = ref(1)
const pageSize = 8
const total = ref(0)
const knowledgeDialogVisible = ref(false)
const knowledgeDetail = ref<any>(null)
const knowledgeFiles = ref<any[]>([])
const openingFileIds = ref<Set<number>>(new Set())

onMounted(async () => {
  await fetchFavorites(1)
})

function goChat(title: string) {
  router.push({ path: '/user/chat', query: { q: `请结合实操解释：${title}` } })
}

async function fetchFavorites(page = pageNum.value) {
  pageNum.value = Number(page || 1)
  loading.value = true
  try {
    const res = await request.get('/user/favorite/page', {
      params: {
        pageNum: pageNum.value,
        pageSize,
        keyword: keyword.value || undefined
      }
    })
    const pageData = unwrapData<any>(res, {})
    list.value = pageData?.records || []
    total.value = Number(pageData?.total || 0)
  } catch {
    list.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function removeFavorite(knowledgeId: number) {
  try {
    await request.delete(`/user/favorite/${knowledgeId}`)
    ElMessage.success('已取消收藏')
    await fetchFavorites(pageNum.value)
  } catch (e: any) {
    ElMessage.error(e?.message || '取消收藏失败')
  }
}

function resetKeyword() {
  keyword.value = ''
  fetchFavorites(1)
}

async function openKnowledge(knowledgeId: number) {
  try {
    const res = await request.get(`/knowledge/${knowledgeId}`)
    const data = unwrapData<any>(res, {})
    knowledgeDetail.value = data.knowledge || null
    knowledgeFiles.value = Array.isArray(data.files) ? data.files : []
    knowledgeDialogVisible.value = true
    await recordAction('browse', { targetType: 'knowledge', targetId: knowledgeId, source: 'favorite' })
    await fetchFavorites(pageNum.value)
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
.favorites-page {
  display: grid;
  gap: 12px;
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.toolbar {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 8px;
  margin-bottom: 12px;
}

.list {
  display: grid;
  gap: 10px;
}

.item {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.meta h4 {
  margin: 0 0 6px;
  font-size: 16px;
}

.meta p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.actions {
  display: flex;
  gap: 8px;
}

.pager {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
}

.muted {
  color: #64748b;
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

@media (max-width: 900px) {
  .toolbar {
    grid-template-columns: 1fr 1fr;
  }

  .item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
