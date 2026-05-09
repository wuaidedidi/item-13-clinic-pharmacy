<template>
  <div>
    <PageHeader title="处方领用管理" description="登记门诊处方领用，系统按近效期优先原则扣减可用批次库存。">
      <el-button type="primary" :icon="Plus" @click="openDialog">新增领用</el-button>
    </PageHeader>
    <ToolbarCard>
      <el-table :data="rows" stripe class="business-table" v-loading="loading">
        <el-table-column prop="issue_no" label="领用单号" min-width="160" />
        <el-table-column prop="patient_name" label="患者" width="110" />
        <el-table-column prop="doctor_name" label="医生" width="110" />
        <el-table-column prop="total_amount" label="金额" width="110" />
        <el-table-column prop="issued_at" label="领用时间" min-width="170" />
        <el-table-column label="状态" width="90"><template #default="{ row }"><StatusTag :value="row.status" /></template></el-table-column>
        <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
      </el-table>
    </ToolbarCard>
    <el-dialog v-model="visible" title="新增处方领用" width="680px" class="form-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="two-col-form">
        <el-form-item label="患者姓名" prop="patient_name"><el-input v-model.trim="form.patient_name" /></el-form-item>
        <el-form-item label="医生姓名" prop="doctor_name"><el-input v-model.trim="form.doctor_name" /></el-form-item>
        <el-form-item label="领用药品" prop="medicine_id">
          <el-select v-model="form.medicine_id" filterable placeholder="请选择药品">
            <el-option v-for="item in medicines" :key="item.id" :label="`${item.name} 库存${item.currentStock}`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="领用数量" prop="quantity"><el-input-number v-model="form.quantity" :min="1" /></el-form-item>
        <el-form-item label="单价" prop="unit_price"><el-input-number v-model="form.unit_price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="备注" prop="remark"><el-input v-model.trim="form.remark" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">确认领用</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'
import ToolbarCard from '../components/ToolbarCard.vue'
import StatusTag from '../components/StatusTag.vue'
import { api } from '../api'

const rows = ref([])
const medicines = ref([])
const loading = ref(false)
const saving = ref(false)
const visible = ref(false)
const formRef = ref()
const form = reactive({ patient_name: '', doctor_name: '', medicine_id: null, quantity: 1, unit_price: 0, remark: '' })
const rules = {
  patient_name: [{ required: true, message: '请输入患者姓名', trigger: 'blur' }],
  doctor_name: [{ required: true, message: '请输入医生姓名', trigger: 'blur' }],
  medicine_id: [{ required: true, message: '请选择药品', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入领用数量', trigger: 'change' }]
}
watch(() => form.medicine_id, (id) => {
  const item = medicines.value.find((m) => m.id === id)
  if (item) form.unit_price = Number(item.sellingPrice)
})
async function loadData() {
  loading.value = true
  try { ;[rows.value, medicines.value] = await Promise.all([api.prescriptions(), api.medicines()]) } finally { loading.value = false }
}
function openDialog() { Object.assign(form, { patient_name: '', doctor_name: '', medicine_id: null, quantity: 1, unit_price: 0, remark: '' }); visible.value = true }
async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    await api.issuePrescription(form)
    ElMessage.success('领用成功')
    visible.value = false
    await loadData()
  } catch (error) {} finally { saving.value = false }
}
onMounted(loadData)
</script>
