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
          <el-option label="草稿" :value="0" />
          <el-option label="已发布" :value="1" />
          <el-option label="已下线" :value="2" />
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
      <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="statusTag(Number(row.status))">
            {{ statusText(Number(row.status)) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="viewCount" label="浏览" width="100" />
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDetail(row.id)">详情</el-button>
          <el-button
            v-if="Number(row.status) === 0"
            link
            type="success"
            @click="changeStatus(row.id, 1, row.title)"
          >
            发布
          </el-button>
          <el-button
            v-if="Number(row.status) === 1"
            link
            type="warning"
            @click="changeStatus(row.id, 2, row.title)"
          >
            下线
          </el-button>
          <el-button
            v-if="Number(row.status) === 2"
            link
            type="primary"
            @click="changeStatus(row.id, 1, row.title)"
          >
            重新发布
          </el-button>
          <el-button link type="danger" @click="removeKnowledge(row.id, row.title)">删除</el-button>
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
        <el-descriptions-item label="标题">{{ detail.title }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ statusText(Number(detail.status)) }}</el-descriptions-item>
        <el-descriptions-item label="摘要">{{ detail.summary || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-divider />
      <LinkifiedText class="content" :text="detail.content || '暂无正文'" />
      <el-divider />
      <div class="files-title">关联文件（{{ detail.files?.length || 0 }}）</div>
      <el-table :data="detail.files || []" stripe size="small">
        <el-table-column prop="id" label="文件ID" width="90" />
        <el-table-column prop="originalName" label="文件名" min-width="180" show-overflow-tooltip />
        <el-table-column prop="fileType" label="类型" width="100" />
        <el-table-column prop="processStatus" label="处理状态" width="120" />
        <el-table-column prop="createdAt" label="上传时间" min-width="180" />
      </el-table>
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

      <el-form-item label="状态">
        <el-radio-group v-model="createForm.status">
          <el-radio :label="0">草稿</el-radio>
          <el-radio :label="1">已发布</el-radio>
          <el-radio :label="2">已下线</el-radio>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { useKnowledgeStore } from '../../../stores/knowledge'
import LinkifiedText from '../../../components/common/LinkifiedText.vue'

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
  content: '',
  status: 0
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

async function removeKnowledge(id: number, title: string) {
  try {
    await ElMessageBox.confirm(`确认删除知识《${title}》吗？该操作不可恢复。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
  } catch {
    return
  }

  try {
    await store.deleteKnowledge(id)
    ElMessage.success('删除成功')
    if (detail.value?.id === id) {
      drawerVisible.value = false
      detail.value = null
    }
    await load(pageNum.value)
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

async function changeStatus(id: number, status: 0 | 1 | 2, title: string) {
  const action = status === 1 ? '发布' : status === 2 ? '下线' : '撤回为草稿'
  try {
    await ElMessageBox.confirm(`确认${action}知识《${title}》吗？`, '状态确认', {
      type: 'warning',
      confirmButtonText: action,
      cancelButtonText: '取消'
    })
  } catch {
    return
  }

  try {
    await store.updateKnowledgeStatus(id, status)
    ElMessage.success(`${action}成功`)
    await load(pageNum.value)
  } catch (e: any) {
    ElMessage.error(e?.message || `${action}失败`)
  }
}

function statusText(status: number) {
  if (status === 0) return '草稿'
  if (status === 1) return '已发布'
  if (status === 2) return '已下线'
  return '未知'
}

function statusTag(status: number) {
  if (status === 1) return 'success'
  if (status === 2) return 'warning'
  return 'info'
}

function openCreate() {
  createForm.value = {
    title: '',
    summary: '',
    categoryId: flatCategories.value[0]?.id,
    content: '',
    status: 0
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
    await store.createKnowledge({
      title: createForm.value.title,
      summary: createForm.value.summary,
      categoryId: createForm.value.categoryId,
      content: createForm.value.content,
      status: createForm.value.status
    })
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

.files-title {
  margin-bottom: 10px;
  font-weight: 600;
  color: #0f172a;
}
</style>

