<template>
  <main class="login-page">
    <section class="login-shell">
      <div class="login-brand">
        <div class="brand-mark">
          <el-icon><FirstAidKit /></el-icon>
          <span>ClinicSafe Pharmacy</span>
        </div>
        <h1>诊所药房药品批次与效期预警系统</h1>
        <p>围绕到货入库、批次上架、处方领用、库存盘点和补货审批，帮助小型药房把药品安全管理落到每日流程。</p>
        <div class="brand-grid">
          <div>
            <strong>90天</strong>
            <span>近效期主动预警</span>
          </div>
          <div>
            <strong>FEFO</strong>
            <span>优先扣减近效批次</span>
          </div>
          <div>
            <strong>全链路</strong>
            <span>入库、领用、盘点闭环</span>
          </div>
        </div>
        <div class="workflow-strip">
          <span>药品到货</span>
          <el-icon><Right /></el-icon>
          <span>批次入库</span>
          <el-icon><Right /></el-icon>
          <span>处方领用</span>
          <el-icon><Right /></el-icon>
          <span>效期预警</span>
        </div>
      </div>

      <div class="login-panel">
        <div class="form-head">
          <span>安全登录</span>
          <h2>进入药房工作台</h2>
        </div>
        <el-form ref="loginFormRef" :model="form" :rules="rules" label-position="top" @keyup.enter="submitLogin">
          <el-form-item label="用户名" prop="username">
            <el-input v-model.trim="form.username" size="large" placeholder="请输入用户名" autocomplete="username" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" size="large" type="password" placeholder="请输入密码" autocomplete="current-password" show-password />
          </el-form-item>
          <el-button class="login-button" size="large" type="primary" :loading="loading" @click="submitLogin">登录系统</el-button>
        </el-form>
      </div>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { z } from 'zod'
import { useAuthStore } from '../store'

const router = useRouter()
const auth = useAuthStore()
const loginFormRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const loginSchema = z.object({
  username: z.string().min(2, '请输入至少2位用户名'),
  password: z.string().min(6, '请输入至少6位密码')
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function submitLogin() {
  const result = loginSchema.safeParse(form)
  if (!result.success) {
    ElMessage.warning(result.error.issues[0].message)
    return
  }
  await loginFormRef.value.validate()
  loading.value = true
  try {
    await auth.login({ ...form })
    ElMessage.success('登录成功')
    router.replace('/dashboard')
  } catch (error) {
  } finally {
    loading.value = false
  }
}
</script>
