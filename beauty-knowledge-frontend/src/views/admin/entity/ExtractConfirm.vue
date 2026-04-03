<template>
  <el-card class="extract-confirm-page">
    <template #header>实体与关系候选确认</template>

    <el-row :gutter="12" class="stats-row">
      <el-col :xs="24" :sm="6">
        <el-statistic title="待确认总数" :value="store.pendingCount" />
      </el-col>
      <el-col :xs="24" :sm="6">
        <el-statistic title="实体候选" :value="candidateCount.entity" />
      </el-col>
      <el-col :xs="24" :sm="6">
        <el-statistic title="关系候选" :value="candidateCount.relation" />
      </el-col>
      <el-col :xs="24" :sm="6">
        <el-statistic title="当前筛选结果" :value="filtered.length" />
      </el-col>
    </el-row>

    <el-alert
      v-if="store.kgExtractionConfig"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
    >
      <template #title>
        规则可调：关系触发词与置信度来自后端配置
        （minSegmentLength={{ store.kgExtractionConfig.minSegmentLength }}，
        产品-成分={{ store.kgExtractionConfig.productIngredientConfidence }}，
        成分-功效={{ store.kgExtractionConfig.ingredientEffectConfidence }}，
        产品-功效={{ store.kgExtractionConfig.productEffectConfidence }}）
      </template>
    </el-alert>

    <el-form inline class="toolbar">
      <el-form-item>
        <el-select v-model="statusFilter" style="width: 150px">
          <el-option label="全部状态" value="ALL" />
          <el-option label="待确认" value="PENDING" />
          <el-option label="已确认" value="CONFIRMED" />
          <el-option label="已拒绝" value="REJECTED" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-select v-model="candidateFilter" style="width: 150px">
          <el-option label="全部候选" value="ALL" />
          <el-option label="实体候选" value="entity" />
          <el-option label="关系候选" value="relation" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-select v-model="entityTypeFilter" clearable placeholder="实体类型" style="width: 140px">
          <el-option label="成分" value="ingredient" />
          <el-option label="功效" value="effect" />
          <el-option label="产品" value="product" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-select v-model="predicateFilter" clearable placeholder="关系谓词" style="width: 220px">
          <el-option label="产品包含成分" value="PRODUCT_CONTAINS_INGREDIENT" />
          <el-option label="成分作用功效" value="INGREDIENT_HAS_EFFECT" />
          <el-option label="产品主打功效" value="PRODUCT_TARGETS_EFFECT" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-input v-model="keyword" clearable placeholder="名称关键词" style="width: 180px" />
      </el-form-item>
      <el-form-item>
        <el-input v-model="fileKeyword" clearable placeholder="文件名关键词" style="width: 200px" />
      </el-form-item>
      <el-form-item>
        <el-button @click="reload">刷新</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="success" :disabled="selectedPendingIds.length === 0" @click="batchReview(true)">
          批量确认
        </el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="danger" :disabled="selectedPendingIds.length === 0" @click="batchReview(false)">
          批量拒绝
        </el-button>
      </el-form-item>
    </el-form>

    <el-divider content-position="left">第二步：关系候选生成（演示可用）</el-divider>
    <el-form inline class="seed-toolbar">
      <el-form-item label="文件ID">
        <el-input-number v-model="demoFileId" :min="1" :step="1" controls-position="right" style="width: 180px" />
      </el-form-item>
      <el-form-item label="条数上限">
        <el-input-number v-model="demoLimit" :min="1" :max="100" :step="1" controls-position="right" style="width: 180px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="seedDemoRelations">一键生成关系候选</el-button>
      </el-form-item>
      <el-form-item>
        <span style="color: #909399; font-size: 13px">
          说明：当文本里暂未命中关系触发词时，可先用该按钮生成可审核的关系候选。
        </span>
      </el-form-item>
    </el-form>

    <el-alert
      v-if="filtered.length === 0"
      title="暂无符合条件的候选记录。请先触发抽取或调整筛选条件。"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
    />

    <el-table ref="tableRef" :data="filtered" stripe class="data-table" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="52" :selectable="isRowSelectable" />
      <el-table-column label="候选类型" width="110">
        <template #default="{ row }">
          <el-tag :type="row.candidateType === 'relation' ? 'warning' : 'success'">
            {{ row.candidateType === 'relation' ? '关系' : '实体' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="entityType" label="实体类型" width="110" />
      <el-table-column prop="entityName" label="候选名称" min-width="200" show-overflow-tooltip />
      <el-table-column label="关系详情" min-width="260" show-overflow-tooltip>
        <template #default="{ row }">
          {{ relationText(row) }}
        </template>
      </el-table-column>
      <el-table-column label="置信度" width="100">
        <template #default="{ row }">
          {{ formatConfidence(row.confidence) }}
        </template>
      </el-table-column>
      <el-table-column prop="extractMethod" label="抽取方式" width="120" />
      <el-table-column prop="sourceText" label="来源文本/文件" min-width="220" show-overflow-tooltip />
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="success" :disabled="!isRowSelectable(row)" @click="reviewOne(row.id, true)">
            确认
          </el-button>
          <el-button size="small" type="danger" :disabled="!isRowSelectable(row)" @click="reviewOne(row.id, false)">
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
const tableRef = ref()
const statusFilter = ref('PENDING')
const candidateFilter = ref('ALL')
const entityTypeFilter = ref<string | undefined>()
const predicateFilter = ref<string | undefined>()
const keyword = ref('')
const fileKeyword = ref('')
const selectedPendingIds = ref<number[]>([])

const demoFileId = ref<number>(1)
const demoLimit = ref<number>(20)

onMounted(async () => {
  await reload()
  try {
    await store.fetchKgExtractionConfig()
  } catch {
    // config is auxiliary; ignore fetch failure
  }
})

watch(statusFilter, async () => {
  await reload()
})

const candidateCount = computed(() => ({
  entity: store.pendingList.filter((it: any) => normalizeCandidateType(it) === 'entity').length,
  relation: store.pendingList.filter((it: any) => normalizeCandidateType(it) === 'relation').length
}))

const filtered = computed(() => {
  return store.pendingList.filter((it: any) => {
    const candidateType = normalizeCandidateType(it)
    const payload = parsePayload(it)
    const name = String(it.entityName || '').toLowerCase()
    const source = String(it.sourceText || '').toLowerCase()
    const predicate = String(payload?.predicate || '').toUpperCase()

    if (candidateFilter.value !== 'ALL' && candidateType !== candidateFilter.value) return false
    if (entityTypeFilter.value && String(it.entityType || '') !== entityTypeFilter.value) return false
    if (predicateFilter.value && predicate !== predicateFilter.value) return false
    if (keyword.value && !name.includes(keyword.value.toLowerCase())) return false
    if (fileKeyword.value && !source.includes(fileKeyword.value.toLowerCase())) return false
    return true
  })
})

function normalizeCandidateType(row: any) {
  return String(row?.candidateType || 'entity').toLowerCase()
}

function parsePayload(row: any) {
  const raw = row?.payloadJson
  if (!raw) return null
  if (typeof raw === 'object') return raw
  try {
    return JSON.parse(String(raw))
  } catch {
    return null
  }
}

function relationText(row: any) {
  if (normalizeCandidateType(row) !== 'relation') return '-'
  const payload = parsePayload(row)
  if (!payload) return 'payload 缺失'
  const predicate = String(payload.predicate || '-')
  const subjectName = String(payload.subjectName || '-')
  const objectName = String(payload.objectName || '-')
  return `${subjectName} --${predicate}--> ${objectName}`
}

function formatConfidence(value: any) {
  const n = Number(value)
  if (Number.isNaN(n)) return '-'
  return n.toFixed(2)
}

function isRowSelectable(row: any) {
  return String(row?.status || '').toUpperCase() === 'PENDING'
}

function onSelectionChange(rows: any[]) {
  selectedPendingIds.value = rows.filter((row) => isRowSelectable(row)).map((row) => Number(row.id))
}

async function reload() {
  try {
    const status = statusFilter.value === 'ALL' ? undefined : statusFilter.value
    await store.fetchKgPending(status)
    selectedPendingIds.value = []
    tableRef.value?.clearSelection?.()
  } catch (e: any) {
    ElMessage.error(e?.message || '加载候选失败')
  }
}

async function seedDemoRelations() {
  if (!demoFileId.value || demoFileId.value <= 0) {
    ElMessage.warning('请先输入有效的文件ID')
    return
  }
  try {
    const result = await store.demoSeedKgRelations(Number(demoFileId.value), Number(demoLimit.value || 20))
    const inserted = Number(result?.inserted || 0)
    const triples = Number(result?.triples || 0)
    if (inserted > 0) {
      ElMessage.success(`已生成关系候选 ${inserted} 条（三元组 ${triples} 组）`)
    } else {
      ElMessage.warning(`未新增关系候选（可能已存在），三元组 ${triples} 组`)
    }
    candidateFilter.value = 'relation'
    statusFilter.value = 'PENDING'
    await reload()
  } catch (e: any) {
    ElMessage.error(e?.message || '生成关系候选失败')
  }
}

async function reviewOne(id: number, accept: boolean) {
  try {
    if (accept) {
      await store.confirmKgPending(id)
    } else {
      await store.rejectKgPending(id)
    }
    ElMessage.success('操作成功')
    await reload()
  } catch (e: any) {
    ElMessage.error(e?.message || '提交失败')
  }
}

async function batchReview(accept: boolean) {
  if (!selectedPendingIds.value.length) return
  const tasks = selectedPendingIds.value.map((id) => {
    return accept ? store.confirmKgPending(id) : store.rejectKgPending(id)
  })
  const result = await Promise.allSettled(tasks)
  const success = result.filter((it) => it.status === 'fulfilled').length
  const failed = result.length - success
  if (failed > 0) {
    ElMessage.warning(`批量完成：成功 ${success}，失败 ${failed}`)
  } else {
    ElMessage.success(`批量处理成功：${success} 条`)
  }
  await reload()
}

function statusText(status?: string) {
  const s = String(status || '').toUpperCase()
  if (s === 'PENDING') return '待确认'
  if (s === 'CONFIRMED') return '已确认'
  if (s === 'REJECTED') return '已拒绝'
  return status || '-'
}

function statusType(status?: string) {
  const s = String(status || '').toUpperCase()
  if (s === 'PENDING') return 'warning'
  if (s === 'CONFIRMED') return 'success'
  if (s === 'REJECTED') return 'danger'
  return 'info'
}
</script>

<style scoped>
.extract-confirm-page {
  --panel-gap: 14px;
}

.stats-row {
  margin-bottom: var(--panel-gap);
}

.toolbar,
.seed-toolbar {
  padding: 10px 12px;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--app-card-bg) 92%, transparent);
}

.toolbar {
  margin-bottom: 10px;
}

.seed-toolbar {
  margin-bottom: var(--panel-gap);
}

.toolbar :deep(.el-form-item),
.seed-toolbar :deep(.el-form-item) {
  margin-bottom: 8px;
}

.data-table {
  border: 1px solid var(--app-border);
  border-radius: 12px;
}
</style>
