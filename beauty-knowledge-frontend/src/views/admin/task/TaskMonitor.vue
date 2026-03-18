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
        <el-tag :type="taskStatusType(task.status)">{{ task.status }}</el-tag>
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
      title="暂无任务数据。执行上传并入队后会生成处理任务。"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
    />

    <el-table :data="store.recentTasks" stripe>
      <el-table-column prop="fileName" label="文件名" min-width="200" show-overflow-tooltip />
      <el-table-column prop="knowledgeTitle" label="所属知识" min-width="200" show-overflow-tooltip />
      <el-table-column label="类型" width="150">
        <template #default="{ row }">
          {{ taskTypeText(row.taskType) }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="taskStatusType(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="进度" width="160">
        <template #default="{ row }">
          <el-progress :percentage="toPercent(row.progress)" :stroke-width="8" />
        </template>
      </el-table-column>
      <el-table-column prop="resultMsg" label="结果信息" min-width="220" show-overflow-tooltip />
      <el-table-column prop="updatedAt" label="更新时间" min-width="170" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="pickTask(row.id)">查看</el-button>
          <el-button
            v-if="canRetry(row.status)"
            link
            type="warning"
            @click="retryTask(row.id)"
          >
            重试
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../../api/request'
import { useKnowledgeStore } from '../../../stores/knowledge'

const store = useKnowledgeStore()
const selectedTaskId = ref<number | null>(null)
const task = ref<any>(null)
const autoRefreshing = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  loadRecent()
})

onUnmounted(() => {
  stopAutoRefresh()
})

function taskStatusType(status?: string) {
  const s = (status || '').toUpperCase()
  if (s.includes('SUCCESS')) return 'success'
  if (s.includes('FAIL')) return 'danger'
  if (s.includes('PROCESS') || s.includes('RUN') || s.includes('PENDING')) return 'warning'
  return 'info'
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
  if (t === 'KNOWLEDGE_CREATE') return '知识创建'
  if (t === 'KNOWLEDGE_PROCESS') return '文件处理'
  return taskType || '-'
}

async function loadRecent() {
  try {
    await store.fetchRecentTasks(12)
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
