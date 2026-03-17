<template>
  <div class="user-manage">
    <el-card shadow="never">
      <template #header>
        <div class="head">
          <strong>User Management</strong>
          <span>Admin only. All self-registered accounts are normal users.</span>
        </div>
      </template>

      <div class="filters">
        <el-input
          v-model.trim="query.keyword"
          placeholder="Username / Nickname"
          clearable
          class="item"
          @keyup.enter="onSearch"
        />
        <el-select v-model="query.role" clearable placeholder="Role" class="item">
          <el-option label="Admin" value="admin" />
          <el-option label="User" value="user" />
        </el-select>
        <el-select v-model="query.status" clearable placeholder="Status" class="item">
          <el-option label="Enabled" :value="1" />
          <el-option label="Disabled" :value="0" />
        </el-select>
        <el-button type="primary" @click="onSearch">Search</el-button>
        <el-button @click="onReset">Reset</el-button>
      </div>

      <el-table v-loading="loading" :data="list" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="Username" min-width="180" />
        <el-table-column prop="nickname" label="Nickname" min-width="120" />
        <el-table-column prop="role" label="Role" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'warning' : 'info'">
              {{ row.role === 'admin' ? 'Admin' : 'User' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? 'Enabled' : 'Disabled' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="Created At" min-width="180" />
        <el-table-column label="Action" width="140" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 1"
              type="danger"
              link
              @click="setStatus(row, 0)"
            >
              Disable
            </el-button>
            <el-button
              v-else
              type="success"
              link
              @click="setStatus(row, 1)"
            >
              Enable
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
    ElMessage.error(e?.message || 'Failed to load users')
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
  const action = status === 1 ? 'Enable' : 'Disable'
  await ElMessageBox.confirm(`Confirm ${action.toLowerCase()} user "${row.username}"?`, 'Confirm', {
    type: 'warning',
    confirmButtonText: action,
    cancelButtonText: 'Cancel'
  })
  try {
    await request.put(`/admin/user/${row.id}/status`, null, { params: { status } })
    ElMessage.success(`${action} success`)
    await fetchPage()
  } catch (e: any) {
    ElMessage.error(e?.message || `${action} failed`)
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
