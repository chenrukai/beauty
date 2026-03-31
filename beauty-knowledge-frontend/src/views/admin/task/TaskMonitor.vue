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
        <el-tag :type="taskStatusType(task.stageCode || task.status)">{{ taskStatusText(task.stageCode || task.status) }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="阶段">{{ task.stageText || '-' }}</el-descriptions-item>
      <el-descriptions-item label="类型">{{ taskTypeText(task.taskType) }}</el-descriptions-item>
      <el-descriptions-item label="文件名">{{ task.fileName || '-' }}</el-descriptions-item>
      <el-descriptions-item label="所属知识">{{ task.knowledgeTitle || '-' }}</el-descriptions-item>
      <el-descriptions-item label="进度">
        <el-progress :percentage="toPercent(task.progress)" :stroke-width="10" />
      </el-descriptions-item>
      <el-descriptions-item label="结果信息">{{ displayResultMsg(task) }}</el-descriptions-item>
      <el-descriptions-item label="失败原因">{{ task.failureReason || '-' }}</el-descriptions-item>
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
          <el-tag :type="taskStatusType(row.stageCode || row.status)">{{ taskStatusText(row.stageCode || row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="阶段" width="120">
        <template #default="{ row }">
          {{ row.stageText || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="进度" width="170">
        <template #default="{ row }">
          <el-progress :percentage="toPercent(row.progress)" :stroke-width="8" />
        </template>
      </el-table-column>
      <el-table-column label="结果信息" min-width="260" show-overflow-tooltip>
        <template #default="{ row }">
          {{ displayResultMsg(row) }}
        </template>
      </el-table-column>
      <el-table-column label="失败原因" min-width="220" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.failureReason || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="updatedAt" label="更新时间" min-width="170" />
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="pickTask(row.id)">查看</el-button>
          <el-button v-if="row.canRetry ?? canRetry(row.status)" link type="warning" @click="retryTask(row.id)">重试</el-button>
          <el-button
            v-if="row.canReExtract ?? canReExtract(row)"
            link
            type="success"
            @click="reExtractEntity(row)"
          >
            重抽实体
          </el-button>
          <el-button
            v-if="row.canConfirm"
            link
            type="primary"
            @click="router.push('/admin/entity/confirm')"
          >
            去确认
          </el-button>
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
import { useRouter } from 'vue-router'
import request from '../../../api/request'
import { useKnowledgeStore } from '../../../stores/knowledge'

const store = useKnowledgeStore()
const router = useRouter()
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
  if (s === 'CONFIRMED' || s === 'PARSE_SUCCESS') return 'success'
  if (s === 'PENDING_CONFIRM') return 'warning'
  if (s === 'UPLOADED' || s === 'PARSING' || s === 'EXTRACTING') return 'warning'
  if (s === 'PARSE_FAILED') return 'danger'
  if (s.includes('SUCCESS')) return 'success'
  if (s.includes('FAIL') || s.includes('ERROR')) return 'danger'
  if (s.includes('PROCESS') || s.includes('RUN') || s.includes('PENDING')) return 'warning'
  return 'info'
}

function taskStatusText(status?: string) {
  const s = (status || '').toUpperCase()
  if (s === 'UPLOADED') return '上传'
  if (s === 'PARSING') return '解析中'
  if (s === 'PARSE_SUCCESS') return '解析成功'
  if (s === 'PARSE_FAILED') return '解析失败'
  if (s === 'EXTRACTING') return '抽取中'
  if (s === 'PENDING_CONFIRM') return '待确认'
  if (s === 'CONFIRMED') return '已确认'
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

function canReExtract(row: any) {
  const type = String(row?.taskType || '').toUpperCase()
  const status = String(row?.status || '').toUpperCase()
  const fileId = Number(row?.fileId || 0)
  return fileId > 0 && type === 'KNOWLEDGE_PROCESS' && status === 'SUCCESS'
}

function taskTypeText(taskType?: string) {
  const t = (taskType || '').toUpperCase()
  if (t === 'KNOWLEDGE_CREATE') return '创建知识'
  if (t === 'KNOWLEDGE_PROCESS') return '处理文件'
  return taskType || '-'
}

function displayResultMsg(row: any) {
  const msg = String(row?.resultMsg || '').trim()
  if (!msg) return '-'
  const lower = msg.toLowerCase()
  if (lower.includes('transcribe_unavailable')) return '视频转写不可用：请检查 Python transcribe 服务和 ffmpeg'
  if (lower.includes('no text extracted')) return '未提取到文本：文件可能不可解析（可先检查任务状态）'
  if (lower.includes('entity_extract_pending')) return '实体待确认表未初始化：请先执行数据库初始化脚本'
  if (lower.includes('connection refused') && lower.includes('5672')) return '消息队列未连接（RabbitMQ 5672 拒绝连接）'
  return msg
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

async function reExtractEntity(row: any) {
  const fileId = Number(row?.fileId || 0)
  if (!fileId) {
    ElMessage.warning('缺少 fileId，无法重抽取')
    return
  }
  try {
    const res = await request.post(`/entity/extract/file/${fileId}`)
    const inserted = Number(res.data?.insertedCount || 0)
    const matched = Number(res.data?.matchedCount || 0)
    const msg = String(res.data?.message || '重抽取完成')
    if (inserted > 0) {
      ElMessage.success(`${msg}（命中 ${matched} 条）`)
    } else {
      ElMessage.warning(`${msg}（命中 ${matched} 条）`)
    }
  } catch (e: any) {
    const raw = String(e?.message || '')
    if (raw.includes('文件尚未解析成功')) {
      ElMessage.error('重抽取失败：文件还未解析成功，请先在任务监控确认状态为成功')
      return
    }
    if (raw.includes('实体待确认表未初始化')) {
      ElMessage.error('重抽取失败：数据库缺少 entity_extract_pending 表')
      return
    }
    ElMessage.error(raw || '重抽取失败')
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
