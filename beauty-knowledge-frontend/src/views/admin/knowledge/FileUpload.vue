<template>
  <el-card class="upload-page">
    <template #header>文件上传与入队</template>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="14">
        <el-form label-width="120px" class="upload-form">
          <el-form-item label="所属知识">
            <el-select
              v-model="knowledgeId"
              filterable
              placeholder="请选择知识"
              style="width: 100%"
            >
              <el-option
                v-for="item in knowledgeOptions"
                :key="item.id"
                :label="item.title || `未命名知识${item.id}`"
                :value="item.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="分类节点">
            <el-select
              v-model="categoryId"
              clearable
              filterable
              placeholder="可选：选择分类节点（仅显示启用）"
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

          <el-form-item label="选择文件">
            <input
              class="native-file-input"
              type="file"
              accept=".txt,.md,.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.png,.jpg,.jpeg,.webp,.bmp,.gif,.mp4,.mov,.avi,.mkv,.webm,.m4v"
              @change="onFile"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading" @click="upload">上传并入队</el-button>
            <el-button @click="loadAssistData">刷新辅助数据</el-button>
          </el-form-item>
        </el-form>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card shadow="never" class="hint-card">
          <template #header>辅助信息</template>
          <div class="hint">已选知识：{{ selectedKnowledgeTitle }}</div>
          <div class="hint">已选分类：{{ selectedCategoryLabel }}</div>
          <div class="hint">已选文件：{{ selectedFileName }}</div>
          <div class="hint">文件大小：{{ selectedFileSize }}</div>
          <div class="hint">支持格式：文档、图片、视频</div>
          <div class="hint" v-if="selectedKind === 'video'">
            转写能力：
            <el-tag size="small" :type="transcribeAvailable ? 'success' : 'danger'">
              {{ transcribeAvailable ? '可用' : '不可用' }}
            </el-tag>
          </div>
          <div class="hint" v-if="selectedKind === 'video'">
            {{ transcribeMessage }}
          </div>
          <div class="hint" v-else-if="selectedKind === 'image'">当前为图片文件：走 OCR 解析，不受转写状态影响</div>
          <div class="hint" v-else-if="selectedKind === 'document'">当前为文档文件：走文档解析，不受转写状态影响</div>
          <div v-if="lastTaskId" class="hint">最近上传任务ID：<b>{{ lastTaskId }}</b></div>
        </el-card>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
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
  status?: number
  children?: CategoryNode[]
}

const knowledgeStore = useKnowledgeStore()
const knowledgeId = ref<number | null>(null)
const categoryId = ref<number | null>(null)
const file = ref<File | null>(null)
const loading = ref(false)
const lastTaskId = ref<number | null>(null)
const transcribeAvailable = ref(false)
const transcribeMessage = ref('正在检测多媒体转写能力...')

const knowledgeOptions = computed<KnowledgeOption[]>(() => knowledgeStore.knowledgeList || [])

const categoryOptions = computed(() => {
  const result: Array<{ id: number; label: string }> = []
  const walk = (nodes: CategoryNode[], path: string[], parentEnabled: boolean) => {
    nodes.forEach((node) => {
      const currentEnabled = parentEnabled && Number(node.status ?? 1) === 1
      if (!currentEnabled) {
        return
      }
      const currentName = node.name || `分类${node.id}`
      const currentPath = [...path, currentName]
      result.push({ id: node.id, label: currentPath.join(' / ') })
      if (node.children?.length) {
        walk(node.children, currentPath, currentEnabled)
      }
    })
  }
  walk(knowledgeStore.categoryTree as CategoryNode[], [], true)
  return result
})

const selectedKnowledgeTitle = computed(() => {
  const hit = knowledgeOptions.value.find((item) => item.id === knowledgeId.value)
  return hit?.title || '未选择'
})

const selectedCategoryLabel = computed(() => {
  const hit = categoryOptions.value.find((item) => item.id === categoryId.value)
  return hit?.label || '未选择'
})

const selectedFileName = computed(() => file.value?.name || '未选择')

const selectedFileSize = computed(() => {
  if (!file.value) return '-'
  const size = file.value.size
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(2)} MB`
})

const selectedKind = computed<'none' | 'image' | 'video' | 'document'>(() => {
  const name = (file.value?.name || '').toLowerCase()
  if (!name) return 'none'
  if (/\.(png|jpg|jpeg|webp|bmp|gif)$/.test(name)) return 'image'
  if (/\.(mp4|mov|avi|mkv|webm|m4v)$/.test(name)) return 'video'
  return 'document'
})

watch(
  categoryOptions,
  (options) => {
    if (categoryId.value && !options.some((item) => item.id === categoryId.value)) {
      categoryId.value = null
    }
  },
  { immediate: true }
)

onMounted(async () => {
  await Promise.all([loadAssistData(), loadTranscribeCapability()])
})

async function loadAssistData() {
  try {
    await Promise.all([
      knowledgeStore.fetchCategoryTree(),
      knowledgeStore.fetchKnowledgePage({ pageNum: 1, pageSize: 100 })
    ])
    if (knowledgeId.value && !knowledgeOptions.value.some((item) => item.id === knowledgeId.value)) {
      knowledgeId.value = null
    }
  } catch {
    ElMessage.error('加载辅助数据失败')
  }
}

async function loadTranscribeCapability() {
  try {
    const res = await request.get('/file/capability/transcribe')
    transcribeAvailable.value = Boolean(res.data?.available)
    transcribeMessage.value = String(res.data?.message || '')
  } catch {
    transcribeAvailable.value = false
    transcribeMessage.value = '转写能力检测失败：请检查后端与 Python transcribe 服务'
  }
}

function onFile(e: Event) {
  const target = e.target as HTMLInputElement
  const chosen = target.files?.[0] || null
  file.value = chosen
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
    if (categoryId.value) fd.append('categoryId', String(categoryId.value))

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
.upload-page {
  --panel-gap: 14px;
}

.upload-form {
  padding: 12px 14px;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--app-card-bg) 92%, transparent);
}

.upload-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.native-file-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px dashed var(--app-border);
  border-radius: 10px;
  background: var(--app-card-bg);
  color: var(--app-text);
}

.hint-card {
  border: 1px solid var(--app-border);
  border-radius: 12px;
}

.hint {
  margin-bottom: 10px;
  color: var(--app-text-muted);
  line-height: 1.65;
}

@media (max-width: 1100px) {
  .upload-form {
    margin-bottom: 12px;
  }
}
</style>
