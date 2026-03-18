<template>
  <div class="report-page">
    <el-card shadow="never">
      <div class="toolbar">
        <div class="title">运营报表</div>
        <div class="actions">
          <el-radio-group v-model="range" @change="loadReport">
            <el-radio-button label="day">按天</el-radio-button>
            <el-radio-button label="week">按周</el-radio-button>
          </el-radio-group>
          <el-button @click="loadReport">刷新</el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="12" style="margin-top: 12px">
      <el-col :xs="24" :md="8">
        <el-card>
          <el-statistic title="活跃用户" :value="active.activeUsers" />
        </el-card>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-card>
          <el-statistic title="行为总数" :value="active.actionCount" />
        </el-card>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-card>
          <el-statistic title="人均行为数" :value="active.avgActionsPerUser" :precision="2" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="12" style="margin-top: 12px">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>浏览趋势</template>
          <div v-if="browseTrend.length" class="trend-chart">
            <div v-for="item in browseTrend" :key="item.label" class="trend-item">
              <div class="trend-label">{{ item.label }}</div>
              <div class="trend-bar-wrap">
                <div class="trend-bar" :style="{ width: `${item.percent}%` }"></div>
              </div>
              <div class="trend-value">{{ item.count }}</div>
            </div>
          </div>
          <el-empty v-else description="暂无数据" :image-size="80" />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>浏览来源占比</template>
          <div v-if="sourceRatio.length" class="ratio-list">
            <div v-for="item in sourceRatio" :key="item.source" class="ratio-item">
              <div class="ratio-label">{{ sourceText(item.source) }}</div>
              <el-progress :percentage="item.percent" :stroke-width="10" />
            </div>
          </div>
          <el-empty v-else description="暂无数据" :image-size="80" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="12" style="margin-top: 12px">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>热门知识</template>
          <el-table :data="hotKnowledge" stripe>
            <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
            <el-table-column prop="browseCount" label="浏览次数" width="120" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>热门关键词</template>
          <el-table :data="hotKeywords" stripe>
            <el-table-column prop="keyword" label="关键词" min-width="200" />
            <el-table-column prop="searchCount" label="搜索次数" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../api/request'

const range = ref<'day' | 'week'>('week')
const active = reactive({
  activeUsers: 0,
  actionCount: 0,
  avgActionsPerUser: 0
})
const browseTrend = ref<Array<{ label: string; count: number; percent: number }>>([])
const sourceRatio = ref<Array<{ source: string; count: number; percent: number }>>([])
const hotKnowledge = ref<any[]>([])
const hotKeywords = ref<any[]>([])

onMounted(() => {
  void loadReport()
})

async function loadReport() {
  try {
    const res = await request.get('/admin/dashboard/report', { params: { range: range.value } })
    const data = res.data || {}
    Object.assign(active, data.active || {})
    hotKnowledge.value = data.hotKnowledge || []
    hotKeywords.value = data.hotKeywords || []

    const trendRaw = data.browseTrend || []
    const trendMax = Math.max(1, ...trendRaw.map((it: any) => Number(it.cnt || 0)))
    browseTrend.value = trendRaw.map((it: any) => {
      const count = Number(it.cnt || 0)
      return {
        label: String(it.label || '-'),
        count,
        percent: Math.max(6, Math.round((count * 10000) / trendMax) / 100)
      }
    })

    const ratioRaw = data.sourceRatio || []
    const ratioTotal = ratioRaw.reduce((sum: number, it: any) => sum + Number(it.count || 0), 0)
    sourceRatio.value = ratioRaw.map((it: any) => {
      const count = Number(it.count || 0)
      return {
        source: String(it.source || 'other'),
        count,
        percent: ratioTotal > 0 ? Math.round((count * 10000) / ratioTotal) / 100 : 0
      }
    })
  } catch {
    ElMessage.error('加载运营报表失败')
  }
}

function sourceText(source?: string) {
  const s = String(source || '').toLowerCase()
  if (s === 'recommend') return '推荐'
  if (s === 'search') return '搜索'
  if (s === 'favorite') return '收藏'
  return '其他'
}
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: 700;
}

.actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.trend-chart {
  display: grid;
  gap: 8px;
}

.trend-item {
  display: grid;
  grid-template-columns: 60px 1fr 56px;
  gap: 8px;
  align-items: center;
}

.trend-label,
.trend-value {
  color: #334155;
  font-size: 12px;
}

.trend-bar-wrap {
  height: 10px;
  border-radius: 999px;
  background: #e2e8f0;
  overflow: hidden;
}

.trend-bar {
  height: 100%;
  background: linear-gradient(90deg, #14b8a6, #0ea5e9);
  border-radius: 999px;
}

.ratio-list {
  display: grid;
  gap: 10px;
}

.ratio-label {
  margin-bottom: 4px;
  color: #334155;
  font-size: 13px;
}
</style>

