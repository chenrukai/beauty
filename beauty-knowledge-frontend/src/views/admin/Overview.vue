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
          <div class="metric-label">待处理任务</div>
          <div class="metric-value">{{ metrics.pendingTask }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="12" style="margin-top: 12px">
      <el-col :xs="24" :lg="16">
        <el-card>
          <template #header>最近任务</template>
          <el-table :data="knowledgeStore.recentTasks" stripe>
            <el-table-column prop="fileName" label="文件名" min-width="200" show-overflow-tooltip />
            <el-table-column prop="knowledgeTitle" label="所属知识" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="进度" width="150">
              <template #default="{ row }">
                <el-progress :percentage="toPercent(row.progress)" :stroke-width="8" />
              </template>
            </el-table-column>
            <el-table-column prop="updatedAt" label="更新时间" min-width="170" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card>
          <template #header>检查提示</template>
          <ul class="tips">
            <li>优先看“文件名 + 所属知识 + 状态 + 结果信息”。</li>
            <li>失败任务可在“任务监控”页面直接重试。</li>
            <li>如果任务长期处于 PENDING，请检查 RabbitMQ 消费端。</li>
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
  if (results.some((it) => it.status === 'rejected')) {
    ElMessage.warning('部分总览数据加载失败')
  }
})

const metrics = computed(() => ({
  knowledgeTotal: knowledgeStore.knowledgePage.total || knowledgeStore.knowledgeList.length,
  categoryTotal: countTreeNodes(knowledgeStore.categoryTree),
  pendingEntity: entityStore.pendingCount,
  pendingTask: knowledgeStore.recentTasks.filter((it: any) =>
    ['PENDING', 'PROCESSING', 'RUNNING'].includes((it.status || '').toUpperCase())
  ).length
}))

function countTreeNodes(list: any[]): number {
  return list.reduce((acc, node) => acc + 1 + countTreeNodes(node.children || []), 0)
}

function statusTagType(status?: string) {
  const s = (status || '').toUpperCase()
  if (s.includes('SUCCESS')) return 'success'
  if (s.includes('FAIL')) return 'danger'
  if (s.includes('PROCESS') || s.includes('RUN') || s.includes('PENDING')) return 'warning'
  return 'info'
}

function toPercent(progress?: number) {
  const val = Number(progress || 0)
  return Math.max(0, Math.min(100, val))
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
