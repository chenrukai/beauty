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
              placeholder="请选择知识"
              style="width: 100%"
            >
              <el-option
                v-for="item in knowledgeOptions"
                :key="item.id"
                :label="item.title || '未命名知识'"
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
            <el-select v-model="fileType" disabled style="width: 260px">
              <el-option label="text_txt" value="text_txt" />
              <el-option label="text_md" value="text_md" />
              <el-option label="doc_pdf" value="doc_pdf" />
              <el-option label="doc_word" value="doc_word" />
              <el-option label="doc_ppt" value="doc_ppt" />
              <el-option label="doc_excel" value="doc_excel" />
              <el-option label="image" value="image" />
            </el-select>
            <span class="tip">已自动跟随知识类型</span>
          </el-form-item>

          <el-form-item label="选择文件">
            <input
              type="file"
              :accept="acceptByType"
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
        <el-card shadow="never">
          <template #header>辅助信息</template>
          <div class="hint">可选知识条目：{{ knowledgeOptions.length }}</div>
          <div class="hint">当前知识类型：{{ normalizeKnowledgeType(currentKnowledge?.type) }}</div>
          <div class="hint">允许扩展名：{{ acceptByType }}</div>
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
  type?: string
}

type CategoryNode = {
  id: number
  name?: string
  children?: CategoryNode[]
}

const knowledgeStore = useKnowledgeStore()
const knowledgeId = ref<number | null>(null)
const categoryId = ref<number | null>(null)
const fileType = ref<'text_txt' | 'text_md' | 'doc_pdf' | 'doc_word' | 'doc_ppt' | 'doc_excel' | 'image'>('text_txt')
const file = ref<File | null>(null)
const loading = ref(false)
const lastTaskId = ref<number | null>(null)

const knowledgeOptions = computed<KnowledgeOption[]>(() => knowledgeStore.knowledgeList || [])
const currentKnowledge = computed(() => knowledgeOptions.value.find((it) => it.id === knowledgeId.value))

const categoryOptions = computed(() => {
  const result: Array<{ id: number; label: string }> = []
  const walk = (nodes: CategoryNode[], depth: number) => {
    nodes.forEach((node) => {
      const prefix = depth === 0 ? '' : `${'  '.repeat(depth)}└ `
      result.push({ id: node.id, label: `${prefix}${node.name || `分类${node.id}`}` })
      if (node.children?.length) walk(node.children, depth + 1)
    })
  }
  walk(knowledgeStore.categoryTree as CategoryNode[], 0)
  return result
})

const acceptByType = computed(() => {
  switch (fileType.value) {
    case 'image':
      return '.png,.jpg,.jpeg,.webp,.bmp,.gif'
    case 'text_txt':
      return '.txt,.csv,.json'
    case 'text_md':
      return '.md'
    case 'doc_pdf':
      return '.pdf'
    case 'doc_word':
      return '.doc,.docx'
    case 'doc_ppt':
      return '.ppt,.pptx'
    case 'doc_excel':
      return '.xls,.xlsx'
    default:
      return '.txt'
  }
})

watch(
  () => currentKnowledge.value?.type,
  (nextType) => {
    fileType.value = mapKnowledgeTypeToUploadType(nextType)
    file.value = null
  },
  { immediate: true }
)

onMounted(async () => {
  await loadAssistData()
})

function normalizeKnowledgeType(type?: string) {
  const t = (type || '').toUpperCase()
  if (t === 'PDF') return 'DOC_PDF'
  if (t === 'DOC') return 'DOC_WORD'
  if (t === 'TEXT') return 'TEXT_TXT'
  if (['TEXT_TXT', 'TEXT_MD', 'DOC_PDF', 'DOC_WORD', 'DOC_PPT', 'DOC_EXCEL', 'IMAGE'].includes(t)) return t
  return 'TEXT_TXT'
}

function mapKnowledgeTypeToUploadType(type?: string): 'text_txt' | 'text_md' | 'doc_pdf' | 'doc_word' | 'doc_ppt' | 'doc_excel' | 'image' {
  const t = normalizeKnowledgeType(type)
  if (t === 'IMAGE') return 'image'
  if (t === 'DOC_PDF') return 'doc_pdf'
  if (t === 'DOC_WORD') return 'doc_word'
  if (t === 'DOC_PPT') return 'doc_ppt'
  if (t === 'DOC_EXCEL') return 'doc_excel'
  if (t === 'TEXT_MD') return 'text_md'
  return 'text_txt'
}

function hasAllowedExtension(name: string, uploadType: string) {
  const lower = name.toLowerCase()
  const byType: Record<string, string[]> = {
    image: ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'],
    text_txt: ['.txt', '.csv', '.json'],
    text_md: ['.md'],
    doc_pdf: ['.pdf'],
    doc_word: ['.doc', '.docx'],
    doc_ppt: ['.ppt', '.pptx'],
    doc_excel: ['.xls', '.xlsx']
  }
  const exts = byType[uploadType] || []
  return exts.some((ext) => lower.endsWith(ext))
}

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
  const chosen = target.files?.[0] || null
  if (!chosen) {
    file.value = null
    return
  }
  if (!hasAllowedExtension(chosen.name, fileType.value)) {
    ElMessage.error(`当前知识类型只允许上传：${acceptByType.value}`)
    target.value = ''
    file.value = null
    return
  }
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

.tip {
  margin-left: 10px;
  font-size: 12px;
  color: #6b7280;
}
</style>
