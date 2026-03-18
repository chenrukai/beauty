import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../api/request'

export const useEntityStore = defineStore('entity', () => {
  const pendingList = ref<any[]>([])
  const ingredientList = ref<any[]>([])
  const productList = ref<any[]>([])
  const pendingCount = ref(0)

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

  async function confirm(items: Array<{ pendingId: number; accept: boolean }>, status?: string) {
    await request.post('/entity/confirm', { items })
    await fetchPending(status)
    await fetchPendingCount()
  }

  return { pendingList, ingredientList, productList, pendingCount, fetchPending, fetchPendingCount, fetchIngredient, fetchProduct, confirm }
})
