<template>
  <el-card>
    <template #header>任务监控</template>

    <el-form inline>
      <el-form-item label="Task ID">
        <el-input v-model.number="taskId" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchTask">查询</el-button>
      </el-form-item>
      <el-form-item>
        <el-button @click="loadRecent">刷新最近任务</el-button>
      </el-form-item>
    </el-form>

    <el-descriptions v-if="task" :column="2" border style="margin-bottom: 12px">
      <el-descriptions-item label="任务ID">{{ task.id }}</el-descriptions-item>
      <el-descriptions-item label="状态">{{ task.status }}</el-descriptions-item>
      <el-descriptions-item label="进度">{{ task.progress }}</el-descriptions-item>
      <el-descriptions-item label="结果">{{ task.resultMsg || '-' }}</el-descriptions-item>
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
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="progress" label="进度" width="90" />
      <el-table-column prop="resultMsg" label="结果信息" />
      <el-table-column label="操作" width="90">
        <template #default="{ row }">
          <el-button link type="primary" @click="pickTask(row.id)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useKnowledgeStore } from '../../../stores/knowledge'

const store = useKnowledgeStore()
const taskId = ref<number>(1)
const task = ref<any>(null)

onMounted(() => {
  loadRecent()
})

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
</script>
