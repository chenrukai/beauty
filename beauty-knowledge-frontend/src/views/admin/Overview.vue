<template>
  <div class="overview">
    <el-row :gutter="12">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="metric">
          <div class="metric-label">知识总数</div>
          <div class="metric-value">{{ overview.knowledgeTotal }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="metric">
          <div class="metric-label">今日新增</div>
          <div class="metric-value">{{ overview.knowledgeTodayAdded }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="metric">
          <div class="metric-label">待确认实体</div>
          <div class="metric-value">{{ overview.entityPending }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="metric">
          <div class="metric-label">失败任务</div>
          <div class="metric-value">{{ overview.taskFailed }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="12" style="margin-top: 12px">
      <el-col :xs="24" :lg="8">
        <el-card>
          <template #header>浏览来源占比</template>
          <div v-if="sourceRatio.length" class="ratio-list">
            <div v-for="it in sourceRatio" :key="it.source" class="ratio-item">
              <div class="ratio-label">{{ sourceText(it.source) }}</div>
              <el-progress :percentage="it.percent" :stroke-width="10" />
            </div>
          </div>
          <el-empty v-else description="暂无数据" :image-size="70" />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="16">
        <el-card>
          <template #header>最近任务</template>
          <el-table :data="knowledgeStore.recentTasks" stripe>
            <el-table-column prop="fileName" label="文件名" min-width="180" show-overflow-tooltip />
            <el-table-column prop="knowledgeTitle" label="所属知识" min-width="180" show-overflow-tooltip />
            <el-table-column label="类型" width="120">
              <template #default="{ row }">
                {{ taskTypeText(row.taskType) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="110">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)">{{ statusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="进度" width="140">
              <template #default="{ row }">
                <el-progress :percentage="toPercent(row.progress)" :stroke-width="8" />
              </template>
            </el-table-column>
            <el-table-column prop="updatedAt" label="更新时间" min-width="170" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card>
          <template #header>热门搜索词（今日）</template>
          <div v-if="hotKeywords.length" class="keyword-list">
            <div v-for="it in hotKeywords" :key="`${it.keyword}-${it.id}`" class="keyword-item">
              <span class="kw">{{ it.keyword }}</span>
              <span class="count">{{ it.searchCount }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无数据" :image-size="70" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="12" style="margin-top: 12px">
      <el-col :xs="24">
        <el-card>
          <template #header>热门内容 Top10</template>
          <el-table :data="hotContents" stripe>
            <el-table-column prop="title" label="标题" min-width="260" show-overflow-tooltip />
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column prop="viewCount" label="浏览量" width="120" />
            <el-table-column prop="updatedAt" label="更新时间" min-width="170" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../api/request'
import { useKnowledgeStore } from '../../stores/knowledge'

const knowledgeStore = useKnowledgeStore()

const overview = reactive({
  knowledgeTotal: 0,
  knowledgeTodayAdded: 0,
  entityPending: 0,
  taskFailed: 0
})
const hotContents = ref<any[]>([])
const hotKeywords = ref<any[]>([])
const sourceRatio = ref<Array<{ source: string; count: number; percent: number }>>([])
let refreshTimer: number | null = null

onMounted(async () => {
  await Promise.allSettled([
    loadOverview(),
    loadSourceRatio(),
    loadHotContents(),
    loadHotKeywords(),
    knowledgeStore.fetchRecentTasks(8)
  ])
  refreshTimer = window.setInterval(() => {
    void loadHotContents()
    void loadSourceRatio()
  }, 15000)
})

onUnmounted(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer)
    refreshTimer = null
  }
})

async function loadOverview() {
  try {
    const res = await request.get('/admin/dashboard/overview')
    Object.assign(overview, res.data || {})
  } catch {
    ElMessage.error('加载总览失败')
  }
}

async function loadHotContents() {
  try {
    const res = await request.get('/admin/dashboard/hot-content')
    hotContents.value = res.data || []
  } catch {
    hotContents.value = []
  }
}

async function loadHotKeywords() {
  try {
    const res = await request.get('/admin/dashboard/hot-keywords')
    hotKeywords.value = res.data || []
  } catch {
    hotKeywords.value = []
  }
}

async function loadSourceRatio() {
  try {
    const res = await request.get('/admin/dashboard/source-ratio', { params: { range: 'week' } })
    const list = res.data || []
    const total = list.reduce((sum: number, it: any) => sum + Number(it.count || 0), 0)
    sourceRatio.value = list.map((it: any) => {
      const count = Number(it.count || 0)
      const percent = total > 0 ? Math.round((count * 10000) / total) / 100 : 0
      return { source: String(it.source || 'other'), count, percent }
    })
  } catch {
    sourceRatio.value = []
  }
}

function statusTagType(status?: string) {
  const s = (status || '').toUpperCase()
  if (s.includes('SUCCESS')) return 'success'
  if (s.includes('FAIL') || s.includes('ERROR')) return 'danger'
  if (s.includes('PROCESS') || s.includes('RUN') || s.includes('PENDING')) return 'warning'
  return 'info'
}

function taskTypeText(taskType?: string) {
  const t = (taskType || '').toUpperCase()
  if (t === 'KNOWLEDGE_CREATE') return '创建知识'
  if (t === 'KNOWLEDGE_PROCESS') return '处理文件'
  return taskType || '-'
}

function toPercent(progress?: number) {
  const val = Number(progress || 0)
  return Math.max(0, Math.min(100, val))
}

function statusText(status?: string) {
  const s = (status || '').toUpperCase()
  if (s.includes('SUCCESS')) return '成功'
  if (s.includes('FAIL') || s.includes('ERROR')) return '失败'
  if (s.includes('PROCESS') || s.includes('RUN')) return '处理中'
  if (s.includes('PENDING')) return '待处理'
  return status || '-'
}

function sourceText(source?: string) {
  const s = String(source || '').toLowerCase()
  if (s === 'recommend') return '推荐'
  if (s === 'search') return '搜索'
  if (s === 'favorite') return '收藏'
  return '其他'
}
</script>

<style scoped>
.metric-label {
  color: #64748b;
  font-size: 13px;
}

.metric-value {
  margin-top: 6px;
  font-size: 30px;
  font-weight: 700;
  color: #0f172a;
}

.keyword-list {
  display: grid;
  gap: 8px;
}

.keyword-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 8px 10px;
}

.kw {
  color: #0f172a;
}

.count {
  color: #0f766e;
  font-weight: 600;
}

.ratio-list {
  display: grid;
  gap: 10px;
}

.ratio-label {
  color: #334155;
  font-size: 13px;
  margin-bottom: 4px;
}
</style>

