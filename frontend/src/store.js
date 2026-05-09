import { defineStore } from 'pinia'
import { api } from './api'

export const roleNames = {
  admin: '系统管理员',
  pharmacist: '药房管理员',
  doctor: '医生',
  purchaser: '采购员'
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token),
    roleName: (state) => roleNames[state.user?.role] || '未登录'
  },
  actions: {
    setSession(data) {
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('token', this.token)
      localStorage.setItem('user', JSON.stringify(this.user))
    },
    async login(payload) {
      const data = await api.login(payload)
      this.setSession(data)
    },
    async refreshMe() {
      const user = await api.me()
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
