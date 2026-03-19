<template>
  <el-card>
    <template #header>分类树管理</template>

    <el-row :gutter="12" class="top-metrics">
      <el-col :xs="24" :sm="8">
        <el-statistic title="分类总节点" :value="totalNodes" />
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-statistic title="一级分类" :value="store.categoryTree.length" />
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-input v-model="keyword" placeholder="按分类名称过滤" clearable />
      </el-col>
    </el-row>

    <div class="toolbar">
      <el-button type="primary" @click="openCreateRoot">新增一级分类</el-button>
      <el-button @click="loadTree">刷新</el-button>
    </div>

    <div class="content-grid">
      <div class="tree-panel">
        <el-alert
          v-if="store.categoryTree.length === 0"
          title="当前没有分类数据，请先新增一级分类。"
          type="warning"
          :closable="false"
          style="margin-bottom: 12px"
        />

        <div class="tree-scroll">
          <el-tree
            ref="treeRef"
            :data="store.categoryTree"
            node-key="id"
            :props="{ label: 'name', children: 'children' }"
            :filter-node-method="filterNode"
            highlight-current
            default-expand-all
            :expand-on-click-node="false"
            empty-text="暂无分类数据"
            @node-click="onNodeClick"
          >
            <template #default="{ data }">
              <div class="tree-row">
                <span class="tree-label" :class="{ 'is-disabled': Number(data.status ?? 1) === 0 }">{{ data.name }}</span>
                <el-tag v-if="Number(data.status ?? 1) === 0" type="info" size="small" effect="plain">停用</el-tag>
                <span v-else-if="data.children?.length" class="tree-count">{{ data.children.length }}</span>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <div class="detail-panel">
        <template v-if="selectedNode">
          <h3 class="detail-title">{{ selectedNode.name }}</h3>
          <div class="detail-item">
            <span>节点 ID</span>
            <strong>{{ selectedNode.id }}</strong>
          </div>
          <div class="detail-item">
            <span>父级 ID</span>
            <strong>{{ selectedNode.parentId || 0 }}</strong>
          </div>
          <div class="detail-item">
            <span>排序值</span>
            <strong>{{ selectedNode.sortOrder || 0 }}</strong>
          </div>
          <div class="detail-item">
            <span>状态</span>
            <el-tag :type="Number(selectedNode.status ?? 1) === 1 ? 'success' : 'info'">
              {{ Number(selectedNode.status ?? 1) === 1 ? '启用' : '停用' }}
            </el-tag>
          </div>

          <div class="detail-actions">
            <el-button type="primary" plain @click="openCreateChild(selectedNode)">新增子分类</el-button>
            <el-button type="warning" plain @click="openEdit(selectedNode)">编辑当前节点</el-button>
            <el-button type="danger" plain @click="removeCategory(selectedNode)">删除当前节点</el-button>
          </div>
        </template>
        <el-empty v-else description="请在左侧选择一个分类节点" :image-size="70" />
      </div>
    </div>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="分类名称" prop="name">
        <el-input v-model.trim="form.name" maxlength="50" show-word-limit />
      </el-form-item>
      <el-form-item label="父级分类">
        <el-select v-model="form.parentId" style="width: 100%">
          <el-option :value="0" label="无（一级分类）" />
          <el-option
            v-for="item in flatCategories"
            :key="item.id"
            :value="item.id"
            :label="item.label"
            :disabled="dialogMode === 'edit' && item.id === form.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="排序值">
        <el-input-number v-model="form.sortOrder" :min="0" :max="999" />
      </el-form-item>
      <el-form-item label="状态">
        <el-radio-group v-model="form.status">
          <el-radio :label="1">启用</el-radio>
          <el-radio :label="0">停用</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ElTree } from 'element-plus'
import request from '../../../api/request'
import { useKnowledgeStore } from '../../../stores/knowledge'

type CategoryNode = {
  id: number
  name: string
  parentId?: number
  sortOrder?: number
  status?: number
  children?: CategoryNode[]
}

const store = useKnowledgeStore()
const keyword = ref('')
const treeRef = ref<InstanceType<typeof ElTree>>()
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const saving = ref(false)
const formRef = ref<any>(null)
const currentNodeId = ref<number | null>(null)

const form = reactive({
  id: 0,
  name: '',
  parentId: 0,
  sortOrder: 0,
  status: 1
})

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

onMounted(async () => {
  await loadTree()
})

watch(keyword, (val) => {
  treeRef.value?.filter(val)
})

const totalNodes = computed(() => countNodes(store.categoryTree as CategoryNode[]))

const flatCategories = computed(() => {
  const result: Array<{ id: number; label: string }> = []
  const walk = (nodes: CategoryNode[], depth = 0) => {
    nodes.forEach((node) => {
      result.push({
        id: node.id,
        label: `${'  '.repeat(depth)}${node.name}`
      })
      if (node.children?.length) {
        walk(node.children, depth + 1)
      }
    })
  }
  walk(store.categoryTree as CategoryNode[])
  return result
})

