<template>
  <el-card>
    <template #header>任务监控</template>

    <el-form inline>
      <el-form-item label="任务ID">
        <el-input v-model.number="taskId" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchTask">查询</el-button>
      </el-form-item>
      <el-form-item>
        <el-button @click="loadRecent">刷新最近任务</el-button>
      </el-form-item>
      <el-form-item>
        <el-button :loading="autoRefreshing" @click="toggleAutoRefresh">
          {{ autoRefreshing ? '停止自动刷新' : '自动刷新(5秒)' }}
        </el-button>
      </el-form-item>
    </el-form>

    <el-descriptions v-if="task" :column="2" border style="margin-bottom: 12px">
      <el-descriptions-item label="任务ID">{{ task.id }}</el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="taskStatusType(task.status)">{{ task.status }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="进度">
        <el-progress :percentage="toPercent(task.progress)" :stroke-width="10" />
      </el-descriptions-item>
      <el-descriptions-item label="结果">{{ task.resultMsg || '-' }}</el-descriptions-item>
      <el-descriptions-item label="开始时间">{{ task.startedAt || '-' }}</el-descriptions-item>
      <el-descriptions-item label="结束时间">{{ task.finishedAt || '-' }}</el-descriptions-item>
    </el-descriptions>

    <el-alert
      v-if="store.recentTasks.length === 0"
      title="暂无任务数据。只有执行上传并入队后，才会生成处理任务。"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
    />

    <el-table :data="store.recentTasks" stripe>
      <el-table-column prop="id" label="任务ID" width="90" />
      <el-table-column prop="fileId" label="文件ID" width="90" />
      <el-table-column prop="taskType" label="类型" width="180" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="taskStatusType(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="进度" width="180">
        <template #default="{ row }">
          <el-progress :percentage="toPercent(row.progress)" :stroke-width="8" />
        </template>
      </el-table-column>
      <el-table-column prop="resultMsg" label="结果信息" />
      <el-table-column label="操作" width="160">
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
const taskId = ref<number>(1)
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
  const normalized = (status || '').toUpperCase()
  if (normalized.includes('SUCCESS') || normalized.includes('DONE')) return 'success'
  if (normalized.includes('FAIL') || normalized.includes('ERROR')) return 'danger'
  if (normalized.includes('RUN') || normalized.includes('PROCESS')) return 'warning'
  return 'info'
}

function toPercent(progress?: number) {
  const val = Number(progress || 0)
  if (val < 0) return 0
  if (val > 100) return 100
  return val
}

function canRetry(status?: string) {
  const normalized = (status || '').toUpperCase()
  return normalized.includes('FAIL') || normalized.includes('ERROR')
}

async function loadRecent() {
  try {
    await store.fetchRecentTasks(12)
  } catch {
    ElMessage.error('加载最近任务失败')
  }
}

async function fetchTask() {
  try {
    task.value = await store.pollTask(taskId.value)
  } catch {
    ElMessage.error('查询任务失败')
  }
}

async function pickTask(id: number) {
  taskId.value = id
  await fetchTask()
}

async function retryTask(id: number) {
  try {
    await request.post(`/file/task/${id}/retry`)
    ElMessage.success('重试任务已提交')
    await loadRecent()
    await pickTask(id)
  } catch (e: any) {
    ElMessage.error(e?.message || '重试任务失败')
  }
}

function startAutoRefresh() {
  if (timer) return
  autoRefreshing.value = true
  timer = setInterval(async () => {
    await loadRecent()
    if (taskId.value) {
      await fetchTask()
    }
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
    return
  }
  startAutoRefresh()
}
</script>
