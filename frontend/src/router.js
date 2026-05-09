import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './store'
import Login from './views/Login.vue'
import Layout from './views/Layout.vue'
import Dashboard from './views/Dashboard.vue'
import Medicines from './views/Medicines.vue'
import Batches from './views/Batches.vue'
import Inbounds from './views/Inbounds.vue'
import Prescriptions from './views/Prescriptions.vue'
import Warnings from './views/Warnings.vue'
import StockCounts from './views/StockCounts.vue'
import Purchases from './views/Purchases.vue'
import Suppliers from './views/Suppliers.vue'
import Profile from './views/Profile.vue'

export const menuItems = [
  { path: '/dashboard', label: '药房看板', icon: 'DataBoard', roles: ['admin', 'pharmacist', 'doctor', 'purchaser'] },
  { path: '/medicines', label: '药品目录', icon: 'Collection', roles: ['admin', 'pharmacist', 'doctor', 'purchaser'] },
  { path: '/batches', label: '批次效期', icon: 'Tickets', roles: ['admin', 'pharmacist', 'doctor', 'purchaser'] },
  { path: '/inbounds', label: '批次入库', icon: 'Box', roles: ['admin', 'pharmacist', 'purchaser'] },
  { path: '/prescriptions', label: '处方领用', icon: 'FirstAidKit', roles: ['admin', 'pharmacist', 'doctor'] },
  { path: '/warnings', label: '效期预警', icon: 'Bell', roles: ['admin', 'pharmacist', 'doctor', 'purchaser'] },
  { path: '/stock-counts', label: '库存盘点', icon: 'Checked', roles: ['admin', 'pharmacist'] },
  { path: '/purchases', label: '采购补货', icon: 'ShoppingCart', roles: ['admin', 'pharmacist', 'purchaser'] },
  { path: '/suppliers', label: '供应商', icon: 'OfficeBuilding', roles: ['admin', 'pharmacist', 'purchaser'] },
  { path: '/profile', label: '个人中心', icon: 'User', roles: ['admin', 'pharmacist', 'doctor', 'purchaser'] }
]

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    {
      path: '/',
      component: Layout,
      redirect: '/dashboard',
      children: [
        { path: 'dashboard', component: Dashboard },
        { path: 'medicines', component: Medicines },
        { path: 'batches', component: Batches },
        { path: 'inbounds', component: Inbounds },
        { path: 'prescriptions', component: Prescriptions },
        { path: 'warnings', component: Warnings },
        { path: 'stock-counts', component: StockCounts },
        { path: 'purchases', component: Purchases },
        { path: 'suppliers', component: Suppliers },
        { path: 'profile', component: Profile }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.path !== '/login' && !auth.isLoggedIn) return '/login'
  if (to.path === '/login' && auth.isLoggedIn) return '/dashboard'
  const userRole = auth.user?.role
  const item = menuItems.find((menu) => menu.path === to.path)
  if (item && userRole && !item.roles.includes(userRole)) return '/dashboard'
})

export default router
