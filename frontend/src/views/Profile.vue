<template>
  <div>
    <PageHeader title="个人中心" description="维护当前账号资料与登录密码，资料保存后顶部账号信息会同步更新。" />
    <div class="profile-grid">
      <ToolbarCard>
        <h2>基本资料</h2>
        <el-form ref="profileRef" :model="profile" :rules="profileRules" label-position="top" class="profile-form">
          <el-form-item label="用户名"><el-input :model-value="auth.user?.username" disabled /></el-form-item>
          <el-form-item label="角色"><el-input :model-value="auth.roleName" disabled /></el-form-item>
          <el-form-item label="姓名" prop="nickname"><el-input v-model.trim="profile.nickname" /></el-form-item>
          <el-form-item label="手机号" prop="phone"><el-input v-model.trim="profile.phone" /></el-form-item>
          <el-form-item label="邮箱" prop="email"><el-input v-model.trim="profile.email" /></el-form-item>
          <el-button type="primary" :loading="savingProfile" @click="saveProfile">保存资料</el-button>
        </el-form>
      </ToolbarCard>
      <ToolbarCard>
        <h2>修改密码</h2>
        <el-form ref="passwordRef" :model="passwordForm" :rules="passwordRules" label-position="top" class="profile-form">
          <el-form-item label="原密码" prop="old_password"><el-input v-model="passwordForm.old_password" type="password" show-password /></el-form-item>
          <el-form-item label="新密码" prop="new_password"><el-input v-model="passwordForm.new_password" type="password" show-password /></el-form-item>
          <el-button type="primary" :loading="savingPassword" @click="savePassword">更新密码</el-button>
        </el-form>
      </ToolbarCard>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { z } from 'zod'
import PageHeader from '../components/PageHeader.vue'
import ToolbarCard from '../components/ToolbarCard.vue'
import { api } from '../api'
import { useAuthStore } from '../store'

const auth = useAuthStore()
const profileRef = ref()
const passwordRef = ref()
const savingProfile = ref(false)
const savingPassword = ref(false)
const profile = reactive({ nickname: auth.user?.nickname || '', phone: auth.user?.phone || '', email: auth.user?.email || '' })
const passwordForm = reactive({ old_password: '', new_password: '' })
const profileSchema = z.object({
  email: z.string().email('邮箱格式不正确').or(z.literal('')).optional(),
  phone: z.string().regex(/^$|^[0-9+\-\s]{6,20}$/, '手机号格式不正确').optional()
})
const profileRules = { nickname: [{ required: true, message: '请输入姓名', trigger: 'blur' }] }
const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }, { min: 6, message: '原密码至少6位', trigger: 'blur' }],
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '新密码至少6位', trigger: 'blur' }]
}
async function saveProfile() {
  const result = profileSchema.safeParse(profile)
  if (!result.success) return ElMessage.warning(result.error.issues[0].message)
  await profileRef.value.validate()
  savingProfile.value = true
  try {
    const user = await api.updateProfile(profile)
    auth.user = user
    localStorage.setItem('user', JSON.stringify(user))
    ElMessage.success('资料已保存')
  } catch (error) {} finally { savingProfile.value = false }
}
async function savePassword() {
  await passwordRef.value.validate()
  savingPassword.value = true
  try {
    await api.changePassword(passwordForm)
    Object.assign(passwordForm, { old_password: '', new_password: '' })
    ElMessage.success('密码已更新')
  } catch (error) {} finally { savingPassword.value = false }
}
</script>
