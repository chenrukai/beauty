export interface ApiEnvelope<T = unknown> {
  code?: number
  message?: string
  msg?: string
  data?: T
}

export function unwrapData<T = any>(payload: any, fallback: T): T {
  if (payload == null) return fallback
  if (payload && typeof payload === 'object' && 'data' in payload) {
    const value = (payload as ApiEnvelope<T>).data
    return (value ?? fallback) as T
  }
  return (payload as T) ?? fallback
}

export function getErrorMessage(error: any, fallback = '请求失败'): string {
  const msgFromResponse =
    error?.response?.data?.message ||
    error?.response?.data?.msg ||
    error?.response?.data?.data?.message ||
    error?.response?.data?.data?.msg
  const msg = msgFromResponse || error?.message || fallback
  return String(msg || fallback)
}

