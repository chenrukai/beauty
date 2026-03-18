<template>
  <el-card>
    <template #header>公告管理</template>

    <el-form inline>
      <el-form-item>
        <el-select v-model="query.status" clearable placeholder="状态" style="width: 140px">
          <el-option label="已发布" :value="1" />
          <el-option label="已下线" :value="0" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-input v-model="query.keyword" clearable placeholder="标题/内容关键词" style="width: 240px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="load(1)">查询</el-button>
      </el-form-item>
      <el-form-item>
        <el-button @click="reset">重置</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="success" @click="openCreate">新增公告</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '已发布' : '已下线' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="isTop" label="置顶" width="100">
        <template #default="{ row }">
          <el-tag :type="row.isTop === 1 ? 'warning' : 'info'">{{ row.isTop === 1 ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="publishTime" label="发布时间" min-width="170" />
      <el-table-column prop="expireTime" label="过期时间" min-width="170" />
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="warning" @click="setTop(row, row.isTop === 1 ? 0 : 1)">
            {{ row.isTop === 1 ? '取消置顶' : '置顶' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        background
        layout="total, prev, pager, next"
        :current-page="pageNum"
        :page-size="pageSize"
        :total="total"
        @current-change="load"
      />
    </div>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="editingId ? '编辑公告' : '新增公告'" width="680px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" maxlength="120" show-word-limit />
      </el-form-item>
      <el-form-item label="内容" prop="content">
        <el-input v-model="form.content" type="textarea" :rows="6" maxlength="2000" show-word-limit />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="form.status">
          <el-radio :label="1">发布</el-radio>
          <el-radio :label="0">下线</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="置顶">
        <el-switch v-model="isTopSwitch" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../../api/request'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const list = ref<any[]>([])
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)

const query = reactive<{ status?: number; keyword?: string }>({})
const formRef = ref<any>(null)
const form = reactive({
  title: '',
  content: '',
  status: 1,
  isTop: 0
})
const isTopSwitch = ref(false)

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

load(1)

async function load(page = 1) {
  pageNum.value = page
  loading.value = true
  try {
    const res = await request.get('/admin/notice/page', {
      params: {
        pageNum: pageNum.value,
        pageSize: pageSize.value,
        status: query.status,
        keyword: query.keyword
      }
    })
    list.value = res.data?.records || []
    total.value = Number(res.data?.total || 0)
  } catch (e: any) {
    ElMessage.error(e?.message || '加载公告失败')
  } finally {
    loading.value = false
  }
}

function reset() {
  query.status = undefined
  query.keyword = undefined
  load(1)
}

function openCreate() {
  editingId.value = null
  form.title = ''
  form.content = ''
  form.status = 1
  form.isTop = 0
  isTopSwitch.value = false
  dialogVisible.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  form.title = row.title || ''
  form.content = row.content || ''
  form.status = Number(row.status || 0)
  form.isTop = Number(row.isTop || 0)
  isTopSwitch.value = form.isTop === 1
  dialogVisible.value = true
}

async function setTop(row: any, isTop: 0 | 1) {
  try {
    await request.put(`/admin/notice/${row.id}/top`, null, { params: { isTop } })
    ElMessage.success(isTop === 1 ? '已置顶' : '已取消置顶')
    await load(pageNum.value)
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  }
}

async function submit() {
  const formEl = formRef.value
  if (!formEl) return
  try {
    await formEl.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    const payload = {
      title: form.title,
      content: form.content,
      status: form.status,
      isTop: isTopSwitch.value ? 1 : 0
    }
    if (editingId.value) {
      await request.put(`/admin/notice/${editingId.value}`, payload)
    } else {
      await request.post('/admin/notice', payload)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    await load(1)
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
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

