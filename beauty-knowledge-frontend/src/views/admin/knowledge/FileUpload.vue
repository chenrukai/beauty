<template>
  <el-card>
    <template #header>文件上传与入队</template>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="14">
        <el-form label-width="120px">
          <el-form-item label="knowledgeId">
            <el-input v-model.number="knowledgeId" />
          </el-form-item>
          <el-form-item label="分类ID">
            <el-input v-model.number="categoryId" />
          </el-form-item>
          <el-form-item label="文件类型">
            <el-select v-model="fileType" style="width: 220px">
              <el-option label="pdf" value="pdf" />
              <el-option label="image" value="image" />
            </el-select>
          </el-form-item>
          <el-form-item label="选择文件">
            <input type="file" @change="onFile" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="upload">上传并入队</el-button>
            <el-button @click="loadAssistData">刷新辅助数据</el-button>
          </el-form-item>
        </el-form>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card shadow="never">
          <template #header>辅助信息</template>
          <div class="hint">可用分类节点：{{ categoryCount }}</div>
          <div class="hint">知识总量（当前加载）：{{ knowledgeCount }}</div>
          <div v-if="lastTaskId" class="hint">最近上传任务ID：<b>{{ lastTaskId }}</b></div>
          <div class="hint">建议：先在“知识列表”确认 knowledgeId，再上传文件。</div>
        </el-card>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../../api/request'
import { useKnowledgeStore } from '../../../stores/knowledge'

const knowledgeStore = useKnowledgeStore()
const knowledgeId = ref(1)
const categoryId = ref<number | undefined>(11)
const fileType = ref('pdf')
const file = ref<File | null>(null)
const loading = ref(false)
const lastTaskId = ref<number | null>(null)

onMounted(() => {
  loadAssistData()
})

const categoryCount = computed(() => countTree(knowledgeStore.categoryTree))
const knowledgeCount = computed(() => knowledgeStore.knowledgePage.total || knowledgeStore.knowledgeList.length)

function countTree(list: any[]): number {
  return list.reduce((sum, item) => sum + 1 + countTree(item.children || []), 0)
}

async function loadAssistData() {
  try {
    await Promise.all([
      knowledgeStore.fetchCategoryTree(),
      knowledgeStore.fetchKnowledgePage({ pageNum: 1, pageSize: 20 })
    ])
  } catch {
    ElMessage.error('加载辅助数据失败')
  }
}

function onFile(e: Event) {
  const target = e.target as HTMLInputElement
  file.value = target.files?.[0] || null
}

async function upload() {
  if (!file.value) {
    ElMessage.warning('请选择文件')
    return
  }

  loading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    fd.append('knowledgeId', String(knowledgeId.value))
    if (categoryId.value) fd.append('categoryId', String(categoryId.value))
    fd.append('fileType', fileType.value)

    const res = await request.post('/file/upload', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    lastTaskId.value = Number(res.data.taskId)
    ElMessage.success(`上传成功，任务ID=${res.data.taskId}`)
  } catch (e: any) {
    ElMessage.error(e?.message || '上传失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.hint {
  margin-bottom: 10px;
  color: #475569;
}
</style>
