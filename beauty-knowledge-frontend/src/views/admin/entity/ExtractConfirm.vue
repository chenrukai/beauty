<template>
  <el-card>
    <template #header>实体待确认</template>

    <el-row :gutter="12" style="margin-bottom: 12px">
      <el-col :xs="24" :sm="8">
        <el-statistic title="待确认总数" :value="store.pendingCount" />
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-statistic title="成分候选" :value="typeCount.ingredient" />
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-statistic title="产品候选" :value="typeCount.product" />
      </el-col>
    </el-row>

    <el-form inline>
      <el-form-item>
        <el-select v-model="typeFilter" clearable placeholder="按实体类型筛选" style="width: 180px">
          <el-option label="成分" value="ingredient" />
          <el-option label="功效" value="effect" />
          <el-option label="产品" value="product" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-select v-model="statusFilter" placeholder="按状态筛选" style="width: 180px">
          <el-option label="全部" value="ALL" />
          <el-option label="待确认" value="PENDING" />
          <el-option label="已确认" value="CONFIRMED" />
          <el-option label="已拒绝" value="REJECTED" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-input v-model="keyword" clearable placeholder="按名称搜索" style="width: 220px" />
      </el-form-item>
      <el-form-item>
        <el-button @click="reload">刷新</el-button>
      </el-form-item>
    </el-form>

    <el-alert
      v-if="filtered.length === 0"
      title="暂无待确认实体。通常在上传文件并完成抽取后会产生记录。"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
    />

    <el-table :data="filtered" stripe>
      <el-table-column prop="entityType" label="类型" width="120" />
      <el-table-column prop="entityName" label="名称" min-width="180" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="extractMethod" label="来源" width="120" />
      <el-table-column prop="sourceText" label="来源文本" min-width="260" show-overflow-tooltip />
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button
            size="small"
            type="success"
            :disabled="row.status !== 'PENDING'"
            @click="confirmOne(row.id, true)"
          >
            确认
          </el-button>
          <el-button
            size="small"
            type="danger"
            :disabled="row.status !== 'PENDING'"
            @click="confirmOne(row.id, false)"
          >
            拒绝
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useEntityStore } from '../../../stores/entity'

const store = useEntityStore()
const typeFilter = ref<string | undefined>()
const statusFilter = ref('ALL')
const keyword = ref('')

onMounted(() => {
  reload()
})

watch(statusFilter, () => {
  reload()
})

const filtered = computed(() => {
  return store.pendingList.filter((it: any) => {
    if (typeFilter.value && it.entityType !== typeFilter.value) return false
    if (keyword.value && !String(it.entityName || '').toLowerCase().includes(keyword.value.toLowerCase())) return false
    return true
  })
})

const typeCount = computed(() => ({
  ingredient: store.pendingList.filter((it: any) => it.entityType === 'ingredient').length,
  effect: store.pendingList.filter((it: any) => it.entityType === 'effect').length,
  product: store.pendingList.filter((it: any) => it.entityType === 'product').length
}))

async function reload() {
  try {
    await Promise.all([store.fetchPending(statusFilter.value), store.fetchPendingCount()])
  } catch {
    ElMessage.error('加载待确认实体失败')
  }
}

async function confirmOne(id: number, accept: boolean) {
  try {
    await store.confirm([{ pendingId: id, accept }], statusFilter.value)
    ElMessage.success('操作成功')
  } catch {
    ElMessage.error('提交确认失败')
  }
}

function statusText(status?: string) {
  const s = (status || '').toUpperCase()
  if (s === 'PENDING') return '待确认'
  if (s === 'CONFIRMED') return '已确认'
  if (s === 'REJECTED') return '已拒绝'
  return status || '-'
}

function statusType(status?: string) {
  const s = (status || '').toUpperCase()
  if (s === 'CONFIRMED') return 'success'
  if (s === 'REJECTED') return 'danger'
  if (s === 'PENDING') return 'warning'
  return 'info'
}
</script>
