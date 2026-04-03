import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../api/request'
import { unwrapData } from '../api/response'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const categoryTree = ref<any[]>([])
  const currentCategory = ref<any | null>(null)
  const knowledgeList = ref<any[]>([])
  const knowledgePage = ref({ total: 0, pageNum: 1, pageSize: 20 })
  const taskMap = ref<Record<number, any>>({})
  const recentTasks = ref<any[]>([])

  async function fetchCategoryTree() {
    const res = await request.get('/category/tree')
    categoryTree.value = unwrapData<any[]>(res, [])
  }

  async function fetchKnowledgePage(params: any = {}) {
    const res = await request.get('/knowledge/page', { params })
    const page = unwrapData<any>(res, {})
    knowledgeList.value = page?.records || []
    knowledgePage.value = {
      total: Number(page?.total || 0),
      pageNum: Number(page?.pageNum || params.pageNum || 1),
      pageSize: Number(page?.pageSize || params.pageSize || 20)
    }
  }

  async function fetchKnowledgeDetail(id: number) {
    const res = await request.get(`/knowledge/${id}`)
    const data = unwrapData<any>(res, {})
    const knowledge = data.knowledge || {}
    return {
      ...knowledge,
      files: data.files || []
    }
  }

  async function createKnowledge(payload: any) {
    await request.post('/knowledge', payload)
  }

  async function deleteKnowledge(id: number) {
    await request.delete(`/knowledge/${id}`)
  }

  async function updateKnowledgeStatus(id: number, status: number) {
    await request.put(`/knowledge/${id}/status`, null, { params: { status } })
  }

  async function pollTask(taskId: number) {
    const res = await request.get(`/file/task/${taskId}`)
    const data = unwrapData<any>(res, null)
    taskMap.value[taskId] = data
    return data
  }

  async function fetchRecentTasks(size = 10) {
    const res = await request.get('/file/task/recent', { params: { size } })
    recentTasks.value = unwrapData<any[]>(res, [])
    return recentTasks.value
  }

  return {
    categoryTree,
    currentCategory,
    knowledgeList,
    knowledgePage,
    taskMap,
    recentTasks,
    fetchCategoryTree,
    fetchKnowledgePage,
    fetchKnowledgeDetail,
    createKnowledge,
    deleteKnowledge,
    updateKnowledgeStatus,
    pollTask,
    fetchRecentTasks
  }
})
