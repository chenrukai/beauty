<template>
  <el-card>
    <template #header>文件上传与入队</template>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="14">
        <el-form label-width="120px">
          <el-form-item label="所属知识">
            <el-select
              v-model="knowledgeId"
              filterable
              placeholder="请选择知识条目"
              style="width: 100%"
            >
              <el-option
                v-for="item in knowledgeOptions"
                :key="item.id"
                :label="`${item.id} - ${item.title || '未命名知识'}`"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="分类节点">
            <el-select
              v-model="categoryId"
              clearable
              filterable
              placeholder="可选：选择分类节点"
              style="width: 100%"
            >
              <el-option
                v-for="item in categoryOptions"
                :key="item.id"
                :label="item.label"
                :value="item.id"
              />
            </el-select>
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
          <div class="hint">可选知识条目：{{ knowledgeOptions.length }}</div>
          <div class="hint">可用分类节点：{{ categoryOptions.length }}</div>
          <div class="hint">知识总量（当前加载）：{{ knowledgeCount }}</div>
          <div v-if="lastTaskId" class="hint">最近上传任务ID：<b>{{ lastTaskId }}</b></div>
          <div class="hint">建议：先在“知识列表”新增知识，再在此页上传文件。</div>
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

type KnowledgeOption = {
  id: number
  title?: string
}

type CategoryNode = {
  id: number
  name?: string
  children?: CategoryNode[]
}

const knowledgeStore = useKnowledgeStore()
const knowledgeId = ref<number | null>(null)
const categoryId = ref<number | null>(null)
const fileType = ref('pdf')
const file = ref<File | null>(null)
const loading = ref(false)
const lastTaskId = ref<number | null>(null)

onMounted(async () => {
  await loadAssistData()
})

const knowledgeCount = computed(() => knowledgeStore.knowledgePage.total || knowledgeStore.knowledgeList.length)

const knowledgeOptions = computed<KnowledgeOption[]>(() => knowledgeStore.knowledgeList || [])

const categoryOptions = computed(() => {
  const result: Array<{ id: number; label: string }> = []
  const walk = (nodes: CategoryNode[], depth: number) => {
    nodes.forEach((node) => {
      const prefix = depth === 0 ? '' : `${'  '.repeat(depth)}└ `
      result.push({
        id: node.id,
        label: `${prefix}${node.name || `分类${node.id}`}`
      })
      if (node.children?.length) {
        walk(node.children, depth + 1)
      }
    })
  }
  walk(knowledgeStore.categoryTree as CategoryNode[], 0)
  return result
})

async function loadAssistData() {
  try {
    await Promise.all([
      knowledgeStore.fetchCategoryTree(),
      knowledgeStore.fetchKnowledgePage({ pageNum: 1, pageSize: 100 })
    ])
    if (!knowledgeId.value && knowledgeOptions.value.length > 0) {
      knowledgeId.value = knowledgeOptions.value[0].id
    }
  } catch {
    ElMessage.error('加载辅助数据失败')
  }
}

function onFile(e: Event) {
  const target = e.target as HTMLInputElement
  file.value = target.files?.[0] || null
}

async function upload() {
  if (!knowledgeId.value) {
    ElMessage.warning('请先选择所属知识')
    return
  }
  if (!file.value) {
    ElMessage.warning('请选择文件')
    return
  }

  loading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    fd.append('knowledgeId', String(knowledgeId.value))
    if (categoryId.value) {
      fd.append('categoryId', String(categoryId.value))
    }
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
