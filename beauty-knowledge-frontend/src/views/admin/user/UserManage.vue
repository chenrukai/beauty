<template>
  <div class="user-manage">
    <el-card shadow="never">
      <template #header>
        <div class="head">
          <strong>用户管理</strong>
          <span>仅管理员可操作。支持启用/禁用，以及普通用户与管理员角色切换。</span>
        </div>
      </template>

      <div class="filters">
        <el-input
          v-model.trim="query.keyword"
          placeholder="用户名 / 昵称"
          clearable
          class="item"
          @keyup.enter="onSearch"
        />
        <el-select v-model="query.role" clearable placeholder="角色" class="item">
          <el-option label="管理员" value="admin" />
          <el-option label="普通用户" value="user" />
        </el-select>
        <el-select v-model="query.status" clearable placeholder="状态" class="item">
          <el-option label="启用" :value="1" />
          <el-option label="禁用" :value="0" />
        </el-select>
        <el-button type="primary" @click="onSearch">查询</el-button>
        <el-button @click="onReset">重置</el-button>
      </div>

      <el-table v-loading="loading" :data="list" stripe>
        <el-table-column prop="username" label="用户名" min-width="180" />
        <el-table-column prop="nickname" label="昵称" min-width="140" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'warning' : 'info'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" min-width="180" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 1"
              type="danger"
              link
              @click="setStatus(row, 0)"
            >
              禁用
            </el-button>
            <el-button
              v-else
              type="success"
              link
              @click="setStatus(row, 1)"
            >
              启用
            </el-button>

            <el-button
              v-if="row.role === 'user'"
              type="warning"
              link
              @click="setRole(row, 'admin')"
            >
              设为管理员
            </el-button>
            <el-button
              v-else
              type="primary"
              link
              @click="setRole(row, 'user')"
            >
              设为普通用户
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :total="total"
          v-model:current-page="pageNum"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          @current-change="fetchPage"
          @size-change="onSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../../../api/request'

interface UserRow {
  id: number
  username: string
  nickname: string
  role: 'admin' | 'user'
  status: number
  createdAt: string
}

const loading = ref(false)
const list = ref<UserRow[]>([])
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)

const query = reactive<{
  keyword: string
  role: '' | 'admin' | 'user'
  status: '' | number
}>({
  keyword: '',
  role: '',
  status: ''
})

onMounted(() => {
  fetchPage()
})

async function fetchPage() {
  loading.value = true
  try {
    const res = await request.get('/admin/user/page', {
      params: {
        pageNum: pageNum.value,
        pageSize: pageSize.value,
        keyword: query.keyword || undefined,
        role: query.role || undefined,
        status: query.status === '' ? undefined : query.status
      }
    })
    list.value = res.data?.records || []
    total.value = Number(res.data?.total || 0)
  } catch (e: any) {
    ElMessage.error(e?.message || '用户列表加载失败')
  } finally {
    loading.value = false
  }
}

function onSearch() {
  pageNum.value = 1
  fetchPage()
}

function onReset() {
  query.keyword = ''
  query.role = ''
  query.status = ''
  pageNum.value = 1
  pageSize.value = 10
  fetchPage()
}

function onSizeChange() {
  pageNum.value = 1
  fetchPage()
}

async function setStatus(row: UserRow, status: 0 | 1) {
  const action = status === 1 ? '启用' : '禁用'
  await ElMessageBox.confirm(`确认${action}用户“${row.username}”吗？`, '操作确认', {
    type: 'warning',
    confirmButtonText: action,
    cancelButtonText: '取消'
  })
  try {
    await request.put(`/admin/user/${row.id}/status`, null, { params: { status } })
    ElMessage.success(`${action}成功`)
    await fetchPage()
  } catch (e: any) {
    ElMessage.error(e?.message || `${action}失败`)
  }
}

async function setRole(row: UserRow, role: 'admin' | 'user') {
  const action = role === 'admin' ? '设为管理员' : '设为普通用户'
  await ElMessageBox.confirm(`确认将用户“${row.username}”${action}吗？`, '角色确认', {
    type: 'warning',
    confirmButtonText: '确认',
    cancelButtonText: '取消'
  })
  try {
    await request.put(`/admin/user/${row.id}/role`, null, { params: { role } })
    ElMessage.success('角色更新成功')
    await fetchPage()
  } catch (e: any) {
    ElMessage.error(e?.message || '角色更新失败')
  }
}
</script>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.head span {
  color: #6b7280;
  font-size: 13px;
}

.filters {
  margin-bottom: 12px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.item {
  width: 220px;
}

.pager {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
}
</style>
