import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '../api/request'

interface UserInfo {
  id: number
  username: string
  nickname: string | null
  role: 'admin' | 'user'
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('bk_token'))
  const userInfo = ref<UserInfo | null>(JSON.parse(localStorage.getItem('bk_user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  async function login(username: string, password: string) {
    clearAuth()
    const res = await request.post('/auth/login', { username, password })
    token.value = res.data.token
    userInfo.value = res.data.userInfo
    localStorage.setItem('bk_token', token.value || '')
    localStorage.setItem('bk_user', JSON.stringify(userInfo.value))
  }

  async function register(username: string, password: string) {
    await request.post('/auth/register', { username, password })
  }

  async function fetchUserInfo() {
    const res = await request.get('/auth/info')
    userInfo.value = res.data
    localStorage.setItem('bk_user', JSON.stringify(userInfo.value))
  }

  async function logout() {
    try {
      await request.post('/auth/logout')
    } finally {
      clearAuth()
    }
  }

  function clearAuth() {
    token.value = null
    userInfo.value = null
    localStorage.removeItem('bk_token')
    localStorage.removeItem('bk_user')
  }

  return { token, userInfo, isLoggedIn, login, register, fetchUserInfo, logout, clearAuth }
})
