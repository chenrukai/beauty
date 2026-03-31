<template>
  <el-card>
    <template #header>知识图谱工作台（演示版）</template>

    <el-row :gutter="16" style="margin-bottom: 12px">
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>1) 产品图谱预览</template>
          <el-form label-width="92px">
            <el-form-item label="选择产品">
              <el-select v-model="selectedProductId" filterable placeholder="请选择产品" style="width: 100%">
                <el-option v-for="item in productOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :disabled="!selectedProductId" @click="loadProductGraph">加载图谱</el-button>
              <el-button @click="runBackfillEvidence">回填历史关系证据</el-button>
            </el-form-item>
          </el-form>

          <el-descriptions v-if="graphSummary" :column="3" border>
            <el-descriptions-item label="中心产品">{{ graphSummary.centerName }}</el-descriptions-item>
            <el-descriptions-item label="节点数">{{ graphSummary.nodeCount }}</el-descriptions-item>
            <el-descriptions-item label="关系数">{{ graphSummary.edgeCount }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>2) 两点关系路径</template>
          <el-form label-width="72px">
            <el-row :gutter="8">
              <el-col :span="10">
                <el-form-item label="起点">
                  <el-select v-model="pathForm.fromType">
                    <el-option label="产品" value="PRODUCT" />
                    <el-option label="成分" value="INGREDIENT" />
                    <el-option label="功效" value="EFFECT" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="14">
                <el-form-item label="名称">
                  <el-select v-model="pathForm.fromId" filterable placeholder="请选择">
                    <el-option v-for="item in fromOptions" :key="item.id" :label="item.name" :value="item.id" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="8">
              <el-col :span="10">
                <el-form-item label="终点">
                  <el-select v-model="pathForm.toType">
                    <el-option label="产品" value="PRODUCT" />
                    <el-option label="成分" value="INGREDIENT" />
                    <el-option label="功效" value="EFFECT" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="14">
                <el-form-item label="名称">
                  <el-select v-model="pathForm.toId" filterable placeholder="请选择">
                    <el-option v-for="item in toOptions" :key="item.id" :label="item.name" :value="item.id" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="深度">
              <el-input-number v-model="pathForm.maxDepth" :min="1" :max="6" controls-position="right" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :disabled="!pathForm.fromId || !pathForm.toId" @click="searchPath">查询路径</el-button>
            </el-form-item>
          </el-form>

          <el-alert
            v-if="pathResult"
            :type="pathResult.found ? 'success' : 'warning'"
            :title="pathResult.found ? `已找到路径，跳数 ${pathResult.hopCount}` : '未找到路径'"
            :description="pathText"
            :closable="false"
          />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never">
          <template #header>3) 关系清单（可查证据）</template>
          <el-table :data="graphEdges" stripe height="420">
            <el-table-column label="关系语义" min-width="320" show-overflow-tooltip>
              <template #default="{ row }">
                {{ edgeSentence(row) }}
              </template>
            </el-table-column>
            <el-table-column label="置信度" width="92">
              <template #default="{ row }">
                {{ formatConfidence(row.confidence) }}
              </template>
            </el-table-column>
            <el-table-column label="证据数" width="90">
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
            <el-timeline-item v-for="item in evidenceList" :key="item.id" :timestamp="item.createdAt || ''" placement="top">
              <div style="font-weight: 600; margin-bottom: 4px">
                文件ID={{ item.fileId || '-' }} | 分块ID={{ item.chunkId || '-' }} | 页码={{ item.pageNo || '-' }}
              </div>
              <div style="margin-bottom: 4px">
                来源={{ item.extractor || '-' }}，置信度={{ formatConfidence(item.confidence) }}
              </div>
              <div class="evidence-text">{{ item.sourceText || '-' }}</div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useEntityStore } from '../../../stores/entity'

const store = useEntityStore()
const selectedProductId = ref<number | null>(null)
const graphData = ref<any | null>(null)
const pathResult = ref<any | null>(null)
const evidenceList = ref<any[]>([])
const pathForm = ref({
  fromType: 'PRODUCT',
  fromId: null as number | null,
  toType: 'EFFECT',
  toId: null as number | null,
  maxDepth: 4
})

