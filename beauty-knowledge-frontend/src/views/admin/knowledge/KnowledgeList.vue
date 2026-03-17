<template>
  <el-card>
    <template #header>知识列表</template>

    <el-row :gutter="12" style="margin-bottom: 12px">
      <el-col :xs="12" :sm="8" :md="6">
        <el-statistic title="当前页条数" :value="store.knowledgeList.length" />
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <el-statistic title="总条数" :value="store.knowledgePage.total" />
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <el-statistic title="已发布" :value="publishedCount" />
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <el-statistic title="总浏览量" :value="viewTotal" />
      </el-col>
    </el-row>

    <el-form inline>
      <el-form-item>
        <el-input
          v-model="keyword"
          clearable
          placeholder="输入关键词搜索标题或内容"
          style="width: 260px"
        />
      </el-form-item>
      <el-form-item>
        <el-select v-model="status" clearable placeholder="状态筛选" style="width: 160px">
          <el-option label="已发布" :value="1" />
          <el-option label="草稿" :value="0" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="load(1)">查询</el-button>
      </el-form-item>
      <el-form-item>
        <el-button @click="reset">重置</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="success" @click="openCreate">新增知识</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="store.knowledgeList" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
      <el-table-column prop="type" label="类型" width="110" />
      <el-table-column prop="status" label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="Number(row.status) === 1 ? 'success' : 'info'">
            {{ Number(row.status) === 1 ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="viewCount" label="浏览" width="100" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDetail(row.id)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        background
        layout="prev, pager, next, total"
        :current-page="pageNum"
        :page-size="pageSize"
        :total="store.knowledgePage.total"
        @current-change="load"
      />
    </div>
  </el-card>

  <el-drawer v-model="drawerVisible" title="知识详情" size="46%">
    <template v-if="detail">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="ID">{{ detail.id }}</el-descriptions-item>
        <el-descriptions-item label="标题">{{ detail.title }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ detail.type }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ Number(detail.status) === 1 ? '已发布' : '草稿' }}</el-descriptions-item>
        <el-descriptions-item label="摘要">{{ detail.summary || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-divider />
      <div class="content">{{ detail.content || '暂无正文' }}</div>
    </template>
  </el-drawer>

  <el-dialog v-model="createVisible" title="新增知识" width="680px" destroy-on-close>
    <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="88px">
      <el-form-item label="标题" prop="title">
        <el-input v-model="createForm.title" maxlength="120" show-word-limit placeholder="请输入标题" />
      </el-form-item>

      <el-form-item label="分类" prop="categoryId">
        <el-select v-model="createForm.categoryId" filterable placeholder="请选择分类">
          <el-option
            v-for="item in flatCategories"
            :key="item.id"
            :label="item.label"
            :value="item.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="类型">
        <el-select v-model="createForm.type" style="width: 180px">
          <el-option label="TEXT" value="TEXT" />
          <el-option label="PDF" value="PDF" />
          <el-option label="IMAGE" value="IMAGE" />
        </el-select>
      </el-form-item>

      <el-form-item label="状态">
        <el-radio-group v-model="createForm.status">
          <el-radio :label="1">已发布</el-radio>
          <el-radio :label="0">草稿</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="摘要">
        <el-input
          v-model="createForm.summary"
          type="textarea"
          :rows="2"
          maxlength="300"
          show-word-limit
          placeholder="请输入摘要（可选）"
        />
      </el-form-item>

      <el-form-item label="正文" prop="content">
        <el-input
          v-model="createForm.content"
          type="textarea"
          :rows="8"
          maxlength="4000"
          show-word-limit
          placeholder="请输入正文内容"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="createVisible = false">取消</el-button>
      <el-button type="primary" :loading="creating" @click="submitCreate">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useKnowledgeStore } from '../../../stores/knowledge'

const store = useKnowledgeStore()
const keyword = ref('')
const status = ref<number | undefined>()
const pageNum = ref(1)
const pageSize = ref(20)
const drawerVisible = ref(false)
const detail = ref<any>(null)
const createVisible = ref(false)
const creating = ref(false)
const createFormRef = ref<any>(null)
const createForm = ref({
  title: '',
  summary: '',
  categoryId: undefined as number | undefined,
  type: 'TEXT',
  content: '',
  status: 1
})
const createRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  categoryId: [{ required: true, message: '请选择分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入正文', trigger: 'blur' }]
}

onMounted(() => {
  store.fetchCategoryTree()
  load(1)
})

const publishedCount = computed(() =>
  store.knowledgeList.filter((it: any) => Number(it.status) === 1).length
)

const viewTotal = computed(() =>
  store.knowledgeList.reduce((sum: number, it: any) => sum + Number(it.viewCount || 0), 0)
)

const flatCategories = computed(() => {
  const out: Array<{ id: number; label: string }> = []
  const walk = (nodes: any[], depth = 0) => {
    for (const n of nodes || []) {
      out.push({ id: n.id, label: `${'  '.repeat(depth)}${n.name}` })
      if (n.children?.length) {
        walk(n.children, depth + 1)
      }
    }
  }
  walk(store.categoryTree || [])
  return out
})

function buildParams(page: number) {
  const params: any = { pageNum: page, pageSize: pageSize.value }
  if (keyword.value) params.keyword = keyword.value
  if (status.value !== undefined) params.status = status.value
  return params
}

async function load(page = 1) {
  pageNum.value = page
  try {
    await store.fetchKnowledgePage(buildParams(page))
  } catch {
    ElMessage.error('加载知识列表失败')
  }
}

function reset() {
  keyword.value = ''
  status.value = undefined
  load(1)
}

async function openDetail(id: number) {
  try {
    detail.value = await store.fetchKnowledgeDetail(id)
    drawerVisible.value = true
  } catch {
    ElMessage.error('加载详情失败')
  }
}

function openCreate() {
  createForm.value = {
    title: '',
    summary: '',
    categoryId: flatCategories.value[0]?.id,
    type: 'TEXT',
    content: '',
    status: 1
  }
  createVisible.value = true
}

async function submitCreate() {
  const formEl = createFormRef.value
  if (!formEl) return

  try {
    await formEl.validate()
  } catch {
    return
  }

  creating.value = true
  try {
    await store.createKnowledge(createForm.value)
    ElMessage.success('新增成功')
    createVisible.value = false
    await load(1)
  } catch (e: any) {
    ElMessage.error(e?.message || '新增失败')
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.pager {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.content {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #334155;
}
</style>
