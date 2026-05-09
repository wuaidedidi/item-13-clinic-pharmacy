<template>
  <div>
    <PageHeader title="供应商管理" description="维护药品配送渠道、联系人和供应范围，支撑入库与补货流程。">
      <el-button type="primary" :icon="Plus" @click="openDialog()">新增供应商</el-button>
    </PageHeader>
    <ToolbarCard>
      <el-table :data="rows" stripe class="business-table" v-loading="loading">
        <el-table-column prop="name" label="供应商名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="contact_person" label="联系人" width="110" />
        <el-table-column prop="phone" label="电话" min-width="130" />
        <el-table-column prop="email" label="邮箱" min-width="170" show-overflow-tooltip />
        <el-table-column prop="supply_scope" label="供应范围" min-width="180" show-overflow-tooltip />
        <el-table-column prop="address" label="地址" min-width="220" show-overflow-tooltip />
        <el-table-column label="状态" width="90"><template #default="{ row }"><StatusTag :value="row.status" /></template></el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </ToolbarCard>
    <el-dialog v-model="visible" :title="form.id ? '编辑供应商' : '新增供应商'" width="720px" class="form-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="two-col-form">
        <el-form-item label="供应商名称" prop="name"><el-input v-model.trim="form.name" /></el-form-item>
        <el-form-item label="联系人" prop="contact_person"><el-input v-model.trim="form.contact_person" /></el-form-item>
        <el-form-item label="联系电话" prop="phone"><el-input v-model.trim="form.phone" /></el-form-item>
        <el-form-item label="邮箱" prop="email"><el-input v-model.trim="form.email" /></el-form-item>
        <el-form-item label="供应范围" prop="supply_scope"><el-input v-model.trim="form.supply_scope" /></el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status"><el-option label="启用" value="active" /><el-option label="停用" value="inactive" /></el-select>
        </el-form-item>
        <el-form-item label="地址" prop="address" class="span-2"><el-input v-model.trim="form.address" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { z } from 'zod'
import PageHeader from '../components/PageHeader.vue'
import ToolbarCard from '../components/ToolbarCard.vue'
import StatusTag from '../components/StatusTag.vue'
import { api } from '../api'

const rows = ref([])
const loading = ref(false)
const saving = ref(false)
const visible = ref(false)
const formRef = ref()
const form = reactive(defaultForm())
function defaultForm() { return { id: null, name: '', contact_person: '', phone: '', email: '', address: '', supply_scope: '', status: 'active' } }
const schema = z.object({ email: z.string().email('邮箱格式不正确').or(z.literal('')).optional() })
const rules = {
  name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  contact_person: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  address: [{ required: true, message: '请输入地址', trigger: 'blur' }],
  supply_scope: [{ required: true, message: '请输入供应范围', trigger: 'blur' }]
}
async function loadData() { loading.value = true; try { rows.value = await api.suppliers() } finally { loading.value = false } }
function openDialog(row) { Object.assign(form, defaultForm(), row || {}); visible.value = true }
async function save() {
  const result = schema.safeParse(form)
  if (!result.success) return ElMessage.warning(result.error.issues[0].message)
  await formRef.value.validate()
  saving.value = true
  try {
    if (form.id) await api.updateSupplier(form.id, form)
    else await api.createSupplier(form)
    ElMessage.success('保存成功')
    visible.value = false
    await loadData()
  } catch (error) {} finally { saving.value = false }
}
async function remove(row) {
  try {
    await ElMessageBox.confirm(`确认删除 ${row.name} 吗？`, '删除供应商', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
    await api.deleteSupplier(row.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {}
}
onMounted(loadData)
</script>
