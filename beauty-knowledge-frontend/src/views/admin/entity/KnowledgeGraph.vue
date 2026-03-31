<template>
  <el-card>
    <template #header>知识图谱工作台</template>

    <el-row :gutter="16" style="margin-bottom: 12px">
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>产品图谱预览</template>
          <el-form label-width="96px">
            <el-form-item label="产品">
              <el-select v-model="selectedProductId" filterable placeholder="请选择产品" style="width: 100%">
                <el-option
                  v-for="item in productOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :disabled="!selectedProductId" @click="loadProductGraph">加载图谱</el-button>
            </el-form-item>
          </el-form>
          <el-descriptions v-if="graphSummary" :column="3" border>
            <el-descriptions-item label="中心节点">{{ graphSummary.centerKey }}</el-descriptions-item>
            <el-descriptions-item label="节点数">{{ graphSummary.nodeCount }}</el-descriptions-item>
            <el-descriptions-item label="边数">{{ graphSummary.edgeCount }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>两点路径查询</template>
          <el-form label-width="72px">
            <el-row :gutter="8">
              <el-col :span="12">
                <el-form-item label="起点">
                  <el-select v-model="pathForm.fromType">
                    <el-option label="产品" value="PRODUCT" />
                    <el-option label="成分" value="INGREDIENT" />
                    <el-option label="功效" value="EFFECT" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="ID">
                  <el-input-number v-model="pathForm.fromId" :min="1" controls-position="right" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="8">
              <el-col :span="12">
                <el-form-item label="终点">
                  <el-select v-model="pathForm.toType">
                    <el-option label="产品" value="PRODUCT" />
                    <el-option label="成分" value="INGREDIENT" />
                    <el-option label="功效" value="EFFECT" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="ID">
                  <el-input-number v-model="pathForm.toId" :min="1" controls-position="right" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="深度">
              <el-input-number v-model="pathForm.maxDepth" :min="1" :max="6" controls-position="right" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="searchPath">查询路径</el-button>
            </el-form-item>
          </el-form>
          <el-alert
            v-if="pathResult"
            :type="pathResult.found ? 'success' : 'warning'"
            :title="pathResult.found ? `已找到路径，跳数 ${pathResult.hopCount}` : '未找到路径'"
            :closable="false"
          />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never">
          <template #header>图谱边列表（可查看证据）</template>
          <el-table :data="graphEdges" stripe height="420">
            <el-table-column prop="predicate" label="关系" width="220" />
            <el-table-column prop="subjectKey" label="起点" min-width="180" show-overflow-tooltip />
            <el-table-column prop="objectKey" label="终点" min-width="180" show-overflow-tooltip />
            <el-table-column label="置信度" width="90">
              <template #default="{ row }">
                {{ formatConfidence(row.confidence) }}
              </template>
            </el-table-column>
            <el-table-column label="证据" width="90">
              <template #default="{ row }">
                {{ row.evidenceCount ?? 0 }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="primary" @click="loadEvidence(row)">查看证据</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card shadow="never">
          <template #header>关系证据</template>
          <el-empty v-if="evidenceList.length === 0" description="请选择一条关系查看证据" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="item in evidenceList"
              :key="item.id"
              :timestamp="item.createdAt || ''"
              placement="top"
            >
              <div style="font-weight: 600; margin-bottom: 4px">
                fileId={{ item.fileId || '-' }} | chunkId={{ item.chunkId || '-' }} | page={{ item.pageNo || '-' }}
              </div>
              <div style="margin-bottom: 4px">extractor={{ item.extractor || '-' }}，confidence={{ formatConfidence(item.confidence) }}</div>
              <div class="evidence-text">{{ item.sourceText || '-' }}</div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useEntityStore } from '../../../stores/entity'

const store = useEntityStore()
const selectedProductId = ref<number | null>(null)
const graphData = ref<any | null>(null)
const pathResult = ref<any | null>(null)
const evidenceList = ref<any[]>([])
const pathForm = ref({
  fromType: 'PRODUCT',
  fromId: 1,
  toType: 'EFFECT',
  toId: 1,
  maxDepth: 4
})

onMounted(async () => {
  try {
    await store.fetchProduct()
  } catch (e: any) {
    ElMessage.error(e?.message || '加载产品列表失败')
  }
})

const productOptions = computed(() => store.productList || [])

const graphSummary = computed(() => {
  if (!graphData.value) return null
  return {
    centerKey: graphData.value.centerKey || '-',
    nodeCount: (graphData.value.nodes || []).length,
    edgeCount: (graphData.value.edges || []).length
  }
})

const graphEdges = computed(() => graphData.value?.edges || [])

function formatConfidence(value: any) {
  const n = Number(value)
  if (Number.isNaN(n)) return '-'
  return n.toFixed(2)
}

async function loadProductGraph() {
  if (!selectedProductId.value) return
  try {
    graphData.value = await store.fetchProductGraph(selectedProductId.value)
    evidenceList.value = []
  } catch (e: any) {
    ElMessage.error(e?.message || '加载图谱失败')
  }
}

async function searchPath() {
  try {
    pathResult.value = await store.findKgPath({
      fromType: pathForm.value.fromType,
      fromId: Number(pathForm.value.fromId),
      toType: pathForm.value.toType,
      toId: Number(pathForm.value.toId),
      maxDepth: Number(pathForm.value.maxDepth)
    })
  } catch (e: any) {
    ElMessage.error(e?.message || '路径查询失败')
  }
}

async function loadEvidence(edge: any) {
  try {
    const isReverse = String(edge.predicate || '').startsWith('REVERSE_')
    const subject = parseNodeKey(edge.subjectKey)
    const object = parseNodeKey(edge.objectKey)
    const realSubject = isReverse ? object : subject
    const realObject = isReverse ? subject : object
    evidenceList.value = await store.fetchRelationEvidence({
      predicate: String(edge.predicate || '').replace(/^REVERSE_/, ''),
      subjectType: realSubject.type,
      subjectId: realSubject.id,
      objectType: realObject.type,
      objectId: realObject.id,
      size: 20
    })
    if (!evidenceList.value.length) {
      ElMessage.info('该关系暂无证据记录')
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '加载证据失败')
  }
}

function parseNodeKey(nodeKey: string) {
  const [type, id] = String(nodeKey || '').split(':')
  return { type, id: Number(id) }
}
</script>

<style scoped>
.evidence-text {
  color: var(--app-text-muted, #666);
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