const selectedNode = computed(() => {
  if (!currentNodeId.value) return null
  return findNodeById(store.categoryTree as CategoryNode[], currentNodeId.value)
})

const dialogTitle = computed(() => (dialogMode.value === 'edit' ? '编辑分类' : '新增分类'))

async function loadTree() {
  try {
    await store.fetchCategoryTree()
    const list = store.categoryTree as CategoryNode[]
    const current = currentNodeId.value ? findNodeById(list, currentNodeId.value) : null
    if (!current) {
      const first = findFirstNode(list)
      currentNodeId.value = first?.id || null
    }
    await nextTick()
    if (currentNodeId.value) {
      treeRef.value?.setCurrentKey?.(currentNodeId.value)
    }
  } catch {
    ElMessage.error('加载分类树失败')
  }
}

function countNodes(list: CategoryNode[]): number {
  return list.reduce((acc, item) => acc + 1 + countNodes(item.children || []), 0)
}

function filterNode(value: string, data: CategoryNode) {
  if (!value) return true
  return String(data.name || '').toLowerCase().includes(value.toLowerCase())
}

function findFirstNode(list: CategoryNode[]): CategoryNode | null {
  if (!list.length) return null
  return list[0]
}

function findNodeById(list: CategoryNode[], id: number): CategoryNode | null {
  for (const node of list) {
    if (node.id === id) return node
    const found = findNodeById(node.children || [], id)
    if (found) return found
  }
  return null
}

function onNodeClick(data: CategoryNode) {
  currentNodeId.value = Number(data.id)
}

function openCreateRoot() {
  dialogMode.value = 'create'
  form.id = 0
  form.name = ''
  form.parentId = 0
  form.sortOrder = 0
  form.status = 1
  dialogVisible.value = true
}

function openCreateChild(node: CategoryNode) {
  dialogMode.value = 'create'
  form.id = 0
  form.name = ''
  form.parentId = Number(node.id)
  form.sortOrder = 0
  form.status = 1
  dialogVisible.value = true
}

function openEdit(node: CategoryNode) {
  dialogMode.value = 'edit'
  form.id = Number(node.id)
  form.name = String(node.name || '')
  form.parentId = Number(node.parentId || 0)
  form.sortOrder = Number(node.sortOrder || 0)
  form.status = Number(node.status ?? 1)
  dialogVisible.value = true
}

async function submit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  saving.value = true
  try {
    const payload = {
      name: form.name,
      parentId: form.parentId,
      sortOrder: form.sortOrder,
      status: form.status
    }
    if (dialogMode.value === 'edit' && form.id) {
      await request.put(`/category/${form.id}`, payload)
      ElMessage.success('分类更新成功')
    } else {
      await request.post('/category', payload)
      ElMessage.success('分类新增成功')
    }
    dialogVisible.value = false
    const updatedId = dialogMode.value === 'edit' ? form.id : null
    await loadTree()
    if (updatedId) {
      currentNodeId.value = updatedId
      await nextTick()
      treeRef.value?.setCurrentKey?.(updatedId)
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '分类保存失败')
  } finally {
    saving.value = false
  }
}

async function removeCategory(node: CategoryNode) {
  try {
    await ElMessageBox.confirm(`确认删除分类“${node.name}”吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
  } catch {
    return
  }

  try {
    await request.delete(`/category/${node.id}`)
    ElMessage.success('删除成功')
    if (currentNodeId.value === node.id) {
      currentNodeId.value = null
    }
    await loadTree()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}
</script>

<style scoped>
.top-metrics {
  margin-bottom: 12px;
}

.toolbar {
  margin-bottom: 12px;
  display: flex;
  gap: 10px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 12px;
  align-items: start;
}

.tree-panel {
  height: clamp(520px, calc(100vh - 280px), 760px);
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  background: #fcfcfd;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tree-scroll {
  flex: 1;
  overflow: auto;
  padding-right: 4px;
}

.tree-row {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.tree-label {
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tree-label.is-disabled {
  color: #94a3b8;
  text-decoration: line-through;
}

.tree-count {
  min-width: 22px;
  height: 22px;
  border-radius: 999px;
  background: #eef2ff;
  color: #4338ca;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.detail-panel {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 14px;
  background: #fff;
  align-self: start;
  position: sticky;
  top: 12px;
  max-height: calc(100vh - 140px);
  overflow: auto;
}

.detail-title {
  margin: 0 0 12px;
  font-size: 18px;
  color: #0f172a;
}

.detail-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px dashed #e5e7eb;
  padding: 8px 0;
  color: #475569;
}

.detail-item strong {
  color: #0f172a;
}

.detail-actions {
  margin-top: 14px;
  display: grid;
  gap: 10px;
}

:deep(.el-tree-node__content) {
  height: 36px;
  border-radius: 8px;
  margin-bottom: 2px;
}

:deep(.el-tree-node__content:hover) {
  background: #eef6ff;
}

@media (max-width: 1080px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .tree-panel {
    height: auto;
  }

  .tree-scroll {
    max-height: 420px;
  }

  .detail-panel {
    position: static;
    max-height: none;
    overflow: visible;
  }
}
</style>
