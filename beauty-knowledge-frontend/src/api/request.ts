import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { getErrorMessage } from './response'

const configuredBaseURL = import.meta.env.VITE_API_BASE_URL?.trim()
const apiBaseURL = configuredBaseURL || 'http://127.0.0.1:8080/api'

const request = axios.create({
  baseURL: apiBaseURL,
  timeout: 30000
})

request.interceptors.request.use((config) => {
  const auth = useAuthStore()
  const url = String(config.url || '')
  const isAuthRequest = url.includes('/auth/login') || url.includes('/auth/register')

  if (auth.token && !isAuthRequest) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

request.interceptors.response.use(
  (res) => {
    const payload = res.data
    const code = Number(payload?.code)

    if (code === 401) {
      useAuthStore().clearAuth()
      return Promise.reject(new Error(getErrorMessage({ response: { data: payload } }, '登录已过期，请重新登录')))
    }

    if (code !== 200) {
      return Promise.reject(new Error(getErrorMessage({ response: { data: payload } }, '请求失败')))
    }

    return payload
  },
  (error) => {
    if (error?.response?.status === 401) {
      useAuthStore().clearAuth()
    }
    return Promise.reject(new Error(getErrorMessage(error, '请求失败')))
  }
)

export default request
