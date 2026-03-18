<template>
  <el-card>
    <template #header>任务监控</template>

    <el-form inline>
      <el-form-item>
        <el-button @click="loadRecent">刷新最近任务</el-button>
      </el-form-item>
      <el-form-item>
        <el-button :loading="autoRefreshing" @click="toggleAutoRefresh">
          {{ autoRefreshing ? '停止自动刷新' : '自动刷新（5秒）' }}
        </el-button>
      </el-form-item>
    </el-form>

    <el-descriptions v-if="task" :column="2" border style="margin-bottom: 12px">
      <el-descriptions-item label="状态">
        <el-tag :type="taskStatusType(task.status)">{{ taskStatusText(task.status) }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="类型">{{ taskTypeText(task.taskType) }}</el-descriptions-item>
      <el-descriptions-item label="文件名">{{ task.fileName || '-' }}</el-descriptions-item>
      <el-descriptions-item label="所属知识">{{ task.knowledgeTitle || '-' }}</el-descriptions-item>
      <el-descriptions-item label="进度">
        <el-progress :percentage="toPercent(task.progress)" :stroke-width="10" />
      </el-descriptions-item>
      <el-descriptions-item label="结果信息">{{ task.resultMsg || '-' }}</el-descriptions-item>
      <el-descriptions-item label="开始时间">{{ task.startedAt || '-' }}</el-descriptions-item>
      <el-descriptions-item label="结束时间">{{ task.finishedAt || '-' }}</el-descriptions-item>
    </el-descriptions>

    <el-alert
      v-if="store.recentTasks.length === 0"
      title="暂无任务数据。执行上传并入队后，会生成处理任务。"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
    />

    <el-table :data="pagedTasks" stripe>
      <el-table-column prop="fileName" label="文件名" min-width="220" show-overflow-tooltip />
      <el-table-column prop="knowledgeTitle" label="所属知识" min-width="220" show-overflow-tooltip />
      <el-table-column label="类型" width="130">
        <template #default="{ row }">
          {{ taskTypeText(row.taskType) }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="taskStatusType(row.status)">{{ taskStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="进度" width="170">
        <template #default="{ row }">
          <el-progress :percentage="toPercent(row.progress)" :stroke-width="8" />
        </template>
      </el-table-column>
      <el-table-column prop="resultMsg" label="结果信息" min-width="220" show-overflow-tooltip />
      <el-table-column prop="updatedAt" label="更新时间" min-width="170" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="pickTask(row.id)">查看</el-button>
          <el-button v-if="canRetry(row.status)" link type="warning" @click="retryTask(row.id)">重试</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager" v-if="store.recentTasks.length > 0">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next"
        :total="store.recentTasks.length"
        :current-page="pageNum"
        :page-size="pageSize"
        :page-sizes="[10, 20, 30, 50]"
        @current-change="onPageChange"
        @size-change="onSizeChange"
      />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../../api/request'
import { useKnowledgeStore } from '../../../stores/knowledge'

const store = useKnowledgeStore()
const selectedTaskId = ref<number | null>(null)
const task = ref<any>(null)
const autoRefreshing = ref(false)
const pageNum = ref(1)
const pageSize = ref(10)
const recentFetchSize = 200
let timer: ReturnType<typeof setInterval> | null = null

const pagedTasks = computed(() => {
  const start = (pageNum.value - 1) * pageSize.value
  return store.recentTasks.slice(start, start + pageSize.value)
})

onMounted(() => {
  loadRecent()
})

onUnmounted(() => {
  stopAutoRefresh()
})

function onPageChange(page: number) {
  pageNum.value = page
}

function onSizeChange(size: number) {
  pageSize.value = size
  pageNum.value = 1
}

function taskStatusType(status?: string) {
  const s = (status || '').toUpperCase()
  if (s.includes('SUCCESS')) return 'success'
  if (s.includes('FAIL') || s.includes('ERROR')) return 'danger'
  if (s.includes('PROCESS') || s.includes('RUN') || s.includes('PENDING')) return 'warning'
  return 'info'
}

function taskStatusText(status?: string) {
  const s = (status || '').toUpperCase()
  if (s.includes('SUCCESS')) return '成功'
  if (s.includes('FAIL') || s.includes('ERROR')) return '失败'
  if (s.includes('PROCESS') || s.includes('RUN')) return '处理中'
  if (s.includes('PENDING')) return '待处理'
  return status || '-'
}

function toPercent(progress?: number) {
  const val = Number(progress || 0)
  return Math.max(0, Math.min(100, val))
}

function canRetry(status?: string) {
  const s = (status || '').toUpperCase()
  return s.includes('FAIL') || s.includes('ERROR')
}

function taskTypeText(taskType?: string) {
  const t = (taskType || '').toUpperCase()
  if (t === 'KNOWLEDGE_CREATE') return '创建知识'
  if (t === 'KNOWLEDGE_PROCESS') return '处理文件'
  return taskType || '-'
}

async function loadRecent() {
  try {
    await store.fetchRecentTasks(recentFetchSize)
    const maxPage = Math.max(1, Math.ceil(store.recentTasks.length / pageSize.value))
    if (pageNum.value > maxPage) pageNum.value = maxPage
  } catch {
    ElMessage.error('加载最近任务失败')
  }
}

async function fetchTask() {
  if (!selectedTaskId.value) return
  try {
    task.value = await store.pollTask(selectedTaskId.value)
  } catch {
    ElMessage.error('加载任务详情失败')
  }
}

async function pickTask(id: number) {
  selectedTaskId.value = id
  await fetchTask()
}

async function retryTask(id: number) {
  try {
    await request.post(`/file/task/${id}/retry`)
    ElMessage.success('已提交重试')
    await loadRecent()
    await pickTask(id)
  } catch (e: any) {
    ElMessage.error(e?.message || '重试失败')
  }
}

function startAutoRefresh() {
  if (timer) return
  autoRefreshing.value = true
  timer = setInterval(async () => {
    await loadRecent()
    await fetchTask()
  }, 5000)
}

function stopAutoRefresh() {
  autoRefreshing.value = false
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function toggleAutoRefresh() {
  if (autoRefreshing.value) {
    stopAutoRefresh()
  } else {
    startAutoRefresh()
  }
}
</script>

<style scoped>
.pager {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
