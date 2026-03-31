import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../api/request'

export const useEntityStore = defineStore('entity', () => {
  const pendingList = ref<any[]>([])
  const ingredientList = ref<any[]>([])
  const effectList = ref<any[]>([])
  const productList = ref<any[]>([])
  const pendingCount = ref(0)
  const kgExtractionConfig = ref<any>(null)

  async function fetchPending(status?: string) {
    const params: any = {}
    if (status) params.status = status
    const res = await request.get('/entity/pending', { params })
    pendingList.value = res.data || []
  }

  async function fetchPendingCount(status?: string) {
    const params: any = {}
    if (status) params.status = status
    const res = await request.get('/entity/pending/count', { params })
    pendingCount.value = Number(res.data?.count || 0)
  }

  async function fetchIngredient() {
    const res = await request.get('/entity/ingredient')
    ingredientList.value = res.data || []
  }

  async function fetchProduct() {
    const res = await request.get('/entity/product')
    productList.value = res.data || []
  }

  async function fetchEffect() {
    const res = await request.get('/entity/effect')
    effectList.value = res.data || []
  }

  async function confirm(items: Array<{ pendingId: number; accept: boolean }>, status?: string) {
    const res = await request.post('/entity/confirm', { items })
    await fetchPending(status)
    await fetchPendingCount()
    return res.data || { total: items.length, successCount: items.length, failedCount: 0, itemResults: [] }
  }

  async function fetchKgPending(status?: string) {
    const params: any = {}
    if (status) params.status = status
    const res = await request.get('/kg/pending', { params })
    pendingList.value = res.data || []
    pendingCount.value = pendingList.value.filter((it: any) => String(it?.status || '').toUpperCase() === 'PENDING').length
  }

  async function confirmKgPending(id: number, comment?: string) {
    const body: any = {}
    if (comment) body.comment = comment
    const res = await request.post(`/kg/pending/${id}/confirm`, body)
    return res.data || null
  }

  async function rejectKgPending(id: number, comment?: string) {
    const body: any = {}
    if (comment) body.comment = comment
    const res = await request.post(`/kg/pending/${id}/reject`, body)
    return res.data || null
  }

  async function fetchKgExtractionConfig() {
    const res = await request.get('/kg/config/extraction')
    kgExtractionConfig.value = res.data || null
    return kgExtractionConfig.value
  }

  async function demoSeedKgRelations(fileId: number, limit?: number) {
    const params: any = {}
    if (limit && limit > 0) params.limit = limit
    const res = await request.post(`/kg/extract/file/${fileId}/demo-seed`, null, { params })
    return res.data || null
  }

  async function fetchProductGraph(productId: number) {
    const res = await request.get(`/kg/product/${productId}/graph`)
    return res.data || { nodes: [], edges: [] }
  }

  async function findKgPath(params: { fromType: string; fromId: number; toType: string; toId: number; maxDepth?: number }) {
    const res = await request.get('/kg/path', { params })
    return res.data || null
  }

  async function fetchRelationEvidence(params: {
    predicate: string
    subjectType?: string
    subjectId?: number
    objectType?: string
    objectId?: number
    size?: number
  }) {
    const res = await request.get('/kg/evidence', { params })
    return res.data || []
  }

  async function backfillKgEvidence(limit?: number) {
    const params: any = {}
    if (limit) params.limit = limit
    const res = await request.post('/kg/evidence/backfill', null, { params })
    return res.data || null
  }

  return {
    pendingList,
    ingredientList,
    effectList,
    productList,
    pendingCount,
    kgExtractionConfig,
    fetchPending,
    fetchPendingCount,
    fetchIngredient,
    fetchEffect,
    fetchProduct,
    confirm,
    fetchKgPending,
    confirmKgPending,
    rejectKgPending,
    fetchKgExtractionConfig,
    demoSeedKgRelations,
    fetchProductGraph,
    findKgPath,
    fetchRelationEvidence,
    backfillKgEvidence
  }
})
