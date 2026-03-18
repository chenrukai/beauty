import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../api/request'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const categoryTree = ref<any[]>([])
  const currentCategory = ref<any | null>(null)
  const knowledgeList = ref<any[]>([])
  const knowledgePage = ref({ total: 0, pageNum: 1, pageSize: 20 })
  const taskMap = ref<Record<number, any>>({})
  const recentTasks = ref<any[]>([])

  async function fetchCategoryTree() {
    const res = await request.get('/category/tree')
    categoryTree.value = res.data || []
  }

  async function fetchKnowledgePage(params: any = {}) {
    const res = await request.get('/knowledge/page', { params })
    knowledgeList.value = res.data?.records || []
    knowledgePage.value = {
      total: Number(res.data?.total || 0),
      pageNum: Number(res.data?.pageNum || params.pageNum || 1),
      pageSize: Number(res.data?.pageSize || params.pageSize || 20)
    }
  }

  async function fetchKnowledgeDetail(id: number) {
    const res = await request.get(`/knowledge/${id}`)
    const data = res.data || {}
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

  async function updateKnowledgeStatus(id: number, status: 0 | 1) {
    await request.put(`/knowledge/${id}/status`, null, { params: { status } })
  }

  async function pollTask(taskId: number) {
    const res = await request.get(`/file/task/${taskId}`)
    taskMap.value[taskId] = res.data
    return res.data
  }

  async function fetchRecentTasks(size = 10) {
    const res = await request.get('/file/task/recent', { params: { size } })
    recentTasks.value = res.data || []
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
