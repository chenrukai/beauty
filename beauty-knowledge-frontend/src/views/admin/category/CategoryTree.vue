<template>
  <el-card>
    <template #header>分类树</template>

    <el-row :gutter="12" style="margin-bottom: 12px">
      <el-col :xs="24" :sm="12" :md="8">
        <el-statistic title="分类总节点" :value="totalNodes" />
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-statistic title="一级分类" :value="store.categoryTree.length" />
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-input v-model="keyword" placeholder="按分类名称过滤" clearable />
      </el-col>
    </el-row>

    <el-alert
      v-if="store.categoryTree.length === 0"
      title="暂无分类数据，可能是接口异常或数据库未初始化。"
      type="warning"
      :closable="false"
      style="margin-bottom: 12px"
    />

    <el-tree
      ref="treeRef"
      :data="store.categoryTree"
      node-key="id"
      :props="{ label: 'name', children: 'children' }"
      :filter-node-method="filterNode"
      default-expand-all
      empty-text="暂无分类数据"
    />
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { ElTree } from 'element-plus'
import { useKnowledgeStore } from '../../../stores/knowledge'

const store = useKnowledgeStore()
const keyword = ref('')
const treeRef = ref<InstanceType<typeof ElTree>>()

onMounted(async () => {
  try {
    await store.fetchCategoryTree()
  } catch {
    ElMessage.error('加载分类树失败')
  }
})

watch(keyword, (val) => {
  treeRef.value?.filter(val)
})

const totalNodes = computed(() => countNodes(store.categoryTree))

function countNodes(list: any[]): number {
  return list.reduce((acc, item) => acc + 1 + countNodes(item.children || []), 0)
}

function filterNode(value: string, data: any) {
  if (!value) return true
  return String(data.name || '').toLowerCase().includes(value.toLowerCase())
}
</script>
