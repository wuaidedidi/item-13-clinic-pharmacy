<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="logo-icon"><el-icon><FirstAidKit /></el-icon></div>
        <div>
          <strong>药房效期管控</strong>
          <span>{{ auth.roleName }}</span>
        </div>
      </div>
      <nav class="nav-list">
        <router-link v-for="item in visibleMenus" :key="item.path" :to="item.path" class="nav-item">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
    </aside>
    <div class="main-column">
      <header class="topbar">
        <div>
          <strong>{{ currentTitle }}</strong>
          <span>{{ todayText }}</span>
        </div>
        <el-dropdown>
          <button class="user-chip">
            <el-icon><User /></el-icon>
            <span>{{ auth.user?.nickname }}</span>
            <el-icon><ArrowDown /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
              <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </header>
      <main class="content-area">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { menuItems } from '../router'
import { useAuthStore } from '../store'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const visibleMenus = computed(() => menuItems.filter((item) => item.roles.includes(auth.user?.role)))
const currentTitle = computed(() => menuItems.find((item) => item.path === route.path)?.label || '药房看板')
const todayText = new Intl.DateTimeFormat('zh-CN', { dateStyle: 'full' }).format(new Date())

function logout() {
  auth.logout()
  router.replace('/login')
}
</script>