onMounted(async () => {
  try {
    await Promise.all([store.fetchProduct(), store.fetchIngredient(), store.fetchEffect()])
  } catch (e: any) {
    ElMessage.error(e?.message || '加载基础数据失败')
  }
})

const productOptions = computed(() => store.productList || [])

const nodeMap = computed(() => {
  const m = new Map<string, any>()
  for (const n of graphData.value?.nodes || []) {
    m.set(String(n.nodeKey), n)
  }
  return m
})

const graphSummary = computed(() => {
  if (!graphData.value) return null
  const centerKey = String(graphData.value.centerKey || '')
  const center = nodeMap.value.get(centerKey)
  return {
    centerName: center?.name || centerKey || '-',
    nodeCount: (graphData.value.nodes || []).length,
    edgeCount: (graphData.value.edges || []).length
  }
})

const graphEdges = computed(() => graphData.value?.edges || [])

const fromOptions = computed(() => {
  if (pathForm.value.fromType === 'PRODUCT') return store.productList || []
  if (pathForm.value.fromType === 'INGREDIENT') return store.ingredientList || []
  return store.effectList || []
})

const toOptions = computed(() => {
  if (pathForm.value.toType === 'PRODUCT') return store.productList || []
  if (pathForm.value.toType === 'INGREDIENT') return store.ingredientList || []
  return store.effectList || []
})

watch(
  () => pathForm.value.fromType,
  () => {
    pathForm.value.fromId = null
  }
)

watch(
  () => pathForm.value.toType,
  () => {
    pathForm.value.toId = null
  }
)

const pathText = computed(() => {
  if (!pathResult.value) return ''
  if (!pathResult.value.found) return '请尝试提高深度，或更换起点/终点。'
  const nodes: any[] = pathResult.value.nodes || []
  const edges: any[] = pathResult.value.edges || []
  if (!nodes.length || !edges.length) return '已找到路径。'
  const pieces: string[] = []
  for (let i = 0; i < edges.length; i++) {
    const left = nodes[i]?.name || formatNodeKey(edges[i].subjectKey)
    const right = nodes[i + 1]?.name || formatNodeKey(edges[i].objectKey)
    pieces.push(`${left} --${predicateZh(edges[i].predicate)}--> ${right}`)
  }
  return pieces.join(' ； ')
})

function formatConfidence(value: any) {
  const n = Number(value)
  if (Number.isNaN(n)) return '-'
  return n.toFixed(2)
}

function typeZh(type: string) {
  if (type === 'PRODUCT') return '产品'
  if (type === 'INGREDIENT') return '成分'
  if (type === 'EFFECT') return '功效'
  return type
}

function predicateZh(predicate: string) {
  const p = String(predicate || '').replace(/^REVERSE_/, '')
  if (p === 'PRODUCT_CONTAINS_INGREDIENT') return '包含成分'
  if (p === 'INGREDIENT_HAS_EFFECT') return '对应功效'
  if (p === 'PRODUCT_TARGETS_EFFECT') return '主打功效'
  return p
}

function formatNodeKey(nodeKey: string) {
  const [type, id] = String(nodeKey || '').split(':')
  return `${typeZh(type)}#${id || '-'}`
}

function nodeName(nodeKey: string) {
  const node = nodeMap.value.get(String(nodeKey))
  if (node?.name) return node.name
  return formatNodeKey(nodeKey)
}

function edgeSentence(edge: any) {
  return `${nodeName(edge.subjectKey)} ${predicateZh(edge.predicate)} ${nodeName(edge.objectKey)}`
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

async function runBackfillEvidence() {
  try {
    const result = await store.backfillKgEvidence(5000)
    ElMessage.success(`回填完成：新增证据 ${Number(result?.insertedEvidence || 0)}，更新关系 ${Number(result?.updatedRelations || 0)}`)
    if (selectedProductId.value) {
      await loadProductGraph()
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '回填失败')
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
