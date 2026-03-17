<template>
  <div class="overview">
    <el-row :gutter="12">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="metric">
          <div class="metric-label">知识总数</div>
          <div class="metric-value">{{ metrics.knowledgeTotal }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="metric">
          <div class="metric-label">分类节点</div>
          <div class="metric-value">{{ metrics.categoryTotal }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="metric">
          <div class="metric-label">待确认实体</div>
          <div class="metric-value">{{ metrics.pendingEntity }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="metric">
          <div class="metric-label">近期待处理任务</div>
          <div class="metric-value">{{ metrics.pendingTask }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="12" style="margin-top: 12px">
      <el-col :xs="24" :lg="14">
        <el-card>
          <template #header>最近任务</template>
          <el-table :data="knowledgeStore.recentTasks" stripe>
            <el-table-column prop="id" label="任务ID" width="90" />
            <el-table-column prop="fileId" label="文件ID" width="90" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" width="90" />
            <el-table-column prop="updatedAt" label="更新时间" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card>
          <template #header>页面提示</template>
          <ul class="tips">
            <li>如果“分类树”为空，先检查后端分类接口是否正常返回数据。</li>
            <li>“实体确认”为 0 是正常现象，需要先上传文件并完成抽取流程。</li>
            <li>“任务监控”可以从最近任务点“查看”，不需要手输 Task ID。</li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useKnowledgeStore } from '../../stores/knowledge'
import { useEntityStore } from '../../stores/entity'

const knowledgeStore = useKnowledgeStore()
const entityStore = useEntityStore()

onMounted(async () => {
  const results = await Promise.allSettled([
    knowledgeStore.fetchKnowledgePage({ pageNum: 1, pageSize: 200 }),
    knowledgeStore.fetchCategoryTree(),
    knowledgeStore.fetchRecentTasks(8),
    entityStore.fetchPendingCount()
  ])
  const hasFailure = results.some((it) => it.status === 'rejected')
  if (hasFailure) {
    ElMessage.warning('部分总览数据加载失败，请检查数据库表是否完整')
  }
})

const metrics = computed(() => ({
  knowledgeTotal: knowledgeStore.knowledgePage.total || knowledgeStore.knowledgeList.length,
  categoryTotal: countTreeNodes(knowledgeStore.categoryTree),
  pendingEntity: entityStore.pendingCount,
  pendingTask: knowledgeStore.recentTasks.filter((it: any) => it.status === 'PENDING' || it.status === 'RUNNING').length
}))

function countTreeNodes(list: any[]): number {
  return list.reduce((acc, node) => acc + 1 + countTreeNodes(node.children || []), 0)
}

function statusTagType(status: string) {
  if (status === 'SUCCESS') return 'success'
  if (status === 'FAILED') return 'danger'
  if (status === 'RUNNING') return 'warning'
  return 'info'
}
</script>

<style scoped>
.metric-label {
  color: #64748b;
  font-size: 13px;
}

.metric-value {
  margin-top: 6px;
  font-size: 30px;
  font-weight: 700;
  color: #0f172a;
}

.tips {
  margin: 0;
  padding-left: 18px;
  color: #334155;
  line-height: 1.8;
}
</style>
