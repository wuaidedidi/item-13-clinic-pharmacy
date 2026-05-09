import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from './router'

const recentMessages = new Set()

export function showError(message) {
  if (!message || recentMessages.has(message)) return
  recentMessages.add(message)
  setTimeout(() => recentMessages.delete(message), 2000)
  ElMessage.error({ message, grouping: true })
}

const http = axios.create({
  baseURL: '/',
  timeout: 12000
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res && typeof res.code !== 'undefined') {
      if (res.code !== 200) {
        const message = res.message || '请求失败'
        showError(message)
        if (res.code === 401) {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          router.replace('/login')
        }
        const error = new Error(message)
        error._isBusinessError = true
        return Promise.reject(error)
      }
      return res.data
    }
    return response.data
  },
  (error) => {
    if (error._isBusinessError) return Promise.reject(error)
    const message = error.response?.data?.message || (error.response ? '服务器错误，请稍后重试' : '网络错误，请检查网络连接')
    showError(message)
    return Promise.reject(error)
  }
)

export default http

export const api = {
  login: (data) => http.post('/auth/login', data),
  register: (data) => http.post('/auth/register', data),
  me: () => http.get('/auth/me'),
  updateProfile: (data) => http.put('/auth/profile', data),
  changePassword: (data) => http.put('/auth/password', data),
  dashboard: () => http.get('/api/dashboard'),
  medicines: () => http.get('/api/medicines'),
  createMedicine: (data) => http.post('/api/medicines', data),
  updateMedicine: (id, data) => http.put(`/api/medicines/${id}`, data),
  deleteMedicine: (id) => http.delete(`/api/medicines/${id}`),
  suppliers: () => http.get('/api/suppliers'),
  createSupplier: (data) => http.post('/api/suppliers', data),
  updateSupplier: (id, data) => http.put(`/api/suppliers/${id}`, data),
  deleteSupplier: (id) => http.delete(`/api/suppliers/${id}`),
  batches: () => http.get('/api/batches'),
  inbounds: () => http.get('/api/inbounds'),
  createInbound: (data) => http.post('/api/inbounds', data),
  prescriptions: () => http.get('/api/prescriptions'),
  issuePrescription: (data) => http.post('/api/prescriptions', data),
  warnings: () => http.get('/api/warnings'),
  stockCounts: () => http.get('/api/stock-counts'),
  createStockCount: (data) => http.post('/api/stock-counts', data),
  adjustments: () => http.get('/api/adjustments'),
  approveAdjustment: (id) => http.put(`/api/adjustments/${id}/approve`),
  purchases: () => http.get('/api/purchases'),
  createPurchase: (data) => http.post('/api/purchases', data),
  approvePurchase: (id) => http.put(`/api/purchases/${id}/approve`)
}
